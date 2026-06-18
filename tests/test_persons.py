from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw

from desaparecidos.persons import (
    export_targets_manifest,
    list_persons_api,
    process_selected_portrait,
    save_persons,
    search_plan,
    upsert_person,
)


def _portrait(path: Path) -> None:
    image = Image.new("RGB", (240, 320), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((54, 48, 186, 288), fill=(130, 122, 112))
    draw.ellipse((92, 78, 148, 142), fill=(74, 66, 58))
    draw.rectangle((80, 148, 160, 270), fill=(96, 86, 76))
    image.save(path)


def test_person_store_reports_missing_fields(tmp_path: Path) -> None:
    store = tmp_path / "persons.json"
    save_persons(
        store,
        [
            {
                "full_name": "Persona Incompleta",
                "date_of_birth": "1940-01-01",
                "remains_status": "unknown",
            }
        ],
    )

    response = list_persons_api(store)

    assert response["summary"]["count"] == 1
    person = response["people"][0]
    assert person["id"] == "persona-incompleta"
    assert "place_of_birth" in person["missing_fields"]
    assert "remains_status" in person["missing_fields"]
    assert "selected_portrait" in person["missing_fields"]


def test_process_selected_portrait_and_export_manifest(tmp_path: Path) -> None:
    raw = tmp_path / "raw.jpg"
    _portrait(raw)
    store = tmp_path / "persons.json"
    save_persons(
        store,
        [
            {
                "id": "persona",
                "full_name": "Persona Completa",
                "date_of_birth": "1940-01-01",
                "place_of_birth": "Montevideo",
                "date_of_disappearance": "1976-01-02",
                "place_of_disappearance": "Buenos Aires",
                "remains_status": "not_found",
                "portrait_candidates": [
                    {
                        "id": "portrait-01",
                        "source_url": "https://example.invalid/persona.jpg",
                        "source_page": "https://example.invalid/persona",
                        "licence_or_terms": "fixture",
                        "raw_path": str(raw),
                    }
                ],
            }
        ],
    )

    person = process_selected_portrait(
        store,
        "persona",
        "portrait-01",
        selected_root=tmp_path / "selected",
        use_face=False,
    )
    selected = person["selected_portrait"]
    assert selected["processed_path"].endswith(".jpg")
    with Image.open(selected["processed_path"]) as image:
        assert abs((image.width / image.height) - 0.75) < 0.01

    manifest = tmp_path / "targets.csv"
    summary = export_targets_manifest(store, manifest, approved=False)

    assert summary["rows_written"] == 1
    with manifest.open(newline="", encoding="utf-8") as handle:
        row = next(csv.DictReader(handle))
    assert row["id"] == "persona"
    assert row["name"] == "Persona Completa"
    assert row["review_status"] == "pending"
    assert row["birth_date"] == "1940-01-01"
    assert row["disappearance_place"] == "Buenos Aires"


def test_upsert_person_normalises_old_import_records(tmp_path: Path) -> None:
    store = tmp_path / "persons.json"

    person = upsert_person(
        store,
        {
            "slug": "old-import",
            "full_name": "Old Import",
            "date_of_detention": "1976-04-01",
            "date_of_remains_found": "2005-01-01",
        },
    )

    assert person["id"] == "old-import"
    assert person["date_of_disappearance"] == "1976-04-01"
    assert person["remains_status"] == "found"


def test_search_plan_lists_records_needing_work(tmp_path: Path) -> None:
    store = tmp_path / "persons.json"
    save_persons(store, [{"id": "missing", "full_name": "Missing Portrait"}])

    plan = search_plan(store)

    assert plan["count"] == 1
    assert plan["items"][0]["id"] == "missing"
    assert plan["items"][0]["links"]
