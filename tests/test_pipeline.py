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
from desaparecidos.pipeline import (
    DEFAULT_MAX_CONTRIBUTION_PER_SOURCE,
    Stage1Settings,
    TilePlacement,
    assemble_target_with_trace,
    run_stage1,
)
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


def test_stage1_settings_default_contribution_cap_is_one() -> None:
    assert DEFAULT_MAX_CONTRIBUTION_PER_SOURCE == 1
    assert Stage1Settings().max_contribution_per_source == 1
    assert Stage1Settings().video_source_layout == "grid"


def test_stage1_generation_is_deterministic(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path)
    settings = Stage1Settings(
        seed=17,
        fragment_size=24,
        reuse_limit=2,
        output_width=96,
        max_contribution_per_source=0,
    )

    first = run_stage1(targets, places, tmp_path / "out-a", settings)[0]
    second = run_stage1(targets, places, tmp_path / "out-b", settings)[0]

    assert digest(Path(first.still_path)) == digest(Path(second.still_path))
    sidecar = json.loads(Path(first.sidecar_path).read_text(encoding="utf-8"))
    assert sidecar["target_id"] == "person-1"
    assert sidecar["settings"]["seed"] == 17
    assert sidecar["settings"]["video_source_layout"] == "grid"
    assert sidecar["max_fragment_reuse_observed"] <= 2
    assert sidecar["tile_count"] == 16
    assert sidecar["source_sequence"]
    assert sidecar["search_trail"]["urls"]


def test_people_artwork_uses_people_manifest_and_records_provenance(tmp_path: Path) -> None:
    targets, _places = write_manifests(tmp_path, source_count=1)
    people = tmp_path / "people.csv"
    with people.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "id", "title", "source_url", "source_page", "licence_or_terms", "accessed_at",
            "local_path", "review_status", "location_label", "notes", "crawl_run_id",
            "content_sha256", "perceptual_hash", "face_x", "face_y", "face_width", "face_height",
        ])
        writer.writerow([
            "face-1", "Face", "https://example.invalid/face.png", "https://example.invalid/page",
            "fixture", "2026-06-20", "source-0.png", "approved", "", "", "", "", "",
            "0", "0", "96", "96",
        ])

    output = run_stage1(
        targets,
        people,
        tmp_path / "people-out",
        Stage1Settings(
            seed=17,
            fragment_size=24,
            reuse_limit=2,
            output_width=96,
            max_contribution_per_source=16,
        ),
        artwork="todos-somos-familiares",
    )[0]
    sidecar = json.loads(Path(output.sidecar_path).read_text(encoding="utf-8"))

    assert sidecar["artwork"] == "todos-somos-familiares"
    assert sidecar["source_kind"] == "people"
    assert sidecar["source_manifest"].endswith("people.csv")


def test_people_artwork_rejects_unlimited_source_contribution(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path, source_count=1)

    with pytest.raises(ValueError, match="requires a positive"):
        run_stage1(
            targets,
            places,
            tmp_path / "out",
            Stage1Settings(max_contribution_per_source=0),
            artwork="todos-somos-familiares",
        )


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
    settings = Stage1Settings(
        seed=17,
        fragment_size=24,
        reuse_limit=1,
        output_width=96,
        max_contribution_per_source=0,
    )

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
        Stage1Settings(
            seed=17,
            fragment_size=24,
            reuse_limit=1,
            output_width=96,
            max_contribution_per_source=0,
        ),
    )

    assert assembly.image.size == (96, 96)
    assert assembly.target_canvas.size == (96, 96)
    assert len(assembly.placements) == 16
    assert assembly.placements[0].source_id == "source-0"
    assert assembly.placements[0].dest_x == 0
    assert assembly.placements[0].dest_y == 0


def test_source_layout_fades_to_true_source_positions_and_transfers_fragments() -> None:
    source = Image.new("RGB", (96, 48), (180, 30, 30))
    ImageDraw.Draw(source).rectangle((48, 0, 95, 47), fill=(20, 40, 220))
    fragment = source.crop((48, 0, 72, 24))
    placement = TilePlacement("source", "source:48:0", fragment, 0, 0, 48, 0)

    full_source, selected, starts = pipeline_module._source_fragment_field(
        [placement], source, (96, 96)
    )
    grid, grid_starts = pipeline_module._contributing_fragment_field(
        [placement], (96, 96), seed=17
    )
    matched, matched_starts = pipeline_module._matched_fragment_field([placement], (96, 96))

    assert full_source.getpixel((12, 36)) == (180, 30, 30)
    assert full_source.getpixel((60, 36)) == (20, 40, 220)
    assert selected.getpixel((12, 36)) == pipeline_module.INK
    assert selected.getpixel((60, 36)) == (20, 40, 220)
    assert starts == [(48, 24, 24)]
    assert grid_starts != starts
    assert matched_starts != starts
    assert matched_starts != grid_starts
    assert grid.getpixel(grid_starts[0][:2]) == (20, 40, 220)
    assert matched.getpixel(matched_starts[0][:2]) == (20, 40, 220)

    transferred = pipeline_module._fragment_transfer_frame(
        [placement], starts, [(0, 0, 24)], 1.0,
        Image.new("RGB", (96, 96), pipeline_module.INK),
    )
    assert transferred.getpixel((12, 12)) == (20, 40, 220)
    assert transferred.getpixel((60, 36)) == pipeline_module.INK


def test_process_video_frames_start_with_full_source_then_change(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path, source_count=1)
    target_row = approved_rows(targets, "targets", require_files=True)[0]
    source_rows = approved_rows(places, "places", require_files=True)
    fragments = extract_fragments(source_rows, places, fragment_size=24)
    assembly = assemble_target_with_trace(
        target_row,
        targets,
        fragments,
        Stage1Settings(
            seed=17,
            fragment_size=24,
            reuse_limit=1,
            output_width=96,
            max_contribution_per_source=0,
        ),
    )

    frames = list(itertools.islice(
        pipeline_module._process_video_frames(
            target_row,
            assembly,
            source_rows,
            places,
            seed=17,
            fps=4,
            source_layout="match",
        ),
        12,
    ))

    assert frames
    assert all(frame.size == assembly.image.size for frame in frames)
    source_region = Image.open(tmp_path / "source-0.png").convert("RGB")
    expected, _selected, _starts = pipeline_module._source_fragment_field(
        pipeline_module._sample_placements(
            assembly.placements,
            pipeline_module.MAX_ANIMATED_FRAGMENTS_PER_SOURCE,
        ),
        source_region,
        assembly.image.size,
    )
    assert frames[0].tobytes() == expected.tobytes()
    assert any(frame.tobytes() != frames[0].tobytes() for frame in frames[1:])


def test_people_video_reveals_only_reviewed_face_region(tmp_path: Path) -> None:
    targets, _places = write_manifests(tmp_path, source_count=1)
    person_image = Image.new("RGB", (96, 96), (220, 20, 20))
    ImageDraw.Draw(person_image).rectangle((48, 0, 95, 95), fill=(20, 40, 220))
    person_image.save(tmp_path / "person-source.png")
    people = tmp_path / "people.csv"
    with people.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "id", "title", "source_url", "source_page", "licence_or_terms", "accessed_at",
            "local_path", "review_status", "location_label", "notes", "crawl_run_id",
            "content_sha256", "perceptual_hash", "face_x", "face_y", "face_width", "face_height",
        ])
        writer.writerow([
            "person-source", "Person", "local://person-source.png", "local://person-source",
            "fixture", "2026-06-21", "person-source.png", "approved", "", "", "", "", "",
            "48", "0", "48", "96",
        ])
    target_row = approved_rows(targets, "targets", require_files=True)[0]
    source_rows = approved_rows(people, "people", require_files=True)
    fragments = extract_fragments(source_rows, people, fragment_size=24, source_kind="people")
    assembly = assemble_target_with_trace(
        target_row,
        targets,
        fragments,
        Stage1Settings(
            fragment_size=24,
            reuse_limit=2,
            output_width=96,
            max_contribution_per_source=16,
            video_source_layout="match",
        ),
    )

    first = next(pipeline_module._process_video_frames(
        target_row,
        assembly,
        source_rows,
        people,
        seed=17,
        fps=4,
        source_layout="match",
    ))

    assert first.getpixel((48, 48)) == (20, 40, 220)
    assert first.getpixel((12, 48)) == pipeline_module.INK


def test_process_video_frames_do_not_show_non_contributing_candidates(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path, source_count=1)
    candidate_path = tmp_path / "candidate.png"
    make_image(candidate_path, (40, 80, 130), (210, 180, 130))
    target_row = approved_rows(targets, "targets", require_files=True)[0]
    source_rows = approved_rows(places, "places", require_files=True)
    fragments = extract_fragments(source_rows, places, fragment_size=24)
    assembly = assemble_target_with_trace(
        target_row,
        targets,
        fragments,
        Stage1Settings(
            seed=17,
            fragment_size=24,
            reuse_limit=1,
            output_width=96,
            max_contribution_per_source=0,
        ),
    )
    displayed: list[dict[str, object]] = []
    candidates = [
        pipeline_module.SearchCandidate(
            run_id="run-1",
            row_id="rejected-1",
            source_id=None,
            page_url="https://example.invalid/page",
            image_url="https://example.invalid/rejected.png",
            decision="cv-rejected",
            path=str(candidate_path),
            cv_label="noise",
        )
    ]

    frames = list(itertools.islice(
        pipeline_module._process_video_frames(
            target_row,
            assembly,
            source_rows,
            places,
            seed=17,
            fps=4,
            search_candidates=candidates,
            search_scan_frames_per_candidate=2,
            search_candidate_display=displayed,
        ),
        4,
    ))

    assert len(frames) == 4
    assert displayed == []
    assert frames[0].tobytes() == frames[1].tobytes()
    assert frames[3].tobytes() != frames[0].tobytes()


def test_search_candidate_sidecar_records_crawl_events_and_cap(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    targets, places = write_manifests(tmp_path, source_count=2)
    candidate_a = tmp_path / "candidate-a.png"
    candidate_b = tmp_path / "candidate-b.png"
    make_image(candidate_a, (30, 70, 120), (180, 160, 120))
    make_image(candidate_b, (130, 70, 50), (200, 190, 160))

    monkeypatch.setattr(
        pipeline_module,
        "image_events_for_runs",
        lambda _root, run_ids: [
            {
                "run_id": run_ids[0],
                "ordinal": 1,
                "page_url": "https://example.invalid/page-a",
                "image_url": "https://example.invalid/a.png",
                "decision": "cv-rejected",
                "row_id": "reject-a",
                "path": str(candidate_a),
                "cv_label": "noise",
            },
            {
                "run_id": run_ids[0],
                "ordinal": 2,
                "page_url": "https://example.invalid/page-b",
                "image_url": "https://example.invalid/source-0.png",
                "decision": "accepted",
                "row_id": "source-0",
                "path": str(candidate_b),
                "cv_label": "place-photo",
            },
        ],
    )

    output = run_stage1(
        targets,
        places,
        tmp_path / "out",
        Stage1Settings(
            seed=17,
            fragment_size=24,
            reuse_limit=4,
            output_width=96,
            max_contribution_per_source=0,
            search_scan_max_candidates=1,
        ),
    )[0]

    sidecar = json.loads(Path(output.sidecar_path).read_text(encoding="utf-8"))
    assert sidecar["search_candidates"]["source"] == "crawl-events"
    assert sidecar["search_candidates"]["available_count"] == 2
    assert sidecar["search_candidates"]["local_count"] == 2
    assert sidecar["search_candidates"]["selected_count"] == 1
    assert sidecar["search_candidates"]["omitted_count"] == 1


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
        Stage1Settings(
            seed=17,
            fragment_size=24,
            reuse_limit=1,
            output_width=96,
            max_contribution_per_source=0,
        ),
    )

    frames = list(pipeline_module._process_video_frames(
        target_row, assembly, source_rows, places, seed=17, fps=4,
    ))

    assert np.asarray(frames[-1]).max() <= 8  # ends on black
    # at least one fully black frame appears mid-sequence (the fades)
    assert any(np.asarray(frame).max() <= 8 for frame in frames[:-1])
    # a text card (mostly black with bright glyphs) appears after the last source settle
    assert any(2 < float(np.asarray(frame).mean()) < 60 for frame in frames)
