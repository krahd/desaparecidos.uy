from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw

from .paths import PROJECT_ROOT, display_path


def _make_image(path: Path, base: tuple[int, int, int], accent: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (240, 240), base)
    draw = ImageDraw.Draw(image)
    for index in range(0, 240, 20):
        draw.rectangle((index, 0, index + 10, 240), fill=accent)
        draw.line((0, index, 240, index), fill=(40, 40, 40), width=1)
    image.save(path)


def create_demo_fixtures(root: str | Path = PROJECT_ROOT) -> dict[str, object]:
    project_root = Path(root)
    demo_root = project_root / "data" / "demo"
    manifest_root = project_root / "data" / "manifests"

    target_path = demo_root / "target-demo.png"
    source_a = demo_root / "place-a.png"
    source_b = demo_root / "place-b.png"
    _make_image(target_path, (210, 210, 205), (80, 80, 78))
    _make_image(source_a, (180, 150, 120), (95, 82, 70))
    _make_image(source_b, (120, 140, 155), (210, 205, 180))

    manifest_root.mkdir(parents=True, exist_ok=True)
    targets_manifest = manifest_root / "demo-targets.csv"
    places_manifest = manifest_root / "demo-places.csv"

    with targets_manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "id",
                "name",
                "source_url",
                "source_page",
                "licence_or_terms",
                "accessed_at",
                "local_path",
                "review_status",
                "birth_date",
                "disappearance_date",
                "disappearance_place",
                "notes",
                "crop_x",
                "crop_y",
                "crop_width",
                "crop_height",
            ]
        )
        writer.writerow(
            [
                "demo-target",
                "Synthetic target",
                "https://example.invalid/target.png",
                "https://example.invalid/target",
                "synthetic local fixture",
                "2026-06-17",
                "../demo/target-demo.png",
                "approved",
                "",
                "",
                "",
                "Generated local fixture",
                "",
                "",
                "",
                "",
            ]
        )

    with places_manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "id",
                "title",
                "source_url",
                "source_page",
                "licence_or_terms",
                "accessed_at",
                "local_path",
                "review_status",
                "location_label",
                "notes",
            ]
        )
        writer.writerow(
            [
                "place-a",
                "Synthetic wall",
                "https://example.invalid/place-a.png",
                "https://example.invalid/place-a",
                "synthetic local fixture",
                "2026-06-17",
                "../demo/place-a.png",
                "approved",
                "demo",
                "Generated local fixture",
            ]
        )
        writer.writerow(
            [
                "place-b",
                "Synthetic pavement",
                "https://example.invalid/place-b.png",
                "https://example.invalid/place-b",
                "synthetic local fixture",
                "2026-06-17",
                "../demo/place-b.png",
                "approved",
                "demo",
                "Generated local fixture",
            ]
        )

    return {
        "ok": True,
        "targets": display_path(targets_manifest),
        "sources": display_path(places_manifest),
        "images": [display_path(target_path), display_path(source_a), display_path(source_b)],
    }
