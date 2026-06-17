from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw

from .paths import PROJECT_ROOT, display_path


def _make_target_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (360, 360), (216, 213, 204))
    draw = ImageDraw.Draw(image)
    for y in range(0, 360, 18):
        shade = 205 + (y // 18) % 3 * 5
        draw.line((0, y, 360, y), fill=(shade, shade - 2, shade - 8), width=1)
    draw.polygon([(82, 360), (118, 252), (242, 252), (282, 360)], fill=(64, 65, 61))
    draw.ellipse((100, 52, 260, 242), fill=(186, 166, 139), outline=(70, 68, 63), width=4)
    draw.pieslice((88, 32, 272, 196), 180, 360, fill=(44, 45, 42))
    draw.rectangle((104, 90, 256, 136), fill=(48, 48, 45))
    draw.ellipse((132, 138, 151, 150), fill=(42, 41, 39))
    draw.ellipse((209, 138, 228, 150), fill=(42, 41, 39))
    draw.line((180, 148, 171, 190, 188, 190), fill=(92, 82, 72), width=3)
    draw.arc((146, 184, 214, 224), 15, 165, fill=(83, 56, 53), width=3)
    draw.rectangle((0, 286, 360, 360), fill=(111, 106, 93))
    draw.rectangle((128, 246, 232, 360), fill=(170, 151, 126))
    draw.polygon([(118, 252), (180, 314), (242, 252), (274, 360), (86, 360)], fill=(58, 60, 56))
    for x in range(24, 360, 48):
        draw.line((x, 0, x + 28, 360), fill=(196, 192, 181), width=1)
    image.save(path)


def _make_surface_image(path: Path, palette: list[tuple[int, int, int]], line: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (360, 360), palette[0])
    draw = ImageDraw.Draw(image)
    tile = 24
    for y in range(0, 360, tile):
        for x in range(0, 360, tile):
            base = palette[((x // tile) * 3 + (y // tile) * 5) % len(palette)]
            delta = ((x * 7 + y * 11) % 19) - 9
            colour = tuple(max(0, min(255, channel + delta)) for channel in base)
            draw.rectangle((x, y, x + tile, y + tile), fill=colour)
            if (x + y) % 72 == 0:
                draw.line((x, y + tile - 3, x + tile, y + 4), fill=line, width=2)
            if (x // tile + y // tile) % 5 == 0:
                draw.rectangle((x + 4, y + 5, x + 17, y + 14), outline=line, width=1)
    for offset in range(0, 360, 36):
        draw.line((0, offset, 360, offset + 28), fill=line, width=1)
        draw.line((offset, 0, offset + 18, 360), fill=line, width=1)
    image.save(path)


def create_demo_fixtures(root: str | Path = PROJECT_ROOT) -> dict[str, object]:
    project_root = Path(root)
    demo_root = project_root / "data" / "demo"
    manifest_root = project_root / "data" / "manifests"

    target_path = demo_root / "target-demo.png"
    source_a = demo_root / "place-a.png"
    source_b = demo_root / "place-b.png"
    source_c = demo_root / "place-c.png"
    source_d = demo_root / "place-d.png"
    _make_target_image(target_path)
    _make_surface_image(
        source_a,
        [(205, 195, 176), (174, 154, 128), (118, 104, 91), (67, 66, 61), (220, 217, 205)],
        (62, 58, 53),
    )
    _make_surface_image(
        source_b,
        [(132, 144, 147), (97, 106, 103), (188, 184, 169), (45, 48, 47), (172, 141, 105)],
        (38, 42, 41),
    )
    _make_surface_image(
        source_c,
        [(178, 78, 62), (221, 212, 190), (79, 54, 49), (151, 123, 96), (200, 168, 132)],
        (81, 46, 40),
    )
    _make_surface_image(
        source_d,
        [(56, 83, 91), (105, 132, 126), (190, 185, 166), (41, 48, 51), (156, 161, 142)],
        (34, 45, 49),
    )

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
                "Synthetic portrait fixture",
                "local://demo/target-demo.png",
                "local://demo/synthetic-portrait",
                "synthetic local fixture, generated for offline testing",
                "2026-06-17",
                "../demo/target-demo.png",
                "approved",
                "",
                "",
                "",
                "Generated local synthetic portrait fixture.",
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
                "Synthetic warm wall",
                "local://demo/place-a.png",
                "local://demo/synthetic-warm-wall",
                "synthetic local fixture, generated for offline testing",
                "2026-06-17",
                "../demo/place-a.png",
                "approved",
                "demo",
                "Generated local synthetic place fixture.",
            ]
        )
        writer.writerow(
            [
                "place-b",
                "Synthetic pavement",
                "local://demo/place-b.png",
                "local://demo/synthetic-pavement",
                "synthetic local fixture, generated for offline testing",
                "2026-06-17",
                "../demo/place-b.png",
                "approved",
                "demo",
                "Generated local synthetic place fixture.",
            ]
        )
        writer.writerow(
            [
                "place-c",
                "Synthetic painted surface",
                "local://demo/place-c.png",
                "local://demo/synthetic-painted-surface",
                "synthetic local fixture, generated for offline testing",
                "2026-06-17",
                "../demo/place-c.png",
                "approved",
                "demo",
                "Generated local synthetic place fixture.",
            ]
        )
        writer.writerow(
            [
                "place-d",
                "Synthetic river wall",
                "local://demo/place-d.png",
                "local://demo/synthetic-river-wall",
                "synthetic local fixture, generated for offline testing",
                "2026-06-17",
                "../demo/place-d.png",
                "approved",
                "demo",
                "Generated local synthetic place fixture.",
            ]
        )

    return {
        "ok": True,
        "targets": display_path(targets_manifest),
        "sources": display_path(places_manifest),
        "images": [
            display_path(target_path),
            display_path(source_a),
            display_path(source_b),
            display_path(source_c),
            display_path(source_d),
        ],
    }
