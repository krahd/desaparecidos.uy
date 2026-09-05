"""Causal, abstaining region search. No source identity or colour descriptors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from PIL import Image

from .pipeline_core import AssemblyResult, TilePlacement

ReconstructionMode = Literal["fixed", "largest-first", "refine"]


@dataclass(frozen=True)
class StructuralSettings:
    reconstruction_mode: ReconstructionMode = "refine"
    max_region_size: int = 384
    structure_threshold: float = 0.82
    min_structure: float = 0.035
    refinement_margin: float = 0.04
    structure_scale: str = "broad"
    tone_mode: str = "source"
    contribution_interval: int = 6
    search_similarity: float = 0.95

    def __post_init__(self) -> None:
        if self.contribution_interval < 1:
            raise ValueError("contribution interval must be at least one encounter")
        if not 0 <= self.search_similarity <= 1:
            raise ValueError("search similarity must be in [0, 1]")
        if self.reconstruction_mode not in {"fixed", "largest-first", "refine"}:
            raise ValueError("unsupported reconstruction mode")
        if self.max_region_size < 8:
            raise ValueError("maximum region size must be at least 8")
        if not 0 < self.structure_threshold <= 1 or not 0 < self.min_structure <= 1:
            raise ValueError("structure thresholds must be in (0, 1]")
        if not 0 <= self.refinement_margin <= 1:
            raise ValueError("refinement margin must be in [0, 1]")
        if self.structure_scale not in {"broad", "fine"}:
            raise ValueError("unsupported structure scale")
        if self.tone_mode not in {"source", "match-region"}:
            raise ValueError("unsupported region tone mode")


def structure_descriptor(image: Image.Image, *, samples: int = 16) -> tuple[np.ndarray, float]:
    """Compare normalised light/dark organisation and signed directional edges.

    Constant brightness and contrast offsets cannot create a match. Flat regions
    have no usable structure; their descriptor is explicitly zero.
    """
    a = np.asarray(image.convert("L").resize((samples, samples), Image.Resampling.BILINEAR), dtype=np.float32) / 255
    contrast = float(a.std())
    gx, gy = np.diff(a, axis=1), np.diff(a, axis=0)
    strength = min(contrast, float(np.sqrt(np.mean(gx * gx) + np.mean(gy * gy))))
    parts = [a - a.mean(), gx, gy]
    vectors = [p.ravel() / max(float(np.linalg.norm(p)), 1e-8) for p in parts]
    vector = np.concatenate([vectors[0] * 0.5, vectors[1], vectors[2]])
    vector /= max(float(np.linalg.norm(vector)), 1e-8)
    if strength < 1e-8:
        vector.fill(0)
    return vector, strength


def _starts(length: int, size: int, step: int) -> list[int]:
    return sorted({*range(0, length - size + 1, max(1, step)), length - size})


def match_region_tone(patch: Image.Image, target: Image.Image) -> tuple[Image.Image, dict[str, float]]:
    """Adjust one accepted source crop's exposure, without adding target pixels."""
    source_levels = np.asarray(patch.convert("L").resize((32, 32), Image.Resampling.BILINEAR), dtype=np.float32)
    target_levels = np.asarray(target.convert("L").resize((32, 32), Image.Resampling.BILINEAR), dtype=np.float32)
    gain = float(np.clip(target_levels.std() / max(float(source_levels.std()), 1.0), 0.25, 4.0))
    offset = float(target_levels.mean() - gain * source_levels.mean())
    pixels = np.asarray(patch.convert("L"), dtype=np.float32) * gain + offset
    adjusted = Image.fromarray(np.clip(pixels, 0, 255).round().astype(np.uint8)).convert("RGB")
    return adjusted, {"gain": gain, "offset": offset, "clipped_fraction": float(((pixels < 0) | (pixels > 255)).mean())}


def search_regions(target: Image.Image, frames: list[dict[str, Any]], settings: Any):
    """Return a replayable event per accepted frame, including replacement events.

    Candidate rectangles form a bounded multiscale lattice. Larger accepted
    uncovered rectangles take precedence. Refinements must improve every covered region;
    untouched areas stay black, even when the walk runs out of frames.
    """
    if settings.fragment_size < 8 or settings.max_region_size < settings.fragment_size:
        raise ValueError("region sizes require 8 <= minimum <= maximum")
    target = target.convert("L").convert("RGB")
    def describe(image: Image.Image):
        return structure_descriptor(image, samples=8 if settings.structure_scale == "broad" else 16)
    minimum = min(settings.fragment_size, target.width, target.height)
    sizes = [minimum]
    if settings.reconstruction_mode != "fixed":
        while sizes[-1] * 2 <= min(settings.max_region_size, max(target.size)):
            sizes.append(sizes[-1] * 2)
    shapes = {(s, s) for s in sizes}
    if settings.reconstruction_mode != "fixed":
        shapes |= {(s, s * 2) for s in sizes if s * 2 <= settings.max_region_size}
        shapes |= {(s * 2, s) for s in sizes if s * 2 <= settings.max_region_size}
    shapes = sorted((p for p in shapes if p[0] <= target.width and p[1] <= target.height), key=lambda p: (-p[0] * p[1], p))
    regions: dict[tuple[int, int], tuple[list[tuple[int, int]], np.ndarray]] = {}
    for w, h in shapes:
        positions, descriptors = [], []
        for y in _starts(target.height, h, minimum):
            for x in _starts(target.width, w, minimum):
                descriptor, strength = describe(target.crop((x, y, x + w, y + h)))
                if strength >= settings.min_structure:
                    positions.append((x, y))
                    descriptors.append(descriptor)
        if positions:
            regions[w, h] = positions, np.stack(descriptors)

    quality = np.full((target.height, target.width), -np.inf, dtype=np.float32)
    output = Image.new("RGB", target.size, 0)
    placements, encounters, decisions = [], [], []
    used_sources: set[str] = set()
    next_contribution = settings.contribution_interval - 1
    target_descriptor, _ = describe(target)
    for frame_index, frame in enumerate(frames):
        source_id = str(frame["id"])
        decision: dict[str, Any] = {"frame_index": frame_index, "source_id": source_id, "action": "skip", "reason": "no-structural-match", "best_similarity": None}
        if source_id in used_sources:
            decision["reason"] = "source-already-contributed"
            decisions.append(decision)
            continue
        if frame_index < next_contribution:
            decision["reason"] = "contribution-spacing"
            decisions.append(decision)
            continue
        with Image.open(str(frame["local_path"])) as raw:
            source = raw.convert("L").convert("RGB")
        best = None
        for (w, h), (positions, descriptors) in regions.items():
            eligible = []
            for i, (x, y) in enumerate(positions):
                q = quality[y:y + h, x:x + w]
                if settings.reconstruction_mode == "refine" or not np.isfinite(q).any():
                    eligible.append(i)
            if not eligible:
                continue
            # Two source scales preserve a region's aspect ratio; no stretching.
            candidates, vectors = [], []
            fit = min(1.0, source.width / w, source.height / h)
            source_sizes = sorted({(round(w * fit * scale), round(h * fit * scale)) for scale in (1.0, 0.5)})
            for sw, sh in source_sizes:
                if min(sw, sh) < 8 or sw > source.width or sh > source.height:
                    continue
                xs, ys = _starts(source.width, sw, max(sw // 2, source.width // 12)), _starts(source.height, sh, max(sh // 2, source.height // 12))
                for sy in ys:
                    for sx in xs:
                        crop = source.crop((sx, sy, sx + sw, sy + sh))
                        descriptor, strength = describe(crop)
                        if strength >= settings.min_structure:
                            candidates.append((sx, sy, sw, sh))
                            vectors.append(descriptor)
            if not candidates:
                continue
            scores = descriptors[eligible] @ np.stack(vectors).T
            best_similarity = round(float(scores.max()), 6)
            if decision["best_similarity"] is None or best_similarity > decision["best_similarity"]:
                decision["best_similarity"] = best_similarity
            for row_index, region_index in enumerate(eligible):
                ci = int(scores[row_index].argmax())
                score = float(scores[row_index, ci])
                if score < settings.structure_threshold:
                    continue
                x, y = positions[region_index]
                q = quality[y:y + h, x:x + w]
                occupied = np.isfinite(q)
                if occupied.any():
                    # Compare at the same spatial scale, including earlier
                    # subregion replacements, so a coarse score cannot hide damage.
                    previous, strength = describe(output.crop((x, y, x + w, y + h)))
                    old_score = float(previous @ descriptors[region_index]) if strength else 0.0
                    if score < max(old_score, float(q[occupied].max())) + settings.refinement_margin:
                        continue
                # Spend a useful encounter on missing structure before polishing
                # an already occupied area. Area still controls the coarse-to-fine search.
                rank = (int((~occupied).sum()), w * h, score)
                if best is None or rank > best[0]:
                    best = (rank, x, y, w, h, candidates[ci], bool(occupied.any()))
            if best is not None and w * h < best[0][0]:
                break
        if best is not None:
            (_, _, score), x, y, w, h, (sx, sy, sw, sh), refining = best
            patch = source.crop((sx, sy, sx + sw, sy + sh)).resize((w, h), Image.Resampling.LANCZOS)
            if settings.tone_mode == "match-region":
                patch, transform = match_region_tone(patch, target.crop((x, y, x + w, y + h)))
                decision["tone_transform"] = transform
            placement = TilePlacement(source_id, f"{source_id}:{sx}:{sy}:{sw}:{sh}", patch, x, y, sx, sy, sw, sh)
            output.paste(patch, (x, y))
            quality[y:y + h, x:x + w] = score
            placements.append(placement)
            encounters.append(frame_index)
            used_sources.add(source_id)
            next_contribution = frame_index + settings.contribution_interval
            decision.update(action="refine" if refining else "place", reason="accepted-structure", score=round(score, 6), target_rect=[x, y, w, h], source_rect=[sx, sy, sw, sh], placement_index=len(placements) - 1)
        decisions.append(decision)
        if best is not None:
            descriptor, _ = describe(output)
            similarity = float(np.clip(descriptor @ target_descriptor, 0, 1))
            tonal_similarity = 1 - float(np.abs(np.asarray(output, dtype=np.float32) - np.asarray(target, dtype=np.float32)).mean()) / 255
            similarity = min(similarity, tonal_similarity)
            coverage = float(np.isfinite(quality).mean())
            decision.update(reconstruction_similarity=similarity, coverage=coverage)
            if settings.search_similarity > 0 and coverage == 1.0 and similarity >= settings.search_similarity:
                decision["stop_reason"] = "quality-target-reached"
                break
    if decisions and "stop_reason" not in decisions[-1]:
        decisions[-1]["stop_reason"] = "approved-frames-exhausted"
    result = AssemblyResult(output, target, {p.source_id: 1 for p in placements}, {p.fragment_id: 1 for p in placements}, placements)
    return result, encounters, decisions, float(np.isfinite(quality).mean())
