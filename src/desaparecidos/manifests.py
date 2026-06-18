from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from .paths import display_path

ManifestKind = Literal["targets", "places"]

TARGET_FIELDS = [
    "id",
    "name",
    "source_url",
    "source_page",
    "licence_or_terms",
    "accessed_at",
    "local_path",
    "review_status",
    "birth_date",
    "disappearance_date",
    "disappearance_place",
    "notes",
    "crop_x",
    "crop_y",
    "crop_width",
    "crop_height",
]

PLACE_FIELDS = [
    "id",
    "title",
    "source_url",
    "source_page",
    "licence_or_terms",
    "accessed_at",
    "local_path",
    "review_status",
    "location_label",
    "notes",
]

REQUIRED_VALUES = {
    "targets": [
        "id",
        "name",
        "source_url",
        "source_page",
        "licence_or_terms",
        "accessed_at",
        "local_path",
        "review_status",
    ],
    "places": [
        "id",
        "title",
        "source_url",
        "source_page",
        "licence_or_terms",
        "accessed_at",
        "local_path",
        "review_status",
    ],
}

EXPECTED_FIELDS = {"targets": TARGET_FIELDS, "places": PLACE_FIELDS}
APPROVED = "approved"


@dataclass(frozen=True)
class ManifestRow:
    kind: ManifestKind
    line_number: int
    values: dict[str, str]

    @property
    def id(self) -> str:
        return self.values.get("id", "")

    @property
    def label(self) -> str:
        return self.values.get("name") or self.values.get("title") or self.id

    @property
    def local_path(self) -> str:
        return self.values.get("local_path", "")

    @property
    def review_status(self) -> str:
        return self.values.get("review_status", "").strip().lower()

    @property
    def approved(self) -> bool:
        return self.review_status == APPROVED

    def to_api(self, manifest_path: str | Path | None = None) -> dict[str, Any]:
        file_path: str | None = None
        if manifest_path is not None and self.local_path:
            try:
                file_path = display_path(row_file_path(self, manifest_path))
            except Exception:
                file_path = None
        return {
            "kind": self.kind,
            "line_number": self.line_number,
            "id": self.id,
            "label": self.label,
            "approved": self.approved,
            "file_path": file_path,
            "values": self.values,
        }


@dataclass
class ManifestValidation:
    path: str
    kind: ManifestKind
    rows: list[ManifestRow] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def approved_count(self) -> int:
        return sum(1 for row in self.rows if row.approved)

    def to_api(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "kind": self.kind,
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "row_count": len(self.rows),
            "approved_count": self.approved_count,
            "rows": [row.to_api(self.path) for row in self.rows],
        }


def read_manifest(path: str | Path, kind: ManifestKind) -> ManifestValidation:
    manifest_path = Path(path)
    result = ManifestValidation(path=str(manifest_path), kind=kind)
    expected_fields = EXPECTED_FIELDS[kind]

    if not manifest_path.exists():
        result.errors.append(f"{manifest_path} does not exist")
        return result

    with manifest_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            result.errors.append(f"{manifest_path} has no header row")
            return result

        missing = [field for field in expected_fields if field not in reader.fieldnames]
        if missing:
            result.errors.append(
                f"{manifest_path} is missing required columns: {', '.join(missing)}"
            )

        unexpected = [field for field in reader.fieldnames if field not in expected_fields]
        if unexpected:
            result.warnings.append(
                f"{manifest_path} has unrecognised columns: {', '.join(unexpected)}"
            )

        for line_number, raw in enumerate(reader, start=2):
            values = {
                key: (value or "").strip()
                for key, value in raw.items()
                if key is not None
            }
            if not any(values.values()):
                continue
            if values.get("id", "").startswith("#"):
                continue
            result.rows.append(ManifestRow(kind=kind, line_number=line_number, values=values))

    if not result.rows:
        result.warnings.append(f"{manifest_path} contains no data rows")

    seen: set[str] = set()
    for row in result.rows:
        if row.id in seen:
            result.errors.append(f"line {row.line_number}: duplicate id {row.id!r}")
        seen.add(row.id)
        for field_name in REQUIRED_VALUES[kind]:
            if not row.values.get(field_name):
                result.errors.append(
                    f"line {row.line_number}: missing value for {field_name!r}"
                )
        if row.review_status and row.review_status not in {APPROVED, "pending", "rejected"}:
            result.errors.append(
                f"line {row.line_number}: review_status must be approved, pending, or rejected"
            )

    return result


def validate_manifest(
    path: str | Path,
    kind: ManifestKind,
    *,
    require_files: bool = False,
) -> ManifestValidation:
    result = read_manifest(path, kind)
    if require_files:
        base = Path(path).resolve().parent
        for row in result.rows:
            if not row.local_path:
                continue
            local_path = Path(row.local_path).expanduser()
            if not local_path.is_absolute():
                local_path = (base / local_path).resolve()
            if row.approved and not local_path.exists():
                result.errors.append(
                    f"line {row.line_number}: approved file does not exist: {row.local_path}"
                )
    return result


def approved_rows(
    path: str | Path,
    kind: ManifestKind,
    *,
    require_files: bool = True,
) -> list[ManifestRow]:
    validation = validate_manifest(path, kind, require_files=require_files)
    if validation.errors:
        raise ValueError("; ".join(validation.errors))
    rows = [row for row in validation.rows if row.approved]
    if not rows:
        raise ValueError(f"{path} has no approved {kind} rows")
    return rows


def row_file_path(row: ManifestRow, manifest_path: str | Path) -> Path:
    value = Path(row.local_path).expanduser()
    if value.is_absolute():
        return value
    return (Path(manifest_path).resolve().parent / value).resolve()


def set_review_status(
    path: str | Path,
    kind: ManifestKind,
    row_id: str,
    review_status: str,
) -> ManifestValidation:
    return set_review_status_bulk(path, kind, review_status, row_ids=[row_id])


def set_review_status_bulk(
    path: str | Path,
    kind: ManifestKind,
    review_status: str,
    *,
    row_ids: list[str] | None = None,
) -> ManifestValidation:
    """Set ``review_status`` for selected rows in one rewrite.

    When ``row_ids`` is ``None`` every data row is updated; otherwise only the
    listed ids are. A missing requested id is an error so callers do not
    silently approve nothing.
    """
    status = review_status.strip().lower()
    if status not in {APPROVED, "pending", "rejected"}:
        raise ValueError("review_status must be approved, pending, or rejected")

    manifest_path = Path(path)
    expected_fields = EXPECTED_FIELDS[kind]
    if not manifest_path.exists():
        raise ValueError(f"{manifest_path} does not exist")

    with manifest_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or expected_fields
        rows = list(reader)

    if "review_status" not in fieldnames:
        fieldnames = [*fieldnames, "review_status"]
    for field_name in expected_fields:
        if field_name not in fieldnames:
            fieldnames = [*fieldnames, field_name]

    requested = None if row_ids is None else set(row_ids)
    present_ids: set[str] = set()
    for row in rows:
        row_id = (row.get("id") or "").strip()
        if not row_id or row_id.startswith("#"):
            continue
        present_ids.add(row_id)
        if requested is None or row_id in requested:
            row["review_status"] = status

    if requested is not None:
        missing = requested - present_ids
        if missing:
            ids = ", ".join(repr(value) for value in sorted(missing))
            raise ValueError(f"{manifest_path} has no row with id {ids}")

    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})

    return validate_manifest(manifest_path, kind, require_files=True)
