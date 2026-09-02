from __future__ import annotations

import argparse
from pathlib import Path

from desaparecidos.refusal_paradata import (
    DEFAULT_REFUSAL_PARADATA_PATH,
    load_refusal_paradata,
    render_refusal_paradata,
    sha256_file,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and render desaparecidos.uy refusal paradata as curatorial Markdown."
    )
    parser.add_argument("--policy", type=Path, default=DEFAULT_REFUSAL_PARADATA_PATH)
    parser.add_argument("--access", choices=["public", "restricted"], default="public")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    policy = load_refusal_paradata(args.policy)
    rendered = render_refusal_paradata(
        policy,
        access=args.access,
        policy_sha256=sha256_file(args.policy),
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
