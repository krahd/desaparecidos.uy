from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .crawl import crawl_pages
from .demo import create_demo_fixtures
from .download import download_manifest
from .manifests import (
    ManifestKind,
    delete_manifest_rows,
    set_review_status,
    set_review_status_bulk,
    validate_manifest,
)
from .outputs import delete_outputs, list_outputs
from .paths import PROJECT_ROOT, safe_project_path
from .pipeline import Stage1Settings, run_stage1


class ValidateRequest(BaseModel):
    targets: str = "data/manifests/targets.csv"
    sources: str = "data/manifests/places.csv"
    people: str = "data/manifests/people.csv"
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
    reuse_limit: int = Field(default=8, ge=1, le=10000)
    output_width: int = Field(default=720, ge=120, le=4096)
    max_contribution_per_source: int = Field(default=0, ge=0, le=1000000)
    make_video: bool = False
    target_id: str | None = None


class CrawlRequest(BaseModel):
    pages: list[str]
    kind: ManifestKind
    manifest: str
    output_root: str = "data/raw/crawl"
    max_images_per_page: int = Field(default=12, ge=1, le=50)
    label_prefix: str = ""
    max_depth: int = Field(default=2, ge=0, le=4)
    max_pages: int = Field(default=60, ge=1, le=500)
    max_images: int = Field(default=80, ge=1, le=1000)
    cross_domain: bool = False
    delay: float = Field(default=0.7, ge=0, le=10)
    respect_robots: bool = True
    use_cv: bool = True


class ReviewRequest(BaseModel):
    manifest: str
    kind: ManifestKind
    row_id: str
    review_status: Literal["approved", "pending", "rejected"]


class ReviewBulkRequest(BaseModel):
    manifest: str
    kind: ManifestKind
    review_status: Literal["approved", "pending", "rejected"]
    row_ids: list[str] = []
    all: bool = False


class DeleteRowRequest(BaseModel):
    manifest: str
    kind: ManifestKind
    row_id: str | None = None
    row_ids: list[str] = []


class DeleteOutputsRequest(BaseModel):
    output_dir: str = "outputs/stage1"
    ids: list[str] = []
    all: bool = False


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
            "people_manifest": "data/manifests/people.csv",
            "output_dir": "outputs/stage1",
        }

    @app.post("/api/validate")
    def validate(request: ValidateRequest) -> dict[str, Any]:
        targets = validate_manifest(request.targets, "targets", require_files=request.require_files)
        sources = validate_manifest(request.sources, "places", require_files=request.require_files)
        people = validate_manifest(request.people, "people", require_files=request.require_files)
        return {
            "ok": targets.ok and sources.ok and people.ok,
            "targets": targets.to_api(),
            "sources": sources.to_api(),
            "people": people.to_api(),
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

    @app.post("/api/crawl")
    def crawl(request: CrawlRequest) -> dict[str, object]:
        try:
            summary = crawl_pages(
                request.pages,
                request.kind,
                safe_project_path(request.manifest),
                output_root=safe_project_path(request.output_root),
                max_images_per_page=request.max_images_per_page,
                label_prefix=request.label_prefix,
                max_depth=request.max_depth,
                max_pages=request.max_pages,
                max_images=request.max_images,
                cross_domain=request.cross_domain,
                delay=request.delay,
                respect_robots=request.respect_robots,
                use_cv=request.use_cv,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return summary.to_api()

    @app.post("/api/review")
    def review(request: ReviewRequest) -> dict[str, Any]:
        try:
            validation = set_review_status(
                safe_project_path(request.manifest),
                request.kind,
                request.row_id,
                request.review_status,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"ok": validation.ok, "manifest": validation.to_api()}

    @app.post("/api/review-bulk")
    def review_bulk(request: ReviewBulkRequest) -> dict[str, Any]:
        try:
            validation = set_review_status_bulk(
                safe_project_path(request.manifest),
                request.kind,
                request.review_status,
                row_ids=None if request.all else request.row_ids,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"ok": validation.ok, "manifest": validation.to_api()}

    @app.post("/api/review/delete")
    def delete_row(request: DeleteRowRequest) -> dict[str, Any]:
        row_ids = list(request.row_ids)
        if request.row_id:
            row_ids.append(request.row_id)
        try:
            validation = delete_manifest_rows(
                safe_project_path(request.manifest),
                request.kind,
                row_ids,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"ok": validation.ok, "manifest": validation.to_api()}

    @app.post("/api/generate")
    def generate(request: GenerateRequest) -> dict[str, Any]:
        settings = Stage1Settings(
            seed=request.seed,
            fragment_size=request.fragment_size,
            reuse_limit=request.reuse_limit,
            output_width=request.output_width,
            max_contribution_per_source=request.max_contribution_per_source,
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

    @app.post("/api/outputs/delete")
    def remove_outputs(request: DeleteOutputsRequest) -> dict[str, Any]:
        try:
            return delete_outputs(
                safe_project_path(request.output_dir),
                ids=request.ids,
                all_outputs=request.all,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/file")
    def file(path: str) -> FileResponse:
        try:
            resolved = safe_project_path(path)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if not resolved.exists() or not resolved.is_file():
            raise HTTPException(status_code=404, detail="file not found")
        media_type = "video/mp4" if resolved.suffix.lower() == ".mp4" else None
        return FileResponse(resolved, media_type=media_type)

    return app


app = create_app()
