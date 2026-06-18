"""Computer-vision gating for crawled images.

Decides whether a candidate image should enter a manifest:

- For ``targets`` we want a clear human face (these become portrait targets), so
  we accept only images where a Haar frontal-face detector finds a face covering
  a meaningful fraction of the frame.
- For ``places`` we want textured scenes/surfaces, so we reject portraits
  (prominent faces), tiny images, extreme aspect ratios, and near-flat graphics
  such as logos and banners.

Detection runs on a downscaled grayscale copy for speed. The OpenCV Haar
cascade ships with ``opencv-python-headless`` (no model download).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

from .manifests import ManifestKind

_CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")

# Tunables.
_MAX_DETECT_SIDE = 640          # downscale longest side before face detection
_TARGET_MIN_FACE_FRACTION = 0.02  # a target face must cover >= 2% of the image
_PLACE_MIN_SIDE = 320           # places need reasonable resolution
_PLACE_ASPECT_RANGE = (0.4, 2.6)  # reject banners/thin strips
_PLACE_MIN_TEXTURE = 0.012      # mean edge density floor (drops flat logos)
_PLACE_MAX_FACE_FRACTION = 0.06  # a place dominated by a face is really a portrait

_cascade: cv2.CascadeClassifier | None = None


@dataclass(frozen=True)
class CVResult:
    accept: bool
    label: str
    score: float
    reason: str


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


def texture_score(image: Image.Image) -> float:
    """Mean gradient magnitude on a small grayscale copy (0..1-ish)."""
    gray = np.asarray(image.convert("L").resize((128, 128)), dtype=np.float32) / 255.0
    gx = float(np.abs(np.diff(gray, axis=1)).mean())
    gy = float(np.abs(np.diff(gray, axis=0)).mean())
    return (gx + gy) / 2.0


def _largest_face_fraction(
    faces: list[tuple[int, int, int, int]], width: int, height: int
) -> float:
    if not faces or width <= 0 or height <= 0:
        return 0.0
    x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
    return (w * h) / float(width * height)


def classify_image(image: Image.Image, kind: ManifestKind) -> CVResult:
    """Decide whether ``image`` should be accepted for the given manifest kind."""
    width, height = image.size
    faces = detect_faces(image)
    face_fraction = _largest_face_fraction(faces, width, height)

    if kind == "targets":
        if face_fraction >= _TARGET_MIN_FACE_FRACTION:
            return CVResult(True, "face", face_fraction, f"face covers {face_fraction:.0%} of frame")
        if faces:
            return CVResult(False, "face-too-small", face_fraction, "face too small for a portrait target")
        return CVResult(False, "no-face", 0.0, "no clear frontal face detected")

    # places
    if min(width, height) < _PLACE_MIN_SIDE:
        return CVResult(False, "too-small", 0.0, f"min side {min(width, height)}px < {_PLACE_MIN_SIDE}px")
    aspect = width / height if height else 0.0
    if not (_PLACE_ASPECT_RANGE[0] <= aspect <= _PLACE_ASPECT_RANGE[1]):
        return CVResult(False, "bad-aspect", aspect, f"aspect {aspect:.2f} outside place range")
    if face_fraction > _PLACE_MAX_FACE_FRACTION:
        return CVResult(False, "portrait", face_fraction, "prominent face: looks like a portrait, not a place")
    texture = texture_score(image)
    if texture < _PLACE_MIN_TEXTURE:
        return CVResult(False, "flat", texture, "too flat (likely logo/graphic)")
    return CVResult(True, "place", texture, f"textured scene (texture {texture:.3f})")
