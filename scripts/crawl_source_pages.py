#!/usr/bin/env python3
"""Run a bounded provenance-preserving crawl into a source manifest."""

from __future__ import annotations

import argparse
import json

from desaparecidos.crawl import crawl_pages


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=("people", "places"), required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--page", action="append", required=True)
    parser.add_argument("--label-prefix", default="Crawled image")
    parser.add_argument("--output-root", default="data/raw/crawl")
    parser.add_argument("--max-images-per-page", type=int, default=50)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--max-pages", type=int, default=300)
    parser.add_argument("--max-images", type=int, default=1000)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument(
        "--image-host",
        action="append",
        help="accept candidate image URLs only from this exact host",
    )
    parser.add_argument(
        "--pagination-only",
        action="store_true",
        help="follow only next/previous links for the same category page",
    )
    args = parser.parse_args()
    summary = crawl_pages(
        args.page,
        args.kind,
        args.manifest,
        output_root=args.output_root,
        label_prefix=args.label_prefix,
        max_images_per_page=args.max_images_per_page,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
        max_images=args.max_images,
        cross_domain=False,
        delay=args.delay,
        respect_robots=True,
        use_cv=True,
        image_hosts=set(args.image_host or ()),
        pagination_only=args.pagination_only,
    )
    result = summary.to_api()
    result.pop("items", None)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary.added else 1


if __name__ == "__main__":
    raise SystemExit(main())
