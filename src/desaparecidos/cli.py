from __future__ import annotations

import argparse
import json
from pathlib import Path

import uvicorn

from .api import create_app
from .download import download_manifest
from .manifests import validate_manifest
from .outputs import list_outputs
from .pipeline import DEFAULT_MAX_CONTRIBUTION_PER_SOURCE, Stage1Settings, run_stage1


def _print_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="desaparecidos")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate target and source manifests.")
    validate.add_argument("--targets", default="data/manifests/targets.csv")
    validate.add_argument("--sources", default="data/manifests/places.csv")
    validate.add_argument("--people", default="data/manifests/people.csv")
    validate.add_argument("--require-files", action="store_true")

    download = subparsers.add_parser("download", help="Download URLs listed in a manifest.")
    download.add_argument("--manifest", required=True)
    download.add_argument("--kind", choices=["targets", "places", "people"], required=True)
    download.add_argument("--output-root", default="data/raw")

    run = subparsers.add_parser("run-stage1", help="Run Stage 1 reconstruction.")
    run.add_argument("--targets", default="data/manifests/targets.csv")
    run.add_argument("--sources", default="data/manifests/places.csv")
    run.add_argument("--output", default="outputs/stage1")
    run.add_argument("--seed", type=int, default=17)
    run.add_argument("--fragment-size", type=int, default=24)
    run.add_argument("--reuse-limit", type=int, default=8)
    run.add_argument("--output-width", type=int, default=720)
    run.add_argument(
        "--max-contribution-per-source",
        type=int,
        default=DEFAULT_MAX_CONTRIBUTION_PER_SOURCE,
        help=(
            "maximum output tiles any single source image may contribute; "
            "use 0 for unlimited"
        ),
    )
    run.add_argument("--search-scan-frames-per-candidate", type=int, default=2)
    run.add_argument("--search-scan-max-candidates", type=int, default=120)
    run.add_argument("--target-id")
    run.add_argument("--video", action="store_true")

    outputs = subparsers.add_parser("outputs", help="List generated outputs.")
    outputs.add_argument("--output", default="outputs/stage1")

    serve = subparsers.add_parser("serve", help="Serve the localhost API.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        targets = validate_manifest(args.targets, "targets", require_files=args.require_files)
        sources = validate_manifest(args.sources, "places", require_files=args.require_files)
        people = validate_manifest(args.people, "people", require_files=args.require_files)
        _print_json({
            "ok": targets.ok and sources.ok and people.ok,
            "targets": targets.to_api(),
            "sources": sources.to_api(),
            "people": people.to_api(),
        })
        return 0 if targets.ok and sources.ok and people.ok else 1

    if args.command == "download":
        summary = download_manifest(args.manifest, args.kind, output_root=args.output_root)
        _print_json(summary.to_api())
        return 0 if summary.ok else 1

    if args.command == "run-stage1":
        settings = Stage1Settings(
            seed=args.seed,
            fragment_size=args.fragment_size,
            reuse_limit=args.reuse_limit,
            output_width=args.output_width,
            max_contribution_per_source=args.max_contribution_per_source,
            search_scan_frames_per_candidate=args.search_scan_frames_per_candidate,
            search_scan_max_candidates=args.search_scan_max_candidates,
            make_video=args.video,
        )
        outputs = run_stage1(
            args.targets,
            args.sources,
            args.output,
            settings,
            target_id=args.target_id,
        )
        _print_json({"ok": True, "outputs": [output.__dict__ for output in outputs]})
        return 0

    if args.command == "outputs":
        _print_json({"items": list_outputs(args.output)})
        return 0

    if args.command == "serve":
        uvicorn.run(create_app(), host=args.host, port=args.port)
        return 0

    parser.error(f"unknown command {args.command}")
    return 2
