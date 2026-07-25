from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from desaparecidos.paths import display_path, safe_project_path
from desaparecidos.pipeline import Stage1Settings, run_stage1
from desaparecidos.traversals import TraversalRenderSettings, render_traversal


def _load_plan(path: Path) -> dict[str, Any]:
    plan = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "target_manifest",
        "people_manifest",
        "places_manifest",
        "traversal_id",
        "traversal_root",
        "target_ids",
        "output_dir",
    }
    missing = sorted(required - set(plan))
    if missing:
        raise ValueError(f"render plan is missing: {', '.join(missing)}")
    if not isinstance(plan["target_ids"], list) or not plan["target_ids"]:
        raise ValueError("render plan target_ids must be a non-empty list")
    return plan


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _concat_mp4(inputs: list[Path], output: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg with libx264 is required for exhibition rendering")
    if not inputs:
        raise ValueError("no videos were generated")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as handle:
        list_path = Path(handle.name)
        for item in inputs:
            escaped = str(item.resolve()).replace("'", "'\\''")
            handle.write(f"file '{escaped}'\n")
    try:
        command = [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output),
        ]
        subprocess.run(command, check=True)
    finally:
        list_path.unlink(missing_ok=True)


def _fragment_loop(
    *,
    artwork: str,
    target_manifest: Path,
    source_manifest: Path,
    target_ids: list[str],
    output_root: Path,
    settings: Stage1Settings,
) -> tuple[Path, list[dict[str, Any]]]:
    segment_dir = output_root / "segments" / artwork
    segment_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    videos: list[Path] = []
    for target_id in target_ids:
        generated = run_stage1(
            target_manifest,
            source_manifest,
            segment_dir,
            settings,
            target_id=target_id,
            artwork=artwork,  # type: ignore[arg-type]
        )[0]
        if not generated.video_path:
            raise RuntimeError(f"{artwork} did not produce a video for {target_id}")
        video = safe_project_path(generated.video_path)
        videos.append(video)
        records.append(
            {
                "target_id": target_id,
                "video": display_path(video),
                "sidecar": generated.sidecar_path,
            }
        )
    loop = output_root / f"{artwork}.mp4"
    _concat_mp4(videos, loop)
    return loop, records


def render(plan: dict[str, Any], *, allow_internal_people_render: bool) -> Path:
    if not allow_internal_people_render:
        raise ValueError(
            "Todos somos familiares remains an internal render until its complete source and output review. "
            "Pass --allow-internal-people-render only for a controlled internal export."
        )

    target_manifest = safe_project_path(plan["target_manifest"])
    people_manifest = safe_project_path(plan["people_manifest"])
    places_manifest = safe_project_path(plan["places_manifest"])
    traversal_root = safe_project_path(plan["traversal_root"])
    output_root = safe_project_path(plan["output_dir"])
    output_root.mkdir(parents=True, exist_ok=True)
    target_ids = [str(value) for value in plan["target_ids"]]
    seed = int(plan.get("seed", 17))
    fragment_size = int(plan.get("fragment_size", 24))
    output_width = int(plan.get("output_width", 1920))

    people_settings = Stage1Settings(
        seed=seed,
        fragment_size=fragment_size,
        reuse_limit=int(plan.get("people_reuse_limit", 8)),
        output_width=output_width,
        max_contribution_per_source=int(plan.get("people_source_cap", 1)),
        video_source_layout=str(plan.get("people_source_layout", "match")),  # type: ignore[arg-type]
        visual_grammar=str(plan.get("people_visual_grammar", "irregular")),  # type: ignore[arg-type]
        target_salience="portrait",
        avoid_source_adjacency=bool(plan.get("avoid_people_source_adjacency", True)),
        make_video=True,
    )
    places_settings = Stage1Settings(
        seed=seed,
        fragment_size=fragment_size,
        reuse_limit=int(plan.get("places_reuse_limit", 8)),
        output_width=output_width,
        max_contribution_per_source=int(plan.get("places_source_cap", 1)),
        video_source_layout=str(plan.get("places_source_layout", "match")),  # type: ignore[arg-type]
        visual_grammar=str(plan.get("places_visual_grammar", "overlap")),  # type: ignore[arg-type]
        target_salience="portrait",
        make_video=True,
    )

    people_loop, people_segments = _fragment_loop(
        artwork="todos-somos-familiares",
        target_manifest=target_manifest,
        source_manifest=people_manifest,
        target_ids=target_ids,
        output_root=output_root,
        settings=people_settings,
    )
    places_loop, places_segments = _fragment_loop(
        artwork="estan-en-todas-partes",
        target_manifest=target_manifest,
        source_manifest=places_manifest,
        target_ids=target_ids,
        output_root=output_root,
        settings=places_settings,
    )

    traversal_settings = TraversalRenderSettings(
        composition=str(plan.get("traversal_composition", "overlay")),  # type: ignore[arg-type]
        target_mode="sequence",
        duration_seconds=int(plan.get("traversal_duration_seconds", 180)),
        fps=int(plan.get("fps", 24)),
        seed=seed,
        fragment_size=fragment_size,
        output_width=output_width,
        reuse_limit=int(plan.get("traversal_reuse_limit", 10000)),
        max_contribution_per_source=int(plan.get("traversal_source_cap", 0)),
        visual_grammar=str(plan.get("traversal_visual_grammar", "overlap")),  # type: ignore[arg-type]
    )
    traversal_output = render_traversal(
        str(plan["traversal_id"]),
        target_manifest,
        output_root / "segments" / "seguimos-buscando",
        target_ids,
        traversal_settings,
        root=traversal_root,
    )[0]
    if not traversal_output.video_path:
        raise RuntimeError("Seguimos buscando did not produce a video")
    traversal_video = safe_project_path(traversal_output.video_path)
    traversal_loop = output_root / "seguimos-buscando.mp4"
    shutil.copy2(traversal_video, traversal_loop)

    videos = {
        "todos-somos-familiares": people_loop,
        "estan-en-todas-partes": places_loop,
        "seguimos-buscando": traversal_loop,
    }
    manifest = {
        "schema": "desaparecidos.uy/exhibition-triptych/1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_status": "internal_unreviewed",
        "plan": plan,
        "settings": {
            "todos-somos-familiares": asdict(people_settings),
            "estan-en-todas-partes": asdict(places_settings),
            "seguimos-buscando": asdict(traversal_settings),
        },
        "videos": {
            name: {
                "path": display_path(path),
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
            for name, path in videos.items()
        },
        "segments": {
            "todos-somos-familiares": people_segments,
            "estan-en-todas-partes": places_segments,
            "seguimos-buscando": [
                {
                    "target_id": traversal_output.target_id,
                    "video": traversal_output.video_path,
                    "sidecar": traversal_output.sidecar_path,
                }
            ],
        },
        "review_required": [
            "historical target portrait and metadata review",
            "source rights and approval review",
            "complete people-derived output recognisability review",
            "full-duration video inspection",
            "installation playback test on the intended displays",
        ],
    }
    manifest_path = output_root / "exhibition-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render and record the three-channel desaparecidos.uy exhibition triptych."
    )
    parser.add_argument("plan", type=Path)
    parser.add_argument(
        "--allow-internal-people-render",
        action="store_true",
        help="acknowledge that the people-derived loop is internal until complete review",
    )
    args = parser.parse_args()
    plan = _load_plan(safe_project_path(args.plan))
    manifest = render(plan, allow_internal_people_render=args.allow_internal_people_render)
    print(display_path(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
