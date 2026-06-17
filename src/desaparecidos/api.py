from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .demo import create_demo_fixtures
from .download import download_manifest
from .manifests import ManifestKind, validate_manifest
from .outputs import list_outputs
from .paths import PROJECT_ROOT, safe_project_path
from .pipeline import Stage1Settings, run_stage1


class ValidateRequest(BaseModel):
    targets: str = "data/manifests/targets.csv"
    sources: str = "data/manifests/places.csv"
    require_files: bool = False


class DownloadRequest(BaseModel):
    manifest: str
    kind: ManifestKind
    output_root: str = "data/raw"


class GenerateRequest(BaseModel):
    targets: str = "data/manifests/targets.csv"
    sources: str = "data/manifests/places.csv"
    output_dir: str = "outputs/stage1"
    seed: int = 17
    fragment_size: int = Field(default=24, ge=8, le=128)
    reuse_limit: int = Field(default=64, ge=1, le=10000)
    output_width: int = Field(default=720, ge=120, le=4096)
    make_video: bool = False
    target_id: str | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="desaparecidos.uy local API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_origin_regex=r"^http://(127\.0\.0\.1|localhost):\d+$",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "project_root": str(PROJECT_ROOT)}

    @app.get("/api/config")
    def config() -> dict[str, str]:
        return {
            "target_manifest": "data/manifests/targets.csv",
            "source_manifest": "data/manifests/places.csv",
            "output_dir": "outputs/stage1",
        }

    @app.post("/api/validate")
    def validate(request: ValidateRequest) -> dict[str, Any]:
        targets = validate_manifest(request.targets, "targets", require_files=request.require_files)
        sources = validate_manifest(request.sources, "places", require_files=request.require_files)
        return {
            "ok": targets.ok and sources.ok,
            "targets": targets.to_api(),
            "sources": sources.to_api(),
        }

    @app.post("/api/download")
    def download(request: DownloadRequest) -> dict[str, Any]:
        summary = download_manifest(
            request.manifest,
            request.kind,
            output_root=request.output_root,
        )
        return summary.to_api()

    @app.post("/api/demo-fixtures")
    def demo_fixtures() -> dict[str, object]:
        return create_demo_fixtures()

    @app.post("/api/generate")
    def generate(request: GenerateRequest) -> dict[str, Any]:
        settings = Stage1Settings(
            seed=request.seed,
            fragment_size=request.fragment_size,
            reuse_limit=request.reuse_limit,
            output_width=request.output_width,
            make_video=request.make_video,
        )
        try:
            outputs = run_stage1(
                request.targets,
                request.sources,
                request.output_dir,
                settings,
                target_id=request.target_id,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"ok": True, "outputs": [output.__dict__ for output in outputs]}

    @app.get("/api/outputs")
    def outputs(output_dir: str = "outputs/stage1") -> dict[str, Any]:
        return {"items": list_outputs(output_dir)}

    @app.get("/api/file")
    def file(path: str) -> FileResponse:
        try:
            resolved = safe_project_path(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if not resolved.exists() or not resolved.is_file():
            raise HTTPException(status_code=404, detail="file not found")
        return FileResponse(resolved)

    return app


app = create_app()
