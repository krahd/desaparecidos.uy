from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .images import Fragment, crop_from_row, descriptor_for, extract_fragments, load_rgb
from .manifests import ManifestRow, approved_rows, row_file_path
from .paths import display_path, safe_project_path
from .pipeline import (
    BACKGROUND,
    INK,
    AssemblyResult,
    Stage1Output,
    TilePlacement,
    _feasibility_error,
    _render_video_ffmpeg,
    _target_canvas,
)
from .placement_history import (
    PlacementGrammar,
    TargetSalience,
    build_placement_history,
    ordered_target_positions,
    placements_visible_after,
    render_placements,
)
from .territorial import balance_territorial_sources, territorial_group, territorial_usage
from .traversals import (
    DEFAULT_TRAVERSAL_ROOT,
    CompositionMode,
    TargetMode,
    TraversalRenderSettings,
    _fit,
    _split_segments,
    assemble_walk,
    load_traversal,
)

ArtworkKind = Literal["todos-somos-familiares", "estan-en-todas-partes"]


@dataclass(frozen=True)
class ArtworkRenderSettings:
    seed: int = 17
    fragment_size: int = 24
    reuse_limit: int = 8
    output_width: int = 720
    max_fragments_per_source: int = 240
    max_contribution_per_source: int = 1
    visual_grammar: PlacementGrammar = "grid"
    target_salience: TargetSalience = "portrait"
    avoid_source_adjacency: bool = False
    territorially_balance_sources: bool = False
    max_sources: int = 0
    make_video: bool = False
    fps: int = 24
    duration_seconds: int = 12
    colour_output: bool = False


@dataclass(frozen=True)
class ArtworkTraversalSettings:
    composition: CompositionMode = "overlay"
    target_mode: TargetMode = "single"
    duration_seconds: int = 60
    fps: int = 24
    seed: int = 17
    fragment_size: int = 24
    output_width: int = 1920
    reuse_limit: int = 10000
    max_contribution_per_source: int = 0
    visual_grammar: PlacementGrammar = "overlap"
    colour_output: bool = False


def _output_image(image: Image.Image, colour_output: bool) -> Image.Image:
    return image.convert("RGB") if colour_output else image.convert("L").convert("RGB")


def _source_kind(artwork: ArtworkKind) -> Literal["people", "places"]:
    return "people" if artwork == "todos-somos-familiares" else "places"


def _select_sources(
    sources: Sequence[ManifestRow],
    settings: ArtworkRenderSettings,
    artwork: ArtworkKind,
) -> list[ManifestRow]:
    selected = list(sources)
    if artwork == "estan-en-todas-partes" and settings.territorially_balance_sources:
        selected = balance_territorial_sources(selected, seed=settings.seed)
    if settings.max_sources > 0:
        selected = selected[: settings.max_sources]
    return selected


def _assemble(
    target_row: ManifestRow,
    target_manifest: str | Path,
    fragments: list[Fragment],
    settings: ArtworkRenderSettings,
) -> AssemblyResult:
    target = crop_from_row(load_rgb(row_file_path(target_row, target_manifest)), target_row)
    target = _target_canvas(target, settings.output_width, settings.fragment_size)
    rng = random.Random(settings.seed + sum(ord(char) for char in target_row.id))
    shuffled = list(fragments)
    rng.shuffle(shuffled)
    if not shuffled:
        raise ValueError("no approved source fragments are available")

    tile = settings.fragment_size
    positions = ordered_target_positions(
        target.width,
        target.height,
        tile,
        settings.target_salience,
    )
    source_count = len({fragment.source_id for fragment in shuffled})
    cap = max(0, settings.max_contribution_per_source)
    error = _feasibility_error(
        len(positions), len(shuffled), settings.reuse_limit, source_count, cap
    )
    if error:
        raise ValueError(error)

    descriptors = np.stack([fragment.descriptor for fragment in shuffled]).astype(np.float32)
    source_keys: dict[str, int] = {}
    source_of = np.empty(len(shuffled), dtype=np.intp)
    for index, fragment in enumerate(shuffled):
        source_of[index] = source_keys.setdefault(fragment.source_id, len(source_keys))
    source_id_by_index = {value: key for key, value in source_keys.items()}
    frag_use = np.zeros(len(shuffled), dtype=np.int64)
    source_use = np.zeros(len(source_keys), dtype=np.int64)
    available = np.ones(len(shuffled), dtype=bool)
    source_at: dict[tuple[int, int], str] = {}
    placements: list[TilePlacement] = []

    for x, y in positions:
        descriptor = descriptor_for(target.crop((x, y, x + tile, y + tile)))
        distances = np.linalg.norm(descriptors - descriptor, axis=1)
        distances[~available] = np.inf
        if settings.avoid_source_adjacency:
            blocked_sources = {
                source_at[position]
                for position in (
                    (x - tile, y),
                    (x + tile, y),
                    (x, y - tile),
                    (x, y + tile),
                )
                if position in source_at
            }
            if blocked_sources:
                blocked_indexes = [source_keys[source_id] for source_id in blocked_sources]
                distances[np.isin(source_of, blocked_indexes)] = np.inf
        index = int(np.argmin(distances))
        if not np.isfinite(distances[index]):
            raise ValueError("fragment reuse, contribution, or adjacency limits exhausted")
        fragment = shuffled[index]
        source_index = int(source_of[index])
        frag_use[index] += 1
        source_use[source_index] += 1
        if frag_use[index] >= settings.reuse_limit:
            available[index] = False
        if cap > 0 and source_use[source_index] >= cap:
            available[source_of == source_index] = False
        placements.append(
            TilePlacement(
                source_id=fragment.source_id,
                fragment_id=fragment.fragment_id,
                image=fragment.image,
                dest_x=x,
                dest_y=y,
                source_x=fragment.x,
                source_y=fragment.y,
            )
        )
        source_at[(x, y)] = fragment.source_id

    image = render_placements(
        placements,
        target.size,
        grammar=settings.visual_grammar,
        seed=settings.seed,
        target_id=target_row.id,
        background=BACKGROUND,
    )
    source_usage = {
        source_id_by_index[index]: int(count)
        for index, count in enumerate(source_use)
        if count > 0
    }
    fragment_usage = {
        shuffled[index].fragment_id: int(count)
        for index, count in enumerate(frag_use)
        if count > 0
    }
    return AssemblyResult(image, target, source_usage, fragment_usage, placements)


def _source_sequence(placements: Sequence[TilePlacement]) -> list[str]:
    result: list[str] = []
    for placement in placements:
        if placement.source_id not in result:
            result.append(placement.source_id)
    return result


def _emergence_frames(
    assembly: AssemblyResult,
    target: ManifestRow,
    settings: ArtworkRenderSettings,
) -> Iterable[Image.Image]:
    total = max(settings.fps, settings.fps * settings.duration_seconds)
    font = ImageFont.load_default()
    hold_start = 0.08
    settle_at = 0.78
    dissolve_at = 0.92
    for frame_index in range(total):
        progress = frame_index / max(1, total - 1)
        if progress <= hold_start:
            visible_count = 0
        elif progress < settle_at:
            local = (progress - hold_start) / (settle_at - hold_start)
            visible_count = min(
                len(assembly.placements),
                max(1, math.ceil(local * len(assembly.placements))),
            )
        else:
            visible_count = len(assembly.placements)
        frame = render_placements(
            assembly.placements[:visible_count],
            assembly.image.size,
            grammar=settings.visual_grammar,
            seed=settings.seed,
            target_id=target.id,
            background=INK,
        )
        if progress >= settle_at:
            blend = min(0.20, (progress - settle_at) / max(0.001, dissolve_at - settle_at) * 0.20)
            frame = Image.blend(frame, assembly.target_canvas, blend)
        if settle_at <= progress < dissolve_at:
            draw = ImageDraw.Draw(frame)
            draw.rectangle((0, frame.height - 42, frame.width, frame.height), fill=INK)
            draw.text(
                (18, frame.height - 29),
                target.values.get("name", target.id),
                fill=(245, 245, 240),
                font=font,
            )
        if progress >= dissolve_at:
            alpha = min(1.0, (progress - dissolve_at) / max(0.001, 1.0 - dissolve_at))
            frame = Image.blend(frame, Image.new("RGB", frame.size, INK), alpha)
        yield frame


def run_artwork(
    target_manifest: str | Path,
    source_manifest: str | Path,
    output_dir: str | Path,
    settings: ArtworkRenderSettings | None = None,
    *,
    target_id: str | None = None,
    artwork: ArtworkKind = "estan-en-todas-partes",
) -> list[Stage1Output]:
    settings = settings or ArtworkRenderSettings()
    source_kind = _source_kind(artwork)
    if source_kind == "people" and settings.max_contribution_per_source <= 0:
        raise ValueError("people-source generation requires a positive source contribution cap")
    targets = approved_rows(target_manifest, "targets", require_files=True)
    sources = approved_rows(source_manifest, source_kind, require_files=True)
    sources = _select_sources(sources, settings, artwork)
    if target_id:
        targets = [target for target in targets if target.id == target_id]
    if not targets:
        raise ValueError("no approved target matches the request")
    if not sources:
        raise ValueError("no approved source rows match the request")
    fragments = extract_fragments(
        sources,
        source_manifest,
        fragment_size=settings.fragment_size,
        max_fragments_per_source=settings.max_fragments_per_source,
        source_kind=source_kind,
    )
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    outputs: list[Stage1Output] = []
    for target in targets:
        assembly = _assemble(target, target_manifest, fragments, settings)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        stem = f"{artwork}-{target.id}-{settings.seed}-{timestamp}"
        still_path = root / f"{stem}.png"
        video_path = root / f"{stem}.mp4" if settings.make_video else None
        sidecar_path = root / f"{stem}.json"
        _output_image(assembly.image, settings.colour_output).save(still_path)
        if video_path is not None and not _render_video_ffmpeg(
            (_output_image(frame, settings.colour_output) for frame in _emergence_frames(assembly, target, settings)),
            assembly.image.size,
            video_path,
            fps=settings.fps,
        ):
            raise RuntimeError("browser-playable MP4 rendering requires ffmpeg with libx264")
        source_sequence = _source_sequence(assembly.placements)
        history = build_placement_history(
            assembly.placements,
            assembly.image.size,
            grammar=settings.visual_grammar,
            seed=settings.seed,
            target_id=target.id,
            source_sequence=source_sequence,
        )
        sidecar: dict[str, Any] = {
            "sidecar_schema": "desaparecidos.uy/output-sidecar/2.0",
            "artwork": artwork,
            "source_kind": source_kind,
            "target_id": target.id,
            "target_name": target.values.get("name", target.id),
            "settings": asdict(settings),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "release_status": "internal_unreviewed" if source_kind == "people" else "review_required",
            "source_manifest": display_path(source_manifest),
            "still_path": display_path(still_path),
            "video_path": display_path(video_path) if video_path else None,
            "video_format": "h264" if video_path else None,
            "video_process_style": "fragment-emergence-without-raw-source-reveal" if video_path else None,
            "source_usage": assembly.source_usage,
            "fragment_usage": assembly.fragment_usage,
            "source_sequence": source_sequence,
            "tile_count": len(assembly.placements),
            "placement_history": history,
            "source_person_risk_controls": {
                "identity_matching": False,
                "raw_source_reveal": False,
                "source_contribution_cap": settings.max_contribution_per_source,
                "adjacent_same_source_prevented": settings.avoid_source_adjacency,
                "anonymity_guaranteed": False,
                "manual_output_review_required": source_kind == "people",
            },
        }
        if artwork == "estan-en-todas-partes":
            sidecar["territorial_source_policy"] = {
                "balanced_order": settings.territorially_balance_sources,
                "max_sources": settings.max_sources,
                "reviewed_groups_available": sorted({territorial_group(row) for row in sources}),
                "realised_usage": territorial_usage(assembly.source_usage, sources),
                "coverage_claim": "none; unlocated and absent territories remain explicit",
            }
        sidecar_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
        outputs.append(
            Stage1Output(
                target.id,
                display_path(still_path),
                display_path(sidecar_path),
                display_path(video_path) if video_path else None,
            )
        )
    return outputs


def _traversal_frames(
    segments: list[list[dict[str, Any]]],
    targets: list[ManifestRow],
    walks: Sequence[Any],
    settings: ArtworkTraversalSettings,
) -> Iterable[Image.Image]:
    total = max(settings.fps, settings.duration_seconds * settings.fps)
    segment_length = max(1, total // len(targets))
    font = ImageFont.load_default()
    for output_index in range(total):
        target_index = min(len(targets) - 1, output_index // segment_length)
        local_index = output_index - target_index * segment_length
        progress = local_index / max(1, segment_length - 1)
        frames = segments[target_index]
        walk = walks[target_index]
        reached_count = max(1, math.ceil(len(frames) * progress))
        reached_index = reached_count - 1
        with Image.open(str(frames[reached_index]["local_path"])) as source:
            street = _fit(source.convert("RGB"), walk.result.image.size)
        visible = placements_visible_after(
            walk.result.placements,
            walk.placed_after_frame,
            reached_index,
        )
        portrait = render_placements(
            visible,
            walk.result.image.size,
            grammar=settings.visual_grammar,
            seed=settings.seed,
            target_id=targets[target_index].id,
            background=INK,
        )
        if progress > 0.82:
            final = render_placements(
                walk.result.placements,
                walk.result.image.size,
                grammar=settings.visual_grammar,
                seed=settings.seed,
                target_id=targets[target_index].id,
                background=INK,
            )
            portrait = Image.blend(portrait, final, min(1.0, (progress - 0.82) / 0.08))
        if progress > 0.94:
            portrait = Image.blend(
                portrait,
                Image.new("RGB", portrait.size, INK),
                min(1.0, (progress - 0.94) / 0.06),
            )
        if settings.composition == "split":
            output = Image.new("RGB", street.size, INK)
            half = street.width // 2
            output.paste(street.crop((0, 0, half, street.height)), (0, 0))
            output.paste(portrait.resize((street.width - half, street.height)), (half, 0))
        elif settings.composition == "alternate":
            phase = (local_index // max(1, settings.fps * 2)) % 2
            output = street if phase == 0 and progress < 0.82 else portrait
        else:
            output = Image.blend(street, portrait, min(0.84, progress * 0.96))
        if 0.82 <= progress <= 0.95:
            draw = ImageDraw.Draw(output)
            draw.rectangle((0, output.height - 42, output.width, output.height), fill=INK)
            draw.text(
                (18, output.height - 29),
                targets[target_index].values.get("name", targets[target_index].id),
                fill=(245, 245, 240),
                font=font,
            )
        yield output


def render_search_artwork(
    traversal_id: str,
    target_manifest: str | Path,
    output_dir: str | Path,
    target_ids: list[str],
    settings: ArtworkTraversalSettings | None = None,
    *,
    root: str | Path = DEFAULT_TRAVERSAL_ROOT,
) -> list[Stage1Output]:
    settings = settings or ArtworkTraversalSettings()
    traversal = load_traversal(traversal_id, root)
    frames = [
        frame
        for frame in traversal.get("frames", [])
        if frame.get("review_status") == "approved"
        and frame.get("local_path")
        and Path(str(frame["local_path"])).exists()
    ]
    if not frames:
        raise ValueError("traversal has no acquired, approved frames")
    targets = approved_rows(target_manifest, "targets", require_files=True)
    selected = [target for target_id in target_ids for target in targets if target.id == target_id]
    if settings.target_mode == "single":
        selected = selected[:1]
    if not selected:
        raise ValueError("select at least one approved target")
    segments = _split_segments(frames, len(selected))
    legacy_settings = TraversalRenderSettings(
        composition=settings.composition,
        target_mode=settings.target_mode,
        duration_seconds=settings.duration_seconds,
        fps=settings.fps,
        seed=settings.seed,
        fragment_size=settings.fragment_size,
        output_width=settings.output_width,
        reuse_limit=settings.reuse_limit,
        max_contribution_per_source=settings.max_contribution_per_source,
        colour_output=settings.colour_output,
    )
    walks = [
        assemble_walk(target, target_manifest, segment, legacy_settings)
        for target, segment in zip(selected, segments)
    ]
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    stem = f"seguimos-buscando-{traversal_id}-{settings.seed}-{timestamp}"
    still_path = output_root / f"{stem}.png"
    video_path = output_root / f"{stem}.mp4"
    sidecar_path = output_root / f"{stem}.json"
    final_image = render_placements(
        walks[-1].result.placements,
        walks[-1].result.image.size,
        grammar=settings.visual_grammar,
        seed=settings.seed,
        target_id=selected[-1].id,
        background=INK,
    )
    _output_image(final_image, settings.colour_output).save(still_path)
    if not _render_video_ffmpeg(
        (_output_image(frame, settings.colour_output) for frame in _traversal_frames(segments, selected, walks, settings)),
        final_image.size,
        video_path,
        fps=settings.fps,
    ):
        raise RuntimeError("browser-playable MP4 rendering requires ffmpeg with libx264")
    histories = {
        target.id: build_placement_history(
            walk.result.placements,
            walk.result.image.size,
            grammar=settings.visual_grammar,
            seed=settings.seed,
            target_id=target.id,
            source_sequence=walk.segment_frame_ids,
            placed_after_frame=walk.placed_after_frame,
        )
        for target, walk in zip(selected, walks)
    }
    sidecar = {
        "sidecar_schema": "desaparecidos.uy/output-sidecar/2.0",
        "artwork": "seguimos-buscando",
        "source_kind": "street-level-traversal",
        "traversal_id": traversal_id,
        "provider": traversal.get("provider"),
        "attribution": traversal.get("attribution"),
        "release_status": "internal_unreviewed",
        "route_geometry": traversal.get("geometry"),
        "regions": traversal.get("regions"),
        "walks": traversal.get("walks"),
        "gap_policy": "direct-jump-cut",
        "approved_frame_ids": [frame["id"] for frame in frames],
        "target_ids": [target.id for target in selected],
        "target_id": selected[0].id if len(selected) == 1 else "sequence",
        "target_segments": {
            target.id: walk.segment_frame_ids for target, walk in zip(selected, walks)
        },
        "composition": settings.composition,
        "target_mode": settings.target_mode,
        "settings": asdict(settings),
        "source_usage": {
            target.id: walk.result.source_usage for target, walk in zip(selected, walks)
        },
        "assembly_policy": "incremental-found-fragments",
        "future_source_frames_used": False,
        "placement_histories": histories,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "still_path": display_path(still_path),
        "video_path": display_path(video_path),
        "video_format": "h264",
    }
    sidecar_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
    return [
        Stage1Output(
            str(sidecar["target_id"]),
            display_path(still_path),
            display_path(sidecar_path),
            display_path(video_path),
        )
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="desaparecidos-artwork")
    subparsers = parser.add_subparsers(dest="command", required=True)
    render = subparsers.add_parser("render", help="Render Todos somos familiares or Están en todas partes.")
    render.add_argument("--artwork", choices=["todos-somos-familiares", "estan-en-todas-partes"], required=True)
    render.add_argument("--targets", default="data/manifests/targets.csv")
    render.add_argument("--sources", required=True)
    render.add_argument("--output", default="outputs/artwork")
    render.add_argument("--target-id")
    render.add_argument("--seed", type=int, default=17)
    render.add_argument("--fragment-size", type=int, default=24)
    render.add_argument("--reuse-limit", type=int, default=8)
    render.add_argument("--output-width", type=int, default=1920)
    render.add_argument("--source-cap", type=int, default=1)
    render.add_argument("--grammar", choices=["grid", "irregular", "overlap"], default="overlap")
    render.add_argument("--salience", choices=["uniform", "portrait"], default="portrait")
    render.add_argument("--avoid-source-adjacency", action="store_true")
    render.add_argument("--territorial-balance", action="store_true")
    render.add_argument("--max-sources", type=int, default=0)
    render.add_argument("--video", action="store_true")
    render.add_argument("--fps", type=int, default=24)
    render.add_argument("--duration", type=int, default=12)
    render.add_argument("--colour", action="store_true", help="render colour output instead of grayscale")

    search = subparsers.add_parser("search", help="Render Seguimos buscando from an approved traversal.")
    search.add_argument("--traversal", required=True)
    search.add_argument("--traversal-root", default="data/raw/traversals")
    search.add_argument("--targets", default="data/manifests/targets.csv")
    search.add_argument("--target-id", action="append", required=True)
    search.add_argument("--target-mode", choices=["single", "sequence"], default="single")
    search.add_argument("--composition", choices=["overlay", "alternate", "split"], default="overlay")
    search.add_argument("--output", default="outputs/artwork")
    search.add_argument("--duration", type=int, default=60)
    search.add_argument("--fps", type=int, default=24)
    search.add_argument("--seed", type=int, default=17)
    search.add_argument("--fragment-size", type=int, default=24)
    search.add_argument("--output-width", type=int, default=1920)
    search.add_argument("--grammar", choices=["grid", "irregular", "overlap"], default="overlap")
    search.add_argument("--colour", action="store_true", help="render colour output instead of grayscale")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "render":
        settings = ArtworkRenderSettings(
            seed=args.seed,
            fragment_size=args.fragment_size,
            reuse_limit=args.reuse_limit,
            output_width=args.output_width,
            max_contribution_per_source=args.source_cap,
            visual_grammar=args.grammar,
            target_salience=args.salience,
            avoid_source_adjacency=args.avoid_source_adjacency,
            territorially_balance_sources=args.territorial_balance,
            max_sources=max(0, args.max_sources),
            make_video=args.video,
            fps=args.fps,
            duration_seconds=args.duration,
            colour_output=args.colour,
        )
        outputs = run_artwork(
            safe_project_path(args.targets),
            safe_project_path(args.sources),
            safe_project_path(args.output),
            settings,
            target_id=args.target_id,
            artwork=args.artwork,
        )
    else:
        outputs = render_search_artwork(
            args.traversal,
            safe_project_path(args.targets),
            safe_project_path(args.output),
            args.target_id,
            ArtworkTraversalSettings(
                composition=args.composition,
                target_mode=args.target_mode,
                duration_seconds=args.duration,
                fps=args.fps,
                seed=args.seed,
                fragment_size=args.fragment_size,
                output_width=args.output_width,
                visual_grammar=args.grammar,
                colour_output=args.colour,
            ),
            root=safe_project_path(args.traversal_root),
        )
    print(json.dumps({"ok": True, "outputs": [output.__dict__ for output in outputs]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
