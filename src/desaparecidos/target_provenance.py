from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Sequence

from .manifests import ManifestRow, row_file_path
from .paths import PROJECT_ROOT, display_path
from .refusal_paradata import sha256_file

DEFAULT_PERSON_STORE = PROJECT_ROOT / "data" / "persons" / "disappeared.json"
DEFAULT_TARGET_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "targets.csv"
NO_ENDORSEMENT_STATEMENT = (
    "Rights clearance permits a stated use; it does not imply endorsement by any source, "
    "archive, memorial organisation, relatives' organisation, rights holder, or depicted person."
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_UNRESOLVED_PERMISSION = re.compile(
    r"(?:\bunknown\b|\bnot recorded\b|\bpending review\b|\btbd\b|"
    r"\bverify (?:before|per)\b|replace-with)",
    re.IGNORECASE,
)


def _text(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def _review_record(
    values: dict[str, Any],
    prefix: str,
) -> dict[str, str | None]:
    status = _text(values.get(f"{prefix}_status"))
    return {
        "state": status or "not_recorded",
        "reviewer": _text(values.get(f"{prefix}_reviewer")),
        "reviewed_at": _text(values.get(f"{prefix}_reviewed_at")),
    }


def _canonical_person(target_id: str, target_manifest: str | Path) -> dict[str, Any] | None:
    try:
        if Path(target_manifest).resolve() != DEFAULT_TARGET_MANIFEST.resolve():
            return None
    except OSError:
        return None
    if not DEFAULT_PERSON_STORE.exists():
        return None
    value = json.loads(DEFAULT_PERSON_STORE.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError(f"{DEFAULT_PERSON_STORE} must contain a JSON array")
    return next(
        (
            record
            for record in value
            if isinstance(record, dict) and str(record.get("id", "")) == target_id
        ),
        None,
    )


def target_provenance_snapshot(
    target: ManifestRow,
    target_manifest: str | Path,
    *,
    output_release_decision: str,
) -> dict[str, Any]:
    """Snapshot target facts without turning image approval into rights or identity clearance."""
    image_path = row_file_path(target, target_manifest)
    if not image_path.exists() or not image_path.is_file():
        raise ValueError(f"target image is missing: {image_path}")
    canonical = _canonical_person(target.id, target_manifest)
    values: dict[str, Any] = dict(target.values)
    if canonical:
        for field in (
            "historical_identification_review_status",
            "historical_identification_review_reviewer",
            "historical_identification_review_reviewed_at",
            "rights_review_status",
            "rights_review_reviewer",
            "rights_review_reviewed_at",
        ):
            if canonical.get(field) not in {None, ""}:
                values[field] = canonical[field]

    field_sources = dict(canonical.get("field_sources") or {}) if canonical else {}
    field_source_refs = dict(canonical.get("field_source_refs") or {}) if canonical else {}
    source_ids = sorted({str(value) for value in field_sources.values() if value})
    metadata_source = {
        "state": "recorded" if canonical else "not_recorded_in_input_manifest",
        "canonical_person_store": display_path(DEFAULT_PERSON_STORE) if canonical else None,
        "canonical_person_store_sha256": sha256_file(DEFAULT_PERSON_STORE) if canonical else None,
        "person_source_page": _text(canonical.get("source_page")) if canonical else None,
        "source_ids": source_ids,
        "field_sources": field_sources,
        "field_source_refs": field_source_refs,
        "canonical_record_review_status": _text(canonical.get("review_status")) if canonical else None,
    }
    return {
        "target_id": target.id,
        "target_name": target.values.get("name", target.id),
        "target_manifest": display_path(target_manifest),
        "target_manifest_review_status": target.review_status or "not_recorded",
        "source_page": _text(target.values.get("source_page")),
        "source_image_url": _text(target.values.get("source_url")),
        "licence_or_permission_basis": _text(target.values.get("licence_or_terms")),
        "accessed_at": _text(target.values.get("accessed_at")),
        "local_target_image": display_path(image_path),
        "local_target_image_sha256": sha256_file(image_path),
        "metadata_source": metadata_source,
        "historical_identification_review": _review_record(
            values, "historical_identification_review"
        ),
        "rights_review": _review_record(values, "rights_review"),
        "output_release": {
            "decision": output_release_decision,
            "reviewer": None,
            "decided_at": None,
        },
        "rights_clearance_is_not_organisational_endorsement": True,
        "non_endorsement_statement": NO_ENDORSEMENT_STATEMENT,
    }


def target_provenance_snapshots(
    targets: Sequence[ManifestRow],
    target_manifest: str | Path,
    *,
    output_release_decision: str,
) -> dict[str, dict[str, Any]]:
    return {
        target.id: target_provenance_snapshot(
            target,
            target_manifest,
            output_release_decision=output_release_decision,
        )
        for target in targets
    }


def validate_sidecar_target_provenance(sidecar: Any) -> dict[str, Any]:
    if not isinstance(sidecar, dict):
        raise ValueError("output sidecar must be an object")
    snapshots = sidecar.get("target_provenance")
    if not isinstance(snapshots, dict) or not snapshots:
        raise ValueError("output sidecar has no target provenance")
    target_ids = sidecar.get("target_ids")
    if isinstance(target_ids, list) and target_ids:
        if len({str(target_id) for target_id in target_ids}) != len(target_ids):
            raise ValueError("output sidecar target_ids must not contain duplicates")
        expected = {str(target_id) for target_id in target_ids}
    else:
        target_id = str(sidecar.get("target_id", ""))
        if target_id == "sequence":
            raise ValueError("sequence output sidecar has no target_ids")
        expected = {target_id} if target_id else set()
    if not expected:
        raise ValueError("output sidecar has no target ids")
    if expected and set(snapshots) != expected:
        raise ValueError("output sidecar target provenance does not match its target ids")
    for target_id, snapshot in snapshots.items():
        if not isinstance(snapshot, dict):
            raise ValueError(f"target provenance for {target_id} must be an object")
        if snapshot.get("target_id") != target_id:
            raise ValueError(f"target provenance id mismatch for {target_id}")
        for field in (
            "target_manifest",
            "target_manifest_review_status",
            "local_target_image",
        ):
            if not _text(snapshot.get(field)):
                raise ValueError(f"target provenance for {target_id} has no {field}")
        digest = snapshot.get("local_target_image_sha256")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise ValueError(f"target provenance for {target_id} has no valid image SHA-256")
        if not isinstance(snapshot.get("metadata_source"), dict):
            raise ValueError(f"target provenance for {target_id} has no metadata source record")
        for field in (
            "historical_identification_review",
            "rights_review",
            "output_release",
        ):
            record = snapshot.get(field)
            if not isinstance(record, dict) or not _text(record.get("state") or record.get("decision")):
                raise ValueError(f"target provenance for {target_id} has no {field} record")
        if snapshot.get("rights_clearance_is_not_organisational_endorsement") is not True:
            raise ValueError(f"target provenance for {target_id} lacks the non-endorsement flag")
        if snapshot.get("non_endorsement_statement") != NO_ENDORSEMENT_STATEMENT:
            raise ValueError(f"target provenance for {target_id} has a stale non-endorsement statement")
    return sidecar


def require_publication_ready_target_provenance(sidecar: Any) -> dict[str, Any]:
    """Require explicit target history and rights decisions at the publication boundary."""
    validated = validate_sidecar_target_provenance(sidecar)
    for target_id, snapshot in validated["target_provenance"].items():
        if snapshot.get("target_manifest_review_status") != "approved":
            raise ValueError(f"target {target_id} is not approved for generation")
        for field in (
            "source_page",
            "source_image_url",
            "licence_or_permission_basis",
            "accessed_at",
        ):
            if not _text(snapshot.get(field)):
                raise ValueError(f"target {target_id} has no recorded {field}")
        permission_basis = str(snapshot["licence_or_permission_basis"])
        if _UNRESOLVED_PERMISSION.search(permission_basis):
            raise ValueError(f"target {target_id} has an unresolved licence or permission basis")
        metadata = snapshot["metadata_source"]
        if metadata.get("state") != "recorded" or not metadata.get("source_ids"):
            raise ValueError(f"target {target_id} has no recorded canonical metadata sources")
        for field, label in (
            ("historical_identification_review", "historical-identification"),
            ("rights_review", "rights"),
        ):
            review = snapshot[field]
            if review.get("state") != "approved":
                raise ValueError(f"target {target_id} has no approved {label} review")
            if not _text(review.get("reviewer")) or not _text(review.get("reviewed_at")):
                raise ValueError(f"target {target_id} {label} review lacks reviewer or date")
    return validated
