#!/usr/bin/env python3
"""Apply authoritative portrait overrides after importing the disappeared-person corpus.

This script is intended to run after scripts/import_sitios_memoria.py. It reads a
small CSV of explicit portrait overrides, downloads each referenced image, creates a
normalised processed derivative, and patches the generated person JSON and target
manifest. Overrides replace existing portrait candidates for the matching slug,
which is useful when the primary site contains a poster or work image rather than a
portrait.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from desaparecidos.manifests import TARGET_FIELDS
from desaparecidos.preprocess import preprocess_file

USER_AGENT = "desaparecidos.uy portrait override importer; research/art archival use"


def request_bytes(url: str, timeout: int = 45) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        return response.read()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_suffix(url: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"


def clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def source_id_for(row: dict[str, str]) -> str:
    """Source registry id (see data/sources.json) for an override row.

    Uses an explicit ``source_id`` column when present, otherwise slugifies the
    human ``source_name`` (e.g. "Parque de la Memoria" -> "parque-de-la-memoria").
    """
    explicit = clean_text(row.get("source_id"))
    if explicit:
        return explicit
    name = clean_text(row.get("source_name"))
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def download_image(url: str, raw_dir: Path, overwrite: bool) -> tuple[Path, str]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    data = request_bytes(url)
    digest = sha256_bytes(data)
    path = raw_dir / f"override_{digest[:12]}{safe_suffix(url)}"
    if overwrite or not path.exists():
        path.write_bytes(data)
    return path, digest


def process_portrait(raw_path: Path, processed_path: Path, size: tuple[int, int], overwrite: bool) -> tuple[int, int]:
    if processed_path.exists() and not overwrite:
        from PIL import Image
        with Image.open(processed_path) as img:
            return img.size
    width, height = size
    return preprocess_file(
        raw_path,
        processed_path,
        aspect=width / height,
        use_face=True,
        max_side=max(width, height),
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def patch_people_json(path: Path, slug: str, candidate: dict[str, object], source_id: str) -> None:
    if not path.exists():
        return
    people = json.loads(path.read_text(encoding="utf-8"))
    for person in people:
        if person.get("slug") == slug:
            person["portrait_candidates"] = [candidate]
            person["portrait_status"] = "ok"
            person["selected_portrait_id"] = candidate.get("id") or "portrait-01"
            field_sources = dict(person.get("field_sources") or {})
            if source_id:
                field_sources["portrait"] = source_id
            person["field_sources"] = field_sources
            sources = list(person.get("sources") or [])
            source_page = candidate.get("source_page")
            if source_page and source_page not in sources:
                sources.append(source_page)
            person["sources"] = sources
            break
    path.write_text(json.dumps(people, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_manifest(path: Path, row: dict[str, str], candidate: dict[str, object]) -> None:
    fieldnames = TARGET_FIELDS
    rows = read_csv(path) if path.exists() else []
    rows = [
        existing for existing in rows
        if existing.get("id") != row["person_slug"] and existing.get("person_slug") != row["person_slug"]
    ]
    processed_path = clean_text(candidate.get("processed_path"))
    rel_local = processed_path
    if processed_path:
        local = Path(processed_path)
        if not local.is_absolute():
            local = Path.cwd() / local
        rel_local = os.path.relpath(local.resolve(), path.resolve().parent)
    review_status = clean_text(row.get("review_status")) or "pending"
    if review_status == "candidate":
        review_status = "pending"
    rows.append({
        "id": row["person_slug"],
        "name": row["full_name"],
        "source_url": row["image_url"],
        "source_page": row["source_page"],
        "licence_or_terms": row.get("licence", ""),
        "accessed_at": "",
        "local_path": rel_local,
        "review_status": review_status,
        "birth_date": "",
        "disappearance_date": "",
        "disappearance_place": "",
        "notes": row.get("notes", ""),
    })
    write_csv(path, rows, fieldnames)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--overrides", type=Path, default=Path("data/manifests/portrait-overrides.csv"))
    parser.add_argument("--people-json", type=Path, default=Path("data/persons/disappeared.json"))
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/targets.csv"))
    parser.add_argument("--raw-dir", type=Path, default=Path("assets/targets/disappeared/raw"))
    parser.add_argument("--processed-dir", type=Path, default=Path("assets/targets/disappeared/selected"))
    parser.add_argument("--width", type=int, default=900)
    parser.add_argument("--height", type=int, default=1200)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.repo_root.resolve()
    overrides_path = root / args.overrides
    people_json = root / args.people_json
    manifest = root / args.manifest
    raw_root = root / args.raw_dir
    processed_root = root / args.processed_dir
    size = (args.width, args.height)

    for row in read_csv(overrides_path):
        slug = clean_text(row.get("person_slug"))
        image_url = clean_text(row.get("image_url"))
        if not slug or not image_url:
            continue
        raw_path, digest = download_image(image_url, raw_root / slug, args.overwrite)
        processed_path = processed_root / f"{slug}.jpg"
        width, height = process_portrait(raw_path, processed_path, size, args.overwrite)
        candidate = {
            "id": "portrait-01",
            "source_url": image_url,
            "source_page": clean_text(row.get("source_page")),
            "source_name": clean_text(row.get("source_name")),
            "raw_path": str(raw_path.relative_to(root)),
            "processed_path": str(processed_path.relative_to(root)),
            "sha256": digest,
            "width": width,
            "height": height,
            "status": clean_text(row.get("review_status")) or "candidate",
            "notes": clean_text(row.get("notes")),
        }
        source_id = source_id_for(row)
        candidate["source_id"] = source_id
        patch_people_json(people_json, slug, candidate, source_id)
        patch_manifest(manifest, row, candidate)
        print(f"applied portrait override: {slug} (source {source_id or 'unknown'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
