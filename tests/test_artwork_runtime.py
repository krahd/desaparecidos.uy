from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw
import pytest

import desaparecidos.artwork_runtime as artwork_runtime_module
from desaparecidos.artwork_runtime import (
    ArtworkRenderSettings,
    ArtworkTraversalSettings,
    render_search_artwork,
    run_artwork,
)
from desaparecidos.placement_history import ordered_target_positions
from desaparecidos.refusal_paradata import sha256_file


def _image(path: Path, index: int) -> None:
    image = Image.new("RGB", (96, 96), (40 + index * 7 % 180, 80, 150))
    draw = ImageDraw.Draw(image)
    draw.rectangle((index % 48, 0, min(95, index % 48 + 20), 95), fill=(210, 180, 90))
    draw.line((0, index % 96, 95, (index * 3) % 96), fill=(20, 20, 20), width=3)
    image.save(path)


def _manifests(tmp_path: Path, *, kind: str = "places", count: int = 16) -> tuple[Path, Path]:
    target_image = tmp_path / "target.png"
    target = Image.new("RGB", (96, 96), (220, 215, 205))
    ImageDraw.Draw(target).ellipse((20, 15, 76, 85), outline=(25, 25, 25), width=6)
    target.save(target_image)
    targets = tmp_path / "targets.csv"
    with targets.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "id", "name", "source_url", "source_page", "licence_or_terms", "accessed_at",
            "local_path", "review_status", "birth_date", "disappearance_date",
            "disappearance_place", "notes", "crop_x", "crop_y", "crop_width", "crop_height",
        ])
        writer.writerow([
            "person-1", "Person One", "local://target", "local://target", "fixture", "2026-07-25",
            target_image.name, "approved", "", "", "", "", "", "", "", "",
        ])

    sources = tmp_path / f"{kind}.csv"
    with sources.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        fields = [
            "id", "title", "source_url", "source_page", "licence_or_terms", "accessed_at",
            "local_path", "review_status", "location_label", "notes", "crawl_run_id",
            "content_sha256", "perceptual_hash",
        ]
        if kind == "people":
            fields.extend(["face_x", "face_y", "face_width", "face_height"])
        writer.writerow(fields)
        departments = ["Montevideo", "Rocha", "Artigas", "Tacuarembó"]
        for index in range(count):
            source_image = tmp_path / f"source-{index}.png"
            _image(source_image, index)
            row = [
                f"source-{index}", f"Source {index}", f"local://source-{index}",
                f"local://source-{index}", "fixture", "2026-07-25", source_image.name,
                "approved", departments[index % len(departments)], "", "", "", "",
            ]
            if kind == "people":
                row.extend(["0", "0", "96", "96"])
            writer.writerow(row)
    return targets, sources


def _traversal(tmp_path: Path) -> tuple[Path, str]:
    traversal_root = tmp_path / "traversals"
    traversal_id = "route-fixture"
    route_dir = traversal_root / traversal_id
    route_dir.mkdir(parents=True)
    frames = []
    for index in range(3):
        image_path = route_dir / f"frame-{index}.png"
        _image(image_path, index + 20)
        frames.append({
            "id": f"frame-{index}",
            "local_path": str(image_path),
            "review_status": "approved",
        })
    (route_dir / "route.json").write_text(json.dumps({
        "id": traversal_id,
        "provider": "fixture",
        "attribution": "fixture",
        "geometry": {
            "type": "LineString",
            "coordinates": [[-56.2, -34.9], [-56.1, -34.8]],
        },
        "frames": frames,
    }), encoding="utf-8")
    return traversal_root, traversal_id


def test_portrait_salience_is_explicit_and_deterministic() -> None:
    uniform = ordered_target_positions(240, 320, 24, "uniform")
    portrait = ordered_target_positions(240, 320, 24, "portrait")

    assert uniform[0] == (0, 0)
    assert portrait == ordered_target_positions(240, 320, 24, "portrait")
    assert portrait[0] != (0, 0)
    centres = [((x + 12) / 240, (y + 12) / 320) for x, y in portrait[:10]]
    assert any(0.25 < x < 0.45 and 0.25 < y < 0.52 for x, y in centres)
    assert any(0.55 < x < 0.75 and 0.25 < y < 0.52 for x, y in centres)


def test_place_runtime_persists_overlap_history_and_territorial_account(tmp_path: Path) -> None:
    targets, places = _manifests(tmp_path, kind="places")
    generated = run_artwork(
        targets,
        places,
        tmp_path / "outputs",
        ArtworkRenderSettings(
            seed=17,
            fragment_size=24,
            reuse_limit=2,
            output_width=96,
            max_contribution_per_source=1,
            visual_grammar="overlap",
            target_salience="portrait",
            territorially_balance_sources=True,
        ),
        target_id="person-1",
        artwork="estan-en-todas-partes",
    )[0]
    sidecar = json.loads(Path(generated.sidecar_path).read_text(encoding="utf-8"))

    assert sidecar["sidecar_schema"] == "desaparecidos.uy/output-sidecar/3.0"
    assert sidecar["placement_history"]["schema"] == "desaparecidos.uy/placement-history/1.0"
    assert sidecar["placement_history"]["visual_grammar"] == "overlap"
    assert sidecar["placement_history"]["placement_count"] == 16
    assert sidecar["territorial_source_policy"]["balanced_order"] is True
    assert set(sidecar["territorial_source_policy"]["reviewed_groups_available"]) == {
        "artigas", "montevideo", "rocha", "tacuarembo"
    }
    assert Path(generated.still_path).exists()
    channels = Image.open(generated.still_path).convert("RGB").split()
    assert ImageChops.difference(channels[0], channels[1]).getbbox() is None
    assert ImageChops.difference(channels[1], channels[2]).getbbox() is None
    assert sidecar["settings"]["colour_output"] is False
    assert sidecar["refusal_policy"]["policy_id"] == "memorial-refusals-2026-01"
    assert "generative-facial-completion" in sidecar["refusal_policy"]["applicable_refusal_ids"]
    manifests = {
        item["role"]: item for item in sidecar["runtime_provenance"]["input_manifests"]
    }
    assert manifests["target_manifest"]["sha256"] == sha256_file(targets)
    assert manifests["source_manifest"]["sha256"] == sha256_file(places)
    assert sidecar["runtime_provenance"]["git_commit"]
    assert sidecar["temporal_causality"]["valid"] is True
    assert sidecar["temporal_causality"]["violation_count"] == 0
    target_provenance = sidecar["target_provenance"]["person-1"]
    assert target_provenance["source_page"] == "local://target"
    assert target_provenance["source_image_url"] == "local://target"
    assert target_provenance["licence_or_permission_basis"] == "fixture"
    assert target_provenance["local_target_image_sha256"] == sha256_file(
        tmp_path / "target.png"
    )
    assert target_provenance["metadata_source"]["state"] == "not_recorded_in_input_manifest"
    assert target_provenance["historical_identification_review"]["state"] == "not_recorded"
    assert target_provenance["rights_review"]["state"] == "not_recorded"
    assert target_provenance["output_release"]["decision"] == "review_required"
    assert target_provenance["output_release"]["reviewer"] is None
    assert target_provenance["rights_clearance_is_not_organisational_endorsement"] is True


def test_people_runtime_records_controls_without_claiming_anonymity(tmp_path: Path) -> None:
    targets, people = _manifests(tmp_path, kind="people")
    generated = run_artwork(
        targets,
        people,
        tmp_path / "people-outputs",
        ArtworkRenderSettings(
            fragment_size=24,
            output_width=96,
            max_contribution_per_source=1,
            visual_grammar="irregular",
            avoid_source_adjacency=True,
        ),
        target_id="person-1",
        artwork="todos-somos-familiares",
    )[0]
    sidecar = json.loads(Path(generated.sidecar_path).read_text(encoding="utf-8"))
    controls = sidecar["source_person_risk_controls"]

    assert sidecar["release_status"] == "internal_unreviewed"
    assert controls["identity_matching"] is False
    assert controls["raw_source_reveal"] is False
    assert controls["adjacent_same_source_prevented"] is True
    assert controls["anonymity_guaranteed"] is False
    assert controls["manual_output_review_required"] is True
    assert "full-context-contemporary-person-reveal" in sidecar["refusal_policy"]["applicable_refusal_ids"]


def test_search_runtime_computes_causality_and_rejects_corrupted_history(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    targets, _places = _manifests(tmp_path, kind="places")
    traversal_root, traversal_id = _traversal(tmp_path)

    def fake_render(frames: object, _size: tuple[int, int], output: Path, *, fps: int) -> bool:
        del fps
        list(frames)  # type: ignore[arg-type]
        output.write_bytes(b"mp4")
        return True

    monkeypatch.setattr(artwork_runtime_module, "_render_video_ffmpeg", fake_render)
    settings = ArtworkTraversalSettings(
        duration_seconds=1,
        fps=2,
        fragment_size=24,
        output_width=96,
        max_contribution_per_source=6,
    )
    generated = render_search_artwork(
        traversal_id,
        targets,
        tmp_path / "search-valid",
        ["person-1"],
        settings,
        root=traversal_root,
    )[0]
    sidecar = json.loads(Path(generated.sidecar_path).read_text(encoding="utf-8"))
    assert sidecar["future_source_frames_used"] is False
    assert sidecar["temporal_causality"]["valid"] is True
    assert sidecar["temporal_causality"]["violation_count"] == 0
    assert len(sidecar["temporal_causality"]["evaluated_history_sha256"]) == 64

    original_builder = artwork_runtime_module.build_placement_history

    def corrupt_history(*args: object, **kwargs: object) -> dict[str, object]:
        history = original_builder(*args, **kwargs)  # type: ignore[arg-type]
        source_indexes = {
            source_id: index for index, source_id in enumerate(history["source_sequence"])
        }
        placement = next(
            item
            for item in history["placements"]
            if source_indexes[item["source_id"]] > 0
        )
        placement["time"]["encounter_index"] = 0
        return history

    monkeypatch.setattr(artwork_runtime_module, "build_placement_history", corrupt_history)
    invalid_output = tmp_path / "search-invalid"
    with pytest.raises(ValueError, match="temporal causality evaluation failed"):
        render_search_artwork(
            traversal_id,
            targets,
            invalid_output,
            ["person-1"],
            settings,
            root=traversal_root,
        )
    assert not invalid_output.exists()
