from __future__ import annotations

import importlib.util
from pathlib import Path

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
