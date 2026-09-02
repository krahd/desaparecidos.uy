from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.publish_static_memorial as publication_module
from desaparecidos.evaluation import evaluate_sidecar, require_temporal_causality
from desaparecidos.manifests import ManifestRow
from desaparecidos.refusal_paradata import output_sidecar_provenance, sha256_file
from desaparecidos.target_provenance import (
    require_publication_ready_target_provenance,
    target_provenance_snapshots,
)


def _history() -> dict[str, object]:
    return {
        "schema": "desaparecidos.uy/placement-history/1.0",
        "target_id": "target",
        "canvas": {"width": 24, "height": 24},
        "visual_grammar": "grid",
        "seed": 17,
        "source_sequence": ["frame-a", "frame-b"],
        "placement_count": 1,
        "timeline_unit": "normalised-output-process",
        "placements": [{
            "placement_id": "target:000000",
            "source_id": "frame-b",
            "fragment_id": "frame-b:0:0",
            "source_rect": {"x": 0, "y": 0, "width": 24, "height": 24},
            "matched_target_rect": {"x": 0, "y": 0, "width": 24, "height": 24},
            "render_geometry": {
                "x": 0,
                "y": 0,
                "width": 24,
                "height": 24,
                "rotation_degrees": 0,
                "opacity": 1,
                "z_index": 0,
            },
            "time": {
                "encounter_index": 1,
                "enter_normalised": 0,
                "settle_normalised": 1,
                "exit_normalised": None,
            },
        }],
    }


def test_publication_target_gate_requires_distinct_history_and_rights_reviews(
    tmp_path: Path,
) -> None:
    target_manifest = tmp_path / "targets.csv"
    target_manifest.write_text("id\ntarget\n", encoding="utf-8")
    target_image = tmp_path / "target.jpg"
    target_image.write_bytes(b"fixture-target")
    target = ManifestRow("targets", 2, {
        "id": "target",
        "name": "Target Person",
        "source_url": "https://example.invalid/target.jpg",
        "source_page": "https://example.invalid/target",
        "licence_or_terms": "fixture permission",
        "accessed_at": "2026-09-01",
        "local_path": target_image.name,
        "review_status": "approved",
    })
    sidecar = {
        "target_id": "target",
        "target_provenance": target_provenance_snapshots(
            [target], target_manifest, output_release_decision="review_required"
        ),
    }
    with pytest.raises(ValueError, match="canonical metadata sources"):
        require_publication_ready_target_provenance(sidecar)

    snapshot = sidecar["target_provenance"]["target"]
    snapshot["metadata_source"].update({
        "state": "recorded",
        "source_ids": ["fixture-source"],
    })
    snapshot["historical_identification_review"] = {
        "state": "approved",
        "reviewer": "Fixture Historian",
        "reviewed_at": "2026-09-01",
    }
    with pytest.raises(ValueError, match="approved rights review"):
        require_publication_ready_target_provenance(sidecar)

    snapshot["rights_review"] = {
        "state": "approved",
        "reviewer": "Fixture Rights Reviewer",
        "reviewed_at": "2026-09-01",
    }
    snapshot["licence_or_permission_basis"] = "verify before public release"
    with pytest.raises(ValueError, match="unresolved licence"):
        require_publication_ready_target_provenance(sidecar)

    snapshot["licence_or_permission_basis"] = "fixture permission"
    require_publication_ready_target_provenance(sidecar)


def test_sequence_target_provenance_requires_explicit_target_ids(tmp_path: Path) -> None:
    target_manifest = tmp_path / "targets.csv"
    target_manifest.write_text("id\ntarget\n", encoding="utf-8")
    target_image = tmp_path / "target.jpg"
    target_image.write_bytes(b"fixture-target")
    target = ManifestRow("targets", 2, {
        "id": "target",
        "local_path": target_image.name,
        "review_status": "approved",
    })
    sidecar = {
        "target_id": "sequence",
        "target_provenance": target_provenance_snapshots(
            [target], target_manifest, output_release_decision="internal_unreviewed"
        ),
    }
    with pytest.raises(ValueError, match="has no target_ids"):
        require_publication_ready_target_provenance(sidecar)


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def _valid_publication_bundle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    sidecar_artwork: str = "seguimos-buscando",
    published_work: str = "seguimos-buscando",
) -> dict[str, object]:
    monkeypatch.setattr(publication_module, "safe_project_path", lambda value: Path(value))
    tmp_path.mkdir(parents=True, exist_ok=True)
    target_manifest = tmp_path / "targets.csv"
    source_manifest = tmp_path / "sources.json"
    target_manifest.write_text("id\ntarget\n", encoding="utf-8")
    source_manifest.write_text("{}\n", encoding="utf-8")
    target_image = tmp_path / "target.jpg"
    target_image.write_bytes(b"fixture-target")
    target = ManifestRow("targets", 2, {
        "id": "target",
        "name": "Target Person",
        "source_url": "https://example.invalid/target.jpg",
        "source_page": "https://example.invalid/target",
        "licence_or_terms": "fixture permission",
        "accessed_at": "2026-09-01",
        "local_path": target_image.name,
        "review_status": "approved",
    })
    manifest_role = (
        "traversal_manifest" if sidecar_artwork == "seguimos-buscando" else "source_manifest"
    )
    history = _history()
    causality = require_temporal_causality({"target": history})
    sidecar: dict[str, object] = {
        **output_sidecar_provenance(
            sidecar_artwork,  # type: ignore[arg-type]
            {"target_manifest": target_manifest, manifest_role: source_manifest},
        ),
        "artwork": sidecar_artwork,
        "target_id": "target",
        "temporal_causality": causality,
        "target_provenance": target_provenance_snapshots(
            [target], target_manifest, output_release_decision="review_required"
        ),
    }
    if sidecar_artwork == "seguimos-buscando":
        sidecar["placement_histories"] = {"target": history}
        sidecar["future_source_frames_used"] = False
    else:
        sidecar["placement_history"] = history
    sidecar["runtime_provenance"]["working_tree_dirty"] = False  # type: ignore[index]
    snapshot = sidecar["target_provenance"]["target"]  # type: ignore[index]
    snapshot["metadata_source"].update({  # type: ignore[index]
        "state": "recorded",
        "source_ids": ["fixture-source"],
    })
    snapshot["historical_identification_review"] = {  # type: ignore[index]
        "state": "approved",
        "reviewer": "Fixture Historian",
        "reviewed_at": "2026-09-01",
    }
    snapshot["rights_review"] = {  # type: ignore[index]
        "state": "approved",
        "reviewer": "Fixture Rights Reviewer",
        "reviewed_at": "2026-09-01",
    }

    sidecar_path = tmp_path / "segment.json"
    _write_json(sidecar_path, sidecar)
    evaluation_path = tmp_path / "segment.evaluation.json"
    _write_json(evaluation_path, evaluate_sidecar(sidecar_path))
    segment_video = tmp_path / "segment.mp4"
    segment_video.write_bytes(b"fixture-segment-video")
    loop_video = tmp_path / "loop.mp4"
    loop_video.write_bytes(b"fixture-loop-video")
    exhibition: dict[str, object] = {
        "schema": "desaparecidos.uy/exhibition-triptych/3.0",
        "videos": {
            published_work: {"path": str(loop_video), "sha256": sha256_file(loop_video)}
        },
        "segments": {
            published_work: [{
                "target_id": "target",
                "video": str(segment_video),
                "video_sha256": sha256_file(segment_video),
                "sidecar": str(sidecar_path),
                "sidecar_sha256": sha256_file(sidecar_path),
                "evaluation": str(evaluation_path),
                "evaluation_sha256": sha256_file(evaluation_path),
            }]
        },
    }
    exhibition_path = tmp_path / "exhibition.json"
    _write_json(exhibition_path, exhibition)
    publication: dict[str, object] = {
        "schema": "desaparecidos.uy/web-publication/2.0",
        "works": {
            work: {
                "publish": work == published_work,
                "release_decision": (
                    "approved-for-publication" if work == published_work
                    else "not-approved-for-publication"
                ),
                "reviewer": "Fixture Reviewer" if work == published_work else "",
                "decided_at": "2026-09-01" if work == published_work else "",
                "rights_clearance_is_not_organisational_endorsement": True,
            }
            for work in publication_module.WORKS
        },
    }
    publication_path = tmp_path / "publication.json"
    _write_json(publication_path, publication)
    return {
        "sidecar_path": sidecar_path,
        "evaluation_path": evaluation_path,
        "segment_video": segment_video,
        "exhibition": exhibition,
        "exhibition_path": exhibition_path,
        "publication": publication,
        "publication_path": publication_path,
        "destination": tmp_path / "published",
        "published_work": published_work,
    }


def test_publication_verifies_complete_segment_binding_and_removes_stale_media(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    bundle = _valid_publication_bundle(monkeypatch, tmp_path)
    destination = bundle["destination"]
    stale = destination / "media" / "todos-somos-familiares.mp4"  # type: ignore[operator]
    stale.parent.mkdir(parents=True)
    stale.write_bytes(b"stale-private-media")

    audit_path = publication_module.publish(
        bundle["exhibition_path"],  # type: ignore[arg-type]
        bundle["publication_path"],  # type: ignore[arg-type]
        destination,  # type: ignore[arg-type]
        acknowledge_review=True,
    )

    assert audit_path.exists()
    assert not stale.exists()
    assert (destination / "media" / "seguimos-buscando.mp4").exists()  # type: ignore[operator]
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    segment = audit["works"]["seguimos-buscando"]["segments"][0]
    assert segment["video_sha256"] == sha256_file(bundle["segment_video"])  # type: ignore[arg-type]


def test_publication_rejects_wrong_artwork_and_target_bindings(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    wrong_artwork = _valid_publication_bundle(
        monkeypatch,
        tmp_path / "wrong-artwork",
        sidecar_artwork="estan-en-todas-partes",
        published_work="seguimos-buscando",
    )
    with pytest.raises(ValueError, match="sidecar artwork mismatch"):
        publication_module.publish(
            wrong_artwork["exhibition_path"],  # type: ignore[arg-type]
            wrong_artwork["publication_path"],  # type: ignore[arg-type]
            wrong_artwork["destination"],  # type: ignore[arg-type]
            acknowledge_review=True,
        )

    wrong_target_root = tmp_path / "wrong-target"
    wrong_target_root.mkdir()
    wrong_target = _valid_publication_bundle(monkeypatch, wrong_target_root)
    exhibition = wrong_target["exhibition"]
    exhibition["segments"]["seguimos-buscando"][0]["target_id"] = "other"  # type: ignore[index]
    _write_json(wrong_target["exhibition_path"], exhibition)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="sidecar target mismatch"):
        publication_module.publish(
            wrong_target["exhibition_path"],  # type: ignore[arg-type]
            wrong_target["publication_path"],  # type: ignore[arg-type]
            wrong_target["destination"],  # type: ignore[arg-type]
            acknowledge_review=True,
        )


def test_publication_rejects_stale_evaluation_and_segment_video(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    stale_evaluation = _valid_publication_bundle(monkeypatch, tmp_path / "evaluation")
    evaluation_path = stale_evaluation["evaluation_path"]
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))  # type: ignore[union-attr]
    evaluation["targets"]["target"]["participation"]["source_count"] = 99
    _write_json(evaluation_path, evaluation)  # type: ignore[arg-type]
    exhibition = stale_evaluation["exhibition"]
    exhibition["segments"]["seguimos-buscando"][0]["evaluation_sha256"] = sha256_file(  # type: ignore[index]
        evaluation_path  # type: ignore[arg-type]
    )
    _write_json(stale_evaluation["exhibition_path"], exhibition)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="target metrics do not match"):
        publication_module.publish(
            stale_evaluation["exhibition_path"],  # type: ignore[arg-type]
            stale_evaluation["publication_path"],  # type: ignore[arg-type]
            stale_evaluation["destination"],  # type: ignore[arg-type]
            acknowledge_review=True,
        )

    video_root = tmp_path / "video"
    video_root.mkdir()
    stale_video = _valid_publication_bundle(monkeypatch, video_root)
    stale_video["segment_video"].write_bytes(b"changed-segment-video")  # type: ignore[union-attr]
    with pytest.raises(ValueError, match="segment video digest mismatch"):
        publication_module.publish(
            stale_video["exhibition_path"],  # type: ignore[arg-type]
            stale_video["publication_path"],  # type: ignore[arg-type]
            stale_video["destination"],  # type: ignore[arg-type]
            acknowledge_review=True,
        )


def test_publication_rejects_placeholder_or_invalid_release_metadata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    bundle = _valid_publication_bundle(monkeypatch, tmp_path)
    publication = bundle["publication"]
    work = publication["works"]["seguimos-buscando"]  # type: ignore[index]
    work["reviewer"] = "replace-with-reviewer-name"
    _write_json(bundle["publication_path"], publication)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="reviewer.*placeholder"):
        publication_module.publish(
            bundle["exhibition_path"],  # type: ignore[arg-type]
            bundle["publication_path"],  # type: ignore[arg-type]
            bundle["destination"],  # type: ignore[arg-type]
            acknowledge_review=True,
        )

    work["reviewer"] = "Fixture Reviewer"
    work["decided_at"] = "not-a-date"
    _write_json(bundle["publication_path"], publication)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="ISO-8601"):
        publication_module.publish(
            bundle["exhibition_path"],  # type: ignore[arg-type]
            bundle["publication_path"],  # type: ignore[arg-type]
            bundle["destination"],  # type: ignore[arg-type]
            acknowledge_review=True,
        )


def test_publication_blocks_intentionally_corrupted_future_history(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(publication_module, "safe_project_path", lambda value: Path(value))
    target_manifest = tmp_path / "targets.csv"
    traversal_manifest = tmp_path / "route.json"
    target_manifest.write_text("id\ntarget\n", encoding="utf-8")
    traversal_manifest.write_text("{}\n", encoding="utf-8")
    target_image = tmp_path / "target.jpg"
    target_image.write_bytes(b"fixture-target")
    target = ManifestRow("targets", 2, {
        "id": "target",
        "name": "Target Person",
        "source_url": "https://example.invalid/target.jpg",
        "source_page": "https://example.invalid/target",
        "licence_or_terms": "fixture permission",
        "accessed_at": "2026-09-01",
        "local_path": target_image.name,
        "review_status": "approved",
    })
    history = _history()
    histories = {"target": history}
    causality = require_temporal_causality(histories)
    sidecar = {
        **output_sidecar_provenance(
            "seguimos-buscando",
            {
                "target_manifest": target_manifest,
                "traversal_manifest": traversal_manifest,
            },
        ),
        "artwork": "seguimos-buscando",
        "target_id": "target",
        "placement_histories": histories,
        "temporal_causality": causality,
        "future_source_frames_used": causality["future_source_frames_used"],
        "target_provenance": target_provenance_snapshots(
            [target],
            target_manifest,
            output_release_decision="internal_unreviewed",
        ),
    }
    sidecar["runtime_provenance"]["working_tree_dirty"] = False
    target_snapshot = sidecar["target_provenance"]["target"]
    target_snapshot["metadata_source"].update({
        "state": "recorded",
        "source_ids": ["fixture-source"],
    })
    target_snapshot["historical_identification_review"] = {
        "state": "approved",
        "reviewer": "Fixture Historian",
        "reviewed_at": "2026-09-01",
    }
    target_snapshot["rights_review"] = {
        "state": "approved",
        "reviewer": "Fixture Rights Reviewer",
        "reviewed_at": "2026-09-01",
    }

    # Corrupt the persisted history after its render-time evaluation. Updating
    # the manifest digest proves that publication blocks on causality, not only
    # on file-integrity mismatch.
    history["placements"][0]["time"]["encounter_index"] = 0  # type: ignore[index]
    sidecar_path = tmp_path / "search.json"
    sidecar_path.write_text(json.dumps(sidecar), encoding="utf-8")
    evaluation_path = tmp_path / "search.evaluation.json"
    evaluation_path.write_text(json.dumps({
        "evaluation_schema": "desaparecidos.uy/artwork-evaluation/2.0",
        "temporal_causality": {**causality, "recorded_evaluation_matches": True},
    }), encoding="utf-8")
    video_path = tmp_path / "seguimos-buscando.mp4"
    video_path.write_bytes(b"fixture-video")

    exhibition_path = tmp_path / "exhibition.json"
    exhibition_path.write_text(json.dumps({
        "schema": "desaparecidos.uy/exhibition-triptych/3.0",
        "videos": {
            "seguimos-buscando": {
                "path": str(video_path),
                "sha256": sha256_file(video_path),
            }
        },
        "segments": {
            "seguimos-buscando": [{
                "target_id": "target",
                "video": str(video_path),
                "video_sha256": sha256_file(video_path),
                "sidecar": str(sidecar_path),
                "sidecar_sha256": sha256_file(sidecar_path),
                "evaluation": str(evaluation_path),
                "evaluation_sha256": sha256_file(evaluation_path),
            }]
        },
    }), encoding="utf-8")
    publication_path = tmp_path / "publication.json"
    publication_path.write_text(json.dumps({
        "schema": "desaparecidos.uy/web-publication/2.0",
        "works": {
            "todos-somos-familiares": {"publish": False},
            "estan-en-todas-partes": {"publish": False},
            "seguimos-buscando": {
                "publish": True,
                "release_decision": "approved-for-publication",
                "reviewer": "Fixture Reviewer",
                "decided_at": "2026-09-01",
                "rights_clearance_is_not_organisational_endorsement": True,
            },
        },
    }), encoding="utf-8")
    destination = tmp_path / "published"

    with pytest.raises(ValueError, match="temporal causality evaluation failed"):
        publication_module.publish(
            exhibition_path,
            publication_path,
            destination,
            acknowledge_review=True,
        )
    assert not destination.exists()
