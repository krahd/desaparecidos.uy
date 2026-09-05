from __future__ import annotations

import bisect
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont

from .manifests import ManifestRow


BLACK = (0, 0, 0)
WHITE = (238, 238, 238)
MID_GREY = (122, 122, 122)
VIDEO_ASPECT_RATIO = "16:9"
VIDEO_TEXT_LANGUAGE = "es"


ARTWORK_TITLES = {
    "seguimos-buscando": "Seguimos Buscando",
    "estan-en-todas-partes": "Están en todas partes",
    "todos-somos-familiares": "Todos somos familiares",
}


@dataclass(frozen=True)
class VideoSettings:
    split_orientation: str = "side-by-side"
    contribution_seconds: float = 2.5
    scan_seconds: float = 0.18
    final_hold_seconds: float = 4.0
    details_hold_seconds: float = 3.0
    text_hold_seconds: float = 2.0
    fade_seconds: float = 1.0
    closing_text: str = ""
    show_match_marks: bool = True


def validate_video_settings(settings: VideoSettings) -> None:
    if settings.split_orientation not in {"side-by-side", "stacked"}:
        raise ValueError("unsupported split orientation")
    for name in ("contribution_seconds", "scan_seconds", "final_hold_seconds", "details_hold_seconds", "text_hold_seconds", "fade_seconds"):
        value = getattr(settings, name)
        if not math.isfinite(value) or not 0 < value <= 60:
            raise ValueError(f"{name} must be in (0, 60]")
    if len(settings.closing_text) > 240:
        raise ValueError("closing text must be at most 240 characters")


@dataclass(frozen=True)
class SearchVideoTimeline:
    search: int
    final_hold: int
    final_fade_out: int
    person_fade_in: int
    person_hold: int
    person_fade_out: int
    title_fade_in: int
    title_hold: int
    title_fade_out: int

    @property
    def total(self) -> int:
        return sum(self.as_dict().values())

    def as_dict(self) -> dict[str, int]:
        return {
            "search": self.search,
            "final_hold": self.final_hold,
            "final_fade_out": self.final_fade_out,
            "person_fade_in": self.person_fade_in,
            "person_hold": self.person_hold,
            "person_fade_out": self.person_fade_out,
            "title_fade_in": self.title_fade_in,
            "title_hold": self.title_hold,
            "title_fade_out": self.title_fade_out,
        }


def video_canvas_size(output_width: int) -> tuple[int, int]:
    """Return an even 16:9 canvas; the 1920-pixel default is full HD."""
    width = max(16, int(output_width))
    if width % 2:
        width -= 1
    height = max(16, int(round(width * 9 / 16)))
    if height % 2:
        height += 1
    return width, height


def search_video_timeline(total_frames: int, fps: int, settings: VideoSettings | None = None) -> SearchVideoTimeline:
    """Allocate a complete closing sequence while keeping short test renders valid."""
    total_frames = max(1, total_frames)
    fps = max(1, fps)
    options = settings or VideoSettings()
    validate_video_settings(options)
    fade = max(1, round(options.fade_seconds * fps))
    requested = {
        "final_hold": max(1, round(options.final_hold_seconds * fps)),
        "final_fade_out": fade,
        "person_fade_in": fade,
        "person_hold": max(1, round(options.details_hold_seconds * fps)),
        "person_fade_out": fade,
        "title_fade_in": fade,
        "title_hold": max(1, round(options.text_hold_seconds * fps)),
        "title_fade_out": fade,
    }
    closing_requested = sum(requested.values())
    closing_available = max(0, min(closing_requested, total_frames - fps))
    if closing_available == closing_requested:
        closing = requested
    elif closing_available == 0:
        closing = {name: 0 for name in requested}
    else:
        exact = {
            name: frames * closing_available / closing_requested
            for name, frames in requested.items()
        }
        closing = {name: int(frames) for name, frames in exact.items()}
        remainder = closing_available - sum(closing.values())
        order = sorted(exact, key=lambda name: (exact[name] - closing[name], requested[name]), reverse=True)
        for name in order[:remainder]:
            closing[name] += 1
    return SearchVideoTimeline(search=total_frames - sum(closing.values()), **closing)


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ) if bold else (
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size=size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _contain(
    image: Image.Image,
    box: tuple[int, int, int, int],
) -> tuple[Image.Image, tuple[int, int, int, int], float]:
    left, top, right, bottom = box
    max_width = max(1, right - left)
    max_height = max(1, bottom - top)
    copy = image.convert("L").convert("RGB")
    scale = min(max_width / copy.width, max_height / copy.height)
    size = (max(1, round(copy.width * scale)), max(1, round(copy.height * scale)))
    copy = copy.resize(size, Image.Resampling.LANCZOS)
    x = left + (max_width - copy.width) // 2
    y = top + (max_height - copy.height) // 2
    return copy, (x, y, x + copy.width, y + copy.height), scale


def _paste_contained(canvas: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    fitted, bounds, _scale = _contain(image, box)
    canvas.paste(fitted, bounds[:2])
    return bounds


def _centred_text(
    canvas: Image.Image,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    *,
    fill: tuple[int, int, int] = WHITE,
) -> None:
    draw = ImageDraw.Draw(canvas)
    bounds = draw.textbbox((0, 0), text, font=font)
    width = bounds[2] - bounds[0]
    draw.text(((canvas.width - width) // 2, y), text, font=font, fill=fill)


_MONTHS = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)


def format_spanish_date(value: str) -> str:
    parts = value.strip().split("-") if value.strip() else []
    try:
        if len(parts) == 3:
            year, month, day = (int(part) for part in parts)
            if 1 <= month <= 12:
                return f"{day} de {_MONTHS[month - 1]} de {year}"
        if len(parts) == 2:
            year, month = (int(part) for part in parts)
            if 1 <= month <= 12:
                return f"{_MONTHS[month - 1]} de {year}"
        if len(parts) == 1 and parts[0]:
            return parts[0]
    except ValueError:
        pass
    return value.strip()


def person_card_lines(target: ManifestRow) -> list[str]:
    values = target.values
    lines = [values.get("name") or target.id]
    birth = format_spanish_date(values.get("birth_date", ""))
    disappeared = format_spanish_date(values.get("disappearance_date", ""))
    place = values.get("disappearance_place", "").strip()
    if birth:
        lines.append(f"Nacimiento · {birth}")
    if disappeared:
        lines.append(f"Desaparición · {disappeared}")
    if place:
        lines.append(f"Lugar de desaparición · {place}")
    return lines


def video_presentation_metadata(
    output_width: int,
    duration_seconds: int,
    fps: int,
    composition: str = "split",
    target_ids: Sequence[str] | None = None,
    *, settings: VideoSettings | None = None, walks: Sequence[Any] | None = None,
    artwork: str = "seguimos-buscando",
) -> dict[str, Any]:
    width, height = video_canvas_size(output_width)
    ids = list(target_ids or ["target"])
    total = max(fps, duration_seconds * fps)
    segment_lengths = [total // len(ids)] * len(ids)
    for index in range(total % len(ids)):
        segment_lengths[index] += 1
    plans = [video_schedule(walk, length, fps, settings or VideoSettings())[0] if walks is not None else search_video_timeline(length, fps, settings)
             for walk, length in zip(walks or [None] * len(ids), segment_lengths)]
    return {
        "schema": "desaparecidos.uy/search-video-presentation/2.0",
        "canvas": {"width": width, "height": height, "aspect_ratio": VIDEO_ASPECT_RATIO},
        "palette": "grayscale",
        "text_language": VIDEO_TEXT_LANGUAGE,
        "search_layout": {
            "split": "busqueda-arriba-reconstruccion-abajo" if settings and settings.split_orientation == "stacked" else "recorrido-izquierda-reconstruccion-derecha",
            "overlay": "recorrido-y-reconstruccion-superpuestos",
            "alternate": "recorrido-y-reconstruccion-alternados",
        }.get(composition, composition),
        "closing_sequence": [
            "reconstruccion-final",
            "nombre-fechas-y-detalles",
            artwork,
        ],
        "timeline_frames_by_target": {
            target_id: plan.as_dict()
            for target_id, plan in zip(ids, plans)
        },
        "fps": fps,
        "requested_duration_seconds": duration_seconds,
        "actual_duration_seconds": sum(plan.total for plan in plans) / fps,
        "duration_policy": "extend-to-show-every-encounter-and-minimum-holds",
        "closing_text": (settings.closing_text if settings else "") or ARTWORK_TITLES[artwork],
    }


def _fade(image: Image.Image, opacity: float) -> Image.Image:
    return Image.blend(Image.new("RGB", image.size, BLACK), image, max(0.0, min(1.0, opacity)))


def _opacity(index: int, length: int, *, rising: bool) -> float:
    if length <= 1:
        return 1.0 if rising else 0.0
    progress = index / (length - 1)
    return progress if rising else 1.0 - progress


def _text_block(canvas: Image.Image, text: str, centre_y: int, size: int, *, bold: bool = False) -> int:
    font = _font(max(9, size), bold=bold)
    draw = ImageDraw.Draw(canvas)
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        for chunk_start in range(0, len(word), 36):
            chunk = word[chunk_start:chunk_start + 36]
            candidate = f"{line} {chunk}".strip()
            if line and draw.textlength(candidate, font=font) > canvas.width * 0.88:
                lines.append(line)
                line = chunk
            else:
                line = candidate
    if line:
        lines.append(line)
    line_height = max(12, round(size * 1.45))
    y = centre_y - len(lines) * line_height // 2
    for line in lines:
        _centred_text(canvas, line, y, font)
        y += line_height
    return y


def _person_card(target: ManifestRow, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGB", size, BLACK)
    lines = person_card_lines(target)
    y = _text_block(canvas, lines[0], round(size[1] * 0.3), round(size[0] * 0.032), bold=True)
    for line in lines[1:]:
        y = _text_block(canvas, line, y + round(size[1] * 0.08), round(size[0] * 0.017))
    return canvas


def _title_card(size: tuple[int, int], text: str = "Seguimos Buscando") -> Image.Image:
    canvas = Image.new("RGB", size, BLACK)
    _text_block(canvas, text, size[1] // 2, round(size[0] * 0.052), bold=True)
    return canvas


def video_schedule(walk: Any, requested_frames: int, fps: int, settings: VideoSettings) -> tuple[SearchVideoTimeline, list[int]]:
    validate_video_settings(settings)
    contributions = set(walk.placed_after_frame)
    holds = [max(2 if i in contributions else 1, math.ceil(fps * (settings.contribution_seconds if i in contributions else settings.scan_seconds)))
             for i in range(len(walk.segment_frame_ids))]
    closing = search_video_timeline(100000 * fps, fps, settings)
    closing_frames = closing.total - closing.search
    total = max(requested_frames, max(fps, sum(holds)) + closing_frames)
    extra = total - sum(holds) - closing_frames
    if holds:
        for i in range(len(holds)):
            holds[i] += extra // len(holds) + (i < extra % len(holds))
    return search_video_timeline(total, fps, settings), holds


def _search_frame(
    source_frame: dict[str, Any],
    source_image: Image.Image,
    target: ManifestRow,
    walk: Any,
    final_image: Image.Image,
    visible_count: int,
    render_progress: Callable[[Any, ManifestRow, int], Image.Image],
    canvas_size: tuple[int, int],
    composition: str,
    settings: VideoSettings,
) -> Image.Image:
    width, height = canvas_size
    margin = max(8, round(width * 0.025))
    gutter = max(8, round(width * 0.018))
    label_height = max(20, round(height * 0.065))
    canvas = Image.new("RGB", canvas_size, BLACK)
    label_font = _font(max(10, round(width * 0.009)), bold=True)
    draw = ImageDraw.Draw(canvas)
    reconstruction = final_image if visible_count >= len(walk.result.placements) else render_progress(walk, target, visible_count)

    if composition != "split":
        content_box = (margin, label_height, width - margin, height - margin)
        source_canvas = Image.new("RGB", canvas_size, BLACK)
        _paste_contained(source_canvas, source_image, content_box)
        reconstruction_canvas = Image.new("RGB", canvas_size, BLACK)
        _paste_contained(reconstruction_canvas, reconstruction, content_box)
        if composition == "alternate":
            span = max(1, len(walk.result.placements) // 8)
            canvas = source_canvas if (visible_count // span) % 2 == 0 else reconstruction_canvas
        else:
            progress = visible_count / max(1, len(walk.result.placements))
            canvas = Image.blend(source_canvas, reconstruction_canvas, min(0.86, progress * 0.90))
        draw = ImageDraw.Draw(canvas)
        draw.text(
            (margin, max(2, label_height // 3)),
            "BÚSQUEDA · RECONSTRUCCIÓN",
            fill=MID_GREY,
            font=label_font,
        )
        return canvas.convert("L").convert("RGB")

    panel_width = (width - margin * 2 - gutter) // 2
    left_box = (margin, label_height, margin + panel_width, height - margin)
    right_box = (margin + panel_width + gutter, label_height, width - margin, height - margin)
    if settings.split_orientation == "stacked":
        left_box = (margin, label_height, width - margin, height // 2 - gutter // 2)
        right_box = (margin, height // 2 + label_height, width - margin, height - margin)
    draw.text((left_box[0], max(2, label_height // 3)), "BÚSQUEDA", fill=MID_GREY, font=label_font)
    draw.text((right_box[0], right_box[1] - label_height + max(2, label_height // 3)), "RECONSTRUCCIÓN", fill=MID_GREY, font=label_font)
    if settings.split_orientation == "stacked":
        draw.line((margin, height // 2, width - margin, height // 2), fill=(55, 55, 55))
    else:
        draw.line((width // 2, label_height, width // 2, height - margin), fill=(55, 55, 55))

    fitted_source, source_bounds, source_scale = _contain(source_image, left_box)
    canvas.paste(fitted_source, source_bounds[:2])
    reconstruction_bounds = _paste_contained(canvas, reconstruction, right_box)

    if visible_count and settings.show_match_marks and not source_frame.get("fragment_field"):
        placement = walk.result.placements[visible_count - 1]
        if placement.source_id == str(source_frame["id"]):
            source_x = source_bounds[0] + round(placement.source_x * source_scale)
            source_y = source_bounds[1] + round(placement.source_y * source_scale)
            source_w = max(3, round((placement.source_width or placement.image.width) * source_scale))
            source_h = max(3, round((placement.source_height or placement.image.height) * source_scale))
            draw.rectangle(
                (source_x, source_y, source_x + source_w, source_y + source_h),
                outline=(225, 225, 225),
                width=max(1, width // 960),
            )
            target_scale = min(
                (reconstruction_bounds[2] - reconstruction_bounds[0]) / reconstruction.width,
                (reconstruction_bounds[3] - reconstruction_bounds[1]) / reconstruction.height,
            )
            destination = (
                reconstruction_bounds[0] + round((placement.dest_x + placement.image.width / 2) * target_scale),
                reconstruction_bounds[1] + round((placement.dest_y + placement.image.height / 2) * target_scale),
            )
            draw.line(
                (source_x + source_w, source_y + source_h // 2, destination[0], destination[1]),
                fill=(112, 112, 112),
                width=max(1, width // 1280),
            )
    return canvas.convert("L").convert("RGB")


def complete_search_video_frames(
    segments: list[list[dict[str, Any]]],
    targets: list[ManifestRow],
    walks: Sequence[Any],
    final_images: Sequence[Image.Image],
    *,
    duration_seconds: int,
    fps: int,
    output_width: int,
    composition: str,
    render_progress: Callable[[Any, ManifestRow, int], Image.Image],
    settings: VideoSettings | None = None,
    artwork: str = "seguimos-buscando",
) -> Iterable[Image.Image]:
    """Render the common search, reconstruction, details and text sequence."""
    settings = settings or VideoSettings()
    total = max(fps, duration_seconds * fps)
    segment_lengths = [total // len(targets)] * len(targets)
    for index in range(total % len(targets)):
        segment_lengths[index] += 1
    canvas_size = video_canvas_size(output_width)

    for target_index, segment_length in enumerate(segment_lengths):
        timeline, holds = video_schedule(walks[target_index], segment_length, fps, settings)
        target = targets[target_index]
        walk = walks[target_index]
        frames = segments[target_index]
        final = final_images[target_index].convert("L").convert("RGB")
        loaded_source_id = ""
        loaded_source: Image.Image | None = None

        for reached, hold in enumerate(holds):
            source_frame = frames[reached]
            if source_frame["id"] != loaded_source_id:
                if "load_image" in source_frame:
                    loaded_source = source_frame["load_image"]().convert("L").convert("RGB")
                elif "image" in source_frame:
                    loaded_source = source_frame["image"].convert("L").convert("RGB")
                else:
                    with Image.open(str(source_frame["local_path"])) as source:
                        loaded_source = source.convert("L").convert("RGB")
                loaded_source_id = str(source_frame["id"])
            assert loaded_source is not None
            before = bisect.bisect_left(walk.placed_after_frame, reached)
            after = bisect.bisect_right(walk.placed_after_frame, reached)
            rendered_count = -1
            rendered_frame: Image.Image | None = None
            for local in range(hold):
                visible_count = before if local < max(1, hold // 3) else after
                if rendered_count != visible_count:
                    rendered_frame = _search_frame(
                        source_frame, loaded_source, target, walk, final, visible_count,
                        render_progress, canvas_size, composition, settings,
                    )
                    rendered_count = visible_count
                assert rendered_frame is not None
                yield rendered_frame

        final_canvas = Image.new("RGB", canvas_size, BLACK)
        _paste_contained(final_canvas, final, (0, 0, *canvas_size))
        for _ in range(timeline.final_hold):
            yield final_canvas
        for index in range(timeline.final_fade_out):
            yield _fade(final_canvas, _opacity(index, timeline.final_fade_out, rising=False))

        person = _person_card(target, canvas_size)
        for index in range(timeline.person_fade_in):
            yield _fade(person, _opacity(index, timeline.person_fade_in, rising=True))
        for _ in range(timeline.person_hold):
            yield person
        for index in range(timeline.person_fade_out):
            yield _fade(person, _opacity(index, timeline.person_fade_out, rising=False))

        title = _title_card(canvas_size, settings.closing_text or ARTWORK_TITLES[artwork])
        for index in range(timeline.title_fade_in):
            yield _fade(title, _opacity(index, timeline.title_fade_in, rising=True))
        for _ in range(timeline.title_hold):
            yield title
        for index in range(timeline.title_fade_out):
            yield _fade(title, _opacity(index, timeline.title_fade_out, rising=False))


def fragment_walk(assembly: Any) -> Any:
    from types import SimpleNamespace
    return SimpleNamespace(result=assembly, placed_after_frame=list(range(len(assembly.placements))),
                           segment_frame_ids=[str(i) for i in range(len(assembly.placements))])


def fragment_video_frames(assembly: Any, target: ManifestRow, settings: Any, artwork: str,
                          source_rows: Sequence[ManifestRow], source_manifest: str | Path,
                          *, grammar: str = "grid", reveal_sources: bool = True) -> Iterable[Image.Image]:
    """Shared four-phase form, revealing only approved source regions or fragments."""
    from .images import load_rgb, source_region_from_row
    from .manifests import row_file_path
    from .placement_history import render_placements
    from .pipeline_core import _contributing_fragment_field, _matched_fragment_field

    rows = {row.id: row for row in source_rows}
    walk = fragment_walk(assembly)
    frames = []
    for index, placement in enumerate(assembly.placements):
        row = rows[placement.source_id]
        def load_source(p=placement, row=row):
            if reveal_sources:
                return source_region_from_row(load_rgb(row_file_path(row, source_manifest)), row, row.kind)
            # Canonical people work retains its fragment-only source display.
            if getattr(settings, "video_source_layout", "grid") == "match":
                return _matched_fragment_field([p], assembly.image.size)[0]
            return _contributing_fragment_field([p], assembly.image.size, seed=settings.seed)[0]
        frames.append({"id": placement.source_id if reveal_sources else str(index), "load_image": load_source,
                       "fragment_field": not reveal_sources})
    if not frames:
        # Empty reconstruction still receives a complete commemorative sequence.
        frames = [{"id": "empty", "image": Image.new("RGB", (16, 16), BLACK), "fragment_field": True}]
        walk.segment_frame_ids = ["empty"]

    cache: dict[int, Image.Image] = {}
    def progress(walk: Any, target: ManifestRow, count: int) -> Image.Image:
        if count not in cache:
            cache.clear()
            placements = walk.result.placements[:count]
            if getattr(settings, "composition_mode", "grid") == "free":
                placements = sorted(placements, key=lambda p: (p.dest_y, p.dest_x))
            cache[count] = render_placements(placements, assembly.image.size, grammar=grammar,
                                              seed=settings.seed, target_id=target.id, background=BLACK)
        return cache[count]
    yield from complete_search_video_frames([frames], [target], [walk], [assembly.image],
        duration_seconds=settings.duration_seconds, fps=settings.fps, output_width=settings.output_width,
        composition="split", render_progress=progress, settings=settings, artwork=artwork)
