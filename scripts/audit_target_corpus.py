#!/usr/bin/env python3
"""Audit the disappeared-person target corpus for curation gaps."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from desaparecidos.persons import (
    DEFAULT_PERSON_STORE,
    load_persons,
    missing_fields,
    portrait_review_summary,
)


def build_audit(
    path: Path,
    *,
    missing_field: str = "",
    portrait_gaps_only: bool = False,
    portrait_review_only: bool = False,
    limit: int = 0,
) -> dict[str, Any]:
    people = load_persons(path)
    missing_by_field: Counter[str] = Counter()
    portrait_sources: Counter[str] = Counter()
    portrait_statuses: Counter[str] = Counter()
    unresolved: list[dict[str, Any]] = []
    unresolved_total = 0
    total_candidates = 0
    records_with_candidates = 0
    portrait_review_count = 0
    for person in people:
        fields = missing_fields(person)
        portrait_review = portrait_review_summary(person)
        if portrait_review["needs_review"]:
            portrait_review_count += 1
        candidates = list(person.get("portrait_candidates") or [])
        total_candidates += len(candidates)
        if candidates:
            records_with_candidates += 1
        missing_by_field.update(fields)
        portrait_source = (person.get("field_sources") or {}).get("portrait") or "missing"
        portrait_sources[portrait_source] += 1
        portrait_statuses[person.get("portrait_status") or "missing"] += 1
        has_gap = bool(fields or person.get("portrait_status") != "ok")
        if has_gap:
            unresolved_total += 1
        should_consider = has_gap or (portrait_review_only and portrait_review["needs_review"])
        if should_consider:
            should_show = True
            if missing_field and missing_field not in fields:
                should_show = False
            if portrait_gaps_only and "selected_portrait" not in fields and person.get("portrait_status") == "ok":
                should_show = False
            if portrait_review_only and not portrait_review["needs_review"]:
                should_show = False
            if should_show:
                unresolved.append(
                    {
                        "id": person["id"],
                        "full_name": person["full_name"],
                        "missing_fields": fields,
                        "portrait_status": person.get("portrait_status"),
                        "portrait_source": portrait_source,
                        "portrait_candidate_count": len(candidates),
                        "portrait_review": portrait_review,
                        "notes": person.get("notes") or "",
                    }
                )
    shown_unresolved = unresolved[:limit] if limit > 0 else unresolved
    return {
        "persons_path": str(path),
        "total_records": len(people),
        "complete_records": len(people) - unresolved_total,
        "records_with_gaps": unresolved_total,
        "selected_portraits": sum(1 for person in people if person.get("selected_portrait_id")),
        "portrait_candidates": total_candidates,
        "records_with_portrait_candidates": records_with_candidates,
        "records_without_portrait_candidates": len(people) - records_with_candidates,
        "portrait_review_count": portrait_review_count,
        "portrait_statuses": dict(sorted(portrait_statuses.items())),
        "portrait_sources": dict(sorted(portrait_sources.items())),
        "missing_by_field": dict(sorted(missing_by_field.items())),
        "unresolved_records_shown": len(shown_unresolved),
        "unresolved_records": shown_unresolved,
    }


def print_text(audit: dict[str, Any]) -> None:
    print(f"Records: {audit['total_records']}")
    print(f"Selected portraits: {audit['selected_portraits']}")
    print(f"Portrait candidates: {audit['portrait_candidates']}")
    print(f"Records with portrait candidates: {audit['records_with_portrait_candidates']}")
    print(f"Records needing portrait review: {audit['portrait_review_count']}")
    print(f"Records with gaps: {audit['records_with_gaps']}")
    print(f"Complete records: {audit['complete_records']}")
    print("Portrait statuses:")
    for status, count in audit["portrait_statuses"].items():
        print(f"  {status}: {count}")
    print("Portrait sources:")
    for source, count in audit["portrait_sources"].items():
        print(f"  {source}: {count}")
    print("Missing fields:")
    for field, count in audit["missing_by_field"].items():
        print(f"  {field}: {count}")
    print("Unresolved records:")
    for record in audit["unresolved_records"]:
        missing = ", ".join(record["missing_fields"]) or "none"
        review = record.get("portrait_review") or {}
        review_reason = f" | portrait: {review.get('reason')}" if review.get("needs_review") else ""
        print(f"  {record['id']} | {record['full_name']} | missing: {missing}{review_reason}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--persons", type=Path, default=DEFAULT_PERSON_STORE)
    parser.add_argument("--json", action="store_true", help="write machine-readable audit JSON to stdout")
    parser.add_argument("--missing-field", default="", help="only list unresolved records missing this field")
    parser.add_argument("--portrait-gaps-only", action="store_true", help="only list records with portrait gaps")
    parser.add_argument("--portrait-review-only", action="store_true", help="only list records needing portrait candidate review")
    parser.add_argument("--limit", type=int, default=0, help="limit unresolved records shown; 0 means no limit")
    parser.add_argument("--fail-on-gaps", action="store_true", help="exit non-zero when any curation gaps remain")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_audit(
        args.persons,
        missing_field=args.missing_field,
        portrait_gaps_only=args.portrait_gaps_only,
        portrait_review_only=args.portrait_review_only,
        limit=args.limit,
    )
    if args.json:
        print(json.dumps(audit, ensure_ascii=False, indent=2))
    else:
        print_text(audit)
    return 1 if args.fail_on_gaps and audit["records_with_gaps"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
