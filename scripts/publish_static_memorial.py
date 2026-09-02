from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from desaparecidos.evaluation import require_sidecar_temporal_causality
from desaparecidos.paths import display_path, safe_project_path
from desaparecidos.refusal_paradata import validate_output_sidecar_provenance
from desaparecidos.target_provenance import require_publication_ready_target_provenance

WORKS = (
    "todos-somos-familiares",
    "estan-en-todas-partes",
    "seguimos-buscando",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _verified_segments(exhibition: dict[str, Any], work: str) -> list[dict[str, Any]]:
    segments_by_work = exhibition.get("segments")
    if not isinstance(segments_by_work, dict):
        raise ValueError("exhibition manifest has no segment records")
    segments = segments_by_work.get(work)
    if not isinstance(segments, list) or not segments:
        raise ValueError(f"exhibition manifest has no segment records for {work}")
    verified: list[dict[str, Any]] = []
    for index, record in enumerate(segments):
        if not isinstance(record, dict):
            raise ValueError(f"segment {index} for {work} must be an object")
        sidecar_path = safe_project_path(str(record.get("sidecar", "")))
        evaluation_path = safe_project_path(str(record.get("evaluation", "")))
        for label, path, digest_field in (
            ("sidecar", sidecar_path, "sidecar_sha256"),
            ("evaluation", evaluation_path, "evaluation_sha256"),
        ):
            if not path.exists() or not path.is_file():
                raise ValueError(f"{label} is missing for {work} segment {index}: {path}")
            expected = str(record.get(digest_field, ""))
            if not expected or _sha256(path) != expected:
                raise ValueError(f"{label} digest mismatch for {work} segment {index}")
        sidecar = require_publication_ready_target_provenance(
            validate_output_sidecar_provenance(
                _load(sidecar_path),
                require_clean_runtime=True,
            )
        )
        causality = require_sidecar_temporal_causality(sidecar)
        evaluation = _load(evaluation_path)
        recorded_causality = evaluation.get("temporal_causality")
        if evaluation.get("evaluation_schema") != "desaparecidos.uy/artwork-evaluation/2.0":
            raise ValueError(f"unsupported evaluation schema for {work} segment {index}")
        if not isinstance(recorded_causality, dict) or any(
            recorded_causality.get(field) != causality.get(field)
            for field in (
                "evaluator_schema",
                "evaluated_history_sha256",
                "history_count",
                "placement_count",
                "violation_count",
                "future_source_frames_used",
                "valid",
            )
        ):
            raise ValueError(f"evaluation does not match the sidecar for {work} segment {index}")
        if recorded_causality.get("recorded_evaluation_matches") is not True:
            raise ValueError(f"evaluation did not verify sidecar causality for {work} segment {index}")
        verified.append({
            "target_id": str(record.get("target_id", "")),
            "sidecar": display_path(sidecar_path),
            "sidecar_sha256": _sha256(sidecar_path),
            "evaluation": display_path(evaluation_path),
            "evaluation_sha256": _sha256(evaluation_path),
            "evaluated_history_sha256": causality["evaluated_history_sha256"],
            "causality_violation_count": causality["violation_count"],
        })
    return verified


def publish(
    exhibition_manifest: Path,
    publication_config: Path,
    destination: Path,
    *,
    acknowledge_review: bool,
) -> Path:
    if not acknowledge_review:
        raise ValueError(
            "publishing requires --acknowledge-review to confirm that rights, source, "
            "recognisability, historical metadata, and full-duration video review are complete"
        )
    exhibition = _load(exhibition_manifest)
    publication = _load(publication_config)
    if exhibition.get("schema") != "desaparecidos.uy/exhibition-triptych/3.0":
        raise ValueError("unsupported or stale exhibition manifest schema")
    if publication.get("schema") != "desaparecidos.uy/web-publication/2.0":
        raise ValueError("unsupported publication configuration schema")
    exhibition_videos = exhibition.get("videos", {})
    publication_works = publication.get("works", {})
    if not isinstance(exhibition_videos, dict) or not isinstance(publication_works, dict):
        raise ValueError("manifest video and publication work records must be objects")

    prepared: dict[str, dict[str, Any]] = {}
    for work in WORKS:
        requested = publication_works.get(work, {})
        if not isinstance(requested, dict):
            raise ValueError(f"publication record for {work} must be an object")
        publish_work = requested.get("publish") is True
        prepared_record: dict[str, Any] = {
            "publish": publish_work,
            "requested": requested,
        }
        if publish_work:
            if requested.get("release_decision") != "approved-for-publication":
                raise ValueError(f"publication release decision is missing for {work}")
            reviewer = str(requested.get("reviewer", "")).strip()
            decided_at = str(requested.get("decided_at", "")).strip()
            if not reviewer or not decided_at:
                raise ValueError(f"publication reviewer and decision date are required for {work}")
            if requested.get("rights_clearance_is_not_organisational_endorsement") is not True:
                raise ValueError(f"the non-endorsement acknowledgement is required for {work}")
            source_record = exhibition_videos.get(work)
            if not isinstance(source_record, dict):
                raise ValueError(f"exhibition manifest has no video record for {work}")
            source = safe_project_path(str(source_record.get("path", "")))
            if not source.exists() or not source.is_file():
                raise ValueError(f"reviewed video is missing for {work}: {source}")
            expected = str(source_record.get("sha256", ""))
            actual = _sha256(source)
            if not expected or actual != expected:
                raise ValueError(f"video digest mismatch for {work}")
            prepared_record.update({
                "source": display_path(source),
                "sha256": actual,
                "segments": _verified_segments(exhibition, work),
            })
        prepared[work] = prepared_record

    source_web = safe_project_path("web")
    destination.mkdir(parents=True, exist_ok=True)
    media = destination / "media"
    media.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "method.html", "style.css", "app.js"):
        shutil.copy2(source_web / name, destination / name)

    emitted: dict[str, Any] = {
        "schema": "desaparecidos.uy/web-publication/2.0",
        "note": str(publication.get("note", "")),
        "works": {},
    }
    audit: dict[str, Any] = {
        "schema": "desaparecidos.uy/web-publication-audit/2.0",
        "exhibition_manifest": display_path(exhibition_manifest),
        "publication_config": display_path(publication_config),
        "works": {},
    }
    for work in WORKS:
        record = prepared[work]
        requested = record["requested"]
        publish_work = record["publish"]
        emitted["works"][work] = {
            "publish": publish_work,
            "path": f"./media/{work}.mp4",
            "poster": str(requested.get("poster", "")),
            "controls": bool(requested.get("controls", False)),
            "release_decision": requested.get("release_decision"),
            "reviewer": requested.get("reviewer"),
            "decided_at": requested.get("decided_at"),
            "rights_clearance_is_not_organisational_endorsement": requested.get(
                "rights_clearance_is_not_organisational_endorsement"
            ),
        }
        audit_record: dict[str, Any] = {"publish": publish_work}
        if publish_work:
            source = safe_project_path(record["source"])
            target = media / f"{work}.mp4"
            shutil.copy2(source, target)
            audit_record.update({
                "source": display_path(source),
                "published": display_path(target),
                "sha256": record["sha256"],
                "bytes": target.stat().st_size,
                "segments": record["segments"],
                "release_decision": requested["release_decision"],
                "reviewer": requested["reviewer"],
                "decided_at": requested["decided_at"],
                "rights_clearance_is_not_organisational_endorsement": True,
            })
        audit["works"][work] = audit_record

    (destination / "publication.json").write_text(
        json.dumps(emitted, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    audit_path = destination / "publication-audit.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    return audit_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish a reviewed, static desaparecidos.uy memorial site."
    )
    parser.add_argument("exhibition_manifest", type=Path)
    parser.add_argument("publication_config", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--acknowledge-review", action="store_true")
    args = parser.parse_args()
    audit = publish(
        safe_project_path(args.exhibition_manifest),
        safe_project_path(args.publication_config),
        safe_project_path(args.destination),
        acknowledge_review=args.acknowledge_review,
    )
    print(display_path(audit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
