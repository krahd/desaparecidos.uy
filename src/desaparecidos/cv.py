"""Computer-vision helpers for crawled images.

The crawler uses this module for lightweight, local filtering only. It never
identifies people. For ``targets`` and internal ``people`` rows it records a
candidate face region for manual review; for ``places`` it rejects tiny,
banner-like, flat, or face-dominated images.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

from .manifests import ManifestKind

_CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")

_MAX_DETECT_SIDE = 640
_TARGET_MIN_FACE_FRACTION = 0.02
_PEOPLE_MIN_FACE_FRACTION = 0.01
_PLACE_MIN_SIDE = 320
_PLACE_ASPECT_RANGE = (0.4, 2.6)
_PLACE_MIN_TEXTURE = 0.012
_PLACE_MAX_FACE_FRACTION = 0.06

_cascade: cv2.CascadeClassifier | None = None


@dataclass(frozen=True)
class CVResult:
    accept: bool
    label: str
    score: float
    reason: str
    face_box: tuple[int, int, int, int] | None = None


def _face_cascade() -> cv2.CascadeClassifier:
    global _cascade
    if _cascade is None:
        _cascade = cv2.CascadeClassifier(_CASCADE_PATH)
    return _cascade


def detect_faces(image: Image.Image) -> list[tuple[int, int, int, int]]:
    """Return face boxes (x, y, w, h) in original-image coordinates."""
    cascade = _face_cascade()
    if cascade.empty():
        return []
    gray = np.asarray(image.convert("L"))
    height, width = gray.shape
    scale = min(1.0, _MAX_DETECT_SIDE / max(height, width))
    if scale < 1.0:
        gray = cv2.resize(gray, (max(1, int(width * scale)), max(1, int(height * scale))))
    gray = cv2.equalizeHist(gray)
    detections = cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    inverse = 1.0 / scale if scale > 0 else 1.0
    return [
        (int(x * inverse), int(y * inverse), int(w * inverse), int(h * inverse))
        for (x, y, w, h) in detections
    ]


def perceptual_hash(image: Image.Image, hash_size: int = 8) -> str:
    """Return a small average hash for near-duplicate detection."""
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
    """Mean gradient magnitude on a small grayscale copy."""
    gray = np.asarray(image.convert("L").resize((128, 128)), dtype=np.float32) / 255.0
    gx = float(np.abs(np.diff(gray, axis=1)).mean())
    gy = float(np.abs(np.diff(gray, axis=0)).mean())
    return (gx + gy) / 2.0


def _largest_face(
    faces: list[tuple[int, int, int, int]],
) -> tuple[int, int, int, int] | None:
    if not faces:
        return None
    return max(faces, key=lambda box: box[2] * box[3])


def _face_fraction(face: tuple[int, int, int, int] | None, width: int, height: int) -> float:
    if face is None or width <= 0 or height <= 0:
        return 0.0
    _x, _y, w, h = face
    return (w * h) / float(width * height)


def _fallback_face_box(width: int, height: int) -> tuple[int, int, int, int]:
    box_width = max(1, int(width * 0.5))
    box_height = max(1, int(height * 0.58))
    return ((width - box_width) // 2, int(height * 0.16), box_width, box_height)


def classify_image(image: Image.Image, kind: ManifestKind) -> CVResult:
    """Decide whether ``image`` should enter the manifest for ``kind``."""
    width, height = image.size
    if min(width, height) < 64:
        return CVResult(False, "too-small", 0.0, f"min side {min(width, height)}px < 64px")

    aspect = width / height if height else 0.0
    texture = texture_score(image)
    faces = detect_faces(image)
    face = _largest_face(faces)
    face_fraction = _face_fraction(face, width, height)

    if kind == "targets":
        if face_fraction >= _TARGET_MIN_FACE_FRACTION:
            return CVResult(
                True,
                "face",
                face_fraction,
                f"face covers {face_fraction:.0%} of frame",
                face,
            )
        if faces:
            return CVResult(
                False,
                "face-too-small",
                face_fraction,
                "face too small for a portrait target",
                face,
            )
        return CVResult(False, "no-face", 0.0, "no clear frontal face detected")

    if kind == "people":
        if not 0.35 <= aspect <= 2.4:
            return CVResult(False, "bad-aspect", aspect, f"aspect {aspect:.2f} outside people range")
        if texture < 0.004:
            return CVResult(False, "flat", texture, "too flat for a people candidate")
        if face_fraction >= _PEOPLE_MIN_FACE_FRACTION:
            return CVResult(
                True,
                "face",
                face_fraction,
                f"face covers {face_fraction:.0%} of frame",
                face,
            )
        return CVResult(
            True,
            "face-candidate",
            texture,
            "manual-review people candidate",
            _fallback_face_box(width, height),
        )

    if kind == "places":
        if min(width, height) < _PLACE_MIN_SIDE:
            return CVResult(False, "too-small", 0.0, f"min side {min(width, height)}px < {_PLACE_MIN_SIDE}px")
        if not (_PLACE_ASPECT_RANGE[0] <= aspect <= _PLACE_ASPECT_RANGE[1]):
            return CVResult(False, "bad-aspect", aspect, f"aspect {aspect:.2f} outside place range")
        if face_fraction > _PLACE_MAX_FACE_FRACTION:
            return CVResult(False, "portrait", face_fraction, "prominent face: looks like a portrait, not a place", face)
        if texture < _PLACE_MIN_TEXTURE:
            return CVResult(False, "flat", texture, "too flat (likely logo/graphic)")
        return CVResult(True, "place", texture, f"textured scene (texture {texture:.3f})")

    return CVResult(False, "unsupported-kind", 0.0, f"unsupported manifest kind {kind}")
