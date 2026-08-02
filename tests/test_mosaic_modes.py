from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw
import pytest

from desaparecidos.pipeline import Stage1Settings, run_stage1


def _make_image(
    path: Path,
    base: tuple[int, int, int],
    accent: tuple[int, int, int],
) -> None:
    image = Image.new("RGB", (144, 144), base)
    draw = ImageDraw.Draw(image)
    for offset in range(0, 144, 12):
        draw.rectangle((offset, 0, offset + 5, 143), fill=accent)
        draw.line((0, offset, 143, offset), fill=(20, 20, 20))
    image.save(path)


def _write_manifests(tmp_path: Path) -> tuple[Path, Path]:
    target = tmp_path / "target.png"
    _make_image(target, (215, 212, 205), (70, 70, 70))
    targets = tmp_path / "targets.csv"
    with targets.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "id", "name", "source_url", "source_page", "licence_or_terms",
            "accessed_at", "local_path", "review_status", "birth_date",
            "disappearance_date", "disappearance_place", "notes", "crop_x",
            "crop_y", "crop_width", "crop_height",
        ])
        writer.writerow([
            "target", "Target", "local://target", "local://target", "fixture",
            "2026-08-02", target.name, "approved", "", "", "", "", "", "", "", "",
        ])

    places = tmp_path / "places.csv"
    with places.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "id", "title", "source_url", "source_page", "licence_or_terms",
            "accessed_at", "local_path", "review_status", "location_label",
            "notes", "crawl_run_id", "content_sha256", "perceptual_hash",
        ])
        for index in range(4):
            source = tmp_path / f"source-{index}.png"
            _make_image(
                source,
                (90 + index * 30, 120 + index * 10, 150),
                (220, 190 - index * 20, 120 + index * 15),
            )
            writer.writerow([
                f"source-{index}", f"Source {index}", f"local://source-{index}",
                f"local://source-{index}", "fixture", "2026-08-02",
                source.name, "approved", "Montevideo", "", "fixture", "", "",
            ])
    return targets, places


def test_unique_spatial_grid_and_free_modes(tmp_path: Path) -> None:
    targets, places = _write_manifests(tmp_path)
    images: dict[str, bytes] = {}
    for mode in ("grid", "free"):
        output = run_stage1(
            targets,
            places,
            tmp_path / mode,
            Stage1Settings(
                seed=17,
                fragment_size=36,
                reuse_limit=8,
                output_width=144,
                max_contribution_per_source=0,
                composition_mode=mode,
                unique_tiles=True,
                matching_mode="spatial",
            ),
        )[0]
        sidecar = json.loads(Path(output.sidecar_path).read_text(encoding="utf-8"))
        assert sidecar["settings"]["composition_mode"] == mode
        assert sidecar["settings"]["matching_mode"] == "spatial"
        assert sidecar["settings"]["unique_tiles"] is True
        assert sidecar["max_fragment_reuse_observed"] == 1
        assert len(sidecar["fragment_usage"]) == sidecar["tile_count"]
        images[mode] = Path(output.still_path).read_bytes()

    assert images["grid"] != images["free"]


def test_unique_mode_reports_insufficient_candidate_pool(tmp_path: Path) -> None:
    targets, places = _write_manifests(tmp_path)
    with pytest.raises(ValueError, match="approve or crawl more source images"):
        run_stage1(
            targets,
            places,
            tmp_path / "too-small",
            Stage1Settings(
                fragment_size=24,
                output_width=240,
                max_fragments_per_source=1,
                max_contribution_per_source=0,
                unique_tiles=True,
                matching_mode="spatial",
            ),
        )
