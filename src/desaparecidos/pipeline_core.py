from __future__ import annotations

import json
import math
import random
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Literal

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .cache import image_events_for_runs, page_trail_for_runs
from .images import (
    Fragment,
    crop_from_row,
    descriptor_for,
    extract_fragments,
    load_rgb,
    source_region_from_row,
)
from .manifests import ManifestRow, approved_rows, row_file_path
from .paths import display_path

BACKGROUND = (245, 245, 242)
INK = (18, 18, 17)
ACCENT = (109, 47, 38)
PROCESS_VIDEO_STYLE = "source-reveal-fragment-transfer"
MAX_ANIMATED_FRAGMENTS_PER_SOURCE = 48
DEFAULT_MAX_CONTRIBUTION_PER_SOURCE = 1
ArtworkKind = Literal["todos-somos-familiares", "estan-en-todas-partes", "seguimos-buscando"]
VideoSourceLayout = Literal["grid", "match"]
ARTWORK_SOURCE_KIND: dict[str, Literal["people", "places"]] = {
    "todos-somos-familiares": "people",
    "estan-en-todas-partes": "places",
}


@dataclass(frozen=True)
class Stage1Settings:
    seed: int = 17
    fragment_size: int = 24
    reuse_limit: int = 8
    output_width: int = 720
    max_fragments_per_source: int = 240
    max_contribution_per_source: int = DEFAULT_MAX_CONTRIBUTION_PER_SOURCE
    search_scan_frames_per_candidate: int = 2
    search_scan_max_candidates: int = 120
    video_source_layout: VideoSourceLayout = "grid"
    make_video: bool = False


@dataclass(frozen=True)
class Stage1Output:
    target_id: str
    still_path: str
    sidecar_path: str
    video_path: str | None = None


@dataclass(frozen=True)
class TilePlacement:
    source_id: str
    fragment_id: str
    image: Image.Image
    dest_x: int
    dest_y: int
    source_x: int
    source_y: int


@dataclass(frozen=True)
class AssemblyResult:
    image: Image.Image
    target_canvas: Image.Image
    source_usage: dict[str, int]
    fragment_usage: dict[str, int]
    placements: list[TilePlacement]


@dataclass(frozen=True)
class SearchCandidate:
    run_id: str
    row_id: str | None
    source_id: str | None
    page_url: str
    image_url: str
    decision: str
    path: str
    cv_label: str | None = None


def _target_canvas(target: Image.Image, output_width: int, fragment_size: int) -> Image.Image:
    ratio = target.height / target.width
    width = max(fragment_size, int(round(output_width / fragment_size)) * fragment_size)
    height = max(fragment_size, int(round((width * ratio) / fragment_size)) * fragment_size)
    return target.resize((width, height), Image.Resampling.LANCZOS)


def _feasibility_error(
    tile_count: int,
    fragments_len: int,
    reuse_limit: int,
    source_count: int,
    cap: int,
) -> str | None:
    fragment_capacity = fragments_len * reuse_limit
    if fragment_capacity < tile_count:
        required = math.ceil(tile_count / max(1, fragments_len))
        return (
            "reuse_limit is too low: "
            f"need at least {required} per extracted fragment for {tile_count} output tiles "
            f"and {fragments_len} fragments from {source_count} approved sources; "
            f"got {reuse_limit}"
        )
    if cap > 0 and source_count * cap < tile_count:
        return (
            "max_contribution_per_source is too low: "
            f"{source_count} approved sources x cap {cap} = {source_count * cap} tiles "
            f"but the portrait needs {tile_count}; raise the cap or approve more sources"
        )
    return None


def assemble_target(
    target_row: ManifestRow,
    target_manifest: str | Path,
    fragments: list[Fragment],
    settings: Stage1Settings,
) -> tuple[Image.Image, dict[str, int], dict[str, int]]:
    result = assemble_target_with_trace(target_row, target_manifest, fragments, settings)
    return result.image, result.source_usage, result.fragment_usage


def assemble_target_with_trace(
    target_row: ManifestRow,
    target_manifest: str | Path,
    fragments: list[Fragment],
    settings: Stage1Settings,
) -> AssemblyResult:
    target = crop_from_row(load_rgb(row_file_path(target_row, target_manifest)), target_row)
    target = _target_canvas(target, settings.output_width, settings.fragment_size)
    rng = random.Random(settings.seed + sum(ord(char) for char in target_row.id))
    shuffled = list(fragments)
    rng.shuffle(shuffled)

    tile = settings.fragment_size
    tile_count = math.ceil(target.width / tile) * math.ceil(target.height / tile)
    source_count = len({fragment.source_id for fragment in fragments})
    cap = max(0, settings.max_contribution_per_source)
    error = _feasibility_error(
        tile_count, len(fragments), settings.reuse_limit, source_count, cap
    )
    if error:
        raise ValueError(error)

    # Vectorised nearest-fragment matcher over the shuffled order: build the
    # 6-D hand-designed colour/contrast/edge descriptor matrix once, then per
    # tile mask out fragments that have hit the reuse limit or whose source has
    # hit the contribution cap and take the L2 nearest neighbour. This is
    # intentionally modest: no learned embeddings, identity model, or smoothing
    # stage is used in Stage 1.
    descriptors = np.stack([fragment.descriptor for fragment in shuffled]).astype(np.float32)
    source_keys: dict[str, int] = {}
    source_of = np.empty(len(shuffled), dtype=np.intp)
    for index, fragment in enumerate(shuffled):
        source_of[index] = source_keys.setdefault(fragment.source_id, len(source_keys))
    source_id_by_index = {value: key for key, value in source_keys.items()}

    frag_use = np.zeros(len(shuffled), dtype=np.int64)
    source_use = np.zeros(len(source_keys), dtype=np.int64)
    available = np.ones(len(shuffled), dtype=bool)

    output = Image.new("RGB", target.size, BACKGROUND)
    placements: list[TilePlacement] = []

    for y in range(0, target.height, tile):
        for x in range(0, target.width, tile):
            target_patch = target.crop((x, y, x + tile, y + tile))
            descriptor = descriptor_for(target_patch)
            distances = np.linalg.norm(descriptors - descriptor, axis=1)
            distances[~available] = np.inf
            idx = int(np.argmin(distances))
            if not np.isfinite(distances[idx]):
                raise ValueError("fragment reuse / contribution limits exhausted")
            fragment = shuffled[idx]
            frag_use[idx] += 1
            source_index = int(source_of[idx])
            source_use[source_index] += 1
            if frag_use[idx] >= settings.reuse_limit:
                available[idx] = False
            if cap > 0 and source_use[source_index] >= cap:
                available[source_of == source_index] = False
            output.paste(fragment.image, (x, y))
            placements.append(
                TilePlacement(
                    source_id=fragment.source_id,
                    fragment_id=fragment.fragment_id,
                    image=fragment.image,
                    dest_x=x,
                    dest_y=y,
                    source_x=fragment.x,
                    source_y=fragment.y,
                )
            )

    source_usage = {
        source_id_by_index[index]: int(count)
        for index, count in enumerate(source_use)
        if count > 0
    }
    fragment_usage = {
        shuffled[index].fragment_id: int(count)
        for index, count in enumerate(frag_use)
        if count > 0
    }

    return AssemblyResult(output, target, source_usage, fragment_usage, placements)


def render_video(
    still: Image.Image,
    target_row: ManifestRow,
    output_path: Path,
    *,
    seed: int,
    assembly: AssemblyResult | None = None,
    source_rows: list[ManifestRow] | None = None,
    source_manifest: str | Path | None = None,
    search_trail: list[str] | None = None,
    search_candidates: list[SearchCandidate] | None = None,
    search_scan_frames_per_candidate: int = 2,
    search_candidate_display: list[dict[str, object]] | None = None,
    source_layout: VideoSourceLayout = "grid",
    fps: int = 12,
    seconds: int = 8,
) -> str:
    if assembly is not None and source_rows is not None and source_manifest is not None:
        frames = _process_video_frames(
            target_row,
            assembly,
            source_rows,
            source_manifest,
            seed=seed,
            fps=fps,
            search_trail=search_trail or [],
            search_candidates=search_candidates or [],
            search_scan_frames_per_candidate=search_scan_frames_per_candidate,
            search_candidate_display=search_candidate_display,
            source_layout=source_layout,
        )
    else:
        frames = _reveal_video_frames(still, target_row, seed=seed, fps=fps, seconds=seconds)

    if _render_video_ffmpeg(frames, still.size, output_path, fps=fps):
        return "h264"
    raise RuntimeError(
        "Browser-playable MP4 rendering requires ffmpeg with libx264. "
        "Install ffmpeg, then restart the launcher and generate the video again."
    )


def _reveal_video_frames(
    still: Image.Image,
    target_row: ManifestRow,
    *,
    seed: int,
    fps: int,
    seconds: int,
) -> Iterable[Image.Image]:
    width, height = still.size
    total = fps * seconds
    still_arr = np.asarray(still, dtype=np.uint8)
    font = ImageFont.load_default()
    for index in range(total):
        progress = index / max(1, total - 1)
        visible = min(1.0, progress * 1.35)
        mask = np.random.default_rng(seed + index).random((height, width, 1)) < visible
        base = np.full_like(still_arr, 235, dtype=np.uint8)
        frame = np.where(mask, still_arr, base)
        pil_frame = Image.fromarray(frame, "RGB")
        if progress > 0.72:
            draw = ImageDraw.Draw(pil_frame)
            label = target_row.values.get("name", target_row.id)
            box_height = 34
            draw.rectangle((0, height - box_height, width, height), fill=(18, 18, 17))
            draw.text((18, height - 24), label, fill=(245, 245, 240), font=font)
        yield pil_frame


def _process_video_frames(
    target_row: ManifestRow,
    assembly: AssemblyResult,
    source_rows: list[ManifestRow],
    source_manifest: str | Path,
    *,
    seed: int,
    fps: int,
    search_trail: list[str] | None = None,
    search_candidates: list[SearchCandidate] | None = None,
    search_scan_frames_per_candidate: int = 2,
    search_candidate_display: list[dict[str, object]] | None = None,
    source_layout: VideoSourceLayout = "grid",
) -> Iterable[Image.Image]:
    if source_layout not in {"grid", "match"}:
        raise ValueError(f"unsupported video source layout: {source_layout}")
    tile = assembly.placements[0].image.width if assembly.placements else 24
    placements_by_source = _placements_by_source(assembly.placements)
    ordered_sources = _ordered_video_sources(placements_by_source, search_candidates or [])
    source_by_id = {row.id: row for row in source_rows}
    mosaic = Image.new("RGB", assembly.image.size, BACKGROUND)
    placed_mask = Image.new("L", assembly.image.size, 0)
    mask_draw = ImageDraw.Draw(placed_mask)
    trail = search_trail or []
    frame_index = 0
    del search_scan_frames_per_candidate, search_candidate_display

    for source_id, placements in ordered_sources:
        samples = _sample_placements(placements, MAX_ANIMATED_FRAGMENTS_PER_SOURCE)
        source_row = source_by_id.get(source_id)
        if source_row is None:
            raise ValueError(f"video source {source_id!r} is missing from the approved manifest rows")
        source_region = source_region_from_row(
            load_rgb(row_file_path(source_row, source_manifest)),
            source_row,
            source_row.kind,
        )
        full_source, source_field, source_starts = _source_fragment_field(
            samples,
            source_region,
            assembly.image.size,
        )
        for _ in range(max(1, int(fps * 0.45))):
            yield _with_url_ticker(full_source.copy(), trail, frame_index, fps)
            frame_index += 1

        fade_steps = max(1, int(fps * 0.45))
        for step in range(fade_steps):
            progress = (step + 1) / fade_steps
            frame = Image.blend(full_source, source_field, progress)
            yield _with_url_ticker(frame, trail, frame_index, fps)
            frame_index += 1

        if source_layout == "grid":
            field, starts = _contributing_fragment_field(
                samples,
                assembly.image.size,
                seed=seed + sum(ord(char) for char in source_id),
            )
        else:
            field, starts = _matched_fragment_field(samples, assembly.image.size)

        transition_steps = max(1, int(fps * 0.5))
        for step in range(transition_steps):
            progress = (step + 1) / transition_steps
            frame = _fragment_transfer_frame(
                samples,
                source_starts,
                starts,
                progress,
                Image.new("RGB", assembly.image.size, INK),
            )
            yield _with_url_ticker(frame, trail, frame_index, fps)
            frame_index += 1

        for _ in range(max(1, int(fps * 0.4))):
            yield _with_url_ticker(field.copy(), trail, frame_index, fps)
            frame_index += 1

        highlighted = field.copy()
        highlight_draw = ImageDraw.Draw(highlighted)
        for x, y, start_size in starts:
            highlight_draw.rectangle((x, y, x + start_size, y + start_size), outline=ACCENT, width=2)
        for _ in range(max(1, int(fps * 0.3))):
            yield _with_url_ticker(highlighted.copy(), trail, frame_index, fps)
            frame_index += 1

        transfer_steps = max(1, int(fps * 1.2))
        destinations = [(placement.dest_x, placement.dest_y, tile) for placement in samples]
        for step in range(transfer_steps):
            progress = (step + 1) / transfer_steps
            background = Image.blend(
                Image.new("RGB", assembly.image.size, INK),
                assembly.target_canvas,
                min(0.25, progress * 0.25),
            )
            frame = _fragment_transfer_frame(samples, starts, destinations, progress, background)
            yield _with_url_ticker(frame, trail, frame_index, fps)
            frame_index += 1

        for placement in placements:
            mosaic.paste(placement.image, (placement.dest_x, placement.dest_y))
            mask_draw.rectangle(
                (
                    placement.dest_x,
                    placement.dest_y,
                    placement.dest_x + placement.image.width,
                    placement.dest_y + placement.image.height,
                ),
                fill=255,
            )

        settled = _composite_with_mask(assembly.target_canvas, mosaic, placed_mask)
        for _ in range(max(1, int(fps * 0.5))):
            yield _with_url_ticker(settled.copy(), trail, frame_index, fps)
            frame_index += 1

    for frame in _outro_frames(assembly.image, target_row, fps=fps):
        yield frame


def _contributing_fragment_field(
    placements: list[TilePlacement],
    size: tuple[int, int],
    *,
    seed: int,
) -> tuple[Image.Image, list[tuple[int, int, int]]]:
    field = Image.new("RGB", size, INK)
    if not placements:
        return field, []
    tile = placements[0].image.width
    width, height = size
    columns = max(1, min(len(placements), math.ceil(math.sqrt(len(placements) * width / max(1, height)))))
    rows = max(1, math.ceil(len(placements) / columns))
    x_gap = width / columns
    y_gap = height / rows
    cells = [
        (min(width - tile, int(column * x_gap + max(0, (x_gap - tile) / 2))),
         min(height - tile, int(row * y_gap + max(0, (y_gap - tile) / 2))))
        for row in range(rows)
        for column in range(columns)
    ]
    random.Random(seed).shuffle(cells)
    starts = [(x, y, tile) for x, y in cells[:len(placements)]]
    for placement, (x, y, _size) in zip(placements, starts):
        field.paste(placement.image, (x, y))
    return field, starts


def _source_fragment_field(
    placements: list[TilePlacement],
    source_region: Image.Image,
    size: tuple[int, int],
) -> tuple[Image.Image, Image.Image, list[tuple[int, int, int]]]:
    width, height = size
    if source_region.width <= 0 or source_region.height <= 0:
        raise ValueError("source region has no displayable pixels")
    scale = min(width / source_region.width, height / source_region.height)
    display_width = max(1, int(round(source_region.width * scale)))
    display_height = max(1, int(round(source_region.height * scale)))
    offset_x = (width - display_width) // 2
    offset_y = (height - display_height) // 2
    fitted = source_region.resize((display_width, display_height), Image.Resampling.LANCZOS)
    full_source = Image.new("RGB", size, INK)
    full_source.paste(fitted, (offset_x, offset_y))
    field = Image.new("RGB", size, INK)
    starts: list[tuple[int, int, int]] = []
    for placement in placements:
        fragment_size = max(1, int(round(placement.image.width * scale)))
        x = max(0, min(width - fragment_size, offset_x + int(round(placement.source_x * scale))))
        y = max(0, min(height - fragment_size, offset_y + int(round(placement.source_y * scale))))
        field.paste(
            placement.image.resize((fragment_size, fragment_size), Image.Resampling.LANCZOS),
            (x, y),
        )
        starts.append((x, y, fragment_size))
    return full_source, field, starts


def _matched_fragment_field(
    placements: list[TilePlacement],
    size: tuple[int, int],
) -> tuple[Image.Image, list[tuple[int, int, int]]]:
    field = Image.new("RGB", size, INK)
    if not placements:
        return field, []
    width, height = size
    tile = placements[0].image.width
    starts: list[tuple[int, int, int]] = []
    for placement in placements:
        column = placement.dest_x // max(1, tile)
        row = placement.dest_y // max(1, tile)
        key = (column * 73856093) ^ (row * 19349663)
        angle = math.radians(key % 360)
        distance = tile * (1.5 + (key % 4) * 0.75)
        x = int(round(placement.dest_x + math.cos(angle) * distance))
        y = int(round(placement.dest_y + math.sin(angle) * distance))
        x = max(0, min(width - tile, x))
        y = max(0, min(height - tile, y))
        field.paste(placement.image, (x, y))
        starts.append((x, y, tile))
    return field, starts


def _fragment_transfer_frame(
    placements: list[TilePlacement],
    starts: list[tuple[int, int, int]],
    destinations: list[tuple[int, int, int]],
    progress: float,
    background: Image.Image,
) -> Image.Image:
    frame = background.copy()
    progress = max(0.0, min(1.0, progress))
    for placement, (sx, sy, start_size), (dx, dy, dest_size) in zip(
        placements, starts, destinations
    ):
        x = int(round(sx + (dx - sx) * progress))
        y = int(round(sy + (dy - sy) * progress))
        fragment_size = max(1, int(round(start_size + (dest_size - start_size) * progress)))
        fragment = placement.image
        if fragment.size != (fragment_size, fragment_size):
            fragment = fragment.resize((fragment_size, fragment_size), Image.Resampling.LANCZOS)
        frame.paste(fragment, (x, y))
    return frame


def _placements_by_source(placements: list[TilePlacement]) -> dict[str, list[TilePlacement]]:
    grouped: dict[str, list[TilePlacement]] = {}
    for placement in placements:
        grouped.setdefault(placement.source_id, []).append(placement)
    return grouped


def _ordered_video_sources(
    placements_by_source: dict[str, list[TilePlacement]],
    candidates: list[SearchCandidate],
) -> list[tuple[str, list[TilePlacement]]]:
    ordered_ids: list[str] = []
    for candidate in candidates:
        if candidate.source_id and candidate.source_id in placements_by_source and candidate.source_id not in ordered_ids:
            ordered_ids.append(candidate.source_id)
    for source_id in placements_by_source:
        if source_id not in ordered_ids:
            ordered_ids.append(source_id)
    return [(source_id, placements_by_source[source_id]) for source_id in ordered_ids]


def _sample_placements(placements: list[TilePlacement], limit: int) -> list[TilePlacement]:
    if len(placements) <= limit:
        return placements
    return [placements[int(index)] for index in np.linspace(0, len(placements) - 1, num=limit, dtype=int)]


def _with_url_ticker(frame: Image.Image, urls: list[str], frame_index: int, fps: int) -> Image.Image:
    if not urls:
        return frame
    out = frame.copy()
    draw = ImageDraw.Draw(out)
    font = ImageFont.load_default()
    height = out.height
    index = min(len(urls) - 1, max(0, frame_index // max(1, fps)))
    text = urls[index]
    draw.rectangle((0, height - 24, out.width, height), fill=(0, 0, 0))
    draw.text((8, height - 17), text[:160], fill=(245, 245, 240), font=font)
    return out


def _composite_with_mask(target: Image.Image, mosaic: Image.Image, mask: Image.Image) -> Image.Image:
    muted_target = Image.blend(Image.new("RGB", target.size, BACKGROUND), target, 0.18)
    return Image.composite(mosaic, muted_target, mask)


def _outro_frames(image: Image.Image, target_row: ManifestRow, *, fps: int) -> Iterable[Image.Image]:
    black = Image.new("RGB", image.size, (0, 0, 0))
    font = ImageFont.load_default()
    for step in range(max(1, fps // 2)):
        alpha = 1 - (step + 1) / max(1, fps // 2)
        yield Image.blend(black, image, alpha)
    for text in [
        target_row.values.get("name", target_row.id),
        target_row.values.get("disappearance_date", ""),
        "Seguimos buscando",
    ]:
        frame = black.copy()
        draw = ImageDraw.Draw(frame)
        if text:
            draw.text((24, frame.height // 2), text, fill=(245, 245, 240), font=font)
        for _ in range(max(1, fps)):
            yield frame.copy()
    for _ in range(max(1, fps // 2)):
        yield black.copy()


def _render_video_ffmpeg(frames: Iterable[Image.Image], size: tuple[int, int], output_path: Path, *, fps: int) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{size[0]}x{size[1]}",
        "-r",
        str(fps),
        "-i",
        "-",
        "-an",
        "-vcodec",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert process.stdin is not None
    try:
        for frame in frames:
            process.stdin.write(frame.convert("RGB").tobytes())
    finally:
        process.stdin.close()
    return process.wait() == 0 and output_path.exists()


def run_stage1(
    target_manifest: str | Path,
    source_manifest: str | Path,
    output_dir: str | Path,
    settings: Stage1Settings | None = None,
    *,
    target_id: str | None = None,
    artwork: ArtworkKind = "estan-en-todas-partes",
) -> list[Stage1Output]:
    settings = settings or Stage1Settings()
    if artwork == "seguimos-buscando":
        raise ValueError("seguimos-buscando generation requires /api/generate/traversal")
    source_kind = ARTWORK_SOURCE_KIND[artwork]
    if source_kind == "people" and settings.max_contribution_per_source == 0:
        raise ValueError("people-source generation requires a positive max_contribution_per_source")
    targets = approved_rows(target_manifest, "targets", require_files=True)
    sources = approved_rows(source_manifest, source_kind, require_files=True)
    if target_id:
        targets = [row for row in targets if row.id == target_id]
        if not targets:
            raise ValueError(f"target_id {target_id!r} is not an approved target")
    fragments = extract_fragments(
        sources,
        source_manifest,
        fragment_size=settings.fragment_size,
        max_fragments_per_source=settings.max_fragments_per_source,
        source_kind=source_kind,
    )
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    outputs: list[Stage1Output] = []
    for target in targets:
        assembly = assemble_target_with_trace(target, target_manifest, fragments, settings)
        stem = f"{target.id}-{settings.seed}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        still_path = root / f"{stem}.png"
        assembly.image.save(still_path)
        search_trail = _search_trail_for_sources(sources)
        available_candidates = _search_candidates_for_sources(sources, source_manifest, search_trail)
        search_candidates = available_candidates[:settings.search_scan_max_candidates]
        search_candidate_display: list[dict[str, object]] = []
        video_path: Path | None = None
        video_format: str | None = None
        if settings.make_video:
            video_path = root / f"{stem}.mp4"
            video_format = render_video(
                assembly.image,
                target,
                video_path,
                seed=settings.seed,
                assembly=assembly,
                source_rows=sources,
                source_manifest=source_manifest,
                search_trail=search_trail["urls"],
                search_candidates=search_candidates,
                search_scan_frames_per_candidate=settings.search_scan_frames_per_candidate,
                search_candidate_display=search_candidate_display,
                source_layout=settings.video_source_layout,
            )
        sidecar_path = root / f"{stem}.json"
        sidecar = {
            "artwork": artwork,
            "source_kind": source_kind,
            "source_manifest": display_path(source_manifest),
            "target_id": target.id,
            "target_name": target.values.get("name", target.id),
            "settings": asdict(settings),
            "still_path": display_path(still_path),
            "video_path": display_path(video_path) if video_path else None,
            "video_format": video_format,
            "video_process_style": PROCESS_VIDEO_STYLE if video_path else None,
            "source_image_display": (
                "reviewed-face-region-reveal" if video_path and source_kind == "people"
                else "approved-place-source-reveal" if video_path
                else None
            ),
            "video_source_layout": settings.video_source_layout if video_path else None,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_usage": assembly.source_usage,
            "fragment_usage": assembly.fragment_usage,
            "source_sequence": list(assembly.source_usage.keys()),
            "tile_count": len(assembly.placements),
            "max_fragment_reuse_observed": max(assembly.fragment_usage.values()) if assembly.fragment_usage else 0,
            "per_source_animated_fragment_cap": MAX_ANIMATED_FRAGMENTS_PER_SOURCE,
            "search_trail": search_trail,
            "search_candidates": _search_candidates_sidecar(
                available_candidates, search_candidates, search_candidate_display, settings
            ),
        }
        sidecar_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
        outputs.append(Stage1Output(target.id, display_path(still_path), display_path(sidecar_path), display_path(video_path) if video_path else None))
    return outputs


def _search_trail_for_sources(sources: list[ManifestRow]) -> dict[str, object]:
    run_ids = sorted({row.values.get("crawl_run_id", "") for row in sources if row.values.get("crawl_run_id")})
    if not run_ids:
        urls = [row.values.get("source_page", row.values.get("source_url", "")) for row in sources]
        return {"source": "manifest", "run_ids": [], "urls": [url for url in urls if url]}
    pages = page_trail_for_runs(Path("data/raw/crawl/cache.sqlite"), run_ids)
    urls = [page.get("url", "") for page in pages if page.get("url")]
    if not urls:
        urls = [row.values.get("source_page", row.values.get("source_url", "")) for row in sources]
    return {"source": "crawl-trail", "run_ids": run_ids, "urls": urls}


def _search_candidates_for_sources(
    sources: list[ManifestRow],
    source_manifest: str | Path,
    trail: dict[str, object],
) -> list[SearchCandidate]:
    run_ids = [str(run_id) for run_id in trail.get("run_ids", [])]
    events = image_events_for_runs(Path("data/raw/crawl/cache.sqlite"), run_ids) if run_ids else []
    if not events:
        return [
            SearchCandidate(
                run_id=row.values.get("crawl_run_id", "manifest"),
                row_id=row.id,
                source_id=row.id,
                page_url=row.values.get("source_page", ""),
                image_url=row.values.get("source_url", ""),
                decision="approved",
                path=display_path(row_file_path(row, source_manifest)),
                cv_label=row.values.get("cv_label", ""),
            )
            for row in sources
        ]
    source_by_image = {row.values.get("source_url", ""): row.id for row in sources}
    candidates: list[SearchCandidate] = []
    for event in events:
        image_url = str(event.get("image_url", ""))
        candidates.append(SearchCandidate(
            run_id=str(event.get("run_id", "")),
            row_id=str(event.get("row_id", "")) or None,
            source_id=source_by_image.get(image_url),
            page_url=str(event.get("page_url", "")),
            image_url=image_url,
            decision=str(event.get("decision", "")),
            path=str(event.get("path", "")),
            cv_label=str(event.get("cv_label", "")) or None,
        ))
    return candidates


def _search_candidates_sidecar(
    available: list[SearchCandidate],
    selected: list[SearchCandidate],
    displayed: list[dict[str, object]],
    settings: Stage1Settings,
) -> dict[str, object]:
    return {
        "source": "crawl-events" if any(candidate.run_id != "manifest" for candidate in available) else "manifest",
        "available_count": len(available),
        "local_count": sum(1 for candidate in available if candidate.path),
        "selected_count": len(selected),
        "displayed_count": len(displayed),
        "omitted_count": max(0, len(available) - len(selected)),
        "raw_source_images_displayed": False,
        "scan_max_candidates": settings.search_scan_max_candidates,
        "scan_frames_per_candidate": settings.search_scan_frames_per_candidate,
        "displayed": displayed,
    }
