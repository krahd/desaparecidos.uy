#!/usr/bin/env python3
"""Acquire raster files from Wikimedia Commons categories."""

from __future__ import annotations

import argparse
import json

from desaparecidos.crawl import crawl_mediawiki_categories


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("people", "places"), required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--category", action="append", required=True)
    parser.add_argument("--label-prefix", default="Wikimedia Commons")
    parser.add_argument("--output-root", default="data/raw/crawl")
    parser.add_argument("--max-category-depth", type=int, default=2)
    parser.add_argument("--max-categories", type=int, default=500)
    parser.add_argument("--max-files", type=int, default=5000)
    parser.add_argument("--max-images", type=int, default=1000)
    parser.add_argument("--thumbnail-width", type=int, default=960)
    parser.add_argument("--delay", type=float, default=0.1)
    args = parser.parse_args()
    summary = crawl_mediawiki_categories(
        args.category,
        args.kind,
        args.manifest,
        output_root=args.output_root,
        label_prefix=args.label_prefix,
        max_category_depth=args.max_category_depth,
        max_categories=args.max_categories,
        max_files=args.max_files,
        max_images=args.max_images,
        thumbnail_width=args.thumbnail_width,
        delay=args.delay,
    )
    result = summary.to_api()
    result.pop("items", None)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary.added else 1


if __name__ == "__main__":
    raise SystemExit(main())
