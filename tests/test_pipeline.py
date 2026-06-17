from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw
import pytest

from desaparecidos.pipeline import Stage1Settings, run_stage1


def make_image(path: Path, base: tuple[int, int, int], accent: tuple[int, int, int]) -> None:
    image = Image.new("RGB", (96, 96), base)
    draw = ImageDraw.Draw(image)
    for offset in range(0, 96, 12):
        draw.rectangle((offset, 0, offset + 5, 96), fill=accent)
        draw.line((0, offset, 96, offset), fill=(25, 25, 25))
    image.save(path)


def write_manifests(tmp_path: Path, source_count: int = 2) -> tuple[Path, Path]:
    target = tmp_path / "target.png"
    make_image(target, (215, 212, 205), (80, 80, 80))
    target_manifest = tmp_path / "targets.csv"
    with target_manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "id", "name", "source_url", "source_page", "licence_or_terms", "accessed_at",
            "local_path", "review_status", "birth_date", "disappearance_date",
            "disappearance_place", "notes", "crop_x", "crop_y", "crop_width", "crop_height"
        ])
        writer.writerow([
            "person-1", "Person One", "https://example.invalid/target.png",
            "https://example.invalid/target", "fixture", "2026-06-17", "target.png",
            "approved", "", "", "", "", "", "", "", ""
        ])

    places_manifest = tmp_path / "places.csv"
    with places_manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "id", "title", "source_url", "source_page", "licence_or_terms", "accessed_at",
            "local_path", "review_status", "location_label", "notes"
        ])
        for index in range(source_count):
            image_path = tmp_path / f"source-{index}.png"
            make_image(image_path, (120 + index * 30, 150, 130), (200, 190 - index * 20, 160))
            writer.writerow([
                f"source-{index}", f"Source {index}", f"https://example.invalid/source-{index}.png",
                f"https://example.invalid/source-{index}", "fixture", "2026-06-17",
                image_path.name, "approved", "fixture", ""
            ])
    return target_manifest, places_manifest


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_stage1_generation_is_deterministic(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path)
    settings = Stage1Settings(seed=17, fragment_size=24, reuse_limit=2, output_width=96)

    first = run_stage1(targets, places, tmp_path / "out-a", settings)[0]
    second = run_stage1(targets, places, tmp_path / "out-b", settings)[0]

    assert digest(Path(first.still_path)) == digest(Path(second.still_path))
    sidecar = json.loads(Path(first.sidecar_path).read_text(encoding="utf-8"))
    assert sidecar["target_id"] == "person-1"
    assert sidecar["settings"]["seed"] == 17
    assert sidecar["max_fragment_reuse_observed"] <= 2


def test_reuse_limit_is_enforced(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path, source_count=1)
    settings = Stage1Settings(
        seed=17,
        fragment_size=24,
        reuse_limit=1,
        output_width=96,
        max_fragments_per_source=2,
    )

    with pytest.raises(ValueError, match="reuse_limit"):
        run_stage1(targets, places, tmp_path / "out", settings)


def test_reuse_limit_applies_per_fragment_not_per_source(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path, source_count=1)
    settings = Stage1Settings(seed=17, fragment_size=24, reuse_limit=1, output_width=96)

    output = run_stage1(targets, places, tmp_path / "out", settings)[0]

    sidecar = json.loads(Path(output.sidecar_path).read_text(encoding="utf-8"))
    assert sidecar["source_usage"]["source-0"] == 16
    assert sidecar["max_fragment_reuse_observed"] == 1
