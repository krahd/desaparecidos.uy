from __future__ import annotations

import csv
import hashlib
import itertools
import json
from pathlib import Path

from PIL import Image, ImageDraw
import pytest

from desaparecidos.images import extract_fragments
from desaparecidos.manifests import approved_rows
from desaparecidos.pipeline import Stage1Settings, assemble_target_with_trace, run_stage1
from desaparecidos import pipeline as pipeline_module


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
            "local_path", "review_status", "location_label", "notes",
            "crawl_run_id", "content_sha256", "perceptual_hash"
        ])
        for index in range(source_count):
            image_path = tmp_path / f"source-{index}.png"
            make_image(image_path, (120 + index * 30, 150, 130), (200, 190 - index * 20, 160))
            writer.writerow([
                f"source-{index}", f"Source {index}", f"https://example.invalid/source-{index}.png",
                f"https://example.invalid/source-{index}", "fixture", "2026-06-17",
                image_path.name, "approved", "fixture", "", "fixture-run", "", ""
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
    assert sidecar["tile_count"] == 16
    assert sidecar["source_sequence"]
    assert sidecar["search_trail"]["urls"]


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


def test_contribution_cap_limits_tiles_per_source(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path, source_count=16)
    target_row = approved_rows(targets, "targets", require_files=True)[0]
    source_rows = approved_rows(places, "places", require_files=True)
    fragments = extract_fragments(source_rows, places, fragment_size=24)

    assembly = assemble_target_with_trace(
        target_row,
        targets,
        fragments,
        Stage1Settings(
            seed=17, fragment_size=24, reuse_limit=8, output_width=96,
            max_contribution_per_source=1,
        ),
    )

    assert len(assembly.placements) == 16
    assert max(assembly.source_usage.values()) == 1


def test_contribution_cap_infeasible_raises(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path, source_count=2)
    settings = Stage1Settings(
        seed=17, fragment_size=24, reuse_limit=8, output_width=96,
        max_contribution_per_source=1,
    )

    with pytest.raises(ValueError, match="max_contribution_per_source"):
        run_stage1(targets, places, tmp_path / "out", settings)


def test_assembly_trace_records_fragment_destinations(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path, source_count=1)
    target_row = approved_rows(targets, "targets", require_files=True)[0]
    source_rows = approved_rows(places, "places", require_files=True)
    fragments = extract_fragments(source_rows, places, fragment_size=24)

    assembly = assemble_target_with_trace(
        target_row,
        targets,
        fragments,
        Stage1Settings(seed=17, fragment_size=24, reuse_limit=1, output_width=96),
    )

    assert assembly.image.size == (96, 96)
    assert assembly.target_canvas.size == (96, 96)
    assert len(assembly.placements) == 16
    assert assembly.placements[0].source_id == "source-0"
    assert assembly.placements[0].dest_x == 0
    assert assembly.placements[0].dest_y == 0


def test_process_video_frames_start_with_full_source_and_end_with_result(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path, source_count=1)
    target_row = approved_rows(targets, "targets", require_files=True)[0]
    source_rows = approved_rows(places, "places", require_files=True)
    fragments = extract_fragments(source_rows, places, fragment_size=24)
    assembly = assemble_target_with_trace(
        target_row,
        targets,
        fragments,
        Stage1Settings(seed=17, fragment_size=24, reuse_limit=1, output_width=96),
    )

    frames = list(itertools.islice(
        pipeline_module._process_video_frames(
            target_row,
            assembly,
            source_rows,
            places,
            seed=17,
            fps=4,
            search_trail=["https://example.invalid/search"],
        ),
        12,
    ))

    assert frames
    assert all(frame.size == assembly.image.size for frame in frames)
    assert frames[0].tobytes() != assembly.image.tobytes()
    assert any(frame.tobytes() != frames[0].tobytes() for frame in frames[1:])


def test_url_ticker_draws_bottom_url() -> None:
    frame = Image.new("RGB", (240, 120), (240, 240, 240))
    rendered = pipeline_module._with_url_ticker(
        frame,
        ["https://example.invalid/search/page"],
        frame_index=0,
        fps=4,
    )

    assert rendered.getpixel((8, 110)) != (240, 240, 240)


def test_process_video_outro_fades_through_text_and_ends_black(tmp_path: Path) -> None:
    import numpy as np

    targets, places = write_manifests(tmp_path, source_count=1)
    target_row = approved_rows(targets, "targets", require_files=True)[0]
    source_rows = approved_rows(places, "places", require_files=True)
    fragments = extract_fragments(source_rows, places, fragment_size=24)
    assembly = assemble_target_with_trace(
        target_row,
        targets,
        fragments,
        Stage1Settings(seed=17, fragment_size=24, reuse_limit=1, output_width=96),
    )

    frames = list(pipeline_module._process_video_frames(
        target_row, assembly, source_rows, places, seed=17, fps=4,
    ))

    assert np.asarray(frames[-1]).max() <= 8  # ends on black
    # at least one fully black frame appears mid-sequence (the fades)
    assert any(np.asarray(frame).max() <= 8 for frame in frames[:-1])
    # a text card (mostly black with bright glyphs) appears after the last source settle
    assert any(2 < float(np.asarray(frame).mean()) < 60 for frame in frames)
