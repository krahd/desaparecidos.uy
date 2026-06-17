from __future__ import annotations

import csv
from pathlib import Path

from desaparecidos.manifests import validate_manifest


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
