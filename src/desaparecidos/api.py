from __future__ import annotations

"""FastAPI facade exposing the artwork-oriented mosaic controls."""

from typing import Any

from fastapi import HTTPException
from pydantic import Field

from . import api_core as _core
from .pipeline import (
    CompositionMode,
    MatchingMode,
    Stage1Settings,
    run_stage1,
)

# Preserve every existing request model and public helper.
for _name in dir(_core):
    if _name not in globals():
        globals()[_name] = getattr(_core, _name)


class GenerateRequest(_core.GenerateRequest):
    fragment_size: int = Field(default=36, ge=8, le=128)
    reuse_limit: int = Field(default=1, ge=1, le=10000)
    composition_mode: CompositionMode = "grid"
    unique_tiles: bool = True
    matching_mode: MatchingMode = "spatial"


def create_app():
    # Existing tests and integrations monkeypatch names on desaparecidos.api.
    # Propagate those replacements to the preserved core before it binds route
    # closures, maintaining the original module's observable behaviour.
    for name in dir(_core):
        if (
            name in globals()
            and name not in {"_core", "app", "create_app", "GenerateRequest"}
        ):
            setattr(_core, name, globals()[name])

    application = _core.create_app()

    # Replace only the Stage 1 generation route. Every other endpoint remains
    # exactly as implemented by api_core.
    application.router.routes = [
        route
        for route in application.router.routes
        if not (
            getattr(route, "path", None) == "/api/generate"
            and "POST" in (getattr(route, "methods", None) or set())
        )
    ]

    @application.post("/api/generate")
    def generate(request: GenerateRequest) -> dict[str, Any]:
        fields_set = getattr(request, "model_fields_set", None)
        if fields_set is None:
            fields_set = getattr(request, "__fields_set__", set())
        unique_tiles = request.unique_tiles
        if "unique_tiles" not in fields_set and request.reuse_limit != 1:
            # Preserve legacy API callers that explicitly request fragment
            # reuse while making one-use regions the default for new callers.
            unique_tiles = False

        settings = Stage1Settings(
            seed=request.seed,
            fragment_size=request.fragment_size,
            reuse_limit=request.reuse_limit,
            output_width=request.output_width,
            max_contribution_per_source=_core._normalise_contribution_cap(
                request.max_contribution_per_source
            ),
            search_scan_frames_per_candidate=request.search_scan_frames_per_candidate,
            search_scan_max_candidates=request.search_scan_max_candidates,
            video_source_layout=request.video_source_layout,
            make_video=request.make_video,
            composition_mode=request.composition_mode,
            unique_tiles=unique_tiles,
            matching_mode=request.matching_mode,
            colour_output=request.colour_output,
        )
        try:
            outputs = run_stage1(
                request.targets,
                request.sources,
                request.output_dir,
                settings,
                target_id=request.target_id,
                artwork=request.artwork,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"ok": True, "outputs": [output.__dict__ for output in outputs]}

    return application


app = create_app()
