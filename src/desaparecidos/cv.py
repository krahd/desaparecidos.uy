from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image

from .manifests import ManifestKind


@dataclass(frozen=True)
class CVResult:
    accept: bool
    label: str
    score: float
    reason: str
    face_box: tuple[int, int, int, int] | None = None


def perceptual_hash(image: Image.Image, hash_size: int = 8) -> str:
    """Return a small average hash for exact and near-duplicate detection."""
    gray = image.convert("L").resize((hash_size, hash_size), Image.Resampling.LANCZOS)
    values = np.asarray(gray, dtype=np.float32)
    mean = float(values.mean())
    bits = values >= mean
    value = 0
    for bit in bits.flatten():
        value = (value << 1) | int(bool(bit))
    return f"{value:0{hash_size * hash_size // 4}x}"


def hamming_distance(left: str, right: str) -> int:
    if not left or not right:
        return 999
    try:
        return (int(left, 16) ^ int(right, 16)).bit_count()
    except ValueError:
        return 999


def texture_score(image: Image.Image) -> float:
    gray = np.asarray(image.convert("L").resize((128, 128)), dtype=np.float32) / 255.0
    gx = float(np.abs(np.diff(gray, axis=1)).mean())
    gy = float(np.abs(np.diff(gray, axis=0)).mean())
    return (gx + gy) / 2.0


def classify_image(image: Image.Image, kind: ManifestKind) -> CVResult:
    width, height = image.size
    if min(width, height) < 64:
        return CVResult(False, "too-small", 0.0, f"min side {min(width, height)}px < 64px")

    aspect = width / height if height else 0.0
    texture = texture_score(image)

    if kind == "places":
        if min(width, height) < 160:
            return CVResult(False, "too-small", 0.0, f"min side {min(width, height)}px < 160px")
        if not 0.35 <= aspect <= 3.2:
            return CVResult(False, "bad-aspect", aspect, f"aspect {aspect:.2f} outside place range")
        if texture < 0.008:
            return CVResult(False, "flat", texture, "too flat for a place/source image")
        return CVResult(True, "place", texture, f"textured place candidate ({texture:.3f})")

    if kind in {"targets", "people"}:
        if not 0.35 <= aspect <= 2.4:
            return CVResult(False, "bad-aspect", aspect, f"aspect {aspect:.2f} outside portrait range")
        if texture < 0.004:
            return CVResult(False, "flat", texture, "too flat for a face/people candidate")
        box_width = max(1, int(width * 0.5))
        box_height = max(1, int(height * 0.58))
        face_box = ((width - box_width) // 2, int(height * 0.16), box_width, box_height)
        return CVResult(True, "face-candidate", texture, "manual-review people/face candidate", face_box)

    return CVResult(False, "unsupported-kind", 0.0, f"unsupported manifest kind {kind}")
