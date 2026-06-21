"""Build a Stage 1 targets manifest from a local directory of portrait images.

This reads a folder of portrait files (for example ``doc/fotos-desaparecidos``)
and writes a targets CSV that the GUI can validate and review. Every row is
written with ``review_status=pending``: nothing is approved automatically, so
the manual review gate still decides what may participate in generation.

Provenance fields that are not known from the local files are recorded as
explicitly unknown rather than invented. Output defaults to an ignored
``data/manifests/local-*.csv`` path so a manifest of real people is not
committed.

Usage:

    python scripts/build_targets_manifest.py
    python scripts/build_targets_manifest.py --source doc/fotos-desaparecidos \
        --output data/manifests/local-targets.csv \
        --processed-root data/processed/targets
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import os
import re
import unicodedata
from pathlib import Path

from desaparecidos.manifests import TARGET_FIELDS
from desaparecidos.paths import PROJECT_ROOT, display_path
from desaparecidos.preprocess import parse_aspect, preprocess_file

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}

# Filenames that are not individual portraits in the source collection:
# numbered book-page scans (``NNNFPMFUDD``/``0.jpg``), untitled exports,
# duplicates, and the places image. The review gate is the final filter, but
# excluding these keeps the manifest focused on portraits.
_EXCLUDE_STEM_PATTERNS = (
    re.compile(r"^\d+$"),
    re.compile(r"\d*FPMFUDD", re.IGNORECASE),
    re.compile(r"^sin\s*t[ií]tulo", re.IGNORECASE),
    re.compile(r"\b(copy|copia)\b", re.IGNORECASE),
)
_EXCLUDE_STEMS = {"logares", "lugares"}

_IMPORT_NOTE = "Imported from doc/fotos-desaparecidos; identity and provenance pending review."

# Trailing per-person image index, e.g. "Altmann - Blanca 1" -> "Altmann - Blanca".
_TRAILING_INDEX = re.compile(r"\s*\d+\s*$")
# Stray qualifiers seen in the collection.
_NOISE_TOKENS = re.compile(r"\b(internet|copia|copy)\b", re.IGNORECASE)
# Source filenames separate family and given names with " - "; the rest of the
# app uses the "Family, Given" convention, so normalise the dash to a comma.
_NAME_SEPARATOR = re.compile(r"\s+-\s+")


def is_portrait(path: Path) -> bool:
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        return False
    stem = path.stem.strip()
    if stem.lower() in _EXCLUDE_STEMS:
        return False
    return not any(pattern.search(stem) for pattern in _EXCLUDE_STEM_PATTERNS)


def display_name(stem: str) -> str:
    """Tidy a filename stem into a label without reordering the recorded name."""
    name = _NOISE_TOKENS.sub(" ", stem)
    name = _TRAILING_INDEX.sub("", name)
    name = _NAME_SEPARATOR.sub(", ", name)
    name = re.sub(r"\s+", " ", name).strip(" -,")
    return name or stem.strip()


def slugify(value: str) -> str:
    ascii_value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    return slug or "target"


def build_rows(
    source_dir: Path,
    manifest_path: Path,
    *,
    preprocess: bool = True,
    processed_root: Path | None = None,
    aspect: float = 3 / 4,
    use_face: bool = True,
    max_side: int = 1200,
) -> list[dict[str, str]]:
    manifest_parent = manifest_path.resolve().parent
    if preprocess:
        processed_root = processed_root or PROJECT_ROOT / "data" / "processed" / "targets"
    portraits = sorted(
        (path for path in source_dir.iterdir() if path.is_file() and is_portrait(path)),
        key=lambda path: path.name.lower(),
    )

    rows: list[dict[str, str]] = []
    used_ids: set[str] = set()
    for path in portraits:
        label = display_name(path.stem)
        base_id = slugify(label)
        row_id = base_id
        suffix = 2
        while row_id in used_ids:
            row_id = f"{base_id}-{suffix}"
            suffix += 1
        used_ids.add(row_id)

        local_path = path
        note = _IMPORT_NOTE
        if preprocess:
            assert processed_root is not None
            processed_path = processed_root / f"{row_id}{path.suffix.lower()}"
            width, height = preprocess_file(
                path,
                processed_path,
                aspect=aspect,
                use_face=use_face,
                max_side=max_side,
            )
            local_path = processed_path
            note = (
                f"{_IMPORT_NOTE} Processed copy auto-trimmed white border/caption margin "
                f"and cropped to aspect {aspect:.4f} ({width}x{height}); "
                f"original file: {display_path(path)}."
            )

        rel_local = os.path.relpath(local_path.resolve(), manifest_parent)
        accessed_at = _dt.date.fromtimestamp(path.stat().st_mtime).isoformat()

        row = {field: "" for field in TARGET_FIELDS}
        row.update(
            {
                "id": row_id,
                "name": label,
                "source_url": f"local://fotos-desaparecidos/{path.name}",
                "source_page": "doc/fotos-desaparecidos",
                "licence_or_terms": "unknown - pending provenance review",
                "accessed_at": accessed_at,
                "local_path": rel_local,
                "review_status": "pending",
                "notes": note,
            }
        )
        rows.append(row)
    return rows


def write_manifest(rows: list[dict[str, str]], manifest_path: Path) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TARGET_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default="doc/fotos-desaparecidos",
        help="Directory of portrait images (default: doc/fotos-desaparecidos).",
    )
    parser.add_argument(
        "--output",
        default="data/manifests/local-targets.csv",
        help="Manifest path to write (default: data/manifests/local-targets.csv).",
    )
    parser.add_argument(
        "--processed-root",
        default="data/processed/targets",
        help="Directory for processed portrait copies (default: data/processed/targets).",
    )
    parser.add_argument(
        "--aspect",
        default="3:4",
        help='Target portrait aspect ratio as width:height or decimal (default: "3:4").',
    )
    parser.add_argument(
        "--max-side",
        type=int,
        default=1200,
        help="Resize processed portraits so the longest side is at most this many pixels.",
    )
    parser.add_argument(
        "--no-preprocess",
        action="store_true",
        help="Write manifest rows pointing at original files instead of processed copies.",
    )
    parser.add_argument(
        "--no-face-centre",
        action="store_true",
        help="Do not use face detection to centre the crop inside the trimmed image.",
    )
    args = parser.parse_args()

    source_dir = Path(args.source)
    if not source_dir.is_absolute():
        source_dir = PROJECT_ROOT / source_dir
    if not source_dir.is_dir():
        raise SystemExit(f"source directory does not exist: {source_dir}")

    manifest_path = Path(args.output)
    if not manifest_path.is_absolute():
        manifest_path = PROJECT_ROOT / manifest_path

    processed_root = Path(args.processed_root)
    if not processed_root.is_absolute():
        processed_root = PROJECT_ROOT / processed_root

    rows = build_rows(
        source_dir,
        manifest_path,
        preprocess=not args.no_preprocess,
        processed_root=processed_root,
        aspect=parse_aspect(args.aspect),
        use_face=not args.no_face_centre,
        max_side=args.max_side,
    )
    write_manifest(rows, manifest_path)
    mode = (
        f"processed copies in {display_path(processed_root)}"
        if not args.no_preprocess
        else "original files"
    )
    print(
        f"Wrote {len(rows)} pending target row(s) from {display_path(source_dir)} "
        f"to {display_path(manifest_path)} using {mode}."
    )


if __name__ == "__main__":
    main()
