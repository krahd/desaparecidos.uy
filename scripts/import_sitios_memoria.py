#!/usr/bin/env python3
"""Import disappeared-person metadata and target portraits from Sitios de Memoria Uruguay.

This script is intentionally source-specific. It downloads the open Sitios de Memoria
forced-disappearance dataset, enriches rows from individual person pages, downloads
available portrait candidates, and writes repository-ready metadata and manifests.

Outputs are written inside the repository by default:

- data/persons/disappeared.json
- data/persons/disappeared-sitios-de-memoria.csv
- data/manifests/targets.csv
- assets/targets/disappeared/raw/<slug>/...
- assets/targets/disappeared/selected/<slug>.jpg

The script never deletes existing portraits or metadata. Existing files are kept unless
--overwrite is passed. Portraits of disappeared persons are treated as target imagery,
not as crawled source-corpus imagery.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import re
import sys
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from desaparecidos.manifests import TARGET_FIELDS
from desaparecidos.persons import (
    load_persons,
    normalise_person,
    save_persons,
    target_row_from_person,
    utc_now,
)
from desaparecidos.preprocess import preprocess_file

BASE_URL = "https://sitiosdememoria.uy"
LIST_URL = f"{BASE_URL}/desaparicion-forzada"
EXPORT_PAGE_URL = f"{BASE_URL}/exportar-datos"
USER_AGENT = "desaparecidos.uy importer; research/art archival use; contact via repository owner"
# Source id (see data/sources.json) for every field this Sitios-specific importer fills.
SITIOS_SOURCE_ID = "sitios-de-memoria"

FIELD_ALIASES = {
    "Nombre": "given_names",
    "Apellido": "family_names",
    "Fecha de nacimiento": "date_of_birth",
    "Lugar de nacimiento": "place_of_birth",
    "Edad": "age_at_disappearance",
    "Nacionalidad": "nationality",
    "Ocupación": "occupations",
    "Militancia gremial": "union_militancy",
    "Militancia política": "political_militancy",
    "Fecha de secuestro/detención": "date_of_detention",
    "País de secuestro/detención": "country_of_detention",
    "Lugar(es) de detención": "places_of_detention",
    "Fecha de muerte": "date_of_death",
    "Lugar de muerte o desaparición": "place_of_disappearance",
    "País de muerte o desaparición": "country_of_disappearance",
    "Fecha de hallazgo de restos": "date_of_remains_found",
    "Lugar de hallazgo de restos": "place_of_remains_found",
    "Fecha de identificación": "date_of_identification",
    "Víctima de": "victim_type",
}
LIST_FIELD_MAP = {
    "Nombre": "full_name",
    "Nacionalidad": "nationality",
    "Edad": "age_at_disappearance",
    "Militancia política": "political_militancy",
    "Fecha de secuestro": "date_of_detention",
    "Fecha de secuestro/detención": "date_of_detention",
    "Lugar(es) de reclusión": "places_of_detention",
    "Lugar de desaparición": "place_of_disappearance",
    "Lugar de hallazgo de restos": "place_of_remains_found",
}
LIST_LIKE_FIELDS = {
    "nationality",
    "occupations",
    "political_militancy",
    "union_militancy",
    "places_of_detention",
}
DATE_FIELDS = {
    "date_of_birth",
    "date_of_detention",
    "date_of_death",
    "date_of_remains_found",
    "date_of_identification",
}


@dataclass
class ImageCandidate:
    source_url: str
    id: str = "portrait-01"
    source_page: str = ""
    source_id: str = SITIOS_SOURCE_ID
    source_name: str = "Sitios de Memoria Uruguay"
    licence_or_terms: str = "CC BY-SA 4.0; verify per item before public release"
    accessed_at: str | None = None
    raw_path: str | None = None
    processed_path: str | None = None
    sha256: str | None = None
    width: int | None = None
    height: int | None = None
    status: str = "candidate"


@dataclass
class PersonRecord:
    slug: str
    full_name: str
    source_page: str
    fields: dict[str, object] = field(default_factory=dict)
    short_bio: str | None = None
    portrait_candidates: list[ImageCandidate] = field(default_factory=list)
    portrait_status: str = "missing"
    sources: list[str] = field(default_factory=list)
    field_sources: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "slug": self.slug,
            "full_name": self.full_name,
            "source_page": self.source_page,
            "sources": self.sources,
        }
        if self.field_sources:
            data["field_sources"] = self.field_sources
        if self.short_bio:
            data["short_bio"] = self.short_bio
        data.update(self.fields)
        data["portrait_status"] = self.portrait_status
        data["portrait_candidates"] = [candidate.__dict__ for candidate in self.portrait_candidates]
        return data


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            attr = dict(attrs)
            href = attr.get("href")
            if href:
                self._href = href
                self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            text = normalise_space(" ".join(self._text))
            self.links.append((self._href, text))
            self._href = None
            self._text = []


class BiographyParser(HTMLParser):
    """Extract the biography body belonging to the person article only."""

    BLOCK_TAGS = {"br", "div", "li", "p"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._person_article_depth = 0
        self._capture_tag: str | None = None
        self._capture_depth = 0
        self._found_field = False
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        classes = set((dict(attrs).get("class") or "").split())
        if self._person_article_depth:
            if tag == "article":
                self._person_article_depth += 1
            if self._capture_tag is not None and tag == self._capture_tag:
                self._capture_depth += 1
                self._parts.append(" ")
            elif not self._found_field and "field--name-body" in classes:
                self._capture_tag = tag
                self._capture_depth = 1
                self._found_field = True
            elif self._capture_tag is not None and tag in self.BLOCK_TAGS:
                self._parts.append(" ")
        elif tag == "article" and "persona" in classes:
            self._person_article_depth = 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._capture_tag is not None and tag in self.BLOCK_TAGS:
            self._parts.append(" ")
        if self._capture_tag is not None and tag == self._capture_tag:
            self._capture_depth -= 1
            if self._capture_depth == 0:
                self._capture_tag = None
        if self._person_article_depth and tag == "article":
            self._person_article_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._capture_tag is not None:
            self._parts.append(data)

    def biography(self) -> str | None:
        value = normalise_space("".join(self._parts))
        return value or None


# The person portrait on a Sitios de Memoria page lives in a single Drupal
# field container. Anchoring to it is far more reliable than scanning every
# image: works posters, materials, judicial scans, and supporter logos live in
# other containers and must never be treated as the person's face.
PORTRAIT_FIELD_MARKER = "field--name-field-fotografia"

# Field-extraction stops at these heading prefixes so trailing fields (e.g.
# "Víctima de") do not slurp the works/materials/footer text that follows.
FIELD_STOP_PREFIXES = (
    "Obras de interés",
    "Materiales de interés",
    "Causas judiciales",
    "Trayecto de detención",
)
FIELD_STOP_LINES = {"PARTICIPAMOS DE:", "APOYAN:", "PARTICIPAMOS DE", "APOYAN"}

# Non-portrait images that can still appear inside or near the portrait field:
# site logos, licence badges, supporter strips, inline link icons, and the
# "access archive" button.
PORTRAIT_SKIP_TOKENS = (
    "logo",
    "licencia",
    "creative-commons",
    "cc-by",
    "participamos",
    "apoyan",
    "inline-images",
    "accederenlace",
    "verarchivo",
)

_IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_IMG_SRC = re.compile(r"""(?:src|data-src|data-original)\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


def normalise_space(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def slugify(value: str) -> str:
    value = value.lower()
    replacements = str.maketrans("áéíóúüñçàèìòùâêîôûäëïöü", "aeiouuncaeiouaeiouaeiou")
    value = value.translate(replacements)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def request_bytes(url: str, timeout: int = 45) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        return response.read()


def request_text(url: str) -> str:
    raw = request_bytes(url)
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def html_lines(page_html: str) -> list[str]:
    page_html = re.sub(r"(?is)<script.*?</script>", "\n", page_html)
    page_html = re.sub(r"(?is)<style.*?</style>", "\n", page_html)
    text = re.sub(r"(?is)<br\s*/?>", "\n", page_html)
    text = re.sub(r"(?is)</(p|div|li|tr|td|th|h1|h2|h3|h4|section)>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", "\n", text)
    return [normalise_space(line) for line in text.splitlines() if normalise_space(line)]


def extract_biography(page_html: str) -> str | None:
    parser = BiographyParser()
    parser.feed(page_html)
    parser.close()
    return parser.biography()


def parse_export_link() -> str | None:
    parser = LinkParser()
    parser.feed(request_text(EXPORT_PAGE_URL))
    for href, text in parser.links:
        combined = f"{href} {text}".lower()
        if "desaparecid" in combined and "csv" in combined:
            return urljoin(EXPORT_PAGE_URL, href)
    for href, text in parser.links:
        combined = f"{href} {text}".lower()
        if "desaparecid" in combined:
            return urljoin(EXPORT_PAGE_URL, href)
    return None


def parse_csv_records(csv_text: str) -> list[dict[str, str]]:
    sample = csv_text[:2048]
    dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    reader = csv.DictReader(io.StringIO(csv_text), dialect=dialect)
    return [{k.strip(): (v or "").strip() for k, v in row.items() if k} for row in reader]


def load_base_records() -> list[dict[str, str]]:
    export_url = parse_export_link()
    candidates = [url for url in [export_url, f"{BASE_URL}/exportar-datos/desaparecidos"] if url]
    errors: list[str] = []
    for url in candidates:
        try:
            text = request_text(url)
            if "," in text or ";" in text or "\t" in text:
                records = parse_csv_records(text)
                if records:
                    return records
        except (HTTPError, URLError, csv.Error, TimeoutError) as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("Could not download the Sitios de Memoria CSV export. Tried: " + "; ".join(errors or candidates))


def find_person_page(row: dict[str, str]) -> tuple[str, str]:
    for key in ("URL", "Url", "url", "Enlace", "Ficha", "Link"):
        if row.get(key):
            page = urljoin(BASE_URL, row[key])
            return page, urlparse(page).path.strip("/").split("/")[-1]
    full_name = row.get("Nombre") or row.get("nombre") or row.get("full_name") or ""
    slug = slugify(full_name)
    return f"{BASE_URL}/{slug}", slug


def coerce_value(key: str, raw_value: str) -> object:
    value = normalise_space(raw_value)
    if not value:
        return [] if key in LIST_LIKE_FIELDS else None
    if key in LIST_LIKE_FIELDS:
        parts = re.split(r"\s*,\s*|\s*\|\s*|\s*;\s*", value)
        return [part for part in (normalise_space(p) for p in parts) if part]
    if key in DATE_FIELDS:
        return normalise_date(value)
    if key == "age_at_disappearance":
        match = re.search(r"\d+", value)
        return int(match.group(0)) if match else value
    return value


def normalise_date(value: str) -> str:
    value = value.strip()
    match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", value)
    if match:
        day, month, year = match.groups()
        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    match = re.fullmatch(r"(\d{1,2})/(\d{4})", value)
    if match:
        month, year = match.groups()
        return f"{int(year):04d}-{int(month):02d}"
    match = re.fullmatch(r"(\d{4})", value)
    if match:
        return value
    return value


def extract_fields(page_html: str) -> tuple[dict[str, object], str | None]:
    lines = html_lines(page_html)
    fields: dict[str, object] = {}
    labels = set(FIELD_ALIASES)
    for i, line in enumerate(lines):
        if line in labels:
            values: list[str] = []
            for candidate in lines[i + 1 :]:
                if (
                    candidate in labels
                    or candidate.startswith("####")
                    or candidate in FIELD_STOP_LINES
                    or any(candidate.startswith(prefix) for prefix in FIELD_STOP_PREFIXES)
                ):
                    break
                if candidate not in {"Documento", "Image"}:
                    values.append(candidate)
            key = FIELD_ALIASES[line]
            fields[key] = coerce_value(key, " | ".join(values))
    return fields, extract_biography(page_html)


def _portrait_field_region(page_html: str) -> str | None:
    """Return the HTML of the person's ``field-fotografia`` container, or None.

    The region runs from the portrait field marker to the start of the next
    Drupal field block, so image scanning cannot wander into the biography,
    works, or materials content that follows.
    """
    start = page_html.find(PORTRAIT_FIELD_MARKER)
    if start == -1:
        return None
    region = page_html[start : start + 6000]
    nxt = region.find("field--name-", len(PORTRAIT_FIELD_MARKER))
    return region[:nxt] if nxt != -1 else region


def select_portrait_urls(page_html: str, page_url: str) -> list[str]:
    """Return at most the single portrait from the person's ``field-fotografia``.

    Images outside that field (works posters, materials, judicial scans,
    supporter logos, inline link icons) are never considered. When the field is
    absent or empty the result is empty and the caller records
    ``portrait_status="missing"`` rather than importing a poster or document as
    the person's face.
    """
    region = _portrait_field_region(page_html)
    if region is None:
        return []
    for match in _IMG_TAG.finditer(region):
        src = _IMG_SRC.search(match.group(0))
        if not src:
            continue
        url = urljoin(page_url, html.unescape(src.group(1)))
        lower = url.lower()
        if "/sites/default/files/" not in lower:
            continue
        if any(token in lower for token in PORTRAIT_SKIP_TOKENS):
            continue
        return [url]
    return []


def safe_suffix(url: str) -> str:
    path = urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return suffix
    return ".jpg"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_portrait(url: str, raw_dir: Path, name_prefix: str, overwrite: bool) -> tuple[Path, str]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    data = request_bytes(url)
    digest = sha256_bytes(data)
    path = raw_dir / f"{name_prefix}_{digest[:12]}{safe_suffix(url)}"
    if overwrite or not path.exists():
        path.write_bytes(data)
    return path, digest


def process_portrait(raw_path: Path, processed_path: Path, size: tuple[int, int], overwrite: bool) -> tuple[int, int]:
    if processed_path.exists() and not overwrite:
        try:
            from PIL import Image
            with Image.open(processed_path) as img:
                return img.size
        except Exception:
            return size
    width, height = size
    return preprocess_file(
        raw_path,
        processed_path,
        aspect=width / height,
        use_face=True,
        max_side=max(width, height),
    )


def first_nonempty(row: dict[str, str], keys: Iterable[str]) -> str:
    for key in keys:
        if row.get(key):
            return row[key].strip()
    return ""


def build_record(row: dict[str, str], args: argparse.Namespace) -> PersonRecord:
    page_url, slug = find_person_page(row)
    full_name = first_nonempty(row, ["Nombre", "nombre", "full_name", "Persona"])
    if not full_name:
        full_name = slug.replace("-", " ").title()
    page_html = ""
    page_error = ""
    try:
        page_html = request_text(page_url)
    except (HTTPError, URLError, TimeoutError) as exc:
        page_error = str(exc)
    page_fields, bio = extract_fields(page_html) if page_html else ({}, None)
    fields: dict[str, object] = {}
    for source_key, target_key in LIST_FIELD_MAP.items():
        if row.get(source_key):
            fields[target_key] = coerce_value(target_key, row[source_key])
    fields.update({k: v for k, v in page_fields.items() if v not in (None, "", [])})
    if fields.get("given_names") and fields.get("family_names"):
        full_name = f"{fields['given_names']} {fields['family_names']}"
    if page_error:
        fields["notes"] = (
            f"Sitios de Memoria person page unavailable during import: {page_url} "
            f"({page_error}). Metadata and portrait candidate imported from the Sitios export row."
        )
    record = PersonRecord(
        slug=slug,
        full_name=full_name,
        source_page=page_url if page_html else LIST_URL,
        fields=fields,
        short_bio=bio,
        sources=[source for source in [page_url if page_html else "", LIST_URL] if source],
    )
    # Provenance: every metadata field imported here comes from Sitios de Memoria.
    record.field_sources = {key: SITIOS_SOURCE_ID for key in fields}
    if bio:
        record.field_sources["short_bio"] = SITIOS_SOURCE_ID
    # Conservative portrait selection: at most the single header-block portrait,
    # or none at all when the page only carries works/materials imagery.
    portrait_urls = select_portrait_urls(page_html, page_url) if page_html else []
    if not portrait_urls and row.get("Foto"):
        portrait_urls = [urljoin(BASE_URL, row["Foto"])]
    record.portrait_status = "ok" if portrait_urls else "missing"
    if portrait_urls:
        record.field_sources["portrait"] = SITIOS_SOURCE_ID
    if portrait_urls and (args.download_images or args.process_images):
        url = portrait_urls[0]
        candidate = ImageCandidate(source_url=url, source_page=page_url if page_html else LIST_URL)
        try:
            raw_path, digest = download_portrait(url, args.raw_dir / slug, "01", args.overwrite)
            candidate.raw_path = str(raw_path.relative_to(args.repo_root))
            candidate.sha256 = digest
            if args.process_images:
                processed_path = args.processed_dir / f"{slug}.jpg"
                width, height = process_portrait(raw_path, processed_path, args.size, args.overwrite)
                candidate.processed_path = str(processed_path.relative_to(args.repo_root))
                candidate.width = width
                candidate.height = height
        except Exception as exc:  # record failure without aborting whole import
            candidate.status = f"failed: {exc}"
        record.portrait_candidates.append(candidate)
    return record


def write_json(path: Path, records: list[PersonRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [normalise_person(record.as_dict()) for record in records]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_people_csv(path: Path, records: list[PersonRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "slug", "full_name", "date_of_birth", "place_of_birth", "age_at_disappearance",
        "nationality", "occupations", "union_militancy", "political_militancy", "date_of_detention",
        "country_of_detention", "places_of_detention", "date_of_death",
        "country_of_disappearance", "place_of_disappearance",
        "date_of_remains_found", "place_of_remains_found", "victim_type", "source_page", "short_bio",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for record in records:
            row = {key: record.as_dict().get(key, "") for key in columns}
            for key, value in list(row.items()):
                if isinstance(value, list):
                    row[key] = " | ".join(str(item) for item in value)
            writer.writerow(row)


def write_target_manifest(path: Path, records: list[PersonRecord], approved_targets: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    people = [normalise_person(record.as_dict()) for record in records]
    rows = [
        row for person in people
        if (row := target_row_from_person(person, path, approved_targets)) is not None
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TARGET_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def refresh_bios(args: argparse.Namespace) -> tuple[int, int, list[str]]:
    """Refresh only canonical biographies, preserving all other curated fields."""
    people = load_persons(args.people_json)
    refreshed = 0
    empty = 0
    errors: list[str] = []
    for index, person in enumerate(people, start=1):
        person_id = str(person.get("id") or person.get("slug") or "").strip()
        page_url = str(person.get("source_page") or "").strip()

        old_bio = str(person.get("short_bio") or "").strip()
        bio = None
        fetch_failed = False
        if page_url != LIST_URL and page_url.startswith(f"{BASE_URL}/"):
            try:
                bio = extract_biography(request_text(page_url))
            except (HTTPError, URLError, TimeoutError) as exc:
                errors.append(f"{person_id}: {exc}")
                fetch_failed = True
        if fetch_failed:
            print(f"[{index}/{len(people)}] biography retained after fetch failure: {person_id}")
            time.sleep(args.sleep)
            continue

        person["short_bio"] = ""
        field_sources = dict(person.get("field_sources") or {})
        field_sources.pop("short_bio", None)
        person["field_sources"] = field_sources
        field_source_refs = dict(person.get("field_source_refs") or {})
        field_source_refs.pop("short_bio", None)
        person["field_source_refs"] = field_source_refs
        if bio:
            person["short_bio"] = bio
            field_sources["short_bio"] = SITIOS_SOURCE_ID
            refreshed += 1
        else:
            empty += 1
        if old_bio != (bio or ""):
            person["updated_at"] = utc_now()
        print(f"[{index}/{len(people)}] biography {'refreshed' if bio else 'empty'}: {person_id}")
        time.sleep(args.sleep)

    save_persons(args.people_json, people)
    return refreshed, empty, errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--limit", type=int, default=0, help="Limit records for testing. 0 means all records.")
    parser.add_argument("--sleep", type=float, default=0.25, help="Delay between individual page fetches.")
    parser.add_argument("--download-images", action="store_true", help="Download portrait candidates.")
    parser.add_argument("--process-images", action="store_true", help="Create normalised 3:4 processed portrait derivatives with white borders removed.")
    parser.add_argument("--approved-targets", action="store_true", help="Write approved review status for target portraits instead of candidate.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing generated import files.")
    parser.add_argument(
        "--refresh-bios-only",
        action="store_true",
        help="Refresh canonical short_bio fields without replacing other person data.",
    )
    parser.add_argument("--width", type=int, default=900)
    parser.add_argument("--height", type=int, default=1200)
    args = parser.parse_args(argv)
    args.repo_root = args.repo_root.resolve()
    args.people_json = args.repo_root / "data/persons/disappeared.json"
    args.people_csv = args.repo_root / "data/persons/disappeared-sitios-de-memoria.csv"
    args.manifest_csv = args.repo_root / "data/manifests/targets.csv"
    args.raw_dir = args.repo_root / "assets/targets/disappeared/raw"
    args.processed_dir = args.repo_root / "assets/targets/disappeared/selected"
    args.size = (args.width, args.height)
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.refresh_bios_only:
        refreshed, empty, errors = refresh_bios(args)
        print(f"Refreshed biographies: {refreshed}")
        print(f"Empty biographies: {empty}")
        for error in errors:
            print(f"Biography refresh failed: {error}", file=sys.stderr)
        return 1 if errors else 0
    rows = load_base_records()
    if args.limit:
        rows = rows[: args.limit]
    records: list[PersonRecord] = []
    for index, row in enumerate(rows, start=1):
        try:
            record = build_record(row, args)
            records.append(record)
            print(f"[{index}/{len(rows)}] imported {record.full_name} ({record.slug})")
        except Exception as exc:
            name = first_nonempty(row, ["Nombre", "nombre", "Persona"]) or f"row {index}"
            print(f"[{index}/{len(rows)}] failed {name}: {exc}", file=sys.stderr)
        time.sleep(args.sleep)
    write_json(args.people_json, records)
    write_people_csv(args.people_csv, records)
    write_target_manifest(args.manifest_csv, records, args.approved_targets)
    print(f"Wrote {len(records)} person records")
    print(args.people_json)
    print(args.people_csv)
    print(args.manifest_csv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
