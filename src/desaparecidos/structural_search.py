"""Causal, abstaining region search. No source identity or colour descriptors."""
from __future__ import annotations

import logging
import math

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
    completion_structure_threshold: float = 0.45
    min_structure: float = 0.035
    refinement_margin: float = 0.04
    structure_scale: str = "broad"
    tone_mode: str = "source"
    finding_interval: int = 1
    contribution_interval: int = 6
    search_source_contribution_cap: int = 1
    search_similarity: float = 0.95
    require_complete: bool = True
    full_refinement_budget: bool = False
    max_search_batches: int = 8
    search_budget_seconds: int = 300

    def __post_init__(self) -> None:
        if not 0 <= self.max_search_batches <= 32 or self.search_budget_seconds < 1:
            raise ValueError("search batches must be in [0, 32] and playback budget positive")
        if self.finding_interval < 1 or self.contribution_interval < 1:
            raise ValueError("finding and contribution intervals must be at least one encounter")
        if self.search_source_contribution_cap < 1:
            raise ValueError("search source contribution cap must be at least one")
        if not 0 <= self.search_similarity <= 1:
            raise ValueError("search similarity must be in [0, 1]")
        if self.reconstruction_mode not in {"fixed", "largest-first", "refine"}:
            raise ValueError("unsupported reconstruction mode")
        if self.max_region_size < 8:
            raise ValueError("maximum region size must be at least 8")
        if not 0 < self.structure_threshold <= 1 or not 0 < self.min_structure <= 1:
            raise ValueError("structure thresholds must be in (0, 1]")
        if not 0 < self.completion_structure_threshold <= 1:
            raise ValueError("completion threshold must be in (0, 1]")
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


def _dense_source_candidates(source: Image.Image, sw: int, sh: int, samples: int):
    """Bounded dense descriptor bank, followed by native verification on use."""
    aw, ah = round(source.width * samples / sw), round(source.height * samples / sh)
    if min(aw, ah) < samples or max(aw, ah) > 128:
        return None
    levels = np.asarray(source.convert('L').resize((aw, ah), Image.Resampling.BILINEAR), dtype=np.float32) / 255
    windows = np.lib.stride_tricks.sliding_window_view(levels, (samples, samples)).reshape(-1, samples, samples)
    gx, gy = np.diff(windows, axis=2), np.diff(windows, axis=1)
    strengths = np.minimum(windows.std(axis=(1, 2)), np.sqrt((gx * gx).mean(axis=(1, 2)) + (gy * gy).mean(axis=(1, 2))))
    parts = [windows - windows.mean(axis=(1, 2), keepdims=True), gx, gy]
    vectors = []
    for i, part in enumerate(parts):
        flat = part.reshape(len(windows), -1)
        vectors.append(flat / np.maximum(np.linalg.norm(flat, axis=1, keepdims=True), 1e-8) * (0.5 if i == 0 else 1))
    vectors = np.concatenate(vectors, axis=1)
    vectors /= np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-8)
    rects = []
    for y in range(ah - samples + 1):
        for x in range(aw - samples + 1):
            sx, sy = round(x * source.width / aw), round(y * source.height / ah)
            ex, ey = round((x + samples) * source.width / aw), round((y + samples) * source.height / ah)
            rects.append((sx, sy, ex - sx, ey - sy))
    return rects, vectors, strengths


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
    used_sources: dict[str, int] = {}
    source_cap = max(1, int(getattr(settings, "search_source_contribution_cap", 1)))
    target_descriptor, _ = describe(target)
    coverage = 0.0
    last_contribution_index = -settings.finding_interval
    refinement_budget = max(1, math.ceil(settings.search_budget_seconds / settings.scan_seconds))
    for frame_index, frame in enumerate(frames):
        if (
            settings.require_complete
            and settings.full_refinement_budget
            and coverage == 1.0
            and frame_index >= refinement_budget
        ):
            decisions[-1]['stop_reason'] = 'reconstruction-complete'
            break
        if frame_index % 100 == 0:
            logging.getLogger(__name__).info("Search %s/%s encounters; %.1f%% covered", frame_index, len(frames), 100 * np.isfinite(quality).mean())
        source_id = str(frame["id"])
        manifest_source_id = str(frame.get("manifest_source_id", frame.get("source_id", source_id)))
        decision: dict[str, Any] = {
            "frame_index": frame_index,
            "source_id": source_id,
            "manifest_source_id": manifest_source_id,
            "action": "skip",
            "reason": "no-structural-match",
            "best_similarity": None,
        }
        match_threshold = settings.structure_threshold
        if settings.require_complete and coverage >= 0.95:
            match_threshold = min(
                settings.structure_threshold,
                settings.completion_structure_threshold,
            )
        decision["required_similarity"] = match_threshold
        decision["completion_threshold_active"] = match_threshold < settings.structure_threshold
        if frame_index - last_contribution_index < settings.finding_interval:
            decision["reason"] = "finding-interval"
            decisions.append(decision)
            continue
        if used_sources.get(manifest_source_id, 0) >= source_cap:
            decision["reason"] = "source-already-contributed"
            decisions.append(decision)
            continue
        if callable(frame.get("load_image")):
            source = frame["load_image"]().convert("L").convert("RGB")
        elif isinstance(frame.get("image"), Image.Image):
            source = frame["image"].convert("L").convert("RGB")
        else:
            with Image.open(str(frame["local_path"])) as raw:
                source = raw.convert("L").convert("RGB")
        # Descriptors have only 8/16 samples. A bounded analysis image avoids
        # repeatedly resampling megapixel crops; accepted candidates are checked
        # again at native resolution before placement.
        analysis_scale = min(1.0, 512 / max(source.size))
        analysis_source = source.resize((round(source.width * analysis_scale), round(source.height * analysis_scale)), Image.Resampling.BILINEAR) if analysis_scale < 1 else source
        best = None
        for (w, h), (positions, descriptors) in regions.items():
            eligible = []
            for i, (x, y) in enumerate(positions):
                q = quality[y:y + h, x:x + w]
                if settings.require_complete and coverage < 1.0 and np.isfinite(q).all():
                    continue
                if settings.reconstruction_mode == "refine" or not np.isfinite(q).any():
                    eligible.append(i)
            if not eligible:
                continue
            # Include wider source fields for difficult shapes without changing
            # the destination region size or its aspect ratio.
            candidates, vectors = [], []
            fit = min(1.0, source.width / w, source.height / h)
            full_fit = min(source.width / w, source.height / h)
            scales = {fit, fit * 0.5, *(full_fit * scale for scale in (0.125, 0.25, 0.5, 1.0))}
            source_sizes = sorted({(round(w * scale), round(h * scale)) for scale in scales})
            for sw, sh in source_sizes:
                if min(sw, sh) < 8 or sw > source.width or sh > source.height:
                    continue
                dense = _dense_source_candidates(source, sw, sh, 8 if settings.structure_scale == 'broad' else 16) if settings.require_complete else None
                if dense is not None:
                    rects, dense_vectors, strengths = dense
                    for i in np.flatnonzero(strengths >= settings.min_structure):
                        candidates.append(rects[i])
                        vectors.append(dense_vectors[i])
                    continue
                xs, ys = _starts(source.width, sw, max(sw // 2, source.width // 12)), _starts(source.height, sh, max(sh // 2, source.height // 12))
                for sy in ys:
                    for sx in xs:
                        crop = analysis_source.crop(tuple(round(v * analysis_scale) for v in (sx, sy, sx + sw, sy + sh)))
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
                # Refine promising coarse locations before rejecting a rare
                # missing-region match. Destination geometry never changes.
                if settings.require_complete and 0.6 <= score < match_threshold:
                    sx, sy, sw, sh = candidates[ci]
                    for fraction in (4, 8):
                        best_rect = (sx, sy, sw, sh)
                        for dy in (-max(1, sh // fraction), 0, max(1, sh // fraction)):
                            for dx in (-max(1, sw // fraction), 0, max(1, sw // fraction)):
                                nx, ny = min(max(0, sx + dx), source.width - sw), min(max(0, sy + dy), source.height - sh)
                                crop = analysis_source.crop(tuple(round(v * analysis_scale) for v in (nx, ny, nx + sw, ny + sh)))
                                vector, strength = describe(crop)
                                local_score = float(vector @ descriptors[region_index])
                                if strength >= settings.min_structure and local_score > score:
                                    score, best_rect = local_score, (nx, ny, sw, sh)
                        sx, sy, sw, sh = best_rect
                    candidates.append((sx, sy, sw, sh))
                    ci = len(candidates) - 1
                if score < match_threshold:
                    continue
                if analysis_scale < 1 or settings.require_complete:
                    sx, sy, sw, sh = candidates[ci]
                    native_descriptor, native_strength = describe(source.crop((sx, sy, sx + sw, sy + sh)))
                    score = float(native_descriptor @ descriptors[region_index])
                    if score < match_threshold or native_strength < settings.min_structure:
                        continue
                x, y = positions[region_index]
                q = quality[y:y + h, x:x + w]
                occupied = np.isfinite(q)
                if occupied.any():
                    if score < settings.structure_threshold:
                        continue
                    # The per-pixel best accepted score is a lower bound for
                    # the refinement threshold. Reject against it before the
                    # substantially more expensive composite-region descriptor.
                    quality_floor = float(q[occupied].max()) + settings.refinement_margin
                    if score < quality_floor:
                        continue
                    # Compare at the same spatial scale, including earlier
                    # subregion replacements, so a coarse score cannot hide damage.
                    previous, strength = describe(output.crop((x, y, x + w, y + h)))
                    old_score = float(previous @ descriptors[region_index]) if strength else 0.0
                    if score < old_score + settings.refinement_margin:
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
            placement = TilePlacement(
                source_id,
                f"{source_id}:{sx}:{sy}:{sw}:{sh}",
                patch,
                x,
                y,
                sx,
                sy,
                sw,
                sh,
                manifest_source_id,
            )
            output.paste(patch, (x, y))
            quality[y:y + h, x:x + w] = score
            placements.append(placement)
            encounters.append(frame_index)
            used_sources[manifest_source_id] = used_sources.get(manifest_source_id, 0) + 1
            last_contribution_index = frame_index
            decision.update(action="refine" if refining else "place", reason="accepted-structure", score=round(score, 6), target_rect=[x, y, w, h], source_rect=[sx, sy, sw, sh], placement_index=len(placements) - 1)
        decisions.append(decision)
        if best is not None:
            descriptor, _ = describe(output)
            similarity = float(np.clip(descriptor @ target_descriptor, 0, 1))
            tonal_similarity = 1 - float(np.abs(np.asarray(output, dtype=np.float32) - np.asarray(target, dtype=np.float32)).mean()) / 255
            similarity = min(similarity, tonal_similarity)
            coverage = float(np.isfinite(quality).mean())
            decision.update(reconstruction_similarity=similarity, coverage=coverage)
            quality_reached = (
                settings.search_similarity == 0
                or similarity >= settings.search_similarity
            )
            budget_reached = frame_index + 1 >= refinement_budget
            should_stop = (
                settings.require_complete
                and (
                    budget_reached
                    if settings.full_refinement_budget
                    else quality_reached or budget_reached
                )
            ) or (
                not settings.require_complete
                and settings.search_similarity > 0
                and quality_reached
            )
            if coverage == 1.0 and should_stop:
                decision["stop_reason"] = "reconstruction-complete" if settings.require_complete else "quality-target-reached"
                break
    if decisions and "stop_reason" not in decisions[-1]:
        decisions[-1]["stop_reason"] = "reconstruction-complete" if settings.require_complete and coverage == 1.0 else "approved-frames-exhausted"
    result = AssemblyResult(output, target, {p.source_id: 1 for p in placements}, {p.fragment_id: 1 for p in placements}, placements)
    return result, encounters, decisions, float(np.isfinite(quality).mean())
