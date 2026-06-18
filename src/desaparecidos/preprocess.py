"""Pre-process disappeared-person portraits for Stage 1.

Many scanned portraits sit inside a near-white photographic border, sometimes
with printed text in the margin. This trims that border and crops the photo to a
single target aspect ratio so every target fills the frame ("full screen")
consistently. When a face is found the crop stays centred on the person.

The originals in ``doc/fotos-desaparecidos/`` are never modified; callers write
processed copies to an ignored location.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from .cv import detect_faces

WHITE_THRESHOLD = 232          # pixels >= this count as "white" border
BORDER_WHITE_FRACTION = 0.9    # a row/col this white is treated as border
MAX_TRIM_FRACTION = 0.45       # never trim more than this from one side
MIN_KEEP_FRACTION = 0.2        # refuse to trim a dimension below this
MIN_FACE_FRACTION = 0.012      # ignore faces smaller than this share of the box
MIN_COMPONENT_FRACTION = 0.003  # ignore tiny dark components such as captions
CONTENT_PADDING_FRACTION = 0.025


def _scan_bounds(white_fraction: np.ndarray) -> tuple[int, int]:
    count = len(white_fraction)
    limit = int(count * MAX_TRIM_FRACTION)
    start = 0
    while start < limit and white_fraction[start] >= BORDER_WHITE_FRACTION:
        start += 1
    back = 0
    while back < limit and white_fraction[count - 1 - back] >= BORDER_WHITE_FRACTION:
        back += 1
    end = count - back
    if end - start < count * MIN_KEEP_FRACTION:
        return 0, count
    return start, end


def content_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    """Bounding box (left, top, right, bottom) of the photo inside a white border."""
    gray = np.asarray(image.convert("L"))
    height, width = gray.shape
    component_box = _component_content_bbox(gray)
    if component_box is not None:
        return component_box

    white = gray >= WHITE_THRESHOLD
    top, bottom = _scan_bounds(white.mean(axis=1))
    left, right = _scan_bounds(white.mean(axis=0))
    if right <= left or bottom <= top:
        return 0, 0, width, height
    return left, top, right, bottom


def _component_content_bbox(gray: np.ndarray) -> tuple[int, int, int, int] | None:
    """Find the main non-white content while ignoring small caption/text marks."""
    height, width = gray.shape
    mask = (gray < WHITE_THRESHOLD).astype(np.uint8)
    if int(mask.sum()) == 0:
        return None

    kernel_size = max(3, int(round(min(width, height) * 0.018)))
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    if int(opened.sum()) == 0:
        return None

    count, _labels, stats, _centres = cv2.connectedComponentsWithStats(opened, 8)
    min_area = max(32, int(width * height * MIN_COMPONENT_FRACTION))
    kept: list[tuple[int, int, int, int]] = []
    for label in range(1, count):
        x, y, w, h, area = (int(value) for value in stats[label])
        if area < min_area:
            continue
        kept.append((x, y, x + w, y + h))
    if not kept:
        return None

    left = min(box[0] for box in kept)
    top = min(box[1] for box in kept)
    right = max(box[2] for box in kept)
    bottom = max(box[3] for box in kept)
    pad = max(2, int(round(min(width, height) * CONTENT_PADDING_FRACTION)))
    return (
        max(0, left - pad),
        max(0, top - pad),
        min(width, right + pad),
        min(height, bottom + pad),
    )


def _aspect_crop(
    box: tuple[int, int, int, int],
    aspect: float,
    faces: list[tuple[int, int, int, int]],
) -> tuple[int, int, int, int]:
    left, top, right, bottom = box
    box_width, box_height = right - left, bottom - top
    if box_width / box_height > aspect:
        new_width, new_height = int(round(box_height * aspect)), box_height
    else:
        new_width, new_height = box_width, int(round(box_width / aspect))

    usable = [f for f in faces if (f[2] * f[3]) >= MIN_FACE_FRACTION * box_width * box_height]
    if usable:
        fx, fy, fw, fh = max(usable, key=lambda f: f[2] * f[3])
        centre_x, centre_y = fx + fw / 2, fy + fh / 2
    else:
        centre_x, centre_y = left + box_width / 2, top + box_height * 0.45

    x0 = int(round(centre_x - new_width / 2))
    y0 = int(round(centre_y - new_height / 2))
    x0 = max(left, min(x0, right - new_width))
    y0 = max(top, min(y0, bottom - new_height))
    return x0, y0, x0 + new_width, y0 + new_height


def normalize_portrait(
    image: Image.Image, *, aspect: float = 3 / 4, use_face: bool = True
) -> Image.Image:
    """Trim the white border and crop to ``aspect`` (width / height)."""
    box = content_bbox(image)
    faces: list[tuple[int, int, int, int]] = []
    if use_face:
        local = detect_faces(image.crop(box))
        faces = [(x + box[0], y + box[1], w, h) for (x, y, w, h) in local]
    return image.crop(_aspect_crop(box, aspect, faces))


def preprocess_file(
    src: str | Path,
    dst: str | Path,
    *,
    aspect: float = 3 / 4,
    use_face: bool = True,
    max_side: int = 1200,
) -> tuple[int, int]:
    image = Image.open(src).convert("RGB")
    result = normalize_portrait(image, aspect=aspect, use_face=use_face)
    if max(result.size) > max_side:
        scale = max_side / max(result.size)
        result = result.resize(
            (max(1, int(result.width * scale)), max(1, int(result.height * scale))),
            Image.Resampling.LANCZOS,
        )
    dst_path = Path(dst)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(dst_path, quality=92)
    return result.size


def parse_aspect(value: str) -> float:
    """Parse ``"3:4"`` or ``"0.75"`` into a width/height ratio."""
    text = value.strip()
    if ":" in text:
        width, height = text.split(":", 1)
        ratio = float(width) / float(height)
    else:
        ratio = float(text)
    if ratio <= 0:
        raise ValueError("aspect must be positive")
    return ratio
