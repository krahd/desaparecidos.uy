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


@dataclass(frozen=True)
class Stage1Settings:
    seed: int = 17
    fragment_size: int = 24
    reuse_limit: int = 8
    output_width: int = 720
    max_fragments_per_source: int = 240
    max_contribution_per_source: int = 0  # 0 means unlimited tiles per source image
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
    # descriptor matrix once, then per tile mask out fragments that have hit the
    # reuse limit or whose source has hit the contribution cap and take argmin.
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

        transition_frames = max(1, int(fps * 1.8))
        for index in range(transition_frames):
            progress = _ease(index / max(1, transition_frames - 1))
            frame = _placed_background(assembly.target_canvas, mosaic, placed_mask)
            if progress < 1.0:
                overlay = source_full.copy()
                alpha = int(round(185 * (1.0 - progress)))
                frame = Image.blend(frame, overlay, alpha / 255.0)
            _draw_destination_grid(frame, samples, tile, progress)
            _draw_flying_fragments(
                frame,
                samples,
                source_rect,
                source_image.size,
                tile,
                progress,
                seed=seed,
            )
            yield _with_url_ticker(frame, trail, frame_index, fps)
            frame_index += 1

        for placement in placements:
            mosaic.paste(placement.image, (placement.dest_x, placement.dest_y))
            mask_draw.rectangle(
                (
                    placement.dest_x,
                    placement.dest_y,
                    placement.dest_x + tile - 1,
                    placement.dest_y + tile - 1,
                ),
                fill=255,
            )
        settled = _placed_background(assembly.target_canvas, mosaic, placed_mask)
        for _ in range(max(1, int(fps * 0.25))):
            yield _with_url_ticker(settled.copy(), trail, frame_index, fps)
            frame_index += 1

    while candidate_index < len(candidates):
        candidate = candidates[candidate_index]
        candidate_index += 1
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

    for _ in range(max(1, int(fps * 2.0))):
        yield _with_url_ticker(assembly.image.copy(), trail, frame_index, fps)
        frame_index += 1

    yield from _outro_frames(assembly.image, target_row, fps=fps)


def _ordered_video_sources(
    placements_by_source: list[tuple[str, list[TilePlacement]]],
    search_candidates: list[SearchCandidate],
) -> list[tuple[str, list[TilePlacement]]]:
    placement_map = {source_id: placements for source_id, placements in placements_by_source}
    ordered_ids: list[str] = []
    for candidate in search_candidates:
        source_id = candidate.source_id
        if source_id and source_id in placement_map and source_id not in ordered_ids:
            ordered_ids.append(source_id)
    for source_id, _placements in placements_by_source:
        if source_id not in ordered_ids:
            ordered_ids.append(source_id)
    return [(source_id, placement_map[source_id]) for source_id in ordered_ids]


def _candidate_for_source(
    source_id: str, search_candidates: list[SearchCandidate]
) -> SearchCandidate | None:
    for candidate in search_candidates:
        if candidate.source_id == source_id:
            return candidate
    return None


def _candidate_scan_frames(
    candidate: SearchCandidate,
    size: tuple[int, int],
    *,
    frames: int,
    frame_index: int,
    fps: int,
) -> Iterable[Image.Image]:
    image = load_rgb(candidate.path)
    rect = _fit_rect(image.size, *size)
    base = Image.new("RGB", size, INK)
    fitted = image.resize((rect[2], rect[3]), Image.Resampling.LANCZOS)
    base.paste(fitted, (rect[0], rect[1]))
    url = candidate.page_url or candidate.image_url
    for offset in range(max(1, frames)):
        yield _with_url_ticker(base.copy(), [url] if url else [], frame_index + offset, fps)


def _record_candidate_display(
    target: list[dict[str, object]] | None,
    candidate: SearchCandidate,
    start_frame: int,
    end_frame: int,
    *,
    role: str,
) -> None:
    if target is None:
        return
    target.append({
        "run_id": candidate.run_id,
        "row_id": candidate.row_id,
        "source_id": candidate.source_id,
        "page_url": candidate.page_url,
        "image_url": candidate.image_url,
        "decision": candidate.decision,
        "path": display_path(candidate.path),
        "cv_label": candidate.cv_label,
        "role": role,
        "frame_start": start_frame,
        "frame_end": end_frame,
    })


def _placements_by_source(placements: list[TilePlacement]) -> list[tuple[str, list[TilePlacement]]]:
    groups: dict[str, list[TilePlacement]] = {}
    order: list[str] = []
    for placement in placements:
        if placement.source_id not in groups:
            groups[placement.source_id] = []
            order.append(placement.source_id)
        groups[placement.source_id].append(placement)
    return [(source_id, groups[source_id]) for source_id in order]


def _sample_placements(placements: list[TilePlacement], limit: int) -> list[TilePlacement]:
    if len(placements) <= limit:
        return placements
    indexes = np.linspace(0, len(placements) - 1, num=limit, dtype=int)
    return [placements[int(index)] for index in indexes]


def _fit_rect(source_size: tuple[int, int], width: int, height: int) -> tuple[int, int, int, int]:
    source_width, source_height = source_size
    scale = min(width / source_width, height / source_height)
    fitted_width = max(1, int(round(source_width * scale)))
    fitted_height = max(1, int(round(source_height * scale)))
    x = (width - fitted_width) // 2
    y = (height - fitted_height) // 2
    return x, y, fitted_width, fitted_height


def _source_fullscreen_frame(
    source_image: Image.Image,
    rect: tuple[int, int, int, int],
    size: tuple[int, int],
    row: ManifestRow,
    *,
    highlight_placements: list[TilePlacement] | None = None,
    fragment_size: int | None = None,
) -> Image.Image:
    frame = Image.new("RGB", size, INK)
    x, y, width, height = rect
    fitted = source_image.resize((width, height), Image.Resampling.LANCZOS)
    frame.paste(fitted, (x, y))

    draw = ImageDraw.Draw(frame, "RGBA")
    if highlight_placements and fragment_size:
        draw.rectangle((0, 0, size[0], size[1]), fill=(18, 18, 17, 70))
        scale_x = width / source_image.width
        scale_y = height / source_image.height
        for placement in highlight_placements:
            left = x + placement.source_x * scale_x
            top = y + placement.source_y * scale_y
            right = left + fragment_size * scale_x
            bottom = top + fragment_size * scale_y
            draw.rectangle((left, top, right, bottom), outline=(255, 253, 248, 220), width=3)
            draw.rectangle((left + 2, top + 2, right - 2, bottom - 2), outline=(*ACCENT, 230), width=2)

    _draw_source_label(frame, row)
    return frame


def _draw_source_label(frame: Image.Image, row: ManifestRow) -> None:
    width, height = frame.size
    draw = ImageDraw.Draw(frame, "RGBA")
    font = ImageFont.load_default()
    label = row.values.get("title") or row.values.get("name") or row.id
    bar_height = 34
    draw.rectangle((0, height - bar_height, width, height), fill=(18, 18, 17, 190))
    draw.text((18, height - 24), label, fill=(245, 245, 240, 235), font=font)


def _with_url_ticker(frame: Image.Image, urls: list[str], frame_index: int, fps: int) -> Image.Image:
    if not urls:
        return frame
    width, height = frame.size
    draw = ImageDraw.Draw(frame, "RGBA")
    font = ImageFont.load_default()
    strip_height = 34
    url_index = (frame_index // max(1, int(fps * 0.75))) % len(urls)
    url = urls[url_index]
    max_chars = max(24, width // 7)
    if len(url) > max_chars:
        url = "..." + url[-(max_chars - 3):]
    draw.rectangle((0, height - strip_height, width, height), fill=(0, 0, 0, 215))
    draw.text((18, height - 23), url, fill=(245, 245, 240, 238), font=font)
    return frame


def _search_trail_for_sources(source_rows: list[ManifestRow]) -> tuple[list[str], list[str]]:
    run_ids: list[str] = []
    for row in source_rows:
        run_id = row.values.get("crawl_run_id", "").strip()
        if run_id and run_id not in run_ids:
            run_ids.append(run_id)
    urls: list[str] = []
    if run_ids:
        for entry in page_trail_for_runs("data/raw/crawl", run_ids):
            url = str(entry.get("url", "")).strip()
            if url and url not in urls:
                urls.append(url)
    for row in source_rows:
        for key in ("source_page", "source_url"):
            url = row.values.get(key, "").strip()
            if url and url not in urls:
                urls.append(url)
    return urls, run_ids


def _search_candidates_for_sources(
    source_rows: list[ManifestRow],
    source_manifest: str | Path,
    assembly: AssemblyResult,
) -> tuple[list[SearchCandidate], dict[str, object]]:
    run_ids: list[str] = []
    for row in source_rows:
        run_id = row.values.get("crawl_run_id", "").strip()
        if run_id and run_id not in run_ids:
            run_ids.append(run_id)

    rows_by_id = {row.id: row for row in source_rows}
    rows_by_url: dict[str, ManifestRow] = {}
    for row in source_rows:
        for key in ("source_url", "source_page"):
            value = row.values.get(key, "").strip()
            if value:
                rows_by_url.setdefault(value, row)

    candidates: list[SearchCandidate] = []
    skipped_no_path = 0
    events = image_events_for_runs("data/raw/crawl", run_ids) if run_ids else []
    if events:
        for event in events:
            path = str(event.get("path") or "")
            if not path or not Path(path).exists():
                skipped_no_path += 1
                continue
            row_id = str(event.get("row_id") or "").strip() or None
            image_url = str(event.get("image_url") or "").strip()
            page_url = str(event.get("page_url") or "").strip()
            row = rows_by_id.get(row_id or "") or rows_by_url.get(image_url) or rows_by_url.get(page_url)
            candidates.append(
                SearchCandidate(
                    run_id=str(event.get("run_id") or ""),
                    row_id=row_id,
                    source_id=row.id if row else None,
                    page_url=page_url,
                    image_url=image_url,
                    decision=str(event.get("decision") or ""),
                    path=path,
                    cv_label=str(event.get("cv_label") or "") or None,
                )
            )
        return candidates, {
            "run_ids": run_ids,
            "source": "crawl-events",
            "available_count": len(events),
            "local_count": len(candidates),
            "skipped_count": skipped_no_path,
        }

    used_sources = set(assembly.source_usage)
    fallback_rows = [row for row in source_rows if row.id not in used_sources]
    for row in fallback_rows:
        path = row_file_path(row, source_manifest)
        if not path.exists():
            skipped_no_path += 1
            continue
        candidates.append(
            SearchCandidate(
                run_id=row.values.get("crawl_run_id", "").strip(),
                row_id=row.id,
                source_id=row.id,
                page_url=row.values.get("source_page", "").strip(),
                image_url=row.values.get("source_url", "").strip(),
                decision="approved-unused-source",
                path=str(path),
                cv_label=None,
            )
        )
    return candidates, {
        "run_ids": run_ids,
        "source": "approved-unused-sources" if candidates else "none",
        "available_count": len(fallback_rows),
        "local_count": len(candidates),
        "skipped_count": skipped_no_path,
    }


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _fit_font(
    draw: ImageDraw.ImageDraw, text: str, max_width: int, start_size: int, min_size: int = 12
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    size = start_size
    while size > min_size:
        font = _load_font(size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return _load_font(min_size)


def _text_panel(size: tuple[int, int], title: str, subtitles: list[str]) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, (0, 0, 0))
    draw = ImageDraw.Draw(image)
    max_width = int(width * 0.86)

    entries = [(title, _fit_font(draw, title, max_width, max(20, width // 14)), (242, 240, 235), int(height * 0.05))]
    for line in subtitles:
        entries.append((line, _fit_font(draw, line, max_width, max(14, width // 30)), (180, 176, 166), int(height * 0.018)))

    measured = []
    total = 0
    for index, (text, font, color, gap) in enumerate(entries):
        bbox = draw.textbbox((0, 0), text, font=font)
        line_height = bbox[3] - bbox[1]
        applied_gap = gap if index < len(entries) - 1 else 0
        measured.append((text, font, color, line_height, bbox[1], applied_gap))
        total += line_height + applied_gap

    y = (height - total) // 2
    for text, font, color, line_height, top, gap in measured:
        x = (width - int(draw.textlength(text, font=font))) // 2
        draw.text((x, y - top), text, font=font, fill=color)
        y += line_height + gap
    return image


def _outro_frames(
    final_image: Image.Image, target_row: ManifestRow, *, fps: int
) -> Iterable[Image.Image]:
    """End sequence: hold result, then fade through name/info, the solidarity
    line, and the result again, each separated by a fade to black."""
    size = final_image.size
    black = Image.new("RGB", size, (0, 0, 0))

    name = target_row.values.get("name") or target_row.id
    info: list[str] = []
    born = target_row.values.get("birth_date", "").strip()
    disappeared = target_row.values.get("disappearance_date", "").strip()
    place = target_row.values.get("disappearance_place", "").strip()
    if born:
        info.append(f"Nacimiento: {born}")
    if disappeared:
        info.append(f"Desaparición: {disappeared}")
    if place:
        info.append(place)
    name_panel = _text_panel(size, name, info)
    solidarity_panel = _text_panel(size, "TODOS SOMOS FAMILIARES", [])

    def hold(image: Image.Image, seconds: float) -> Iterable[Image.Image]:
        for _ in range(max(1, int(round(fps * seconds)))):
            yield image.copy()

    def fade(start: Image.Image, end: Image.Image, seconds: float) -> Iterable[Image.Image]:
        steps = max(1, int(round(fps * seconds)))
        for index in range(1, steps + 1):
            yield Image.blend(start, end, index / steps)

    yield from hold(final_image, 2.5)
    yield from fade(final_image, black, 1.0)
    yield from hold(black, 0.4)
    yield from fade(black, name_panel, 1.0)
    yield from hold(name_panel, 3.0)
    yield from fade(name_panel, black, 1.0)
    yield from hold(black, 0.4)
    yield from fade(black, solidarity_panel, 1.0)
    yield from hold(solidarity_panel, 3.0)
    yield from fade(solidarity_panel, black, 1.0)
    yield from hold(black, 0.4)
    yield from fade(black, final_image, 1.0)
    yield from hold(final_image, 2.5)
    yield from fade(final_image, black, 1.0)
    yield from hold(black, 0.5)


def _placed_background(target_canvas: Image.Image, mosaic: Image.Image, placed_mask: Image.Image) -> Image.Image:
    blank = Image.new("RGB", target_canvas.size, BACKGROUND)
    ghost = target_canvas.convert("L").convert("RGB")
    frame = Image.blend(blank, ghost, 0.18)
    frame.paste(mosaic, (0, 0), placed_mask)
    return frame


def _draw_destination_grid(
    frame: Image.Image,
    placements: list[TilePlacement],
    tile: int,
    progress: float,
) -> None:
    draw = ImageDraw.Draw(frame, "RGBA")
    alpha = int(round(120 * progress))
    for placement in placements:
        draw.rectangle(
            (
                placement.dest_x,
                placement.dest_y,
                placement.dest_x + tile,
                placement.dest_y + tile,
            ),
            outline=(*ACCENT, alpha),
            width=1,
        )


def _draw_flying_fragments(
    frame: Image.Image,
    placements: list[TilePlacement],
    source_rect: tuple[int, int, int, int],
    source_size: tuple[int, int],
    tile: int,
    progress: float,
    *,
    seed: int,
) -> None:
    if not placements:
        return
    draw = ImageDraw.Draw(frame, "RGBA")
    source_x, source_y, source_width, source_height = source_rect
    scale_x = source_width / source_size[0]
    scale_y = source_height / source_size[1]
    max_start_size = max(tile * 3, min(frame.size) * 0.18)
    stagger_span = 0.48
    motion_span = 1.0 - stagger_span + (stagger_span / max(1, len(placements)))

    for index, placement in enumerate(placements):
        stagger = (index / max(1, len(placements) - 1)) * stagger_span
        local = min(1.0, max(0.0, (progress - stagger) / max(0.01, motion_span)))
        eased = _ease(local)
        start_cx = source_x + (placement.source_x + tile / 2) * scale_x
        start_cy = source_y + (placement.source_y + tile / 2) * scale_y
        end_cx = placement.dest_x + tile / 2
        end_cy = placement.dest_y + tile / 2
        cx = start_cx + (end_cx - start_cx) * eased
        cy = start_cy + (end_cy - start_cy) * eased
        start_size = min(max_start_size, max(tile * 1.8, tile * max(scale_x, scale_y)))
        current_size = max(1, int(round(start_size + (tile - start_size) * eased)))
        angle = _fragment_angle(placement.fragment_id, seed) * (1.0 - eased)

        draw.line((cx, cy, end_cx, end_cy), fill=(*ACCENT, int(80 * (1.0 - eased))), width=1)
        patch = placement.image.resize((current_size, current_size), Image.Resampling.LANCZOS).convert("RGBA")
        patch = patch.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=(0, 0, 0, 0))
        px = int(round(cx - patch.width / 2))
        py = int(round(cy - patch.height / 2))
        frame.paste(patch, (px, py), patch)


def _fragment_angle(fragment_id: str, seed: int) -> float:
    value = seed + sum((index + 1) * ord(char) for index, char in enumerate(fragment_id))
    return float((value % 25) - 12)


def _ease(value: float) -> float:
    value = min(1.0, max(0.0, value))
    return value * value * (3.0 - 2.0 * value)


def _render_video_ffmpeg(
    frames: Iterable[Image.Image],
    size: tuple[int, int],
    output_path: Path,
    *,
    fps: int,
) -> bool:
    ffmpeg = _find_ffmpeg()
    if not ffmpeg:
        return False

    width, height = size
    command = [
        ffmpeg,
        "-loglevel",
        "error",
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{width}x{height}",
        "-r",
        str(fps),
        "-i",
        "-",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None
    try:
        for frame in frames:
            if frame.size != size:
                frame = frame.resize(size, Image.Resampling.LANCZOS)
            if frame.mode != "RGB":
                frame = frame.convert("RGB")
            process.stdin.write(frame.tobytes())
        process.stdin.close()
        stderr = process.stderr.read().decode("utf-8", errors="replace") if process.stderr else ""
        return_code = process.wait()
    except Exception:
        process.kill()
        output_path.unlink(missing_ok=True)
        raise

    if return_code != 0:
        output_path.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg could not render H.264 MP4: {stderr.strip() or 'unknown error'}")
    return True


def _find_ffmpeg() -> str | None:
    found = shutil.which("ffmpeg")
    if found:
        return found
    for candidate in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        path = Path(candidate)
        if path.exists() and path.is_file():
            return str(path)
    return None


def run_stage1(
    target_manifest: str | Path,
    source_manifest: str | Path,
    output_dir: str | Path,
    settings: Stage1Settings,
    *,
    target_id: str | None = None,
) -> list[Stage1Output]:
    target_rows = approved_rows(target_manifest, "targets", require_files=True)
    source_rows = approved_rows(source_manifest, "places", require_files=True)
    if target_id:
        target_rows = [row for row in target_rows if row.id == target_id]
        if not target_rows:
            raise ValueError(f"target id is not approved or does not exist: {target_id}")

    fragments = extract_fragments(
        source_rows,
        source_manifest,
        fragment_size=settings.fragment_size,
        max_fragments_per_source=settings.max_fragments_per_source,
    )
    search_trail, search_run_ids = _search_trail_for_sources(source_rows)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    outputs: list[Stage1Output] = []
    for target_row in target_rows:
        assembly = assemble_target_with_trace(target_row, target_manifest, fragments, settings)
        still = assembly.image
        source_usage = assembly.source_usage
        fragment_usage = assembly.fragment_usage
        safe_id = "".join(char if char.isalnum() or char in "-_" else "_" for char in target_row.id)
        stem = f"{safe_id}_seed{settings.seed}_f{settings.fragment_size}"
        still_path = output_root / f"{stem}.png"
        sidecar_path = output_root / f"{stem}.json"
        video_path = output_root / f"{stem}.mp4" if settings.make_video else None
        video_codec = None

        still.save(still_path)
        if video_path is not None:
            all_candidates, candidate_info = _search_candidates_for_sources(
                source_rows, source_manifest, assembly
            )
            max_candidates = max(0, settings.search_scan_max_candidates)
            selected_candidates = all_candidates[:max_candidates] if max_candidates else []
            candidate_display: list[dict[str, object]] = []
            video_codec = render_video(
                still,
                target_row,
                video_path,
                seed=settings.seed,
                assembly=assembly,
                source_rows=source_rows,
                source_manifest=source_manifest,
                search_trail=search_trail,
                search_candidates=selected_candidates,
                search_scan_frames_per_candidate=settings.search_scan_frames_per_candidate,
                search_candidate_display=candidate_display,
            )
        else:
            all_candidates, candidate_info = _search_candidates_for_sources(
                source_rows, source_manifest, assembly
            )
            max_candidates = max(0, settings.search_scan_max_candidates)
            selected_candidates = all_candidates[:max_candidates] if max_candidates else []
            candidate_display = []

        source_sequence = [
            {
                "source_id": source_id,
                "tile_count": len(placements),
                "animated_fragment_count": min(len(placements), MAX_ANIMATED_FRAGMENTS_PER_SOURCE),
            }
            for source_id, placements in _placements_by_source(assembly.placements)
        ]

        sidecar = {
            "target": target_row.values,
            "target_id": target_row.id,
            "source_ids": sorted(source_usage),
            "source_usage": source_usage,
            "fragment_count": len(fragments),
            "fragment_usage_count": len(fragment_usage),
            "max_fragment_reuse_observed": max(fragment_usage.values(), default=0),
            "tile_count": len(assembly.placements),
            "source_sequence": source_sequence,
            "settings": asdict(settings),
            "still_path": display_path(still_path),
            "video_path": display_path(video_path) if video_path else None,
            "video_codec": video_codec,
            "video_process": {
                "style": PROCESS_VIDEO_STYLE,
                "full_screen_source_intro": True,
                "animated_fragment_limit_per_source": MAX_ANIMATED_FRAGMENTS_PER_SOURCE,
                "url_ticker": bool(search_trail),
                "search_candidate_scan": bool(selected_candidates),
                "search_scan_frames_per_candidate": settings.search_scan_frames_per_candidate,
                "search_scan_max_candidates": settings.search_scan_max_candidates,
            } if video_path else None,
            "search_trail": {
                "run_ids": search_run_ids,
                "urls": search_trail,
                "url_count": len(search_trail),
            },
            "search_candidates": {
                **candidate_info,
                "frames_per_candidate": settings.search_scan_frames_per_candidate,
                "max_candidates": settings.search_scan_max_candidates,
                "selected_count": len(selected_candidates),
                "displayed_count": len(candidate_display),
                "omitted_count": max(0, len(all_candidates) - len(selected_candidates)),
                "displayed": candidate_display,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "method": "Stage 1 place-fragment reconstruction prototype",
        }
        sidecar_path.write_text(
            json.dumps(sidecar, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        outputs.append(
            Stage1Output(
                target_id=target_row.id,
                still_path=str(still_path),
                sidecar_path=str(sidecar_path),
                video_path=str(video_path) if video_path else None,
            )
        )
    return outputs
