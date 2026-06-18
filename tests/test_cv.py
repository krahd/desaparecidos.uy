from __future__ import annotations

import numpy as np
from PIL import Image

from desaparecidos.cv import classify_image, detect_faces


def noise_image(width: int = 400, height: int = 400) -> Image.Image:
    arr = np.random.default_rng(0).integers(0, 255, (height, width, 3), dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def test_place_rejects_flat_graphic() -> None:
    flat = Image.new("RGB", (500, 400), (200, 60, 60))
    result = classify_image(flat, "places")
    assert result.accept is False
    assert result.label == "flat"


def test_place_rejects_low_resolution() -> None:
    small = Image.new("RGB", (120, 90), (100, 120, 140))
    result = classify_image(small, "places")
    assert result.accept is False
    assert result.label == "too-small"


def test_place_accepts_textured_scene() -> None:
    result = classify_image(noise_image(), "places")
    assert result.accept is True
    assert result.label == "place"


def test_target_rejects_image_without_face() -> None:
    result = classify_image(noise_image(), "targets")
    assert result.accept is False
    assert result.label in {"no-face", "face-too-small"}


def test_face_detector_runs_on_noise() -> None:
    # No crash, and pure noise should not yield a confident face.
    assert detect_faces(noise_image()) == []
