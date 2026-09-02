from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.publish_static_memorial as publication_module
from desaparecidos.evaluation import require_temporal_causality
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
    require_publication_ready_target_provenance(sidecar)


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
