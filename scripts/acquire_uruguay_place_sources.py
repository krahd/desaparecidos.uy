#!/usr/bin/env python3
"""Discover and acquire a bounded, quality-gated Uruguay traversal corpus."""

from __future__ import annotations

import argparse
import json

from desaparecidos.traversals import acquire_traversal, discover_traversal


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="Están en todas partes source acquisition")
    parser.add_argument("--root", default="data/raw/traversals")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--regions", type=int, default=12)
    parser.add_argument("--max-frames", type=int, default=600)
    parser.add_argument("--rural-probability", type=float, default=0.45)
    args = parser.parse_args()
    traversal = discover_traversal(
        name=args.name,
        mode="autonomous",
        duration_seconds=max(1, args.max_frames // 2),
        root=args.root,
        max_frames=args.max_frames,
        regions=args.regions,
        scope="uruguay",
        rural_probability=args.rural_probability,
        seed=args.seed,
    )
    acquired = acquire_traversal(
        traversal["id"],
        root=args.root,
        max_frames=args.max_frames,
        auto_approve=True,
    )
    print(json.dumps({
        "id": acquired["id"],
        "places": acquired.get("places", []),
        "walks": acquired.get("walks", []),
        "acquisition": acquired.get("acquisition", {}),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
