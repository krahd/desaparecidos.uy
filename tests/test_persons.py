from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw

from desaparecidos.persons import (
    export_targets_manifest,
    list_persons_api,
    missing_fields,
    process_selected_portrait,
    portrait_review_summary,
    save_persons,
    search_plan,
    upsert_person,
)
from scripts.apply_person_metadata_overrides import apply_overrides


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


def test_person_store_preserves_relevant_import_fields(tmp_path: Path) -> None:
    store = tmp_path / "persons.json"

    saved = save_persons(
        store,
        [
            {
                "id": "persona",
                "full_name": "Persona Con Datos",
                "age_at_disappearance": 31,
                "nationality": ["Uruguaya"],
                "occupations": ["Estudiante"],
                "union_militancy": ["Sindicato"],
                "political_militancy": ["Organizacion"],
                "country_of_detention": "Argentina",
                "date_of_identification": "2011",
                "date_of_death": "1975-08-30",
                "victim_type": "Desaparición forzada",
            }
        ],
    )

    person = saved[0]
    assert person["age_at_disappearance"] == 31
    assert person["nationality"] == ["Uruguaya"]
    assert person["occupations"] == ["Estudiante"]
    assert person["union_militancy"] == ["Sindicato"]
    assert person["political_militancy"] == ["Organizacion"]
    assert person["country_of_detention"] == "Argentina"
    assert person["date_of_identification"] == "2011"
    assert person["date_of_death"] == "1975-08-30"
    assert person["victim_type"] == "Desaparición forzada"


def test_death_date_and_place_satisfy_loss_fields(tmp_path: Path) -> None:
    store = tmp_path / "persons.json"
    saved = save_persons(
        store,
        [
            {
                "id": "persona",
                "full_name": "Persona Fallecida",
                "date_of_birth": "1940-01-01",
                "place_of_birth": "Montevideo",
                "date_of_death": "1975-08-30",
                "place_of_death": "Buenos Aires, Argentina",
                "remains_status": "unknown",
            }
        ],
    )

    person = saved[0]
    assert "date_of_disappearance" not in missing_fields(person)
    assert "place_of_disappearance" not in missing_fields(person)
    assert "remains_status" in missing_fields(person)

    manifest = tmp_path / "targets.csv"
    raw = tmp_path / "raw.jpg"
    _portrait(raw)
    person["portrait_candidates"] = [
        {
            "id": "portrait-01",
            "source_url": "https://example.invalid/persona.jpg",
            "source_page": "https://example.invalid/persona",
            "processed_path": str(raw),
        }
    ]
    person["selected_portrait_id"] = "portrait-01"
    save_persons(store, [person])
    export_targets_manifest(store, manifest, approved=False)
    with manifest.open(newline="", encoding="utf-8") as handle:
        row = next(csv.DictReader(handle))
    assert row["disappearance_date"] == "1975-08-30"
    assert row["disappearance_place"] == "Buenos Aires, Argentina"


def test_person_store_extracts_embedded_death_date_from_old_imports(tmp_path: Path) -> None:
    store = tmp_path / "persons.json"

    saved = save_persons(
        store,
        [
            {
                "id": "persona",
                "full_name": "Persona Con Etiqueta Embebida",
                "country_of_detention": "Argentina | Fecha de muerte | 30/08/1975",
                "places_of_detention": ["Centro", "Fecha de muerte", "04/1976"],
                "field_sources": {
                    "country_of_detention": "sitios-de-memoria",
                    "places_of_detention": "sitios-de-memoria",
                },
            }
        ],
    )

    person = saved[0]
    assert person["country_of_detention"] == "Argentina"
    assert person["places_of_detention"] == ["Centro"]
    assert person["date_of_death"] == "1975-08-30"
    assert person["field_sources"]["date_of_death"] == "sitios-de-memoria"


def test_apply_metadata_overrides_records_field_provenance(tmp_path: Path) -> None:
    store = tmp_path / "persons.json"
    people = save_persons(
        store,
        [
            {
                "id": "persona",
                "full_name": "Persona Con Gaps",
            }
        ],
    )

    result = apply_overrides(
        people,
        [
            {
                "id": "persona",
                "field": "date_of_birth",
                "value": "1946-09-28",
                "source_id": "investigacion-historica",
                "source_ref": "Fichas D.pdf",
                "source_page": "doc/writings/references/DDHH/Fichas D.pdf",
                "notes": "Fixture source.",
            }
        ],
        source_ids={"investigacion-historica"},
    )

    assert result["errors"] == []
    assert result["applied"] == [{"id": "persona", "field": "date_of_birth", "value": "1946-09-28"}]
    assert people[0]["date_of_birth"] == "1946-09-28"
    assert people[0]["field_sources"]["date_of_birth"] == "investigacion-historica"
    assert people[0]["field_source_refs"]["date_of_birth"] == "Fichas D.pdf"
    assert people[0]["sources"] == ["doc/writings/references/DDHH/Fichas D.pdf"]
    assert "Metadata override (date_of_birth): Fixture source." in people[0]["notes"]


def test_search_plan_lists_records_needing_work(tmp_path: Path) -> None:
    store = tmp_path / "persons.json"
    save_persons(store, [{"id": "missing", "full_name": "Missing Portrait"}])

    plan = search_plan(store)

    assert plan["count"] == 1
    assert plan["items"][0]["id"] == "missing"
    assert plan["items"][0]["links"]


def test_raw_portrait_candidate_is_not_auto_selected(tmp_path: Path) -> None:
    raw = tmp_path / "raw.jpg"
    _portrait(raw)
    store = tmp_path / "persons.json"

    saved = save_persons(
        store,
        [
            {
                "id": "persona",
                "full_name": "Persona Con Candidato",
                "portrait_status": "candidate",
                "portrait_candidates": [
                    {
                        "id": "candidate-01",
                        "source_url": "local://fixture/raw.jpg",
                        "source_page": "fixture",
                        "raw_path": str(raw),
                        "status": "candidate",
                    }
                ],
            }
        ],
    )

    person = saved[0]
    assert person["selected_portrait_id"] == ""
    assert "selected_portrait" in person["missing_fields"]


def test_portrait_review_summary_flags_higher_resolution_candidate(tmp_path: Path) -> None:
    store = tmp_path / "persons.json"
    saved = save_persons(
        store,
        [
            {
                "id": "persona",
                "full_name": "Persona Con Alternativa",
                "selected_portrait_id": "portrait-01",
                "portrait_candidates": [
                    {
                        "id": "portrait-01",
                        "processed_path": "selected.jpg",
                        "width": 200,
                        "height": 300,
                    },
                    {
                        "id": "local-01",
                        "raw_path": "local.jpg",
                        "width": 800,
                        "height": 1200,
                        "source_id": "local-fotos-desaparecidos",
                    },
                ],
            }
        ],
    )

    summary = portrait_review_summary(saved[0])
    api = list_persons_api(store)

    assert summary["needs_review"] is True
    assert summary["reason"] == "higher-resolution-alternative"
    assert summary["best_alternative_id"] == "local-01"
    assert api["summary"]["portrait_review_count"] == 1
    assert api["people"][0]["portrait_review"]["best_alternative_source"] == "local-fotos-desaparecidos"
