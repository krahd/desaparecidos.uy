from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(relative: str, old: str, new: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"expected text not found in {relative}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_once(relative: str, marker: str, content: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    path.write_text(text.rstrip() + "\n\n" + content.strip() + "\n", encoding="utf-8")


def patch_pipeline() -> None:
    replace_once(
        "src/desaparecidos/pipeline.py",
        "from .paths import display_path\n",
        "from .paths import display_path\n"
        "from .placement_history import (\n"
        "    PlacementGrammar,\n"
        "    TargetSalience,\n"
        "    build_placement_history,\n"
        "    ordered_target_positions,\n"
        "    render_placements,\n"
        ")\n",
    )
    replace_once(
        "src/desaparecidos/pipeline.py",
        '    video_source_layout: VideoSourceLayout = "grid"\n    make_video: bool = False\n',
        '    video_source_layout: VideoSourceLayout = "grid"\n'
        '    visual_grammar: PlacementGrammar = "grid"\n'
        '    target_salience: TargetSalience = "portrait"\n'
        '    avoid_source_adjacency: bool = False\n'
        '    make_video: bool = False\n',
    )
    old_loop = '''    for y in range(0, target.height, tile):
        for x in range(0, target.width, tile):
            target_patch = target.crop((x, y, x + tile, y + tile))
            descriptor = descriptor_for(target_patch)
            distances = np.linalg.norm(descriptors - descriptor, axis=1)
            distances[~available] = np.inf
            idx = int(np.argmin(distances))
            if not np.isfinite(distances[idx]):
                raise ValueError("fragment reuse / contribution limits exhausted")
            fragment = shuffled[idx]
            frag_use[idx] += 1
            source_index = int(source_of[idx])
            source_use[source_index] += 1
            if frag_use[idx] >= settings.reuse_limit:
                available[idx] = False
            if cap > 0 and source_use[source_index] >= cap:
                available[source_of == source_index] = False
            output.paste(fragment.image, (x, y))
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
'''
    new_loop = '''    source_at: dict[tuple[int, int], str] = {}
    for x, y in ordered_target_positions(
        target.width, target.height, tile, settings.target_salience
    ):
        target_patch = target.crop((x, y, x + tile, y + tile))
        descriptor = descriptor_for(target_patch)
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
        idx = int(np.argmin(distances))
        if not np.isfinite(distances[idx]):
            raise ValueError("fragment reuse / contribution / adjacency limits exhausted")
        fragment = shuffled[idx]
        frag_use[idx] += 1
        source_index = int(source_of[idx])
        source_use[source_index] += 1
        if frag_use[idx] >= settings.reuse_limit:
            available[idx] = False
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

    output = render_placements(
        placements,
        target.size,
        grammar=settings.visual_grammar,
        seed=settings.seed,
        target_id=target_row.id,
        background=BACKGROUND,
    )
'''
    replace_once("src/desaparecidos/pipeline.py", old_loop, new_loop)
    replace_once(
        "src/desaparecidos/pipeline.py",
        '''        sidecar_path = root / f"{stem}.json"
        sidecar = {
            "artwork": artwork,
''',
        '''        source_sequence = []
        for placement in assembly.placements:
            if placement.source_id not in source_sequence:
                source_sequence.append(placement.source_id)
        placement_history = build_placement_history(
            assembly.placements,
            assembly.image.size,
            grammar=settings.visual_grammar,
            seed=settings.seed,
            target_id=target.id,
            source_sequence=source_sequence,
        )
        sidecar_path = root / f"{stem}.json"
        sidecar = {
            "sidecar_schema": "desaparecidos.uy/output-sidecar/2.0",
            "artwork": artwork,
''',
    )
    replace_once(
        "src/desaparecidos/pipeline.py",
        '            "source_sequence": list(assembly.source_usage.keys()),\n            "tile_count": len(assembly.placements),\n',
        '            "source_sequence": source_sequence,\n'
        '            "placement_history": placement_history,\n'
        '            "tile_count": len(assembly.placements),\n',
    )


def patch_traversals() -> None:
    replace_once(
        "src/desaparecidos/traversals.py",
        "from .paths import display_path\n",
        "from .paths import display_path\n"
        "from .placement_history import (\n"
        "    PlacementGrammar,\n"
        "    build_placement_history,\n"
        "    placements_visible_after,\n"
        "    render_placements,\n"
        ")\n",
    )
    replace_once(
        "src/desaparecidos/traversals.py",
        '    max_contribution_per_source: int = 0\n',
        '    max_contribution_per_source: int = 0\n'
        '    visual_grammar: PlacementGrammar = "overlap"\n',
    )
    replace_once(
        "src/desaparecidos/traversals.py",
        '''class WalkAssembly:
    """An assembly built strictly in walk order, with the frame index that supplied each tile."""
    result: AssemblyResult
    placed_after_frame: list[int]
    segment_frame_ids: list[str]
''',
        '''class WalkAssembly:
    """An assembly built strictly in walk order, with the frame index that supplied each tile."""
    result: AssemblyResult
    placed_after_frame: list[int]
    segment_frame_ids: list[str]
    visual_grammar: PlacementGrammar
    seed: int
    target_id: str
''',
    )
    replace_once(
        "src/desaparecidos/traversals.py",
        '''    result = AssemblyResult(output, target, source_usage, fragment_usage, placements)
    return WalkAssembly(result, placed_after, [str(frame["id"]) for frame in frames])
''',
        '''    output = render_placements(
        placements,
        target.size,
        grammar=settings.visual_grammar,
        seed=settings.seed,
        target_id=target_row.id,
        background=(0, 0, 0),
    )
    result = AssemblyResult(output, target, source_usage, fragment_usage, placements)
    return WalkAssembly(
        result,
        placed_after,
        [str(frame["id"]) for frame in frames],
        settings.visual_grammar,
        settings.seed,
        target_row.id,
    )
''',
    )
    old_progress = '''def _walk_progress(walk: WalkAssembly, reached_frame: int) -> Image.Image:
    assembly = walk.result
    mosaic = Image.new("RGB", assembly.image.size, (0, 0, 0))
    mask = Image.new("L", assembly.image.size, 0)
    draw = ImageDraw.Draw(mask)
    for placement, placed_after in zip(assembly.placements, walk.placed_after_frame):
        if placed_after > reached_frame:
            continue
        mosaic.paste(placement.image, (placement.dest_x, placement.dest_y))
        draw.rectangle(
            (placement.dest_x, placement.dest_y, placement.dest_x + placement.image.width, placement.dest_y + placement.image.height),
            fill=255,
        )
    return Image.composite(mosaic, Image.new("RGB", assembly.image.size, (0, 0, 0)), mask)
'''
    new_progress = '''def _walk_progress(walk: WalkAssembly, reached_frame: int) -> Image.Image:
    assembly = walk.result
    visible = placements_visible_after(
        assembly.placements, walk.placed_after_frame, reached_frame
    )
    return render_placements(
        visible,
        assembly.image.size,
        grammar=walk.visual_grammar,
        seed=walk.seed,
        target_id=walk.target_id,
        background=(0, 0, 0),
    )
'''
    replace_once("src/desaparecidos/traversals.py", old_progress, new_progress)
    replace_once(
        "src/desaparecidos/traversals.py",
        '''    sidecar = {
        "artwork": "seguimos-buscando",
''',
        '''    placement_histories = {
        target.id: build_placement_history(
            walk.result.placements,
            walk.result.image.size,
            grammar=walk.visual_grammar,
            seed=walk.seed,
            target_id=target.id,
            source_sequence=walk.segment_frame_ids,
            placed_after_frame=walk.placed_after_frame,
        )
        for target, walk in zip(selected, walks)
    }
    sidecar = {
        "sidecar_schema": "desaparecidos.uy/output-sidecar/2.0",
        "artwork": "seguimos-buscando",
''',
    )
    replace_once(
        "src/desaparecidos/traversals.py",
        '        "future_source_frames_used": False,\n        "generated_at": _now(),\n',
        '        "future_source_frames_used": False,\n'
        '        "placement_histories": placement_histories,\n'
        '        "generated_at": _now(),\n',
    )


def patch_api() -> None:
    replace_once(
        "src/desaparecidos/api.py",
        "from .paths import PROJECT_ROOT, safe_project_path\n",
        "from .paths import PROJECT_ROOT, safe_project_path\n"
        "from .placement_history import PlacementGrammar, TargetSalience\n",
    )
    replace_once(
        "src/desaparecidos/api.py",
        '    video_source_layout: VideoSourceLayout = "grid"\n    make_video: bool = False\n',
        '    video_source_layout: VideoSourceLayout = "grid"\n'
        '    visual_grammar: PlacementGrammar = "grid"\n'
        '    target_salience: TargetSalience = "portrait"\n'
        '    avoid_source_adjacency: bool = False\n'
        '    make_video: bool = False\n',
    )
    replace_once(
        "src/desaparecidos/api.py",
        '    max_contribution_per_source: int = Field(default=0, ge=0, le=1000000)\n\n\nclass TraversalReviewRequest',
        '    max_contribution_per_source: int = Field(default=0, ge=0, le=1000000)\n'
        '    visual_grammar: PlacementGrammar = "overlap"\n\n\nclass TraversalReviewRequest',
    )
    replace_once(
        "src/desaparecidos/api.py",
        '    max_contribution_per_source: int = Field(default=0, ge=0, le=1000000)\n\n\ndef _normalise_contribution_cap',
        '    max_contribution_per_source: int = Field(default=0, ge=0, le=1000000)\n'
        '    visual_grammar: PlacementGrammar = "overlap"\n\n\ndef _normalise_contribution_cap',
    )
    replace_once(
        "src/desaparecidos/api.py",
        '''        targets = validate_manifest(request.targets, "targets", require_files=request.require_files)
        sources = validate_manifest(request.sources, "places", require_files=request.require_files)
        people = validate_manifest(request.people, "people", require_files=request.require_files)
''',
        '''        targets = validate_manifest(safe_project_path(request.targets), "targets", require_files=request.require_files)
        sources = validate_manifest(safe_project_path(request.sources), "places", require_files=request.require_files)
        people = validate_manifest(safe_project_path(request.people), "people", require_files=request.require_files)
''',
    )
    replace_once(
        "src/desaparecidos/api.py",
        '''            request.manifest,
            request.kind,
            output_root=request.output_root,
''',
        '''            safe_project_path(request.manifest),
            request.kind,
            output_root=safe_project_path(request.output_root),
''',
    )
    replace_once(
        "src/desaparecidos/api.py",
        '''            video_source_layout=request.video_source_layout,
            make_video=request.make_video,
''',
        '''            video_source_layout=request.video_source_layout,
            visual_grammar=request.visual_grammar,
            target_salience=request.target_salience,
            avoid_source_adjacency=request.avoid_source_adjacency,
            make_video=request.make_video,
''',
    )
    replace_once(
        "src/desaparecidos/api.py",
        '''                request.targets,
                request.sources,
                request.output_dir,
''',
        '''                safe_project_path(request.targets),
                safe_project_path(request.sources),
                safe_project_path(request.output_dir),
''',
    )
    replace_once(
        "src/desaparecidos/api.py",
        '        return {"items": list_outputs(output_dir)}\n',
        '        return {"items": list_outputs(safe_project_path(output_dir))}\n',
    )
    # Both traversal settings constructors contain this exact tail.
    path = ROOT / "src/desaparecidos/api.py"
    text = path.read_text(encoding="utf-8")
    old = '            max_contribution_per_source=request.max_contribution_per_source,\n        )'
    new = (
        '            max_contribution_per_source=request.max_contribution_per_source,\n'
        '            visual_grammar=request.visual_grammar,\n'
        '        )'
    )
    if new not in text:
        count = text.count(old)
        if count != 2:
            raise RuntimeError(f"expected two traversal settings constructors, found {count}")
        path.write_text(text.replace(old, new), encoding="utf-8")


def patch_cli() -> None:
    replace_once(
        "src/desaparecidos/cli.py",
        '''    run.add_argument("--target-id")
''',
        '''    run.add_argument(
        "--visual-grammar", choices=["grid", "irregular", "overlap"], default="grid",
        help="final fragment grammar; matching remains accountable to target sections",
    )
    run.add_argument(
        "--target-salience", choices=["uniform", "portrait"], default="portrait",
        help="order target sections uniformly or prioritise explicit portrait regions",
    )
    run.add_argument(
        "--avoid-source-adjacency", action="store_true",
        help="prevent neighbouring target sections from using the same source",
    )
    run.add_argument("--target-id")
''',
    )
    replace_once(
        "src/desaparecidos/cli.py",
        '    traversal.add_argument("--output", default="outputs/stage1")\n',
        '    traversal.add_argument("--output", default="outputs/stage1")\n'
        '    traversal.add_argument(\n'
        '        "--visual-grammar", choices=["grid", "irregular", "overlap"], default="overlap"\n'
        '    )\n',
    )
    replace_once(
        "src/desaparecidos/cli.py",
        '''            video_source_layout=args.video_source_layout,
            make_video=args.video,
''',
        '''            video_source_layout=args.video_source_layout,
            visual_grammar=args.visual_grammar,
            target_salience=args.target_salience,
            avoid_source_adjacency=args.avoid_source_adjacency,
            make_video=args.video,
''',
    )
    replace_once(
        "src/desaparecidos/cli.py",
        '''                output_width=args.output_width,
            ),
''',
        '''                output_width=args.output_width,
                visual_grammar=args.visual_grammar,
            ),
''',
    )


def patch_crawl() -> None:
    replace_once(
        "src/desaparecidos/crawl.py",
        "from .manifests import EXPECTED_FIELDS, ManifestKind, read_manifest\n",
        "from .manifests import EXPECTED_FIELDS, ManifestKind, read_manifest\n"
        "from .net import safe_get\n",
    )
    path = ROOT / "src/desaparecidos/crawl.py"
    text = path.read_text(encoding="utf-8")
    replacements = {
        '''page_response = client.get(
                        page_url, timeout=timeout, headers={"User-Agent": USER_AGENT}
                    )''': '''page_response = safe_get(
                        client, page_url, timeout=timeout, headers={"User-Agent": USER_AGENT}
                    )''',
        '''page_response = client.get(page_url, timeout=timeout, headers={"User-Agent": USER_AGENT})''': '''page_response = safe_get(
                        client, page_url, timeout=timeout, headers={"User-Agent": USER_AGENT}
                    )''',
        '''response = client.get(image_url, timeout=timeout, headers={"User-Agent": USER_AGENT})''': '''response = safe_get(
            client, image_url, timeout=timeout, headers={"User-Agent": USER_AGENT}
        )''',
        '''response = client.get(
                urljoin(base, "/robots.txt"), timeout=timeout, headers={"User-Agent": USER_AGENT}
            )''': '''response = safe_get(
                client,
                urljoin(base, "/robots.txt"),
                timeout=timeout,
                headers={"User-Agent": USER_AGENT},
            )''',
    }
    for old, new in replacements.items():
        if new in text:
            continue
        if old not in text:
            raise RuntimeError(f"crawl replacement not found: {old[:100]!r}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")


def patch_tests() -> None:
    append_once(
        "tests/test_pipeline.py",
        "test_sidecar_persists_replayable_placement_history",
        r'''
def test_sidecar_persists_replayable_placement_history(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path, source_count=16)
    output = run_stage1(
        targets,
        places,
        tmp_path / "history",
        Stage1Settings(
            seed=19,
            fragment_size=24,
            reuse_limit=2,
            output_width=96,
            max_contribution_per_source=1,
            visual_grammar="overlap",
            target_salience="portrait",
        ),
    )[0]
    sidecar = json.loads(Path(output.sidecar_path).read_text(encoding="utf-8"))
    history = sidecar["placement_history"]

    assert sidecar["sidecar_schema"] == "desaparecidos.uy/output-sidecar/2.0"
    assert history["schema"] == "desaparecidos.uy/placement-history/1.0"
    assert history["visual_grammar"] == "overlap"
    assert history["placement_count"] == sidecar["tile_count"] == 16
    assert len(history["placements"]) == 16
    first = history["placements"][0]
    assert first["source_id"]
    assert first["fragment_id"]
    assert first["source_rect"]["width"] == 24
    assert first["matched_target_rect"]["width"] == 24
    assert first["render_geometry"]["width"] >= 24
    assert first["time"]["settle_normalised"] > first["time"]["enter_normalised"]


def test_visual_grammars_are_deterministic_and_materially_distinct(tmp_path: Path) -> None:
    targets, places = write_manifests(tmp_path, source_count=16)
    base = dict(
        seed=23,
        fragment_size=24,
        reuse_limit=2,
        output_width=96,
        max_contribution_per_source=1,
    )
    digests: dict[str, str] = {}
    for grammar in ("grid", "irregular", "overlap"):
        first = run_stage1(
            targets, places, tmp_path / f"{grammar}-a",
            Stage1Settings(**base, visual_grammar=grammar),
        )[0]
        second = run_stage1(
            targets, places, tmp_path / f"{grammar}-b",
            Stage1Settings(**base, visual_grammar=grammar),
        )[0]
        assert digest(Path(first.still_path)) == digest(Path(second.still_path))
        digests[grammar] = digest(Path(first.still_path))

    assert len(set(digests.values())) == 3


def test_portrait_salience_prioritises_features_before_corners() -> None:
    from desaparecidos.placement_history import ordered_target_positions

    ordered = ordered_target_positions(240, 320, 24, "portrait")
    uniform = ordered_target_positions(240, 320, 24, "uniform")

    assert uniform[0] == (0, 0)
    assert ordered[0] != (0, 0)
    first_centres = [((x + 12) / 240, (y + 12) / 320) for x, y in ordered[:8]]
    assert any(0.25 < x < 0.45 and 0.25 < y < 0.50 for x, y in first_centres)
    assert any(0.55 < x < 0.75 and 0.25 < y < 0.50 for x, y in first_centres)
''',
    )


def main() -> None:
    patch_pipeline()
    patch_traversals()
    patch_api()
    patch_cli()
    patch_crawl()
    patch_tests()


if __name__ == "__main__":
    main()
