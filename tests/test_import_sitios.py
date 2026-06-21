"""Tests for the conservative portrait selection and field extraction in the
Sitios de Memoria importer (scripts/import_sitios_memoria.py).

The importer is a standalone script, so it is loaded by path rather than as a
package module. Fixtures mimic the real Drupal markup: the person portrait
lives in a ``field--name-field-fotografia`` container; works/materials imagery
lives in other field containers.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "import_sitios_memoria.py"
_spec = importlib.util.spec_from_file_location("import_sitios_memoria", _SCRIPT)
assert _spec is not None and _spec.loader is not None
importer = importlib.util.module_from_spec(_spec)
# Register before exec so dataclass introspection can resolve the module.
sys.modules[_spec.name] = importer
_spec.loader.exec_module(importer)


# A page like Horacio Adolfo Abeledo Sotuyo: there is NO portrait field; the
# only /sites/default/files/ image is a work poster inside "Obras de interés".
POSTER_ONLY_PAGE = """
<html><body>
<nav><a href="/causas">Causas judiciales</a></nav>
<header><img src="/sites/default/files/logo-para-banner.png" alt="logo"></header>
<main>
<h1 class="page-header"><span>Abeledo Sotuyo, Horacio Adolfo</span></h1>
<div class="field field--name-field-nombres"><p>Nombre</p><p>Horacio Adolfo</p></div>
<div class="field field--name-field-apellidos"><p>Apellido</p><p>Abeledo Sotuyo</p></div>
<div class="field field--name-field-nacimiento"><p>Fecha de nacimiento</p><p>25/07/1953</p></div>
<div class="field field--name-field-secuestro-pais"><p>País de secuestro/detención</p><p>Argentina</p></div>
<div class="field field--name-field-muerte"><p>Fecha de muerte</p><p>30/08/1975</p></div>
<div class="field field--name-field-hallazgo"><p>Lugar de hallazgo de restos</p><p>Playa Blancarena</p></div>
<div class="field field--name-field-identificacion"><p>Fecha de identificación</p><p>2011</p></div>
<div class="field field--name-field-victima-de"><p>Víctima de</p><p>Desaparición forzada</p></div>
<h2>Obras de interés (1)</h2>
<p>El tiempo pasa (2013)</p>
<img src="/sites/default/files/styles/medium/public/2020-01/El-tiempo-pasa.jpg" alt="El tiempo pasa">
<h2>Materiales de interés (1)</h2>
<img src="/sites/default/files/inline-images/accederenlace.png">
<footer>PARTICIPAMOS DE:</footer>
</main></body></html>
"""

# A page that carries a real portrait inside the fotografia field.
PORTRAIT_PAGE = """
<html><head><title>Wrong page-title biography</title></head><body>
<nav><a href="/causas">Causas judiciales</a></nav>
<header><img src="/sites/default/files/logo-para-banner.png" alt="logo"></header>
<main>
<h1 class="page-header"><span>Persona, Con Retrato</span></h1>
<article class="persona is-promoted full">
  <div class="field field--name-field-fotografia field--type-image">
    <a class="colorbox"><img src="/sites/default/files/styles/ficha_lugares_800px/public/2021-08/retrato-persona.jpg?itok=abc" alt=""></a>
  </div>
  <div class="field field--name-body"><p>Biografía <strong>correcta</strong>.</p><p>Segundo párrafo.</p></div>
  <div class="field field--name-field-victima-de"><p>Víctima de</p><p>Desaparición forzada</p></div>
</article>
<h2>Obras de interés (1)</h2>
<img src="/sites/default/files/styles/medium/public/obra.jpg">
</main></body></html>
"""

# A portrait field that only holds an "access archive" icon: still no portrait.
ICON_ONLY_FIELD_PAGE = """
<html><body>
<main>
<div class="field field--name-field-fotografia">
  <img src="/sites/default/files/inline-images/verarchivo.png">
</div>
<div class="field field--name-body"><p>x</p></div>
</main></body></html>
"""

PAGE_URL = "https://sitiosdememoria.uy/persona"


def test_no_portrait_field_means_no_portrait() -> None:
    assert importer.select_portrait_urls(POSTER_ONLY_PAGE, PAGE_URL) == []


def test_portrait_field_image_is_selected() -> None:
    urls = importer.select_portrait_urls(PORTRAIT_PAGE, PAGE_URL)
    assert urls == [
        "https://sitiosdememoria.uy/sites/default/files/styles/ficha_lugares_800px/"
        "public/2021-08/retrato-persona.jpg?itok=abc"
    ]


def test_portrait_field_with_only_an_icon_is_missing() -> None:
    assert importer.select_portrait_urls(ICON_ONLY_FIELD_PAGE, PAGE_URL) == []


def test_at_most_one_portrait_is_returned() -> None:
    assert len(importer.select_portrait_urls(PORTRAIT_PAGE, PAGE_URL)) <= 1


def test_fields_stop_before_works_section() -> None:
    fields, _bio = importer.extract_fields(POSTER_ONLY_PAGE)
    # "Víctima de" must not slurp the "Obras de interés" / footer text.
    assert fields.get("victim_type") == "Desaparición forzada"
    assert fields.get("date_of_birth") == "1953-07-25"
    assert fields.get("country_of_detention") == "Argentina"
    assert fields.get("date_of_death") == "1975-08-30"
    assert fields.get("place_of_remains_found") == "Playa Blancarena"
    assert fields.get("date_of_identification") == "2011"


def test_biography_is_scoped_to_person_article_body() -> None:
    _fields, bio = importer.extract_fields(PORTRAIT_PAGE)
    assert bio == "Biografía correcta. Segundo párrafo."
    assert "page-title" not in bio


def test_page_without_person_biography_returns_none() -> None:
    _fields, bio = importer.extract_fields(POSTER_ONLY_PAGE)
    assert bio is None


def test_build_record_records_biography_provenance(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(importer, "request_text", lambda _url: PORTRAIT_PAGE)
    args = importer.parse_args(["--repo-root", str(tmp_path)])
    record = importer.build_record({"Nombre": "Persona, Con Retrato"}, args)
    assert record.short_bio == "Biografía correcta. Segundo párrafo."
    assert record.field_sources["short_bio"] == importer.SITIOS_SOURCE_ID


def test_refresh_bios_preserves_curated_data_and_clears_unavailable_bio(
    monkeypatch, tmp_path: Path
) -> None:
    store = tmp_path / "data" / "persons" / "disappeared.json"
    store.parent.mkdir(parents=True)
    store.write_text(
        json.dumps(
            [
                {
                    "id": "persona-con-retrato",
                    "full_name": "Persona, Con Retrato",
                    "source_page": f"{importer.BASE_URL}/persona-con-retrato",
                    "short_bio": "polluted navigation",
                    "notes": "curated note",
                },
                {
                    "id": "sin-pagina",
                    "full_name": "Sin Página",
                    "source_page": importer.LIST_URL,
                    "short_bio": "polluted navigation",
                    "notes": "keep this too",
                },
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(importer, "request_text", lambda _url: PORTRAIT_PAGE)
    args = importer.parse_args(["--repo-root", str(tmp_path), "--sleep", "0"])

    refreshed, empty, errors = importer.refresh_bios(args)

    assert (refreshed, empty, errors) == (1, 1, [])
    payload = json.loads(store.read_text(encoding="utf-8"))
    by_id = {person["id"]: person for person in payload}
    assert by_id["persona-con-retrato"]["short_bio"] == "Biografía correcta. Segundo párrafo."
    assert by_id["persona-con-retrato"]["notes"] == "curated note"
    assert by_id["persona-con-retrato"]["field_sources"]["short_bio"] == importer.SITIOS_SOURCE_ID
    assert by_id["sin-pagina"]["short_bio"] == ""
    assert by_id["sin-pagina"]["notes"] == "keep this too"


def test_refresh_bios_retains_existing_bio_on_fetch_failure(
    monkeypatch, tmp_path: Path
) -> None:
    store = tmp_path / "data" / "persons" / "disappeared.json"
    store.parent.mkdir(parents=True)
    store.write_text(
        json.dumps(
            [
                {
                    "id": "persona",
                    "full_name": "Persona",
                    "source_page": f"{importer.BASE_URL}/persona",
                    "short_bio": "Existing reviewed biography.",
                    "field_sources": {"short_bio": importer.SITIOS_SOURCE_ID},
                }
            ]
        ),
        encoding="utf-8",
    )

    def fail_request(_url: str) -> str:
        raise importer.URLError("temporary failure")

    monkeypatch.setattr(importer, "request_text", fail_request)
    args = importer.parse_args(["--repo-root", str(tmp_path), "--sleep", "0"])
    refreshed, empty, errors = importer.refresh_bios(args)

    assert (refreshed, empty) == (0, 0)
    assert len(errors) == 1
    payload = json.loads(store.read_text(encoding="utf-8"))
    assert payload[0]["short_bio"] == "Existing reviewed biography."
    assert payload[0]["field_sources"]["short_bio"] == importer.SITIOS_SOURCE_ID
