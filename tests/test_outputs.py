from __future__ import annotations

from pathlib import Path

import pytest

from desaparecidos.outputs import delete_outputs, list_outputs


def write_output(root: Path, stem: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{stem}.json").write_text('{"target_id": "target"}', encoding="utf-8")
    (root / f"{stem}.png").write_bytes(b"png")
    (root / f"{stem}.mp4").write_bytes(b"mp4")


def test_delete_outputs_removes_selected_sidecars_and_media(tmp_path: Path) -> None:
    write_output(tmp_path, "one")
    write_output(tmp_path, "two")

    summary = delete_outputs(tmp_path, ids=["one"])

    assert summary == {"ok": True, "deleted": ["one"], "errors": []}
    assert not (tmp_path / "one.json").exists()
    assert not (tmp_path / "one.png").exists()
    assert not (tmp_path / "one.mp4").exists()
    assert (tmp_path / "two.json").exists()
    assert [item["id"] for item in list_outputs(tmp_path)] == ["two"]


def test_delete_outputs_removes_all_outputs(tmp_path: Path) -> None:
    write_output(tmp_path, "one")
    write_output(tmp_path, "two")

    summary = delete_outputs(tmp_path, all_outputs=True)

    assert summary["ok"] is True
    assert summary["deleted"] == ["one", "two"]
    assert list_outputs(tmp_path) == []


def test_delete_outputs_requires_selection(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="select at least one output"):
        delete_outputs(tmp_path)


def test_delete_outputs_reports_missing_ids(tmp_path: Path) -> None:
    write_output(tmp_path, "one")

    summary = delete_outputs(tmp_path, ids=["missing"])

    assert summary["ok"] is False
    assert summary["deleted"] == []
    assert summary["errors"] == ["output not found: missing"]
    assert (tmp_path / "one.json").exists()
