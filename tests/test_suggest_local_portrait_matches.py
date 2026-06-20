from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

from PIL import Image

from desaparecidos.persons import load_persons, save_persons

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "suggest_local_portrait_matches.py"
_spec = importlib.util.spec_from_file_location("suggest_local_portrait_matches", _SCRIPT)
assert _spec is not None and _spec.loader is not None
suggest = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = suggest
_spec.loader.exec_module(suggest)


def _write_manifest(path: Path, image_name: str) -> None:
    fields = [
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
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerow(
            {
                "id": "altmann-blanca",
                "name": "Altmann - Blanca",
                "source_url": f"local://fotos-desaparecidos/{image_name}",
                "source_page": "doc/fotos-desaparecidos",
                "licence_or_terms": "unknown - pending provenance review",
                "accessed_at": "2026-06-18",
                "local_path": "",
                "review_status": "approved",
                "notes": "fixture",
            }
        )


def test_score_match_accepts_partial_family_and_given_name() -> None:
    person = {
        "id": "altmann-levy-blanca-haydee",
        "full_name": "Altmann Levy, Blanca Haydée",
        "given_names": "Blanca Haydée",
        "family_names": "Altmann Levy",
    }
    row = {"id": "altmann-blanca", "name": "Altmann - Blanca"}

    match = suggest.score_match(person, row)

    assert match["score"] >= 0.82
    assert "family-name-overlap" in match["reasons"]
    assert "given-name-overlap" in match["reasons"]


def test_collect_and_apply_local_candidate_without_selecting(tmp_path: Path) -> None:
    source_dir = tmp_path / "fotos"
    source_dir.mkdir()
    image_path = source_dir / "Altmann - Blanca 1.jpg"
    Image.new("RGB", (64, 96), "white").save(image_path)
    manifest = tmp_path / "local-targets.csv"
    _write_manifest(manifest, image_path.name)
    store = tmp_path / "persons.json"
    save_persons(
        store,
        [
            {
                "id": "altmann-levy-blanca-haydee",
                "full_name": "Altmann Levy, Blanca Haydée",
                "given_names": "Blanca Haydée",
                "family_names": "Altmann Levy",
                "portrait_status": "missing",
            }
        ],
    )

    suggestions = suggest.collect_suggestions(
        persons_path=store,
        manifest_path=manifest,
        source_dir=source_dir,
        min_score=0.82,
    )
    result = suggest.apply_suggestions(store, suggestions)
    person = load_persons(store)[0]

    assert len(suggestions) == 1
    assert result["added"] == 1
    assert person["portrait_status"] == "candidate"
    assert person["selected_portrait_id"] == ""
    assert person["portrait_candidates"][0]["source_id"] == "local-fotos-desaparecidos"
