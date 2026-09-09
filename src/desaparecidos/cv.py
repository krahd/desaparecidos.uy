"""Computer-vision helpers for crawled images.

The crawler uses this module for lightweight, local filtering only. It never
identifies people. For ``targets`` and internal ``people`` rows it requires a
detected face region for manual review; for ``places`` it rejects tiny,
banner-like, flat, graphic, noisy, or face-dominated images.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

from .manifests import ManifestKind

CV_POLICY_VERSION = 4
_CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
_EYE_CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_eye.xml")

_MAX_DETECT_SIDE = 640
_TARGET_MIN_FACE_FRACTION = 0.02
_PEOPLE_MIN_SIDE = 160
_PEOPLE_MIN_FACE_FRACTION = 0.015
_PEOPLE_MIN_FACE_SIDE = 32
_PEOPLE_ASPECT_RANGE = (0.35, 2.4)
_PEOPLE_MIN_TEXTURE = 0.004
_PLACE_MIN_SIDE = 320
_PLACE_ASPECT_RANGE = (0.4, 2.6)
_PLACE_MIN_TEXTURE = 0.009
_PLACE_MAX_FACE_FRACTION = 0.02
_PLACE_MIN_GRAY_STD = 0.035
_PLACE_MIN_COLOR_STD = 0.018
_PLACE_MIN_EDGE_DENSITY = 0.015
_PLACE_MAX_EDGE_DENSITY = 0.32
_PLACE_MIN_UNIQUE_RATIO = 0.004
_PLACE_MAX_NOISE_UNIQUE_RATIO = 0.08
_PLACE_MAX_POSTER_WHITE_FRACTION = 0.78
_PLACE_MIN_POSTER_LOW_SATURATION_FRACTION = 0.85
_PLACE_MAX_POSTER_MIDTONE_FRACTION = 0.21

_cascade: cv2.CascadeClassifier | None = None
_eye_cascade: cv2.CascadeClassifier | None = None
_yunet_detector: cv2.FaceDetectorYN | None = None
_yunet_model_path: str | None = None


@dataclass(frozen=True)
class CVResult:
    accept: bool
    label: str
    score: float
    reason: str
    face_box: tuple[int, int, int, int] | None = None


@dataclass(frozen=True)
class PhotoLikeness:
    score: float
    texture: float
    gray_std: float
    color_std: float
    edge_density: float
    unique_ratio: float


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


def _face_regions_with_eyes(
    image: Image.Image,
    faces: list[tuple[int, int, int, int]],
) -> list[tuple[int, int, int, int]]:
    """Return supplied face detections with an independent eye confirmation."""
    global _eye_cascade
    if _eye_cascade is None:
        _eye_cascade = cv2.CascadeClassifier(_EYE_CASCADE_PATH)
    if _eye_cascade.empty():
        return []
    gray = np.asarray(image.convert("L"))
    verified: list[tuple[int, int, int, int]] = []
    for x, y, width, height in faces:
        face = gray[y:y + height, x:x + width]
        minimum = max(8, min(width, height) // 10)
        eyes = _eye_cascade.detectMultiScale(
            face,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(minimum, minimum),
        )
        if len(eyes):
            verified.append((x, y, width, height))
    return verified


def detect_face_regions_with_eyes(image: Image.Image) -> list[tuple[int, int, int, int]]:
    """Return face detections that contain at least one independently detected eye."""
    return _face_regions_with_eyes(image, detect_faces(image))


def detect_yunet_face_regions(
    image: Image.Image,
) -> list[tuple[int, int, int, int]] | None:
    """Return landmark-bearing YuNet detections, or ``None`` when not configured."""
    global _yunet_detector, _yunet_model_path
    model_path = os.environ.get("DESAPARECIDOS_YUNET_MODEL", "").strip()
    if not model_path:
        return None
    if not os.path.isfile(model_path):
        raise ValueError(f"YuNet face model does not exist: {model_path}")
    if _yunet_detector is None or _yunet_model_path != model_path:
        _yunet_detector = cv2.FaceDetectorYN.create(
            model_path,
            "",
            (320, 320),
            score_threshold=0.88,
            nms_threshold=0.3,
            top_k=5000,
        )
        _yunet_model_path = model_path
    rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    height, width = rgb.shape[:2]
    scale = min(1.0, _MAX_DETECT_SIDE / max(height, width))
    if scale < 1.0:
        rgb = cv2.resize(rgb, (max(1, round(width * scale)), max(1, round(height * scale))))
    detect_height, detect_width = rgb.shape[:2]
    _yunet_detector.setInputSize((detect_width, detect_height))
    _status, detections = _yunet_detector.detect(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    if detections is None:
        return []
    inverse = 1.0 / scale if scale else 1.0
    boxes: list[tuple[int, int, int, int]] = []
    for detection in detections:
        x, y, box_width, box_height = detection[:4]
        boxes.append((
            max(0, round(float(x) * inverse)),
            max(0, round(float(y) * inverse)),
            max(1, round(float(box_width) * inverse)),
            max(1, round(float(box_height) * inverse)),
        ))
    return boxes


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


def photo_likeness_score(image: Image.Image) -> PhotoLikeness:
    """Return simple local statistics for conservative place-photo gating.

    This is not a semantic scene recogniser. It rejects obvious graphics, flat
    fills, and noise-like textures before manual review.
    """
    resized = image.convert("RGB").resize((160, 160), Image.Resampling.LANCZOS)
    rgb_u8 = np.asarray(resized, dtype=np.uint8)
    rgb = rgb_u8.astype(np.float32) / 255.0
    gray_u8 = np.asarray(resized.convert("L"), dtype=np.uint8)
    gray = gray_u8.astype(np.float32) / 255.0

    texture = texture_score(image)
    gray_std = float(gray.std())
    color_std = float(rgb.reshape(-1, 3).std(axis=0).mean())
    edges = cv2.Canny(gray_u8, 40, 110)
    edge_density = float((edges > 0).mean())
    quantised = (rgb_u8 // 16).reshape(-1, 3)
    unique_ratio = float(len(np.unique(quantised, axis=0)) / max(1, len(quantised)))
    score = (texture + gray_std + color_std + edge_density + unique_ratio) / 5.0
    return PhotoLikeness(score, texture, gray_std, color_std, edge_density, unique_ratio)


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


def classify_image(image: Image.Image, kind: ManifestKind) -> CVResult:
    """Decide whether ``image`` should enter the manifest for ``kind``."""
    width, height = image.size
    if min(width, height) < 64:
        return CVResult(False, "too-small", 0.0, f"min side {min(width, height)}px < 64px")

    aspect = width / height if height else 0.0
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
        texture = texture_score(image)
        if min(width, height) < _PEOPLE_MIN_SIDE:
            return CVResult(
                False,
                "too-small",
                0.0,
                f"min side {min(width, height)}px < {_PEOPLE_MIN_SIDE}px",
            )
        if not _PEOPLE_ASPECT_RANGE[0] <= aspect <= _PEOPLE_ASPECT_RANGE[1]:
            return CVResult(False, "bad-aspect", aspect, f"aspect {aspect:.2f} outside people range")
        if texture < _PEOPLE_MIN_TEXTURE:
            return CVResult(False, "flat", texture, "too flat for a people candidate")
        yunet_faces = detect_yunet_face_regions(image)
        verified_faces = (
            yunet_faces
            if yunet_faces is not None
            else _face_regions_with_eyes(image, faces)
        )
        face = _largest_face(verified_faces)
        face_fraction = _face_fraction(face, width, height)
        if face is None:
            label = "no-face" if not faces and not yunet_faces else "unconfirmed-face"
            return CVResult(
                False,
                label,
                0.0,
                "no frontal face with independent eye confirmation detected",
            )
        _x, _y, face_width, face_height = face
        if (
            face_width < _PEOPLE_MIN_FACE_SIDE
            or face_height < _PEOPLE_MIN_FACE_SIDE
            or face_fraction < _PEOPLE_MIN_FACE_FRACTION
        ):
            return CVResult(
                False,
                "face-too-small",
                face_fraction,
                "face too small for a people candidate",
                face,
            )
        return CVResult(
            True,
            "face-yunet" if yunet_faces is not None else "face",
            face_fraction,
            f"face covers {face_fraction:.0%} of frame",
            face,
        )

    if kind == "places":
        if min(width, height) < _PLACE_MIN_SIDE:
            return CVResult(False, "too-small", 0.0, f"min side {min(width, height)}px < {_PLACE_MIN_SIDE}px")
        if not (_PLACE_ASPECT_RANGE[0] <= aspect <= _PLACE_ASPECT_RANGE[1]):
            return CVResult(False, "bad-aspect", aspect, f"aspect {aspect:.2f} outside place range")
        if face_fraction > _PLACE_MAX_FACE_FRACTION:
            return CVResult(False, "portrait", face_fraction, "prominent face: looks like a portrait, not a place", face)
        photo = photo_likeness_score(image)
        diagnostic = image.convert("RGB").resize((160, 160), Image.Resampling.LANCZOS)
        rgb = np.asarray(diagnostic, dtype=np.uint8)
        gray = np.asarray(diagnostic.convert("L"), dtype=np.uint8)
        saturation = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)[:, :, 1]
        near_white_fraction = float((gray > 235).mean())
        low_saturation_fraction = float((saturation < 15).mean())
        midtone_fraction = float(((gray >= 35) & (gray <= 235)).mean())
        if (
            near_white_fraction > _PLACE_MAX_POSTER_WHITE_FRACTION
            and low_saturation_fraction > _PLACE_MIN_POSTER_LOW_SATURATION_FRACTION
            and midtone_fraction < _PLACE_MAX_POSTER_MIDTONE_FRACTION
        ):
            return CVResult(False, "graphic", near_white_fraction, "mostly white low-saturation layout; likely poster/graphic")
        if photo.texture < _PLACE_MIN_TEXTURE:
            return CVResult(False, "flat", photo.texture, "too flat (likely logo/graphic)")
        if photo.gray_std < _PLACE_MIN_GRAY_STD or photo.color_std < _PLACE_MIN_COLOR_STD:
            return CVResult(False, "flat", photo.score, "too little tonal or colour variation for a place photo")
        if photo.unique_ratio < _PLACE_MIN_UNIQUE_RATIO:
            return CVResult(False, "graphic", photo.unique_ratio, "limited palette; likely graphic/logo/poster")
        if photo.edge_density < _PLACE_MIN_EDGE_DENSITY:
            return CVResult(False, "flat", photo.edge_density, "too few edges for a place photo")
        if (
            photo.edge_density > _PLACE_MAX_EDGE_DENSITY
            or photo.unique_ratio > _PLACE_MAX_NOISE_UNIQUE_RATIO
        ):
            return CVResult(False, "noise", photo.score, "too noisy/random-looking for a place photo")
        reason = (
            "photo-like scene "
            f"(texture {photo.texture:.3f}, edges {photo.edge_density:.3f}, "
            f"unique {photo.unique_ratio:.3f})"
        )
        return CVResult(True, "place-photo", photo.score, reason)

    return CVResult(False, "unsupported-kind", 0.0, f"unsupported manifest kind {kind}")
