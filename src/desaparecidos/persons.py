from __future__ import annotations

import csv
import datetime as dt
import hashlib
import html
import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .manifests import TARGET_FIELDS
from .paths import PROJECT_ROOT, display_path
from .preprocess import preprocess_file

DEFAULT_PERSON_STORE = PROJECT_ROOT / "data" / "persons" / "disappeared.json"
DEFAULT_RAW_ROOT = PROJECT_ROOT / "assets" / "targets" / "disappeared" / "raw"
DEFAULT_SELECTED_ROOT = PROJECT_ROOT / "assets" / "targets" / "disappeared" / "selected"
DEFAULT_TARGET_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "targets.csv"
DEFAULT_SOURCE_REGISTRY = PROJECT_ROOT / "data" / "sources.json"

USER_AGENT = "desaparecidos.uy target corpus curation; research/art archival use"
PERSON_REVIEW_STATUSES = {"pending", "approved", "rejected"}
REMAINS_STATUSES = {"found", "not_found", "unknown"}
REQUIRED_PERSON_FIELDS = (
    "full_name",
    "date_of_birth",
    "place_of_birth",
    "date_of_disappearance",
    "place_of_disappearance",
    "remains_status",
    "selected_portrait",
)


def slugify(value: str) -> str:
    ascii_value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    return slug or "person"


def today() -> str:
    return dt.date.today().isoformat()


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clean_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def ensure_list(value: object) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [clean_text(item) for item in value if clean_text(item)]
    return [clean_text(value)]


def infer_remains_status(record: dict[str, Any]) -> str:
    explicit = clean_text(record.get("remains_status")).lower()
    if explicit in REMAINS_STATUSES:
        return explicit
    if clean_text(record.get("date_of_remains_found")) or clean_text(record.get("place_of_remains_found")):
        return "found"
    return "unknown"


def normalise_portrait_candidate(
    raw: dict[str, Any],
    *,
    person_id: str,
    index: int,
) -> dict[str, Any]:
    candidate_id = clean_text(raw.get("id")) or f"portrait-{index:02d}"
    source_url = clean_text(raw.get("source_url") or raw.get("image_url"))
    source_page = clean_text(raw.get("source_page"))
    candidate = {
        "id": candidate_id,
        "source_url": source_url,
        "source_page": source_page,
        "source_id": clean_text(raw.get("source_id")),
        "source_name": clean_text(raw.get("source_name")),
        "licence_or_terms": clean_text(raw.get("licence_or_terms") or raw.get("licence")),
        "accessed_at": clean_text(raw.get("accessed_at")) or today(),
        "raw_path": clean_text(raw.get("raw_path")),
        "processed_path": clean_text(raw.get("processed_path")),
        "sha256": clean_text(raw.get("sha256")),
        "width": raw.get("width") or "",
        "height": raw.get("height") or "",
        "status": clean_text(raw.get("status")) or "candidate",
        "confidence": clean_text(raw.get("confidence")),
        "notes": clean_text(raw.get("notes")),
    }
    if not candidate["source_page"]:
        candidate["source_page"] = candidate["source_url"]
    if not candidate["id"]:
        candidate["id"] = f"{person_id}-portrait-{index:02d}"
    return candidate


def selected_candidate(person: dict[str, Any]) -> dict[str, Any] | None:
    candidates = list(person.get("portrait_candidates") or [])
    selected_id = clean_text(person.get("selected_portrait_id"))
    if selected_id:
        for candidate in candidates:
            if candidate.get("id") == selected_id:
                return candidate
    for candidate in candidates:
        if candidate.get("processed_path") or candidate.get("raw_path"):
            return candidate
    return None


def missing_fields(person: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in REQUIRED_PERSON_FIELDS:
        if field == "selected_portrait":
            candidate = selected_candidate(person)
            if candidate is None or not candidate.get("processed_path"):
                missing.append(field)
            continue
        value = clean_text(person.get(field))
        if not value or (field == "remains_status" and value == "unknown"):
            missing.append(field)
    return missing


def normalise_person(raw: dict[str, Any]) -> dict[str, Any]:
    full_name = clean_text(raw.get("full_name") or raw.get("name"))
    person_id = clean_text(raw.get("id") or raw.get("slug") or slugify(full_name))
    if not full_name:
        full_name = person_id.replace("-", " ").title()
    slug = clean_text(raw.get("slug")) or person_id
    date_of_disappearance = clean_text(
        raw.get("date_of_disappearance") or raw.get("date_of_detention")
    )
    candidates = [
        normalise_portrait_candidate(candidate, person_id=person_id, index=index)
        for index, candidate in enumerate(raw.get("portrait_candidates") or [], start=1)
        if isinstance(candidate, dict)
    ]
    selected_id = clean_text(raw.get("selected_portrait_id"))
    if not selected_id:
        for candidate in candidates:
            if candidate.get("processed_path") or candidate.get("raw_path"):
                selected_id = candidate["id"]
                break
    review_status = clean_text(raw.get("review_status")).lower() or "pending"
    if review_status not in PERSON_REVIEW_STATUSES:
        review_status = "pending"
    person = {
        "id": person_id,
        "slug": slug,
        "full_name": full_name,
        "given_names": clean_text(raw.get("given_names")),
        "family_names": clean_text(raw.get("family_names")),
        "date_of_birth": clean_text(raw.get("date_of_birth")),
        "place_of_birth": clean_text(raw.get("place_of_birth")),
        "date_of_disappearance": date_of_disappearance,
        "date_of_detention": clean_text(raw.get("date_of_detention")),
        "place_of_disappearance": clean_text(raw.get("place_of_disappearance")),
        "country_of_disappearance": clean_text(raw.get("country_of_disappearance")),
        "places_of_detention": ensure_list(raw.get("places_of_detention")),
        "remains_status": infer_remains_status(raw),
        "date_of_remains_found": clean_text(raw.get("date_of_remains_found")),
        "place_of_remains_found": clean_text(raw.get("place_of_remains_found")),
        "short_bio": clean_text(raw.get("short_bio")),
        "notes": clean_text(raw.get("notes")),
        "source_page": clean_text(raw.get("source_page")),
        "sources": ensure_list(raw.get("sources")),
        "field_sources": dict(raw.get("field_sources") or {}),
        "portrait_status": clean_text(raw.get("portrait_status")) or ("ok" if candidates else "missing"),
        "portrait_candidates": candidates,
        "selected_portrait_id": selected_id,
        "review_status": review_status,
        "created_at": clean_text(raw.get("created_at")) or utc_now(),
        "updated_at": clean_text(raw.get("updated_at")) or utc_now(),
    }
    person["missing_fields"] = missing_fields(person)
    return person


def load_persons(path: str | Path = DEFAULT_PERSON_STORE) -> list[dict[str, Any]]:
    store_path = Path(path)
    if not store_path.exists():
        return []
    payload = json.loads(store_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{store_path} must contain a JSON array")
    people = [normalise_person(item) for item in payload if isinstance(item, dict)]
    return sorted(people, key=lambda item: item["full_name"].casefold())


def save_persons(path: str | Path, people: list[dict[str, Any]]) -> list[dict[str, Any]]:
    store_path = Path(path)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    normalised = [normalise_person(person) for person in people]
    normalised = sorted(normalised, key=lambda item: item["full_name"].casefold())
    store_path.write_text(
        json.dumps(normalised, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return normalised


def person_to_api(person: dict[str, Any]) -> dict[str, Any]:
    candidate = selected_candidate(person)
    api_person = dict(person)
    api_person["missing_fields"] = missing_fields(person)
    api_person["selected_portrait"] = candidate
    return api_person


def person_summary(people: list[dict[str, Any]]) -> dict[str, Any]:
    missing = [person for person in people if missing_fields(person)]
    weak_portraits = [
        person for person in people
        if "selected_portrait" in missing_fields(person) or person.get("portrait_status") != "ok"
    ]
    return {
        "count": len(people),
        "missing_count": len(missing),
        "weak_portrait_count": len(weak_portraits),
        "approved_count": sum(1 for person in people if person.get("review_status") == "approved"),
    }


def load_sources_registry(path: str | Path = DEFAULT_SOURCE_REGISTRY) -> dict[str, Any]:
    registry_path = Path(path)
    if not registry_path.exists():
        return {"description": "", "sources": []}
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{registry_path} must contain a JSON object")
    return payload


def list_persons_api(path: str | Path = DEFAULT_PERSON_STORE) -> dict[str, Any]:
    people = load_persons(path)
    return {
        "ok": True,
        "path": display_path(path),
        "summary": person_summary(people),
        "required_fields": list(REQUIRED_PERSON_FIELDS),
        "people": [person_to_api(person) for person in people],
    }


def upsert_person(path: str | Path, person: dict[str, Any]) -> dict[str, Any]:
    people = load_persons(path)
    incoming = normalise_person({**person, "updated_at": utc_now()})
    updated = False
    for index, current in enumerate(people):
        if current["id"] == incoming["id"]:
            incoming["created_at"] = current.get("created_at") or incoming["created_at"]
            people[index] = incoming
            updated = True
            break
    if not updated:
        people.append(incoming)
    saved = save_persons(path, people)
    return person_to_api(next(item for item in saved if item["id"] == incoming["id"]))


def get_person(path: str | Path, person_id: str) -> dict[str, Any]:
    for person in load_persons(path):
        if person["id"] == person_id:
            return person_to_api(person)
    raise ValueError(f"person not found: {person_id}")


def delete_person(path: str | Path, person_id: str) -> dict[str, Any]:
    people = load_persons(path)
    kept = [person for person in people if person["id"] != person_id]
    if len(kept) == len(people):
        raise ValueError(f"person not found: {person_id}")
    saved = save_persons(path, kept)
    return {"ok": True, "summary": person_summary(saved)}


def safe_suffix(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def request_bytes(url: str, timeout: int = 45) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("portrait URL must use http or https")
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        return response.read()


def add_portrait_candidate(
    path: str | Path,
    person_id: str,
    *,
    image_url: str,
    source_page: str = "",
    source_id: str = "",
    source_name: str = "",
    licence_or_terms: str = "",
    notes: str = "",
    raw_root: str | Path = DEFAULT_RAW_ROOT,
    overwrite: bool = False,
) -> dict[str, Any]:
    people = load_persons(path)
    for person in people:
        if person["id"] == person_id:
            data = request_bytes(image_url)
            digest = sha256_bytes(data)
            raw_dir = Path(raw_root) / person_id
            raw_dir.mkdir(parents=True, exist_ok=True)
            raw_path = raw_dir / f"candidate_{digest[:12]}{safe_suffix(image_url)}"
            if overwrite or not raw_path.exists():
                raw_path.write_bytes(data)
            candidate = {
                "id": f"portrait-{len(person.get('portrait_candidates') or []) + 1:02d}",
                "source_url": image_url,
                "source_page": source_page or image_url,
                "source_id": source_id,
                "source_name": source_name,
                "licence_or_terms": licence_or_terms,
                "accessed_at": today(),
                "raw_path": display_path(raw_path),
                "processed_path": "",
                "sha256": digest,
                "width": "",
                "height": "",
                "status": "candidate",
                "confidence": "web-candidate",
                "notes": notes,
            }
            person["portrait_candidates"] = [*list(person.get("portrait_candidates") or []), candidate]
            person["portrait_status"] = "candidate"
            person["updated_at"] = utc_now()
            saved = save_persons(path, people)
            return person_to_api(next(item for item in saved if item["id"] == person_id))
    raise ValueError(f"person not found: {person_id}")


def process_selected_portrait(
    path: str | Path,
    person_id: str,
    candidate_id: str,
    *,
    selected_root: str | Path = DEFAULT_SELECTED_ROOT,
    aspect: float = 3 / 4,
    use_face: bool = True,
    max_side: int = 1200,
    overwrite: bool = True,
) -> dict[str, Any]:
    people = load_persons(path)
    for person in people:
        if person["id"] != person_id:
            continue
        for candidate in person.get("portrait_candidates") or []:
            if candidate.get("id") != candidate_id:
                continue
            source_path = candidate.get("raw_path") or candidate.get("processed_path")
            if not source_path:
                raise ValueError(f"portrait candidate has no local file: {candidate_id}")
            source = PROJECT_ROOT / source_path if not Path(source_path).is_absolute() else Path(source_path)
            if not source.exists():
                raise ValueError(f"portrait candidate file does not exist: {source_path}")
            suffix = ".jpg" if source.suffix.lower() in {".jpg", ".jpeg", ".webp"} else ".png"
            dst = Path(selected_root) / f"{person_id}{suffix}"
            if overwrite or not dst.exists():
                width, height = preprocess_file(
                    source,
                    dst,
                    aspect=aspect,
                    use_face=use_face,
                    max_side=max_side,
                )
            else:
                from PIL import Image

                with Image.open(dst) as image:
                    width, height = image.size
            candidate["processed_path"] = display_path(dst)
            candidate["width"] = width
            candidate["height"] = height
            candidate["status"] = "selected"
            person["selected_portrait_id"] = candidate_id
            person["portrait_status"] = "ok"
            if candidate.get("source_id"):
                person["field_sources"] = {
                    **dict(person.get("field_sources") or {}),
                    "portrait": candidate["source_id"],
                }
            sources = set(ensure_list(person.get("sources")))
            if candidate.get("source_page"):
                sources.add(candidate["source_page"])
            if candidate.get("source_url"):
                sources.add(candidate["source_url"])
            person["sources"] = sorted(sources)
            person["updated_at"] = utc_now()
            saved = save_persons(path, people)
            return person_to_api(next(item for item in saved if item["id"] == person_id))
        raise ValueError(f"portrait candidate not found: {candidate_id}")
    raise ValueError(f"person not found: {person_id}")


def set_selected_portrait(path: str | Path, person_id: str, candidate_id: str) -> dict[str, Any]:
    people = load_persons(path)
    for person in people:
        if person["id"] != person_id:
            continue
        if not any(candidate.get("id") == candidate_id for candidate in person.get("portrait_candidates") or []):
            raise ValueError(f"portrait candidate not found: {candidate_id}")
        person["selected_portrait_id"] = candidate_id
        person["updated_at"] = utc_now()
        saved = save_persons(path, people)
        return person_to_api(next(item for item in saved if item["id"] == person_id))
    raise ValueError(f"person not found: {person_id}")


def source_search_links(person: dict[str, Any]) -> list[dict[str, str]]:
    name = html.escape(person["full_name"], quote=True)
    query = re.sub(r"\s+", "+", person["full_name"].strip())
    return [
        {
            "label": "Madres y Familiares",
            "source_id": "madres-familiares",
            "url": f"https://www.google.com/search?q=site%3Adesaparecidos.org.uy+{query}",
        },
        {
            "label": "Parque de la Memoria",
            "source_id": "parque-de-la-memoria",
            "url": f"https://www.google.com/search?q=site%3Abasededatos.parquedelamemoria.org.ar+{query}",
        },
        {
            "label": "General image search",
            "source_id": "web-search",
            "url": f"https://www.google.com/search?tbm=isch&q={query}+desaparecido+Uruguay",
        },
        {
            "label": f"Copy query for {name}",
            "source_id": "web-search",
            "url": f"{person['full_name']} desaparecido Uruguay retrato",
        },
    ]


def search_plan(path: str | Path) -> dict[str, Any]:
    people = load_persons(path)
    needs_work = [
        person for person in people
        if missing_fields(person) or person.get("portrait_status") != "ok"
    ]
    return {
        "ok": True,
        "path": display_path(path),
        "count": len(needs_work),
        "items": [
            {
                "id": person["id"],
                "full_name": person["full_name"],
                "missing_fields": missing_fields(person),
                "portrait_status": person.get("portrait_status"),
                "links": source_search_links(person),
            }
            for person in needs_work
        ],
    }


def target_row_from_person(person: dict[str, Any], manifest_path: Path, approved: bool) -> dict[str, str] | None:
    candidate = selected_candidate(person)
    if not candidate:
        return None
    image_path = clean_text(candidate.get("processed_path"))
    if not image_path:
        return None
    local_path = Path(image_path)
    if not local_path.is_absolute():
        local_path = PROJECT_ROOT / local_path
    try:
        rel_local = os.path.relpath(local_path.resolve(), manifest_path.resolve().parent)
    except ValueError:
        rel_local = str(local_path)
    row = {field: "" for field in TARGET_FIELDS}
    row.update(
        {
            "id": person["id"],
            "name": person["full_name"],
            "source_url": clean_text(candidate.get("source_url")),
            "source_page": clean_text(candidate.get("source_page") or person.get("source_page")),
            "licence_or_terms": clean_text(candidate.get("licence_or_terms"))
            or "verify before public release",
            "accessed_at": clean_text(candidate.get("accessed_at")) or today(),
            "local_path": rel_local,
            "review_status": "approved" if approved else "pending",
            "birth_date": clean_text(person.get("date_of_birth")),
            "disappearance_date": clean_text(
                person.get("date_of_disappearance") or person.get("date_of_detention")
            ),
            "disappearance_place": clean_text(person.get("place_of_disappearance")),
            "notes": (
                "Derived from canonical disappeared-person store; "
                "target portrait is historical reference material, not source-corpus imagery."
            ),
        }
    )
    return row


def export_targets_manifest(
    persons_path: str | Path = DEFAULT_PERSON_STORE,
    manifest_path: str | Path = DEFAULT_TARGET_MANIFEST,
    *,
    approved: bool = False,
) -> dict[str, Any]:
    people = load_persons(persons_path)
    output = Path(manifest_path)
    rows = [
        row for person in people
        if (row := target_row_from_person(person, output, approved)) is not None
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TARGET_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return {
        "ok": True,
        "manifest": display_path(output),
        "rows_written": len(rows),
        "people_seen": len(people),
        "skipped": len(people) - len(rows),
    }
