#!/usr/bin/env python3
"""Apply reviewed metadata overrides to the canonical disappeared-person store."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from desaparecidos.persons import (
    DEFAULT_PERSON_STORE,
    DEFAULT_SOURCE_REGISTRY,
    clean_text,
    load_persons,
    load_sources_registry,
    save_persons,
    utc_now,
)

DEFAULT_OVERRIDES = Path("data/persons/metadata-overrides.csv")
BOOLEAN_TRUE = {"1", "true", "yes", "y"}


def truthy(value: object) -> bool:
    return clean_text(value).casefold() in BOOLEAN_TRUE


def read_overrides(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            {key: clean_text(value) for key, value in row.items() if key}
            for row in csv.DictReader(handle)
        ]


def known_source_ids(path: Path) -> set[str]:
    registry = load_sources_registry(path)
    return {
        clean_text(source.get("id"))
        for source in registry.get("sources", [])
        if isinstance(source, dict) and clean_text(source.get("id"))
    }


def apply_overrides(
    people: list[dict[str, Any]],
    overrides: list[dict[str, str]],
    *,
    source_ids: set[str],
    allow_overwrite: bool = False,
) -> dict[str, Any]:
    by_id = {person["id"]: person for person in people}
    applied: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    errors: list[str] = []

    for index, row in enumerate(overrides, start=2):
        person_id = clean_text(row.get("id"))
        field = clean_text(row.get("field"))
        value = clean_text(row.get("value"))
        source_id = clean_text(row.get("source_id"))
        overwrite = allow_overwrite or truthy(row.get("overwrite"))

        if not person_id or not field or not value:
            errors.append(f"line {index}: id, field, and value are required")
            continue
        if source_id and source_id not in source_ids:
            errors.append(f"line {index}: unknown source_id {source_id!r}")
            continue
        person = by_id.get(person_id)
        if person is None:
            errors.append(f"line {index}: unknown person id {person_id!r}")
            continue

        current = clean_text(person.get(field))
        if current and current != value and not overwrite:
            skipped.append({"id": person_id, "field": field, "reason": "existing-value"})
            continue

        person[field] = value
        if source_id:
            field_sources = dict(person.get("field_sources") or {})
            field_sources[field] = source_id
            person["field_sources"] = field_sources
        source_ref = clean_text(row.get("source_ref"))
        if source_ref:
            refs = dict(person.get("field_source_refs") or {})
            refs[field] = source_ref
            person["field_source_refs"] = refs
        source_page = clean_text(row.get("source_page"))
        if source_page:
            sources = set(person.get("sources") or [])
            sources.add(source_page)
            person["sources"] = sorted(sources)
        note = clean_text(row.get("notes"))
        if note:
            notes = clean_text(person.get("notes"))
            marker = f"Metadata override ({field}): {note}"
            if marker not in notes:
                person["notes"] = f"{notes} {marker}".strip()
        person["updated_at"] = utc_now()
        applied.append({"id": person_id, "field": field, "value": value})

    return {"applied": applied, "skipped": skipped, "errors": errors}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--persons", type=Path, default=DEFAULT_PERSON_STORE)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCE_REGISTRY)
    parser.add_argument("--write", action="store_true", help="write changes; otherwise only report")
    parser.add_argument("--allow-overwrite", action="store_true", help="allow overriding existing non-empty values")
    parser.add_argument("--json", action="store_true", help="print JSON summary")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    people = load_persons(args.persons)
    result = apply_overrides(
        people,
        read_overrides(args.overrides),
        source_ids=known_source_ids(args.sources),
        allow_overwrite=args.allow_overwrite,
    )
    if args.write and not result["errors"]:
        save_persons(args.persons, people)
    payload = {**result, "written": bool(args.write and not result["errors"])}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Applied: {len(result['applied'])}")
        print(f"Skipped: {len(result['skipped'])}")
        print(f"Errors: {len(result['errors'])}")
        if not payload["written"]:
            print("Written: no")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
