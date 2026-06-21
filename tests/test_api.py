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
            "local_path", "review_status", "location_label", "notes",
            "crawl_run_id", "content_sha256", "perceptual_hash"
        ])
        writer.writerow([
            "s1", "Source", "https://example.invalid/s.png", "https://example.invalid/s",
            "fixture", "2026-06-17", "source.png", "approved", "fixture", "", "", "", ""
        ])
    return targets, sources


def test_health_and_validate(tmp_path: Path) -> None:
    targets, sources = write_fixture(tmp_path)
    client = TestClient(create_app())

    assert client.get("/api/health").json()["ok"] is True
    assert client.get("/api/config").json()["default_max_contribution_per_source"] == 1
    response = client.post(
        "/api/validate",
        json={"targets": str(targets), "sources": str(sources), "require_files": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["targets"]["approved_count"] == 1
    assert body["people"]["row_count"] == 0
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
            "max_contribution_per_source": 0,
            "make_video": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert (tmp_path / "outputs").exists()


def test_generate_endpoint_defaults_to_one_contribution(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    targets, sources = write_fixture(tmp_path)
    captured: dict[str, int] = {}

    def fake_run_stage1(
        target_manifest: str,
        source_manifest: str,
        output_dir: str,
        settings: object,
        *,
        target_id: str | None = None,
        artwork: str = "estan-en-todas-partes",
    ) -> list[object]:
        del target_manifest, source_manifest, output_dir, target_id, artwork
        captured["cap"] = getattr(settings, "max_contribution_per_source")
        return []

    monkeypatch.setattr(api_module, "run_stage1", fake_run_stage1)
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
    assert captured["cap"] == 1


def test_generate_endpoint_preserves_zero_as_unlimited(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    targets, sources = write_fixture(tmp_path)
    captured: dict[str, int] = {}

    def fake_run_stage1(
        target_manifest: str,
        source_manifest: str,
        output_dir: str,
        settings: object,
        *,
        target_id: str | None = None,
        artwork: str = "estan-en-todas-partes",
    ) -> list[object]:
        del target_manifest, source_manifest, output_dir, target_id, artwork
        captured["cap"] = getattr(settings, "max_contribution_per_source")
        return []

    monkeypatch.setattr(api_module, "run_stage1", fake_run_stage1)
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
            "max_contribution_per_source": 0,
            "make_video": False,
        },
    )

    assert response.status_code == 200
    assert captured["cap"] == 0


def test_generate_endpoint_passes_contribution_cap(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    targets, sources = write_fixture(tmp_path)
    captured: dict[str, int] = {}

    def fake_run_stage1(
        target_manifest: str,
        source_manifest: str,
        output_dir: str,
        settings: object,
        *,
        target_id: str | None = None,
        artwork: str = "estan-en-todas-partes",
    ) -> list[object]:
        del target_manifest, source_manifest, output_dir, target_id, artwork
        captured["cap"] = getattr(settings, "max_contribution_per_source")
        captured["scan_frames"] = getattr(settings, "search_scan_frames_per_candidate")
        captured["scan_max"] = getattr(settings, "search_scan_max_candidates")
        return []

    monkeypatch.setattr(api_module, "run_stage1", fake_run_stage1)
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
            "max_contribution_per_source": 7,
            "search_scan_frames_per_candidate": 3,
            "search_scan_max_candidates": 45,
            "make_video": False,
        },
    )

    assert response.status_code == 200
    assert captured["cap"] == 7
    assert captured["scan_frames"] == 3
    assert captured["scan_max"] == 45


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


def test_review_bulk_endpoint_approves_all(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    targets, _ = write_fixture(tmp_path)
    with targets.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "t2", "Target two", "https://example.invalid/t2.png", "https://example.invalid/t2",
            "fixture", "2026-06-17", "target.png", "pending", "", "", "", "", "", "", "", ""
        ])
    monkeypatch.setattr(api_module, "safe_project_path", lambda value: Path(value))
    client = TestClient(create_app())

    response = client.post(
        "/api/review-bulk",
        json={
            "manifest": str(targets),
            "kind": "targets",
            "review_status": "approved",
            "all": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["manifest"]["approved_count"] == 2


def test_review_delete_endpoint_removes_row(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    targets, _ = write_fixture(tmp_path)
    monkeypatch.setattr(api_module, "safe_project_path", lambda value: Path(value))
    client = TestClient(create_app())

    response = client.post(
        "/api/review/delete",
        json={"manifest": str(targets), "kind": "targets", "row_id": "t1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert all(row["id"] != "t1" for row in body["manifest"]["rows"])


def test_review_delete_endpoint_removes_many(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    targets, _ = write_fixture(tmp_path)
    with targets.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "t2", "Target two", "https://example.invalid/t2.png", "https://example.invalid/t2",
            "fixture", "2026-06-17", "target.png", "pending", "", "", "", "", "", "", "", ""
        ])
    monkeypatch.setattr(api_module, "safe_project_path", lambda value: Path(value))
    client = TestClient(create_app())

    response = client.post(
        "/api/review/delete",
        json={"manifest": str(targets), "kind": "targets", "row_ids": ["t1", "t2"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["manifest"]["rows"] == []


def test_review_delete_endpoint_rejects_missing_id(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    targets, _ = write_fixture(tmp_path)
    monkeypatch.setattr(api_module, "safe_project_path", lambda value: Path(value))
    client = TestClient(create_app())

    response = client.post(
        "/api/review/delete",
        json={"manifest": str(targets), "kind": "targets", "row_ids": ["t1", "nope"]},
    )

    assert response.status_code == 400
    # The bad id rejects the whole request; t1 is left in place.
    assert "no row with id" in response.json()["detail"]


def test_crawl_endpoint(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    class FakeSummary:
        def to_api(self) -> dict[str, object]:
            return {
                "ok": True,
                "manifest": "data/manifests/crawled-places.csv",
                "kind": "places",
                "pages": ["https://example.test/page"],
                "run_id": "test-run",
                "trail_path": "data/raw/crawl/runs/test-run.jsonl",
                "pages_crawled": 1,
                "images_seen": 0,
                "from_cache": 0,
                "cv_rejected": 0,
                "duplicates": 0,
                "added": 0,
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
            "max_depth": 1,
            "max_pages": 10,
            "max_images": 20,
            "cross_domain": False,
            "use_cv": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_combined_crawl_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeCombinedSummary:
        def to_api(self) -> dict[str, object]:
            return {
                "ok": True,
                "pages": ["https://example.test/page"],
                "pages_crawled": 1,
                "images_seen": 1,
                "errors": [],
                "results": {
                    "places": {"manifest": "data/manifests/crawled-places.csv", "added": 1},
                    "people": {"manifest": "data/manifests/crawled-people.csv", "added": 1},
                },
            }

    monkeypatch.setattr(api_module, "crawl_pages_combined", lambda *_args, **_kwargs: FakeCombinedSummary())
    client = TestClient(create_app())

    response = client.post(
        "/api/crawl/combined",
        json={
            "pages": ["https://example.test/page"],
            "places_manifest": "data/manifests/crawled-places.csv",
            "people_manifest": "data/manifests/crawled-people.csv",
        },
    )

    assert response.status_code == 200
    assert response.json()["images_seen"] == 1


def test_traversal_endpoints_expose_provider_neutral_contract(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    traversal = {
        "id": "route-one",
        "name": "Route one",
        "artwork": "seguimos-buscando",
        "provider": "mapillary",
        "frames": [],
    }
    monkeypatch.setattr(api_module, "safe_project_path", lambda value: Path(value))
    monkeypatch.setattr(api_module, "discover_traversal", lambda **_kwargs: traversal)
    monkeypatch.setattr(api_module, "acquire_traversal", lambda *_args, **_kwargs: traversal)
    monkeypatch.setattr(api_module, "review_traversal_frames", lambda *_args, **_kwargs: traversal)
    client = TestClient(create_app())

    discovered = client.post(
        "/api/traversals/discover",
        json={
            "name": "Route one",
            "mode": "manual",
            "geometry": {"type": "LineString", "coordinates": [[-56.2, -34.9], [-56.1, -34.8]]},
            "root": str(tmp_path),
        },
    )
    assert discovered.status_code == 200
    assert discovered.json()["traversal"]["provider"] == "mapillary"
    assert client.post(
        "/api/traversals/acquire", json={"traversal_id": "route-one", "root": str(tmp_path)}
    ).status_code == 200
    assert client.post(
        "/api/traversals/route-one/frames/review",
        json={"frame_ids": [], "review_status": "approved", "root": str(tmp_path)},
    ).status_code == 200


def test_traversal_generate_endpoint_records_third_artwork(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class Output:
        def __init__(self) -> None:
            self.target_id = "target-one"
            self.still_path = "outputs/one.png"
            self.sidecar_path = "outputs/one.json"
            self.video_path = "outputs/one.mp4"

    monkeypatch.setattr(api_module, "safe_project_path", lambda value: Path(value))
    monkeypatch.setattr(api_module, "render_traversal", lambda *_args, **_kwargs: [Output()])
    response = TestClient(create_app()).post(
        "/api/generate/traversal",
        json={
            "traversal_id": "route-one",
            "targets": str(tmp_path / "targets.csv"),
            "output_dir": str(tmp_path / "outputs"),
            "traversal_root": str(tmp_path / "routes"),
            "target_ids": ["target-one"],
            "target_mode": "single",
            "composition": "split",
        },
    )
    assert response.status_code == 200
    assert response.json()["outputs"][0]["video_path"].endswith(".mp4")


def test_persons_endpoints_save_list_and_export(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    image = tmp_path / "portrait.jpg"
    Image.new("RGB", (120, 160), (120, 110, 100)).save(image)
    store = tmp_path / "persons.json"
    manifest = tmp_path / "targets.csv"
    monkeypatch.setattr(api_module, "safe_project_path", lambda value: Path(value))
    client = TestClient(create_app())

    response = client.post(
        "/api/persons/save",
        json={
            "store": str(store),
            "person": {
                "id": "person-one",
                "full_name": "Person One",
                "date_of_birth": "1940-01-01",
                "place_of_birth": "Montevideo",
                "date_of_disappearance": "1976-01-02",
                "place_of_disappearance": "Buenos Aires",
                "remains_status": "not_found",
                "portrait_candidates": [
                    {
                        "id": "portrait-01",
                        "source_url": "https://example.invalid/person.jpg",
                        "source_page": "https://example.invalid/person",
                        "licence_or_terms": "fixture",
                        "processed_path": str(image),
                    }
                ],
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["person"]["missing_fields"] == []

    listed = client.get("/api/persons", params={"store": str(store)})
    assert listed.status_code == 200
    assert listed.json()["summary"]["count"] == 1

    exported = client.post(
        "/api/persons/export-targets",
        json={"store": str(store), "manifest": str(manifest), "approved": False},
    )
    assert exported.status_code == 200
    assert exported.json()["rows_written"] == 1
    assert manifest.exists()


def test_person_sources_endpoint_does_not_hit_person_id_route() -> None:
    client = TestClient(create_app())

    response = client.get("/api/persons/sources")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["registry"]["sources"]


def test_delete_outputs_endpoint(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    (output_dir / "one.json").write_text('{"target_id": "t1"}', encoding="utf-8")
    (output_dir / "one.png").write_bytes(b"png")
    (output_dir / "two.json").write_text('{"target_id": "t2"}', encoding="utf-8")

    monkeypatch.setattr(api_module, "safe_project_path", lambda value: Path(value))
    client = TestClient(create_app())

    response = client.post(
        "/api/outputs/delete",
        json={"output_dir": str(output_dir), "ids": ["one"], "all": False},
    )

    assert response.status_code == 200
    assert response.json()["deleted"] == ["one"]
    assert not (output_dir / "one.json").exists()
    assert not (output_dir / "one.png").exists()
    assert (output_dir / "two.json").exists()


def test_file_endpoint_serves_mp4_media_type(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    video = tmp_path / "video.mp4"
    video.write_bytes(b"mp4")

    monkeypatch.setattr(api_module, "safe_project_path", lambda value: Path(value))
    client = TestClient(create_app())

    response = client.get("/api/file", params={"path": str(video)})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("video/mp4")
