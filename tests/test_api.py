from __future__ import annotations

import csv
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image
import pytest

import desaparecidos.api as api_module
from desaparecidos.api import create_app


def write_fixture(tmp_path: Path) -> tuple[Path, Path]:
    Image.new("RGB", (64, 64), (210, 210, 205)).save(tmp_path / "target.png")
    Image.new("RGB", (64, 64), (120, 130, 140)).save(tmp_path / "source.png")

    targets = tmp_path / "targets.csv"
    with targets.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "id", "name", "source_url", "source_page", "licence_or_terms", "accessed_at",
            "local_path", "review_status", "birth_date", "disappearance_date",
            "disappearance_place", "notes", "crop_x", "crop_y", "crop_width", "crop_height"
        ])
        writer.writerow([
            "t1", "Target", "https://example.invalid/t.png", "https://example.invalid/t",
            "fixture", "2026-06-17", "target.png", "approved", "", "", "", "", "", "", "", ""
        ])

    sources = tmp_path / "places.csv"
    with sources.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "id", "title", "source_url", "source_page", "licence_or_terms", "accessed_at",
            "local_path", "review_status", "location_label", "notes"
        ])
        writer.writerow([
            "s1", "Source", "https://example.invalid/s.png", "https://example.invalid/s",
            "fixture", "2026-06-17", "source.png", "approved", "fixture", ""
        ])
    return targets, sources


def test_health_and_validate(tmp_path: Path) -> None:
    targets, sources = write_fixture(tmp_path)
    client = TestClient(create_app())

    assert client.get("/api/health").json()["ok"] is True
    response = client.post(
        "/api/validate",
        json={"targets": str(targets), "sources": str(sources), "require_files": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["targets"]["approved_count"] == 1
    assert body["targets"]["rows"][0]["file_path"].endswith("target.png")


def test_generate_endpoint(tmp_path: Path) -> None:
    targets, sources = write_fixture(tmp_path)
    client = TestClient(create_app())

    response = client.post(
        "/api/generate",
        json={
            "targets": str(targets),
            "sources": str(sources),
            "output_dir": str(tmp_path / "outputs"),
            "seed": 17,
            "fragment_size": 16,
            "reuse_limit": 100,
            "output_width": 120,
            "make_video": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert (tmp_path / "outputs").exists()


def test_demo_fixtures_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_create_demo_fixtures() -> dict[str, object]:
        return {
            "ok": True,
            "targets": "data/manifests/demo-targets.csv",
            "sources": "data/manifests/demo-places.csv",
            "images": [],
        }

    monkeypatch.setattr(api_module, "create_demo_fixtures", fake_create_demo_fixtures)
    client = TestClient(create_app())

    response = client.post("/api/demo-fixtures")

    assert response.status_code == 200
    assert response.json()["targets"] == "data/manifests/demo-targets.csv"


def test_review_endpoint_updates_manifest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    targets, _ = write_fixture(tmp_path)
    monkeypatch.setattr(api_module, "safe_project_path", lambda value: Path(value))
    client = TestClient(create_app())

    response = client.post(
        "/api/review",
        json={
            "manifest": str(targets),
            "kind": "targets",
            "row_id": "t1",
            "review_status": "rejected",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["manifest"]["rows"][0]["values"]["review_status"] == "rejected"


def test_crawl_endpoint(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class FakeSummary:
        def to_api(self) -> dict[str, object]:
            return {
                "ok": True,
                "manifest": "data/manifests/crawled-places.csv",
                "kind": "places",
                "pages": ["https://example.test/page"],
                "items": [],
                "errors": [],
            }

    def fake_crawl_pages(*_: object, **__: object) -> FakeSummary:
        return FakeSummary()

    monkeypatch.setattr(api_module, "crawl_pages", fake_crawl_pages)
    client = TestClient(create_app())

    response = client.post(
        "/api/crawl",
        json={
            "pages": ["https://example.test/page"],
            "kind": "places",
            "manifest": "data/manifests/crawled-places.csv",
            "output_root": "data/raw/crawl",
        },
    )

    assert response.status_code == 200
    assert response.json()["ok"] is True
