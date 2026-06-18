from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image

from desaparecidos.images import extract_fragments
from desaparecidos.manifests import approved_rows


def test_fragment_limit_samples_across_source_image(tmp_path: Path) -> None:
    image = Image.new("RGB", (120, 24), (220, 220, 210))
    for index, x in enumerate(range(0, 120, 24)):
        colour = (50 + index * 35, 80 + index * 20, 100 + index * 15)
        for xx in range(x, x + 24):
            for yy in range(24):
                image.putpixel((xx, yy), colour)
    image.save(tmp_path / "source.png")

    manifest = tmp_path / "places.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "id", "title", "source_url", "source_page", "licence_or_terms", "accessed_at",
            "local_path", "review_status", "location_label", "notes",
            "crawl_run_id", "content_sha256", "perceptual_hash"
        ])
        writer.writerow([
            "source", "Source", "local://source.png", "local://source",
            "fixture", "2026-06-17", "source.png", "approved", "fixture", "", "", "", ""
        ])

    rows = approved_rows(manifest, "places")
    fragments = extract_fragments(
        rows,
        manifest,
        fragment_size=24,
        max_fragments_per_source=2,
    )

    assert [fragment.x for fragment in fragments] == [0, 96]
