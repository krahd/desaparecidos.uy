from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from desaparecidos.preprocess import content_bbox, normalize_portrait


def bordered_portrait() -> Image.Image:
    image = Image.new("RGB", (200, 260), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 30, 160, 230), fill=(130, 120, 110))
    draw.ellipse((75, 62, 125, 120), fill=(70, 62, 55))
    draw.rectangle((68, 122, 132, 215), fill=(92, 83, 74))
    draw.text((55, 238), "caption in border", fill=(0, 0, 0))
    return image


def scan_bordered_portrait() -> Image.Image:
    """A portrait sitting inside a wide white scan margin, with a thin dark
    artefact reaching into the left margin (the kind of stray mark that drags
    component detection into the border)."""
    image = Image.new("RGB", (300, 400), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((90, 110, 210, 290), fill=(120, 110, 100))
    draw.ellipse((120, 130, 180, 190), fill=(70, 62, 55))
    draw.line((20, 200, 90, 200), fill=(60, 55, 50), width=1)  # thin protrusion
    return image


def _max_white_border(image: Image.Image, threshold: int = 232, fraction: float = 0.9) -> int:
    white = np.asarray(image.convert("L")) >= threshold
    rows, cols = white.mean(axis=1), white.mean(axis=0)

    def lead(values: np.ndarray) -> int:
        index = 0
        while index < len(values) and values[index] >= fraction:
            index += 1
        return index

    return max(lead(rows), lead(rows[::-1]), lead(cols), lead(cols[::-1]))


def test_content_bbox_ignores_text_in_white_border() -> None:
    left, top, right, bottom = content_bbox(bordered_portrait())

    assert left <= 40
    assert top <= 30
    assert right >= 160
    assert bottom <= 236


def test_normalize_portrait_crops_to_target_aspect() -> None:
    normalized = normalize_portrait(bordered_portrait(), aspect=3 / 4, use_face=False)

    assert abs((normalized.width / normalized.height) - 0.75) < 0.01
    assert normalized.width < 200
    assert normalized.height < 260


def test_content_bbox_tightens_past_white_scan_margin() -> None:
    # The dark block starts at x=90; a thin artefact reaches to x=20. Tightening
    # must trim the near-white margin back to the real content edge.
    left, _top, _right, _bottom = content_bbox(scan_bordered_portrait())

    assert left >= 70


def test_normalize_portrait_removes_white_scan_border() -> None:
    normalized = normalize_portrait(scan_bordered_portrait(), aspect=3 / 4, use_face=False)

    assert _max_white_border(normalized) <= 2


def test_build_targets_manifest_points_to_processed_copy(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_targets_manifest.py"
    spec = importlib.util.spec_from_file_location("build_targets_manifest", script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    source = tmp_path / "source"
    source.mkdir()
    bordered_portrait().save(source / "Apellido - Nombre.jpg")
    manifest = tmp_path / "data" / "manifests" / "local-targets.csv"
    processed_root = tmp_path / "data" / "processed" / "targets"

    rows = module.build_rows(
        source,
        manifest,
        processed_root=processed_root,
        aspect=3 / 4,
        use_face=False,
    )

    assert len(rows) == 1
    local_path = rows[0]["local_path"]
    assert "processed" in local_path
    processed = (manifest.parent / local_path).resolve()
    assert processed.exists()
    with Image.open(processed) as image:
        assert abs((image.width / image.height) - 0.75) < 0.01
