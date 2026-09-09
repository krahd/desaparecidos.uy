"""Repeatable CV quality pass for crawled source manifests."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from PIL import Image

from .cv import CV_POLICY_VERSION, classify_image, hamming_distance, perceptual_hash
from .manifests import EXPECTED_FIELDS, ManifestKind, read_manifest, row_file_path


@dataclass(frozen=True)
class SourceQualitySummary:
    manifest: str
    kind: ManifestKind
    checked: int
    approved: int
    rejected: int
    unchanged: int
    reasons: dict[str, int]
    cv_policy_version: int = CV_POLICY_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "manifest": self.manifest,
            "kind": self.kind,
            "checked": self.checked,
            "approved": self.approved,
            "rejected": self.rejected,
            "unchanged": self.unchanged,
            "reasons": self.reasons,
            "cv_policy_version": self.cv_policy_version,
        }


def quality_pass_source_manifest(
    manifest: str | Path,
    kind: ManifestKind,
    *,
    statuses: set[str] | None = None,
) -> SourceQualitySummary:
    """Reclassify selected rows and persist approval only after category gating.

    People require a landmark-bearing YuNet face when configured, or a frontal
    face plus an independent eye detection otherwise. Place rows must pass the
    conservative photographic-scene gate. The pass never performs identity
    recognition and does not delete cached source files.
    """
    if kind not in {"people", "places"}:
        raise ValueError("source quality pass supports only people and places")
    selected_statuses = statuses or {"pending"}
    manifest_path = Path(manifest)
    validation = read_manifest(manifest_path, kind)
    if validation.errors:
        raise ValueError("; ".join(validation.errors))

    with manifest_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or EXPECTED_FIELDS[kind])
        rows = list(reader)

    checked = approved = rejected = unchanged = 0
    reasons: Counter[str] = Counter()
    parsed_by_id = {row.id: row for row in validation.rows}
    for values in rows:
        row_id = (values.get("id") or "").strip()
        status = (values.get("review_status") or "").strip().lower()
        if status not in selected_statuses or row_id not in parsed_by_id:
            unchanged += 1
            continue
        checked += 1
        row = parsed_by_id[row_id]
        try:
            with Image.open(row_file_path(row, manifest_path)) as opened:
                result = classify_image(opened.convert("RGB"), kind)
        except Exception:
            result = None
        if result is None:
            values["review_status"] = "rejected"
            rejected += 1
            reasons["unreadable"] += 1
            continue
        reasons[result.label] += 1
        if not result.accept:
            values["review_status"] = "rejected"
            rejected += 1
            continue
        values["review_status"] = "approved"
        approved += 1
        if kind == "people" and result.face_box is not None:
            for field, value in zip(
                ("face_x", "face_y", "face_width", "face_height"),
                result.face_box,
            ):
                values[field] = str(value)

    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(
            {field: row.get(field, "") for field in fieldnames}
            for row in rows
        )

    return SourceQualitySummary(
        manifest=str(manifest_path),
        kind=kind,
        checked=checked,
        approved=approved,
        rejected=rejected,
        unchanged=unchanged,
        reasons=dict(sorted(reasons.items())),
    )


def import_traversal_places(
    traversal_root: str | Path,
    manifest: str | Path,
    *,
    route_ids: list[str] | None = None,
) -> dict[str, object]:
    """Import unique acquired Uruguay traversal frames as approved place rows."""
    root = Path(traversal_root)
    manifest_path = Path(manifest)
    validation = read_manifest(manifest_path, "places")
    if validation.errors:
        raise ValueError("; ".join(validation.errors))
    seen_sha = {
        row.values.get("content_sha256", "")
        for row in validation.rows
        if row.values.get("content_sha256")
    }
    seen_phashes = [
        row.values.get("perceptual_hash", "")
        for row in validation.rows
        if row.values.get("perceptual_hash")
    ]
    seen_paths: set[Path] = set()
    additions: list[dict[str, str]] = []
    reasons: Counter[str] = Counter()
    checked = 0

    route_paths = (
        [root / route_id / "route.json" for route_id in route_ids]
        if route_ids
        else sorted(root.glob("*/route.json"))
    )
    for route_path in route_paths:
        if not route_path.exists():
            raise ValueError(f"traversal metadata does not exist: {route_path}")
        route = json.loads(route_path.read_text(encoding="utf-8"))
        route_id = str(route.get("id") or route_path.parent.name)
        provider = str(route.get("provider") or "mapillary")
        attribution = str(route.get("attribution") or "provider attribution required")
        for frame in route.get("frames", []):
            local_value = str(frame.get("local_path") or "")
            if not local_value or frame.get("review_status") != "approved":
                continue
            image_path = Path(local_value).resolve()
            if image_path in seen_paths or not image_path.exists():
                continue
            seen_paths.add(image_path)
            checked += 1
            try:
                payload = image_path.read_bytes()
                sha = hashlib.sha256(payload).hexdigest()
                with Image.open(image_path) as opened:
                    image = opened.convert("RGB")
                    result = classify_image(image, "places")
                    phash = perceptual_hash(image)
            except Exception:
                reasons["unreadable"] += 1
                continue
            if not result.accept:
                reasons[result.label] += 1
                continue
            if sha in seen_sha:
                reasons["duplicate-content"] += 1
                continue
            if any(
                hamming_distance(phash, existing) <= 4
                for existing in seen_phashes
            ):
                reasons["duplicate-visual"] += 1
                continue
            seen_sha.add(sha)
            seen_phashes.append(phash)
            provider_id = str(frame.get("provider_id") or "")
            source_url = (
                f"https://www.mapillary.com/app/?pKey={provider_id}"
                if provider == "mapillary" and provider_id
                else f"local://traversal/{route_id}/{frame.get('id', '')}"
            )
            location = str(frame.get("place_name") or "Uruguay")
            additions.append({
                "id": f"traversal-{sha[:16]}",
                "title": f"{location} traversal frame {frame.get('ordinal', checked)}",
                "source_url": source_url,
                "source_page": source_url,
                "licence_or_terms": attribution,
                "accessed_at": date.today().isoformat(),
                "local_path": os.path.relpath(image_path, manifest_path.resolve().parent),
                "review_status": "approved",
                "location_label": location,
                "notes": (
                    f"Imported from approved {provider} traversal {route_id}; "
                    f"CV policy {CV_POLICY_VERSION} place gate passed."
                ),
                "crawl_run_id": route_id,
                "content_sha256": sha,
                "perceptual_hash": phash,
            })
            reasons["approved-place"] += 1

    if additions:
        with manifest_path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=EXPECTED_FIELDS["places"],
                extrasaction="ignore",
                lineterminator="\n",
            )
            writer.writerows(additions)
    return {
        "manifest": str(manifest_path),
        "checked": checked,
        "added": len(additions),
        "rejected": checked - len(additions),
        "reasons": dict(sorted(reasons.items())),
        "cv_policy_version": CV_POLICY_VERSION,
        "route_ids": route_ids or "all",
    }
