#!/usr/bin/env python3
"""Apply the project CV category gates before internal source approval."""

from __future__ import annotations

import argparse
import json

from desaparecidos.source_quality import quality_pass_source_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--kind", choices=("people", "places"), required=True)
    parser.add_argument(
        "--include-approved",
        action="store_true",
        help="recheck already approved rows as well as pending rows",
    )
    args = parser.parse_args()
    statuses = {"pending", "approved"} if args.include_approved else {"pending"}
    summary = quality_pass_source_manifest(args.manifest, args.kind, statuses=statuses)
    print(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
