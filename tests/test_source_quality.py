from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image

import desaparecidos.source_quality as quality_module
from desaparecidos.cv import CVResult
from desaparecidos.manifests import read_manifest
from desaparecidos.source_quality import quality_pass_source_manifest


def _manifest(path: Path, kind: str) -> None:
    image_path = path.parent / "image.png"
    Image.new("RGB", (400, 400), "grey").save(image_path)
    fields = [
        "id", "title", "source_url", "source_page", "licence_or_terms",
        "accessed_at", "local_path", "review_status", "location_label", "notes",
        "crawl_run_id", "content_sha256", "perceptual_hash",
    ]
    if kind == "people":
        fields.extend(["face_x", "face_y", "face_width", "face_height"])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        row = {
            "id": "candidate", "title": "Candidate", "source_url": "local://image",
            "source_page": "local://page", "licence_or_terms": "internal test",
            "accessed_at": "2026-09-08", "local_path": image_path.name,
            "review_status": "pending",
        }
        writer.writerow(row)


def test_people_quality_pass_approves_only_confirmed_face_and_updates_box(
    monkeypatch, tmp_path: Path
) -> None:
    manifest = tmp_path / "people.csv"
    _manifest(manifest, "people")
    monkeypatch.setattr(
        quality_module,
        "classify_image",
        lambda _image, _kind: CVResult(True, "face", 0.2, "confirmed", (20, 30, 80, 90)),
    )

    summary = quality_pass_source_manifest(manifest, "people")
    row = read_manifest(manifest, "people").rows[0]

    assert summary.approved == 1
    assert row.approved is True
    assert [row.values[key] for key in ("face_x", "face_y", "face_width", "face_height")] == [
        "20", "30", "80", "90"
    ]


def test_place_quality_pass_rejects_failed_scene_gate(monkeypatch, tmp_path: Path) -> None:
    manifest = tmp_path / "places.csv"
    _manifest(manifest, "places")
    monkeypatch.setattr(
        quality_module,
        "classify_image",
        lambda _image, _kind: CVResult(False, "graphic", 0.8, "poster"),
    )

    summary = quality_pass_source_manifest(manifest, "places")
    row = read_manifest(manifest, "places").rows[0]

    assert summary.rejected == 1
    assert row.review_status == "rejected"
