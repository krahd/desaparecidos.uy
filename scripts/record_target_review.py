from __future__ import annotations

import argparse

from desaparecidos.paths import safe_project_path
from desaparecidos.persons import record_target_review


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record an explicit human historical-identification or target-rights review."
    )
    parser.add_argument("person_id")
    parser.add_argument(
        "kind",
        choices=["historical-identification", "rights"],
    )
    parser.add_argument("status", choices=["pending", "approved", "rejected"])
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--reviewed-at", default="")
    parser.add_argument("--store", default="data/persons/disappeared.json")
    args = parser.parse_args()

    person = record_target_review(
        safe_project_path(args.store),
        args.person_id,
        args.kind,
        args.status,
        reviewer=args.reviewer,
        reviewed_at=args.reviewed_at,
    )
    print(f"{person['id']}: {args.kind}={args.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
