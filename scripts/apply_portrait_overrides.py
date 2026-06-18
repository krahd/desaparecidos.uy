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
import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

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
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise RuntimeError("Pillow is required. Install with: python -m pip install Pillow") from exc
    with Image.open(raw_path) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        gray = ImageOps.grayscale(img)
        mask = gray.point(lambda p: 255 if p < 245 else 0)
        bbox = mask.getbbox()
        if bbox:
            pad = 10
            left, top, right, bottom = bbox
            img = img.crop((max(0, left - pad), max(0, top - pad), min(img.width, right + pad), min(img.height, bottom + pad)))
        target_w, target_h = size
        target_ratio = target_w / target_h
        ratio = img.width / img.height
        if ratio > target_ratio:
            new_h = int(round(img.width / target_ratio))
            canvas = Image.new("RGB", (img.width, new_h), "white")
            canvas.paste(img, (0, (new_h - img.height) // 2))
            img = canvas
        elif ratio < target_ratio:
            new_w = int(round(img.height * target_ratio))
            canvas = Image.new("RGB", (new_w, img.height), "white")
            canvas.paste(img, ((new_w - img.width) // 2, 0))
            img = canvas
        img = img.resize(size, Image.Resampling.LANCZOS)
        processed_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(processed_path)
        return img.size


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


def patch_people_json(path: Path, slug: str, candidate: dict[str, object]) -> None:
    if not path.exists():
        return
    people = json.loads(path.read_text(encoding="utf-8"))
    for person in people:
        if person.get("slug") == slug:
            person["portrait_candidates"] = [candidate]
            sources = list(person.get("sources") or [])
            source_page = candidate.get("source_page")
            if source_page and source_page not in sources:
                sources.append(source_page)
            person["sources"] = sources
            break
    path.write_text(json.dumps(people, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_manifest(path: Path, row: dict[str, str], candidate: dict[str, object]) -> None:
    fieldnames = [
        "target_id", "person_slug", "full_name", "image_path", "raw_image_path", "source_url",
        "source_page", "licence", "review_status", "date_of_birth", "date_of_disappearance", "notes",
    ]
    rows = read_csv(path) if path.exists() else []
    rows = [existing for existing in rows if existing.get("person_slug") != row["person_slug"]]
    rows.append({
        "target_id": f"{row['person_slug']}-override-01",
        "person_slug": row["person_slug"],
        "full_name": row["full_name"],
        "image_path": str(candidate.get("processed_path") or ""),
        "raw_image_path": str(candidate.get("raw_path") or ""),
        "source_url": row["image_url"],
        "source_page": row["source_page"],
        "licence": row.get("licence", ""),
        "review_status": row.get("review_status") or "candidate",
        "date_of_birth": "",
        "date_of_disappearance": "",
        "notes": row.get("notes", ""),
    })
    write_csv(path, rows, fieldnames)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--overrides", type=Path, default=Path("data/manifests/portrait-overrides.csv"))
    parser.add_argument("--people-json", type=Path, default=Path("data/persons/disappeared-sitios-de-memoria.json"))
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/targets-sitios-de-memoria.csv"))
    parser.add_argument("--raw-dir", type=Path, default=Path("assets/targets/disappeared/raw"))
    parser.add_argument("--processed-dir", type=Path, default=Path("assets/targets/disappeared/processed"))
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=1500)
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
        processed_path = processed_root / f"{slug}.png"
        width, height = process_portrait(raw_path, processed_path, size, args.overwrite)
        candidate = {
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
        patch_people_json(people_json, slug, candidate)
        patch_manifest(manifest, row, candidate)
        print(f"applied portrait override: {slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
