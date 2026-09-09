#!/usr/bin/env python3
"""Import quality-gated Uruguay traversal frames into the place dataset."""

from __future__ import annotations

import argparse
import json

from desaparecidos.source_quality import import_traversal_places


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--traversal-root", default="data/raw/traversals")
    parser.add_argument("--manifest", default="data/manifests/crawled-places.csv")
    parser.add_argument("--route-id", action="append")
    args = parser.parse_args()
    result = import_traversal_places(
        args.traversal_root,
        args.manifest,
        route_ids=args.route_id,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
