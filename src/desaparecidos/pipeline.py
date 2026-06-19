from __future__ import annotations

import json
import math
import random
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .cache import image_events_for_runs, page_trail_for_runs
from .images import Fragment, crop_from_row, descriptor_for, extract_fragments, load_rgb
from .manifests import ManifestRow, approved_rows, row_file_path
from .paths import display_path

BACKGROUND = (245, 245, 242)
INK = (18, 18, 17)
ACCENT = (109, 47, 38)
PROCESS_VIDEO_STYLE = "source-fullscreen-fragment-flight"
MAX_ANIMATED_FRAGMENTS_PER_SOURCE = 48
DEFAULT_MAX_CONTRIBUTION_PER_SOURCE = 240


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
) -> Iterable[Image.Image]:
    width, height = assembly.image.size
    tile = assembly.placements[0].image.width if assembly.placements else 24
    source_rows_by_id = {row.id: row for row in source_rows}
    placements_by_source = _placements_by_source(assembly.placements)
    ordered_sources = _ordered_video_sources(placements_by_source, search_candidates or [])
    mosaic = Image.new("RGB", assembly.image.size, BACKGROUND)
    placed_mask = Image.new("L", assembly.image.size, 0)
    mask_draw = ImageDraw.Draw(placed_mask)
    trail = search_trail or []
    frame_index = 0
    candidates = list(search_candidates or [])
    candidate_index = 0
    scan_frames = max(1, search_scan_frames_per_candidate)

    for source_id, placements in ordered_sources:
        while candidate_index < len(candidates):
            candidate = candidates[candidate_index]
            candidate_index += 1
            if candidate.source_id == source_id:
                break
            start_frame = frame_index
            for frame in _candidate_scan_frames(
                candidate,
                assembly.image.size,
                frames=scan_frames,
                frame_index=frame_index,
                fps=fps,
            ):
                yield frame
                frame_index += 1
            _record_candidate_display(
                search_candidate_display,
                candidate,
                start_frame,
                frame_index,
                role="scan",
            )

        row = source_rows_by_id.get(source_id)
        if row is None:
            continue
        source_image = load_rgb(row_file_path(row, source_manifest))
        source_rect = _fit_rect(source_image.size, width, height)
        source_full = _source_fullscreen_frame(source_image, source_rect, assembly.image.size, row)
        samples = _sample_placements(placements, MAX_ANIMATED_FRAGMENTS_PER_SOURCE)

        matching_candidate = _candidate_for_source(source_id, candidates)
        intro_start = frame_index
        for _ in range(max(1, int(fps * 0.9))):
            yield _with_url_ticker(source_full.copy(), trail, frame_index, fps)
            frame_index += 1
        if matching_candidate is not None:
            _record_candidate_display(
                search_candidate_display,
                matching_candidate,
                intro_start,
                frame_index,
                role="contributor",
            )

        highlighted = _source_fullscreen_frame(
            source_image,
            source_rect,
            assembly.image.size,
            row,
            highlight_placements=samples,
            fragment_size=tile,
        )
        for _ in range(max(1, int(fps * 0.7))):
            yield _with_url_ticker(highlighted.copy(), trail, frame_index, fps)
            frame_index += 1

        for step in range(max(1, int(fps * 1.2))):
            frame = Image.blend(source_full, assembly.target_canvas, min(0.35, (step + 1) / max(1, fps * 3)))
            draw = ImageDraw.Draw(frame)
            progress = (step + 1) / max(1, int(fps * 1.2))
            visible_count = max(1, int(len(samples) * progress))
            for placement in samples[:visible_count]:
                sx1 = source_rect[0] + int(placement.source_x * source_rect[2] / max(1, source_image.width))
                sy1 = source_rect[1] + int(placement.source_y * source_rect[3] / max(1, source_image.height))
                sx2 = sx1 + max(2, int(tile * source_rect[2] / max(1, source_image.width)))
                sy2 = sy1 + max(2, int(tile * source_rect[3] / max(1, source_image.height)))
                dx = int(sx1 + (placement.dest_x - sx1) * progress)
                dy = int(sy1 + (placement.dest_y - sy1) * progress)
                draw.rectangle((sx1, sy1, sx2, sy2), outline=ACCENT, width=2)
                frame.paste(placement.image, (dx, dy))
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


def _candidate_for_source(source_id: str, candidates: list[SearchCandidate]) -> SearchCandidate | None:
    for candidate in candidates:
        if candidate.source_id == source_id:
            return candidate
    return None


def _record_candidate_display(
    collector: list[dict[str, object]] | None,
    candidate: SearchCandidate,
    frame_start: int,
    frame_end: int,
    *,
    role: str,
) -> None:
    if collector is None:
        return
    collector.append({
        "role": role,
        "run_id": candidate.run_id,
        "row_id": candidate.row_id,
        "source_id": candidate.source_id,
        "page_url": candidate.page_url,
        "image_url": candidate.image_url,
        "decision": candidate.decision,
        "cv_label": candidate.cv_label,
        "path": candidate.path,
        "frame_start": frame_start,
        "frame_end": frame_end,
    })


def _sample_placements(placements: list[TilePlacement], limit: int) -> list[TilePlacement]:
    if len(placements) <= limit:
        return placements
    return [placements[int(index)] for index in np.linspace(0, len(placements) - 1, num=limit, dtype=int)]


def _fit_rect(size: tuple[int, int], width: int, height: int) -> tuple[int, int, int, int]:
    src_w, src_h = size
    scale = min(width / max(1, src_w), height / max(1, src_h))
    w = max(1, int(src_w * scale))
    h = max(1, int(src_h * scale))
    return ((width - w) // 2, (height - h) // 2, w, h)


def _source_fullscreen_frame(
    source: Image.Image,
    rect: tuple[int, int, int, int],
    size: tuple[int, int],
    row: ManifestRow,
    *,
    highlight_placements: list[TilePlacement] | None = None,
    fragment_size: int = 24,
) -> Image.Image:
    frame = Image.new("RGB", size, INK)
    x, y, w, h = rect
    resized = source.resize((w, h), Image.Resampling.LANCZOS)
    frame.paste(resized, (x, y))
    draw = ImageDraw.Draw(frame)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, size[0], 28), fill=(0, 0, 0))
    draw.text((12, 9), row.values.get("title", row.id), fill=(245, 245, 240), font=font)
    if highlight_placements:
        for placement in highlight_placements:
            sx1 = x + int(placement.source_x * w / max(1, source.width))
            sy1 = y + int(placement.source_y * h / max(1, source.height))
            sx2 = sx1 + max(2, int(fragment_size * w / max(1, source.width)))
            sy2 = sy1 + max(2, int(fragment_size * h / max(1, source.height)))
            draw.rectangle((sx1, sy1, sx2, sy2), outline=ACCENT, width=2)
    return frame


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


def _candidate_scan_frames(
    candidate: SearchCandidate,
    size: tuple[int, int],
    *,
    frames: int,
    frame_index: int,
    fps: int,
) -> Iterable[Image.Image]:
    width, height = size
    path = Path(candidate.path)
    if path.exists():
        image = load_rgb(path)
        rect = _fit_rect(image.size, width, height)
        frame = Image.new("RGB", size, INK)
        x, y, w, h = rect
        frame.paste(image.resize((w, h), Image.Resampling.LANCZOS), (x, y))
    else:
        frame = Image.new("RGB", size, (35, 35, 35))
    draw = ImageDraw.Draw(frame)
    font = ImageFont.load_default()
    status = f"{candidate.decision} {candidate.cv_label or ''}".strip()
    draw.rectangle((0, 0, width, 28), fill=(0, 0, 0))
    draw.text((12, 9), status, fill=(245, 245, 240), font=font)
    for offset in range(frames):
        yield _with_url_ticker(frame.copy(), [candidate.page_url], frame_index + offset, fps)


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
) -> list[Stage1Output]:
    settings = settings or Stage1Settings()
    targets = approved_rows(target_manifest, "targets", require_files=True)
    sources = approved_rows(source_manifest, "places", require_files=True)
    if target_id:
        targets = [row for row in targets if row.id == target_id]
        if not targets:
            raise ValueError(f"target_id {target_id!r} is not an approved target")
    fragments = extract_fragments(
        sources,
        source_manifest,
        fragment_size=settings.fragment_size,
        max_fragments_per_source=settings.max_fragments_per_source,
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
        search_candidates = _search_candidates_for_sources(sources, source_manifest, search_trail)
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
            )
        sidecar_path = root / f"{stem}.json"
        sidecar = {
            "target_id": target.id,
            "target_name": target.values.get("name", target.id),
            "settings": asdict(settings),
            "still_path": display_path(still_path),
            "video_path": display_path(video_path) if video_path else None,
            "video_format": video_format,
            "video_process_style": PROCESS_VIDEO_STYLE if video_path else None,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_usage": assembly.source_usage,
            "fragment_usage": assembly.fragment_usage,
            "source_sequence": list(assembly.source_usage.keys()),
            "tile_count": len(assembly.placements),
            "max_fragment_reuse_observed": max(assembly.fragment_usage.values()) if assembly.fragment_usage else 0,
            "per_source_animated_fragment_cap": MAX_ANIMATED_FRAGMENTS_PER_SOURCE,
            "search_trail": search_trail,
            "search_candidates": _search_candidates_sidecar(search_candidates, search_candidate_display, settings),
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
    candidates: list[SearchCandidate],
    displayed: list[dict[str, object]],
    settings: Stage1Settings,
) -> dict[str, object]:
    return {
        "source": "crawl-events" if any(candidate.run_id != "manifest" for candidate in candidates) else "manifest",
        "available_count": len(candidates),
        "local_count": sum(1 for candidate in candidates if candidate.path),
        "selected_count": len(displayed),
        "omitted_count": max(0, len(candidates) - len(displayed)),
        "scan_max_candidates": settings.search_scan_max_candidates,
        "scan_frames_per_candidate": settings.search_scan_frames_per_candidate,
        "displayed": displayed[: settings.search_scan_max_candidates],
    }
