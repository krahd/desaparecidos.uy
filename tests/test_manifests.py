from __future__ import annotations

import csv
from pathlib import Path

import pytest

from desaparecidos.manifests import (
    delete_manifest_row,
    set_review_status,
    set_review_status_bulk,
    validate_manifest,
)


TARGET_HEADER = [
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


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def test_empty_manifest_is_valid_with_warning(tmp_path: Path) -> None:
    path = tmp_path / "targets.csv"
    write_csv(path, TARGET_HEADER, [])

    result = validate_manifest(path, "targets")

    assert result.ok
    assert result.rows == []
    assert "contains no data rows" in result.warnings[0]


def test_review_status_is_validated(tmp_path: Path) -> None:
    path = tmp_path / "targets.csv"
    write_csv(
        path,
        TARGET_HEADER,
        [[
            "p1",
            "Person",
            "https://example.invalid/a.png",
            "https://example.invalid/a",
            "fixture",
            "2026-06-17",
            "a.png",
            "ready",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]],
    )

    result = validate_manifest(path, "targets")

    assert not result.ok
    assert any("review_status" in error for error in result.errors)


def test_approved_file_must_exist_when_required(tmp_path: Path) -> None:
    path = tmp_path / "targets.csv"
    write_csv(
        path,
        TARGET_HEADER,
        [[
            "p1",
            "Person",
            "https://example.invalid/a.png",
            "https://example.invalid/a",
            "fixture",
            "2026-06-17",
            "missing.png",
            "approved",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]],
    )

    result = validate_manifest(path, "targets", require_files=True)

    assert not result.ok
    assert any("does not exist" in error for error in result.errors)


def write_pending_targets(path: Path) -> None:
    (path.parent / "a.png").write_bytes(b"a")
    (path.parent / "b.png").write_bytes(b"b")
    write_csv(
        path,
        TARGET_HEADER,
        [
            ["p1", "One", "u", "p", "fixture", "2026-06-17", "a.png", "pending",
             "", "", "", "", "", "", "", ""],
            ["p2", "Two", "u", "p", "fixture", "2026-06-17", "b.png", "pending",
             "", "", "", "", "", "", "", ""],
        ],
    )


def test_bulk_review_updates_all_rows(tmp_path: Path) -> None:
    path = tmp_path / "targets.csv"
    write_pending_targets(path)

    result = set_review_status_bulk(path, "targets", "approved")

    assert result.approved_count == 2
    assert all(row.approved for row in result.rows)


def test_bulk_review_updates_selected_rows(tmp_path: Path) -> None:
    path = tmp_path / "targets.csv"
    write_pending_targets(path)

    result = set_review_status_bulk(path, "targets", "approved", row_ids=["p2"])

    statuses = {row.id: row.review_status for row in result.rows}
    assert statuses == {"p1": "pending", "p2": "approved"}


def test_single_review_reports_missing_id(tmp_path: Path) -> None:
    path = tmp_path / "targets.csv"
    write_pending_targets(path)

    with pytest.raises(ValueError, match="no row with id"):
        set_review_status(path, "targets", "missing", "approved")


def test_delete_manifest_row_removes_one(tmp_path: Path) -> None:
    path = tmp_path / "targets.csv"
    write_pending_targets(path)

    result = delete_manifest_row(path, "targets", "p1")

    assert [row.id for row in result.rows] == ["p2"]


def test_delete_manifest_row_missing_id(tmp_path: Path) -> None:
    path = tmp_path / "targets.csv"
    write_pending_targets(path)

    with pytest.raises(ValueError, match="no row with id"):
        delete_manifest_row(path, "targets", "nope")
