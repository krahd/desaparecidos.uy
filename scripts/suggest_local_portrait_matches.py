#!/usr/bin/env python3
"""Suggest review-only portrait candidates from the local tracked portrait corpus.

The local ``doc/fotos-desaparecidos`` images are useful for improving target
portrait quality, but their own manifest marks identity and provenance as
pending review. This script therefore never selects a portrait automatically.
It ranks plausible name matches and can optionally append them as non-selected
``portrait_candidates`` for later GUI review.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from PIL import Image

from desaparecidos.persons import (
    DEFAULT_PERSON_STORE,
    PROJECT_ROOT,
    clean_text,
    load_persons,
    save_persons,
    slugify,
    today,
    utc_now,
)

DEFAULT_LOCAL_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "local-targets.csv"
DEFAULT_LOCAL_SOURCE = PROJECT_ROOT / "doc" / "fotos-desaparecidos"
SOURCE_ID = "local-fotos-desaparecidos"
SOURCE_NAME = "Local tracked fotos-desaparecidos portrait corpus"
SOURCE_PAGE = "doc/fotos-desaparecidos"

STOP_TOKENS = {
    "da",
    "das",
    "de",
    "del",
    "do",
    "dos",
    "e",
    "el",
    "la",
    "las",
    "le",
    "los",
    "van",
    "von",
    "y",
}
MIN_TOKEN_SIMILARITY = 0.84


def normalise_text(value: object) -> str:
    text = clean_text(value)
    text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def tokens(value: object) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for token in normalise_text(value).split():
        if len(token) < 2 or token in STOP_TOKENS or token in seen:
            continue
        seen.add(token)
        result.append(token)
    return result


def _derive_family_given(person: dict[str, Any]) -> tuple[list[str], list[str]]:
    family = tokens(person.get("family_names"))
    given = tokens(person.get("given_names"))
    if family or given:
        return family, given
    full_name = clean_text(person.get("full_name"))
    if "," in full_name:
        left, right = full_name.split(",", 1)
        return tokens(left), tokens(right)
    parts = tokens(full_name)
    return parts[:1], parts[1:]


def token_similarity(left: str, right: str) -> float:
    if left == right:
        return 1.0
    if len(left) >= 4 and len(right) >= 4 and left.rstrip("s") == right.rstrip("s"):
        return 0.96
    if min(len(left), len(right)) < 4:
        return 0.0
    ratio = SequenceMatcher(a=left, b=right).ratio()
    return ratio if ratio >= MIN_TOKEN_SIMILARITY else 0.0


def match_token_sets(candidate_tokens: list[str], person_tokens: list[str]) -> dict[str, Any]:
    used_person: set[int] = set()
    matches: list[dict[str, Any]] = []
    for candidate in candidate_tokens:
        best_index = -1
        best_score = 0.0
        best_token = ""
        for index, person_token in enumerate(person_tokens):
            if index in used_person:
                continue
            score = token_similarity(candidate, person_token)
            if score > best_score:
                best_index = index
                best_score = score
                best_token = person_token
        if best_index >= 0 and best_score > 0:
            used_person.add(best_index)
            matches.append(
                {
                    "candidate": candidate,
                    "person": best_token,
                    "similarity": round(best_score, 3),
                }
            )
    matched_candidates = {match["candidate"] for match in matches}
    matched_person = {match["person"] for match in matches}
    return {
        "matches": matches,
        "matched_candidate_tokens": matched_candidates,
        "matched_person_tokens": matched_person,
    }


def score_match(person: dict[str, Any], row: dict[str, str]) -> dict[str, Any]:
    candidate_tokens = tokens(row.get("name") or row.get("id"))
    person_tokens = tokens(
        " ".join(
            [
                clean_text(person.get("full_name")),
                clean_text(person.get("given_names")),
                clean_text(person.get("family_names")),
            ]
        )
    )
    family_tokens, given_tokens = _derive_family_given(person)
    if not candidate_tokens or not person_tokens:
        return {"score": 0.0, "matches": [], "reasons": ["missing-name-tokens"]}
    matches = match_token_sets(candidate_tokens, person_tokens)
    matched_candidate = matches["matched_candidate_tokens"]
    matched_person = matches["matched_person_tokens"]
    candidate_coverage = len(matched_candidate) / len(candidate_tokens)
    person_coverage = len(matched_person) / len(person_tokens)
    score = (0.72 * candidate_coverage) + (0.28 * person_coverage)

    family_match = bool(match_token_sets(candidate_tokens, family_tokens)["matches"]) if family_tokens else True
    given_match = bool(match_token_sets(candidate_tokens, given_tokens)["matches"]) if given_tokens else True
    reasons: list[str] = []
    if family_match:
        reasons.append("family-name-overlap")
    else:
        score *= 0.45
        reasons.append("no-family-name-overlap")
    if given_match:
        reasons.append("given-name-overlap")
    elif len(candidate_tokens) > 1:
        score *= 0.78
        reasons.append("no-given-name-overlap")
    if len(matched_candidate) < 2 and row.get("id") != person.get("id"):
        score *= 0.65
        reasons.append("single-token-overlap")
    if row.get("id") == person.get("id"):
        score = 1.0
        reasons.append("exact-id-match")
    return {
        "score": round(min(score, 1.0), 3),
        "candidate_tokens": candidate_tokens,
        "person_tokens": person_tokens,
        "matches": matches["matches"],
        "reasons": reasons,
    }


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def local_image_path(row: dict[str, str], source_dir: Path) -> Path | None:
    source_url = clean_text(row.get("source_url"))
    if source_url.startswith("local://fotos-desaparecidos/"):
        parsed = urlparse(source_url)
        filename = unquote(parsed.path.lstrip("/"))
        path = source_dir / filename
        return path if path.exists() else None
    raw = clean_text(row.get("local_path"))
    if raw:
        path = Path(raw)
        if not path.is_absolute():
            path = path.resolve()
        return path if path.exists() else None
    return None


def image_metadata(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    with Image.open(path) as image:
        width, height = image.size
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "width": width,
        "height": height,
    }


def existing_candidate_keys(person: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for candidate in person.get("portrait_candidates") or []:
        for key in ("source_url", "raw_path", "sha256"):
            value = clean_text(candidate.get(key))
            if value:
                keys.add(f"{key}:{value}")
    return keys


def candidate_from_suggestion(suggestion: dict[str, Any]) -> dict[str, Any]:
    row = suggestion["manifest_row"]
    image_path = suggestion["image_path"]
    metadata = suggestion["image_metadata"]
    candidate_id = f"{SOURCE_ID}-{slugify(Path(image_path).stem)[:42]}"
    reasons = ", ".join(suggestion["match"]["reasons"])
    return {
        "id": candidate_id,
        "source_url": clean_text(row.get("source_url")),
        "source_page": SOURCE_PAGE,
        "source_id": SOURCE_ID,
        "source_name": SOURCE_NAME,
        "licence_or_terms": clean_text(row.get("licence_or_terms")) or "unknown - pending provenance review",
        "accessed_at": clean_text(row.get("accessed_at")) or today(),
        "raw_path": image_path,
        "processed_path": "",
        "sha256": metadata["sha256"],
        "width": metadata["width"],
        "height": metadata["height"],
        "status": "candidate",
        "confidence": f"local-name-match:{suggestion['match']['score']:.3f}",
        "notes": (
            "Review-only candidate from local tracked portrait corpus; "
            "identity and provenance must be confirmed before selection. "
            f"Match reasons: {reasons}."
        ),
    }


def collect_suggestions(
    *,
    persons_path: Path = DEFAULT_PERSON_STORE,
    manifest_path: Path = DEFAULT_LOCAL_MANIFEST,
    source_dir: Path = DEFAULT_LOCAL_SOURCE,
    min_score: float = 0.82,
    only_portrait_gaps: bool = False,
) -> list[dict[str, Any]]:
    people = load_persons(persons_path)
    rows = read_manifest(manifest_path)
    suggestions: list[dict[str, Any]] = []
    for person in people:
        if only_portrait_gaps and person.get("selected_portrait_id"):
            continue
        existing = existing_candidate_keys(person)
        for row in rows:
            match = score_match(person, row)
            if match["score"] < min_score:
                continue
            image_path = local_image_path(row, source_dir)
            if image_path is None:
                continue
            metadata = image_metadata(image_path)
            source_url = clean_text(row.get("source_url"))
            rel_image = str(image_path.relative_to(PROJECT_ROOT)) if image_path.is_relative_to(PROJECT_ROOT) else str(image_path)
            if (
                f"source_url:{source_url}" in existing
                or f"raw_path:{rel_image}" in existing
                or f"sha256:{metadata['sha256']}" in existing
            ):
                continue
            suggestions.append(
                {
                    "person_id": person["id"],
                    "full_name": person["full_name"],
                    "current_portrait_status": person.get("portrait_status"),
                    "selected_portrait_id": person.get("selected_portrait_id"),
                    "manifest_id": row.get("id"),
                    "manifest_name": row.get("name"),
                    "source_url": source_url,
                    "image_path": rel_image,
                    "image_metadata": metadata,
                    "match": match,
                    "manifest_row": row,
                }
            )
    suggestions.sort(key=lambda item: (-item["match"]["score"], item["full_name"], item["manifest_name"]))
    return suggestions


def apply_suggestions(persons_path: Path, suggestions: list[dict[str, Any]]) -> dict[str, Any]:
    people = load_persons(persons_path)
    by_id = {person["id"]: person for person in people}
    added = 0
    for suggestion in suggestions:
        person = by_id.get(suggestion["person_id"])
        if person is None:
            continue
        candidate = candidate_from_suggestion(suggestion)
        existing = existing_candidate_keys(person)
        if (
            f"source_url:{candidate['source_url']}" in existing
            or f"raw_path:{candidate['raw_path']}" in existing
            or f"sha256:{candidate['sha256']}" in existing
        ):
            continue
        candidate_ids = {clean_text(item.get("id")) for item in person.get("portrait_candidates") or []}
        base_id = candidate["id"]
        suffix = 2
        while candidate["id"] in candidate_ids:
            candidate["id"] = f"{base_id}-{suffix}"
            suffix += 1
        person["portrait_candidates"] = [*list(person.get("portrait_candidates") or []), candidate]
        if person.get("portrait_status") == "missing":
            person["portrait_status"] = "candidate"
        person["updated_at"] = utc_now()
        added += 1
    if added:
        save_persons(persons_path, people)
    return {"ok": True, "added": added, "suggestions_seen": len(suggestions)}


def public_suggestion(suggestion: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in suggestion.items()
        if key not in {"manifest_row"}
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--persons", type=Path, default=DEFAULT_PERSON_STORE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_LOCAL_MANIFEST)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_LOCAL_SOURCE)
    parser.add_argument("--min-score", type=float, default=0.82)
    parser.add_argument("--only-portrait-gaps", action="store_true")
    parser.add_argument("--write", action="store_true", help="append suggestions as review-only portrait candidates")
    parser.add_argument("--json", action="store_true", help="write machine-readable JSON to stdout")
    parser.add_argument("--limit", type=int, default=0, help="limit suggestions printed; 0 means all")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    suggestions = collect_suggestions(
        persons_path=args.persons,
        manifest_path=args.manifest,
        source_dir=args.source_dir,
        min_score=args.min_score,
        only_portrait_gaps=args.only_portrait_gaps,
    )
    result = {"ok": True, "suggestions": len(suggestions), "added": 0}
    if args.write:
        result.update(apply_suggestions(args.persons, suggestions))
    shown = suggestions[: args.limit] if args.limit > 0 else suggestions
    payload = {**result, "items": [public_suggestion(item) for item in shown], "items_shown": len(shown)}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Suggestions: {result['suggestions']}")
        if args.write:
            print(f"Added candidates: {result['added']}")
        for item in shown:
            print(
                f"{item['person_id']} | {item['full_name']} | "
                f"{item['manifest_name']} | score {item['match']['score']:.3f} | {item['image_path']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
