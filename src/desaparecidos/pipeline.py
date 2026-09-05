from __future__ import annotations

"""Public Stage 1 pipeline with spatial matching and selectable composition.

The previous implementation is preserved in :mod:`desaparecidos.pipeline_core`.
This facade keeps its public API while adding artwork-oriented matching and
composition controls. Legacy behaviour remains available for benchmarks and
older callers.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
from PIL import Image

from . import pipeline_core as _core
from .images import Fragment, crop_from_row, descriptor_for, load_rgb
from .manifests import ManifestRow, row_file_path
from .search_video import VideoSettings
from .placement_history import ordered_target_positions, render_placements

# Preserve the complete historical public and test-facing surface, including
# intentionally private helpers used by the existing regression suite.
for _name in dir(_core):
    if _name not in globals():
        globals()[_name] = getattr(_core, _name)

CompositionMode = Literal["grid", "free"]
MatchingMode = Literal["legacy", "spatial"]


@dataclass(frozen=True)
class Stage1Settings(VideoSettings):
    seed: int = 17
    fragment_size: int = 24
    reuse_limit: int = 8
    output_width: int = 1920
    max_fragments_per_source: int = 240
    max_contribution_per_source: int = _core.DEFAULT_MAX_CONTRIBUTION_PER_SOURCE
    search_scan_frames_per_candidate: int = 2
    search_scan_max_candidates: int = 120
    video_source_layout: _core.VideoSourceLayout = "grid"
    make_video: bool = False
    composition_mode: CompositionMode = "grid"
    unique_tiles: bool = False
    matching_mode: MatchingMode = "legacy"
    colour_output: bool = False
    duration_seconds: int = 60
    fps: int = 24


def _spatial_descriptor_for(image: Image.Image) -> np.ndarray:
    """Describe the internal organisation of an image region.

    The earlier descriptor summarises a region through global colour, contrast,
    and edge magnitudes. That remains useful for controlled comparisons, but it
    can make source regions behave as enlarged pixels. Spatial mode retains a
    coarse map of colour, luminance, and directional changes, requiring a
    candidate region to match the target region's internal arrangement.
    """

    array = np.asarray(
        image.convert("RGB").resize((8, 8), Image.Resampling.BILINEAR),
        dtype=np.float32,
    ) / 255.0
    colour_blocks = array.reshape(4, 2, 4, 2, 3).mean(axis=(1, 3))
    luminance = (
        0.2126 * array[:, :, 0]
        + 0.7152 * array[:, :, 1]
        + 0.0722 * array[:, :, 2]
    )
    gradient_x = np.pad(np.diff(luminance, axis=1), ((0, 0), (0, 1)))
    gradient_y = np.pad(np.diff(luminance, axis=0), ((0, 1), (0, 0)))
    return np.concatenate(
        [
            colour_blocks.reshape(-1) * 1.5,
            luminance.reshape(-1),
            np.abs(gradient_x).reshape(-1) * 0.75,
            np.abs(gradient_y).reshape(-1) * 0.75,
        ]
    ).astype(np.float32)


def _matching_descriptor(image: Image.Image, mode: MatchingMode) -> np.ndarray:
    if mode == "legacy":
        return descriptor_for(image)
    if mode == "spatial":
        return _spatial_descriptor_for(image)
    raise ValueError(f"unsupported matching mode: {mode}")


def assemble_target_with_trace(
    target_row: ManifestRow,
    target_manifest: str | Path,
    fragments: list[Fragment],
    settings: Stage1Settings,
) -> _core.AssemblyResult:
    target = crop_from_row(load_rgb(row_file_path(target_row, target_manifest)), target_row)
    target = _core._target_canvas(target, settings.output_width, settings.fragment_size)

    import random

    rng = random.Random(settings.seed + sum(ord(char) for char in target_row.id))
    shuffled = list(fragments)
    rng.shuffle(shuffled)
    if not shuffled:
        raise ValueError("no approved source fragments are available")

    tile = settings.fragment_size
    tile_count = (target.width // tile) * (target.height // tile)
    source_count = len({fragment.source_id for fragment in shuffled})
    cap = max(0, settings.max_contribution_per_source)
    effective_reuse_limit = 1 if settings.unique_tiles else settings.reuse_limit

    if settings.unique_tiles and len(shuffled) < tile_count:
        raise ValueError(
            "unique tile pool is too small: "
            f"need {tile_count} distinct image regions but only {len(shuffled)} are available; "
            "approve or crawl more source images, increase tile size, or reduce output width"
        )

    error = _core._feasibility_error(
        tile_count,
        len(shuffled),
        effective_reuse_limit,
        source_count,
        cap,
    )
    if error:
        raise ValueError(error)

    descriptors = np.stack(
        [
            fragment.descriptor
            if settings.matching_mode == "legacy"
            else _spatial_descriptor_for(fragment.image)
            for fragment in shuffled
        ]
    ).astype(np.float32)

    source_keys: dict[str, int] = {}
    source_of = np.empty(len(shuffled), dtype=np.intp)
    for index, fragment in enumerate(shuffled):
        source_of[index] = source_keys.setdefault(fragment.source_id, len(source_keys))
    source_id_by_index = {value: key for key, value in source_keys.items()}

    fragment_use = np.zeros(len(shuffled), dtype=np.int64)
    source_use = np.zeros(len(source_keys), dtype=np.int64)
    available = np.ones(len(shuffled), dtype=bool)
    placements: list[_core.TilePlacement] = []

    grid_image = Image.new("RGB", target.size, _core.BACKGROUND)
    if settings.matching_mode == "spatial":
        # Allocate the strongest unique matches to the eyes, mouth, and central
        # facial structure before less salient regions consume the same candidates.
        positions = ordered_target_positions(target.width, target.height, tile, "portrait")
    else:
        # Preserve the exact row-major allocation used by the historical
        # implementation and its reproducible benchmark.
        positions = [
            (x, y)
            for y in range(0, target.height, tile)
            for x in range(0, target.width, tile)
        ]
    for x, y in positions:
        target_patch = target.crop((x, y, x + tile, y + tile))
        target_descriptor = _matching_descriptor(target_patch, settings.matching_mode)
        distances = np.linalg.norm(descriptors - target_descriptor, axis=1)
        distances[~available] = np.inf
        index = int(np.argmin(distances))
        if not np.isfinite(distances[index]):
            raise ValueError(
                "unique-region, fragment-reuse, or source-contribution limits exhausted; "
                "approve or crawl more source images, increase tile size, or reduce output width"
            )

        fragment = shuffled[index]
        fragment_use[index] += 1
        source_index = int(source_of[index])
        source_use[source_index] += 1

        if fragment_use[index] >= effective_reuse_limit:
            available[index] = False
        if cap > 0 and source_use[source_index] >= cap:
            available[source_of == source_index] = False

        placement = _core.TilePlacement(
            source_id=fragment.source_id,
            fragment_id=fragment.fragment_id,
            image=fragment.image,
            dest_x=x,
            dest_y=y,
            source_x=fragment.x,
            source_y=fragment.y,
        )
        placements.append(placement)
        grid_image.paste(fragment.image, (x, y))

    if settings.composition_mode == "grid":
        image = grid_image
    elif settings.composition_mode == "free":
        image = render_placements(
            sorted(placements, key=lambda placement: (placement.dest_y, placement.dest_x)),
            target.size,
            grammar="overlap",
            seed=settings.seed,
            target_id=target_row.id,
            background=_core.BACKGROUND,
        )
    else:
        raise ValueError(f"unsupported composition mode: {settings.composition_mode}")

    source_usage = {
        source_id_by_index[index]: int(count)
        for index, count in enumerate(source_use)
        if count > 0
    }
    fragment_usage = {
        shuffled[index].fragment_id: int(count)
        for index, count in enumerate(fragment_use)
        if count > 0
    }
    return _core.AssemblyResult(
        image,
        target,
        source_usage,
        fragment_usage,
        placements,
    )


def assemble_target(
    target_row: ManifestRow,
    target_manifest: str | Path,
    fragments: list[Fragment],
    settings: Stage1Settings,
) -> tuple[Image.Image, dict[str, int], dict[str, int]]:
    result = assemble_target_with_trace(target_row, target_manifest, fragments, settings)
    return result.image, result.source_usage, result.fragment_usage


# The preserved orchestration functions resolve these names in their own module
# namespace. Rebinding them keeps all existing video, sidecar, and provenance
# behaviour while routing assembly through this facade.
_core.Stage1Settings = Stage1Settings
_core.assemble_target = assemble_target
_core.assemble_target_with_trace = assemble_target_with_trace


def run_stage1(
    target_manifest: str | Path,
    source_manifest: str | Path,
    output_dir: str | Path,
    settings: Stage1Settings | None = None,
    *,
    target_id: str | None = None,
    artwork: _core.ArtworkKind = "estan-en-todas-partes",
) -> list[_core.Stage1Output]:
    return _core.run_stage1(
        target_manifest,
        source_manifest,
        output_dir,
        settings or Stage1Settings(),
        target_id=target_id,
        artwork=artwork,
    )
