from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw
import pytest

import desaparecidos.cv as cv_module
from desaparecidos.cv import classify_image, detect_faces


def noise_image(width: int = 400, height: int = 400) -> Image.Image:
    arr = np.random.default_rng(0).integers(0, 255, (height, width, 3), dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def place_photo_image(width: int = 480, height: int = 360) -> Image.Image:
    rng = np.random.default_rng(1)
    yy = np.linspace(0, 1, height)[:, None]
    xx = np.linspace(0, 1, width)[None, :]
    red = 90 + 80 * xx + 20 * yy
    green = 105 + 70 * yy + 15 * np.sin(xx * 8)
    blue = 95 + 45 * (1 - yy) + 10 * np.cos(xx * 5)
    arr = np.stack(
        [
            np.broadcast_to(red, (height, width)),
            np.broadcast_to(green, (height, width)),
            np.broadcast_to(blue, (height, width)),
        ],
        axis=2,
    )
    arr += rng.normal(0, 8, arr.shape)
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    image = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(image)
    draw.rectangle((35, 170, 160, 300), fill=(115, 110, 100))
    draw.rectangle((190, 120, 430, 250), fill=(145, 132, 118))
    draw.line((0, 300, width, 260), fill=(55, 60, 58), width=4)
    draw.line((0, 320, width, 330), fill=(65, 70, 68), width=3)
    for x in range(200, 420, 35):
        draw.rectangle((x, 145, x + 18, 190), fill=(70, 82, 90))
    return image


def test_place_rejects_flat_graphic() -> None:
    flat = Image.new("RGB", (500, 400), (200, 60, 60))
    result = classify_image(flat, "places")
    assert result.accept is False
    assert result.label == "flat"


def test_place_rejects_mostly_white_low_saturation_poster() -> None:
    poster = Image.new("RGB", (800, 500), "white")
    draw = ImageDraw.Draw(poster)
    draw.rectangle((80, 100, 300, 320), fill=(225, 225, 225))
    for y, width in ((105, 300), (180, 420), (245, 360), (315, 460)):
        draw.rectangle((380, y, 380 + width, y + 22), fill=(15, 15, 15))
    result = classify_image(poster, "places")
    assert result.accept is False
    assert result.label == "graphic"


def test_place_rejects_low_resolution() -> None:
    small = Image.new("RGB", (120, 90), (100, 120, 140))
    result = classify_image(small, "places")
    assert result.accept is False
    assert result.label == "too-small"


def test_place_accepts_textured_scene() -> None:
    result = classify_image(place_photo_image(), "places")
    assert result.accept is True
    assert result.label == "place-photo"


def test_place_rejects_random_noise() -> None:
    result = classify_image(noise_image(), "places")
    assert result.accept is False
    assert result.label == "noise"


def test_place_rejects_prominent_face(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cv_module, "detect_faces", lambda image: [(50, 50, 160, 160)])
    result = classify_image(place_photo_image(400, 400), "places")
    assert result.accept is False
    assert result.label == "portrait"


def test_target_rejects_image_without_face() -> None:
    result = classify_image(noise_image(), "targets")
    assert result.accept is False
    assert result.label in {"no-face", "face-too-small"}


def test_people_rejects_image_without_face() -> None:
    result = classify_image(place_photo_image(), "people")
    assert result.accept is False
    assert result.label == "no-face"


def test_people_accepts_clear_detected_face(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cv_module, "detect_faces", lambda image: [(90, 70, 90, 90)])
    monkeypatch.setattr(
        cv_module,
        "_face_regions_with_eyes",
        lambda _image, faces: faces,
    )
    result = classify_image(place_photo_image(260, 260), "people")
    assert result.accept is True
    assert result.label == "face"
    assert result.face_box == (90, 70, 90, 90)


def test_people_rejects_unconfirmed_face(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cv_module, "detect_faces", lambda image: [(90, 70, 90, 90)])
    monkeypatch.setattr(cv_module, "_face_regions_with_eyes", lambda _image, _faces: [])

    result = classify_image(place_photo_image(260, 260), "people")

    assert result.accept is False
    assert result.label == "unconfirmed-face"


def test_face_detector_runs_on_noise() -> None:
    # No crash, and pure noise should not yield a confident face.
    assert detect_faces(noise_image()) == []
