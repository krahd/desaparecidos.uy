from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
DEMO_ROOT = ROOT / "data" / "demo"
MANIFEST_ROOT = ROOT / "data" / "manifests"


def make_image(path: Path, base: tuple[int, int, int], accent: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (240, 240), base)
    draw = ImageDraw.Draw(image)
    for index in range(0, 240, 20):
        draw.rectangle((index, 0, index + 10, 240), fill=accent)
        draw.line((0, index, 240, index), fill=(40, 40, 40), width=1)
    image.save(path)


def main() -> None:
    target_path = DEMO_ROOT / "target-demo.png"
    source_a = DEMO_ROOT / "place-a.png"
    source_b = DEMO_ROOT / "place-b.png"
    make_image(target_path, (210, 210, 205), (80, 80, 78))
    make_image(source_a, (180, 150, 120), (95, 82, 70))
    make_image(source_b, (120, 140, 155), (210, 205, 180))

    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    with (MANIFEST_ROOT / "demo-targets.csv").open("w", newline="", encoding="utf-8") as handle:
      writer = csv.writer(handle)
      writer.writerow([
          "id", "name", "source_url", "source_page", "licence_or_terms", "accessed_at",
          "local_path", "review_status", "birth_date", "disappearance_date",
          "disappearance_place", "notes", "crop_x", "crop_y", "crop_width", "crop_height"
      ])
      writer.writerow([
          "demo-target", "Synthetic target", "https://example.invalid/target.png",
          "https://example.invalid/target", "synthetic local fixture", "2026-06-17",
          "../demo/target-demo.png", "approved", "", "", "", "Generated local fixture", "", "", "", ""
      ])

    with (MANIFEST_ROOT / "demo-places.csv").open("w", newline="", encoding="utf-8") as handle:
      writer = csv.writer(handle)
      writer.writerow([
          "id", "title", "source_url", "source_page", "licence_or_terms", "accessed_at",
          "local_path", "review_status", "location_label", "notes"
      ])
      writer.writerow([
          "place-a", "Synthetic wall", "https://example.invalid/place-a.png",
          "https://example.invalid/place-a", "synthetic local fixture", "2026-06-17",
          "../demo/place-a.png", "approved", "demo", "Generated local fixture"
      ])
      writer.writerow([
          "place-b", "Synthetic pavement", "https://example.invalid/place-b.png",
          "https://example.invalid/place-b", "synthetic local fixture", "2026-06-17",
          "../demo/place-b.png", "approved", "demo", "Generated local fixture"
      ])

    print("Created synthetic demo fixtures under data/demo and data/manifests/demo-*.csv")


if __name__ == "__main__":
    main()
