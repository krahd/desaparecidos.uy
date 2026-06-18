from __future__ import annotations

import csv
from pathlib import Path

import pytest

from desaparecidos.manifests import (
    delete_manifest_row,
    delete_manifest_rows,
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

PEOPLE_HEADER = [
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
    "crawl_run_id",
    "content_sha256",
    "perceptual_hash",
    "face_x",
    "face_y",
    "face_width",
    "face_height",
]

PLACE_HEADER = [
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
    "crawl_run_id",
    "content_sha256",
    "perceptual_hash",
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


def test_people_manifest_kind_is_validated(tmp_path: Path) -> None:
    path = tmp_path / "people.csv"
    write_csv(
        path,
        PEOPLE_HEADER,
        [[
            "p1",
            "Public event person",
            "https://example.invalid/person.png",
            "https://example.invalid/event",
            "fixture",
            "2026-06-18",
            "person.png",
            "pending",
            "Montevideo",
            "manual review",
            "run-1",
            "abc",
            "ff00",
            "10",
            "12",
            "80",
            "90",
        ]],
    )

    result = validate_manifest(path, "people")

    assert result.ok
    assert result.rows[0].label == "Public event person"


def write_pending_manifest(path: Path, kind: str) -> None:
    (path.parent / "a.png").write_bytes(b"a")
    (path.parent / "b.png").write_bytes(b"b")
    if kind == "targets":
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
    elif kind == "places":
        write_csv(
            path,
            PLACE_HEADER,
            [
                ["p1", "Place one", "u", "p", "fixture", "2026-06-17", "a.png", "pending",
                 "Montevideo", "", "run", "sha1", "ph1"],
                ["p2", "Place two", "u", "p", "fixture", "2026-06-17", "b.png", "pending",
                 "Montevideo", "", "run", "sha2", "ph2"],
            ],
        )
    elif kind == "people":
        write_csv(
            path,
            PEOPLE_HEADER,
            [
                ["p1", "Person one", "u", "p", "fixture", "2026-06-17", "a.png", "pending",
                 "Montevideo", "", "run", "sha1", "ph1", "1", "2", "30", "40"],
                ["p2", "Person two", "u", "p", "fixture", "2026-06-17", "b.png", "pending",
                 "Montevideo", "", "run", "sha2", "ph2", "3", "4", "32", "42"],
            ],
        )
    else:
        raise AssertionError(f"unexpected kind: {kind}")


@pytest.mark.parametrize("kind", ["targets", "places", "people"])
def test_bulk_review_updates_all_rows(tmp_path: Path, kind: str) -> None:
    path = tmp_path / f"{kind}.csv"
    write_pending_manifest(path, kind)

    result = set_review_status_bulk(path, kind, "approved")

    assert result.approved_count == 2
    assert all(row.approved for row in result.rows)


@pytest.mark.parametrize("kind", ["targets", "places", "people"])
def test_bulk_review_updates_selected_rows(tmp_path: Path, kind: str) -> None:
    path = tmp_path / f"{kind}.csv"
    write_pending_manifest(path, kind)

    result = set_review_status_bulk(path, kind, "approved", row_ids=["p2"])

    statuses = {row.id: row.review_status for row in result.rows}
    assert statuses == {"p1": "pending", "p2": "approved"}


@pytest.mark.parametrize("kind", ["targets", "places", "people"])
def test_single_review_reports_missing_id(tmp_path: Path, kind: str) -> None:
    path = tmp_path / f"{kind}.csv"
    write_pending_manifest(path, kind)

    with pytest.raises(ValueError, match="no row with id"):
        set_review_status(path, kind, "missing", "approved")


@pytest.mark.parametrize("kind", ["targets", "places", "people"])
def test_delete_manifest_row_removes_one(tmp_path: Path, kind: str) -> None:
    path = tmp_path / f"{kind}.csv"
    write_pending_manifest(path, kind)

    result = delete_manifest_row(path, kind, "p1")

    assert [row.id for row in result.rows] == ["p2"]


@pytest.mark.parametrize("kind", ["targets", "places", "people"])
def test_delete_manifest_row_missing_id(tmp_path: Path, kind: str) -> None:
    path = tmp_path / f"{kind}.csv"
    write_pending_manifest(path, kind)

    with pytest.raises(ValueError, match="no row with id"):
        delete_manifest_row(path, kind, "nope")


@pytest.mark.parametrize("kind", ["targets", "places", "people"])
def test_delete_manifest_rows_removes_many(tmp_path: Path, kind: str) -> None:
    path = tmp_path / f"{kind}.csv"
    write_pending_manifest(path, kind)

    result = delete_manifest_rows(path, kind, ["p1", "p2"])

    assert [row.id for row in result.rows] == []


@pytest.mark.parametrize("kind", ["targets", "places", "people"])
def test_delete_manifest_rows_missing_id_is_error(tmp_path: Path, kind: str) -> None:
    path = tmp_path / f"{kind}.csv"
    write_pending_manifest(path, kind)

    with pytest.raises(ValueError, match="no row with id"):
        delete_manifest_rows(path, kind, ["p1", "nope"])

    # The whole rewrite is rejected; nothing is deleted on a bad id.
    result = validate_manifest(path, kind)
    assert {row.id for row in result.rows} == {"p1", "p2"}


@pytest.mark.parametrize("kind", ["targets", "places", "people"])
def test_delete_manifest_rows_requires_ids(tmp_path: Path, kind: str) -> None:
    path = tmp_path / f"{kind}.csv"
    write_pending_manifest(path, kind)

    with pytest.raises(ValueError, match="no row ids provided"):
        delete_manifest_rows(path, kind, [])
