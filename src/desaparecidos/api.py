from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .crawl import crawl_pages, crawl_pages_combined
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
from .persons import (
    add_portrait_candidate,
    delete_person,
    export_targets_manifest,
    get_person,
    list_persons_api,
    load_sources_registry,
    process_selected_portrait,
    search_plan,
    set_selected_portrait,
    upsert_person,
)
from .pipeline import (
    ArtworkKind,
    DEFAULT_MAX_CONTRIBUTION_PER_SOURCE,
    Stage1Settings,
    VideoSourceLayout,
    run_stage1,
)
from .traversals import (
    CompositionMode,
    TargetMode,
    TraversalMode,
    TraversalRenderSettings,
    acquire_traversal,
    discover_traversal,
    list_traversals,
    load_traversal,
    normalise_geojson,
    parse_route_import,
    render_traversal,
    review_traversal_frames,
    run_autonomous_uruguay,
)


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
    max_contribution_per_source: int = Field(default=DEFAULT_MAX_CONTRIBUTION_PER_SOURCE, ge=0, le=1000000)
    search_scan_frames_per_candidate: int = Field(default=2, ge=1, le=24)
    search_scan_max_candidates: int = Field(default=120, ge=0, le=10000)
    video_source_layout: VideoSourceLayout = "grid"
    make_video: bool = False
    target_id: str | None = None
    artwork: ArtworkKind = "estan-en-todas-partes"


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


class CombinedCrawlRequest(BaseModel):
    pages: list[str]
    places_manifest: str = "data/manifests/crawled-places.csv"
    people_manifest: str = "data/manifests/crawled-people.csv"
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


class PersonSaveRequest(BaseModel):
    store: str = "data/persons/disappeared.json"
    person: dict[str, Any]


class PersonDeleteRequest(BaseModel):
    store: str = "data/persons/disappeared.json"
    person_id: str


class PersonPortraitAddRequest(BaseModel):
    store: str = "data/persons/disappeared.json"
    person_id: str
    image_url: str
    source_page: str = ""
    source_id: str = ""
    source_name: str = ""
    licence_or_terms: str = ""
    notes: str = ""
    raw_root: str = "assets/targets/disappeared/raw"
    overwrite: bool = False


class PersonPortraitSelectRequest(BaseModel):
    store: str = "data/persons/disappeared.json"
    person_id: str
    candidate_id: str


class PersonPortraitProcessRequest(BaseModel):
    store: str = "data/persons/disappeared.json"
    person_id: str
    candidate_id: str
    selected_root: str = "assets/targets/disappeared/selected"
    aspect: float = Field(default=0.75, gt=0, le=4)
    use_face: bool = True
    max_side: int = Field(default=1200, ge=128, le=4096)
    overwrite: bool = True


class PersonExportTargetsRequest(BaseModel):
    store: str = "data/persons/disappeared.json"
    manifest: str = "data/manifests/targets.csv"
    approved: bool = False


class TraversalDiscoverRequest(BaseModel):
    name: str = "Uruguay traversal"
    mode: TraversalMode = "manual"
    scope: Literal["drawn", "uruguay"] = "drawn"
    geometry: dict[str, Any] | None = None
    import_content: str = ""
    import_format: Literal["geojson", "gpx"] | None = None
    duration_seconds: int = Field(default=60, ge=1, le=3600)
    max_frames: int = Field(default=600, ge=1, le=1200)
    regions: int = Field(default=1, ge=1, le=12)
    rural_probability: float = Field(default=0.25, ge=0.0, le=1.0)
    seed: int | None = None
    root: str = "data/raw/traversals"


class TraversalAcquireRequest(BaseModel):
    traversal_id: str
    root: str = "data/raw/traversals"
    max_frames: int = Field(default=600, ge=1, le=600)
    auto_approve: bool = False


class TraversalAutoRequest(BaseModel):
    name: str = "Seguimos buscando · Uruguay"
    regions: int = Field(default=4, ge=1, le=12)
    duration_seconds: int = Field(default=60, ge=1, le=3600)
    max_frames: int = Field(default=240, ge=1, le=600)
    rural_probability: float = Field(default=0.25, ge=0.0, le=1.0)
    seed: int | None = None
    root: str = "data/raw/traversals"
    targets: str = "data/manifests/targets.csv"
    output_dir: str = "outputs/stage1"
    target_ids: list[str]
    target_mode: TargetMode = "single"
    composition: CompositionMode = "overlay"
    fps: int = Field(default=24, ge=1, le=60)
    render_seed: int = 17
    fragment_size: int = Field(default=24, ge=8, le=128)
    output_width: int = Field(default=1920, ge=120, le=4096)
    reuse_limit: int = Field(default=10000, ge=1, le=100000)
    max_contribution_per_source: int = Field(default=0, ge=0, le=1000000)


class TraversalReviewRequest(BaseModel):
    frame_ids: list[str]
    review_status: Literal["approved", "pending", "rejected"]
    root: str = "data/raw/traversals"


class TraversalGenerateRequest(BaseModel):
    traversal_id: str
    targets: str = "data/manifests/targets.csv"
    output_dir: str = "outputs/stage1"
    traversal_root: str = "data/raw/traversals"
    target_ids: list[str]
    target_mode: TargetMode = "single"
    composition: CompositionMode = "overlay"
    duration_seconds: int = Field(default=60, ge=1, le=3600)
    fps: int = Field(default=24, ge=1, le=60)
    seed: int = 17
    fragment_size: int = Field(default=24, ge=8, le=128)
    output_width: int = Field(default=1920, ge=120, le=4096)
    reuse_limit: int = Field(default=10000, ge=1, le=100000)
    max_contribution_per_source: int = Field(default=0, ge=0, le=1000000)


def _normalise_contribution_cap(value: int) -> int:
    return max(0, value)


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
    def config() -> dict[str, str | int]:
        return {
            "target_manifest": "data/manifests/targets.csv",
            "source_manifest": "data/manifests/places.csv",
            "people_manifest": "data/manifests/people.csv",
            "person_store": "data/persons/disappeared.json",
            "output_dir": "outputs/stage1",
            "default_max_contribution_per_source": DEFAULT_MAX_CONTRIBUTION_PER_SOURCE,
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

    @app.get("/api/persons")
    def persons(store: str = "data/persons/disappeared.json") -> dict[str, Any]:
        try:
            return list_persons_api(safe_project_path(store))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/persons/save")
    def save_person(request: PersonSaveRequest) -> dict[str, Any]:
        try:
            person = upsert_person(safe_project_path(request.store), request.person)
            return {"ok": True, "person": person}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/persons/delete")
    def remove_person(request: PersonDeleteRequest) -> dict[str, Any]:
        try:
            return delete_person(safe_project_path(request.store), request.person_id)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/persons/sources")
    def person_sources() -> dict[str, Any]:
        try:
            return {"ok": True, "registry": load_sources_registry()}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/persons/search-plan")
    def persons_search_plan(store: str = "data/persons/disappeared.json") -> dict[str, Any]:
        try:
            return search_plan(safe_project_path(store))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/persons/{person_id}")
    def person(person_id: str, store: str = "data/persons/disappeared.json") -> dict[str, Any]:
        try:
            return {"ok": True, "person": get_person(safe_project_path(store), person_id)}
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/persons/portrait/add")
    def persons_add_portrait(request: PersonPortraitAddRequest) -> dict[str, Any]:
        try:
            person = add_portrait_candidate(
                safe_project_path(request.store),
                request.person_id,
                image_url=request.image_url,
                source_page=request.source_page,
                source_id=request.source_id,
                source_name=request.source_name,
                licence_or_terms=request.licence_or_terms,
                notes=request.notes,
                raw_root=safe_project_path(request.raw_root),
                overwrite=request.overwrite,
            )
            return {"ok": True, "person": person}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/persons/portrait/select")
    def persons_select_portrait(request: PersonPortraitSelectRequest) -> dict[str, Any]:
        try:
            person = set_selected_portrait(
                safe_project_path(request.store),
                request.person_id,
                request.candidate_id,
            )
            return {"ok": True, "person": person}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/persons/portrait/process")
    def persons_process_portrait(request: PersonPortraitProcessRequest) -> dict[str, Any]:
        try:
            person = process_selected_portrait(
                safe_project_path(request.store),
                request.person_id,
                request.candidate_id,
                selected_root=safe_project_path(request.selected_root),
                aspect=request.aspect,
                use_face=request.use_face,
                max_side=request.max_side,
                overwrite=request.overwrite,
            )
            return {"ok": True, "person": person}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/persons/export-targets")
    def persons_export_targets(request: PersonExportTargetsRequest) -> dict[str, Any]:
        try:
            return export_targets_manifest(
                safe_project_path(request.store),
                safe_project_path(request.manifest),
                approved=request.approved,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

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

    @app.post("/api/crawl/combined")
    def crawl_combined(request: CombinedCrawlRequest) -> dict[str, object]:
        try:
            summary = crawl_pages_combined(
                request.pages,
                safe_project_path(request.places_manifest),
                safe_project_path(request.people_manifest),
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

    @app.get("/api/traversals")
    def traversals(root: str = "data/raw/traversals") -> dict[str, Any]:
        try:
            return {"ok": True, "items": list_traversals(safe_project_path(root))}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/traversals/{traversal_id}")
    def traversal(traversal_id: str, root: str = "data/raw/traversals") -> dict[str, Any]:
        try:
            return {"ok": True, "traversal": load_traversal(traversal_id, safe_project_path(root))}
        except Exception as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/api/traversals/discover")
    def traversal_discover(request: TraversalDiscoverRequest) -> dict[str, Any]:
        try:
            geometry: dict[str, Any] | None = None
            if request.scope != "uruguay":
                if request.import_format:
                    geometry = parse_route_import(request.import_content, request.import_format)
                elif request.geometry:
                    geometry = normalise_geojson(request.geometry)
                else:
                    raise ValueError("route geometry or imported GeoJSON/GPX is required")
            result = discover_traversal(
                name=request.name,
                mode=request.mode,
                geometry=geometry,
                duration_seconds=request.duration_seconds,
                root=safe_project_path(request.root),
                max_frames=request.max_frames,
                regions=request.regions,
                scope=request.scope,
                rural_probability=request.rural_probability,
                seed=request.seed,
            )
            return {"ok": True, "traversal": result}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/traversals/acquire")
    def traversal_acquire(request: TraversalAcquireRequest) -> dict[str, Any]:
        try:
            result = acquire_traversal(
                request.traversal_id,
                root=safe_project_path(request.root),
                max_frames=request.max_frames,
                auto_approve=request.auto_approve,
            )
            return {"ok": True, "traversal": result}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/traversals/auto")
    def traversal_auto(request: TraversalAutoRequest) -> dict[str, Any]:
        settings = TraversalRenderSettings(
            composition=request.composition,
            target_mode=request.target_mode,
            duration_seconds=request.duration_seconds,
            fps=request.fps,
            seed=request.render_seed,
            fragment_size=request.fragment_size,
            output_width=request.output_width,
            reuse_limit=request.reuse_limit,
            max_contribution_per_source=request.max_contribution_per_source,
        )
        try:
            traversal, outputs = run_autonomous_uruguay(
                name=request.name,
                regions=request.regions,
                duration_seconds=request.duration_seconds,
                max_frames=request.max_frames,
                rural_probability=request.rural_probability,
                seed=request.seed,
                root=safe_project_path(request.root),
                target_manifest=safe_project_path(request.targets),
                output_dir=safe_project_path(request.output_dir),
                target_ids=request.target_ids,
                settings=settings,
            )
            return {
                "ok": True,
                "traversal": traversal,
                "outputs": [output.__dict__ for output in outputs],
            }
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/traversals/{traversal_id}/frames/review")
    def traversal_review(traversal_id: str, request: TraversalReviewRequest) -> dict[str, Any]:
        try:
            result = review_traversal_frames(
                traversal_id,
                request.frame_ids,
                request.review_status,
                root=safe_project_path(request.root),
            )
            return {"ok": True, "traversal": result}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/generate/traversal")
    def generate_traversal(request: TraversalGenerateRequest) -> dict[str, Any]:
        settings = TraversalRenderSettings(
            composition=request.composition,
            target_mode=request.target_mode,
            duration_seconds=request.duration_seconds,
            fps=request.fps,
            seed=request.seed,
            fragment_size=request.fragment_size,
            output_width=request.output_width,
            reuse_limit=request.reuse_limit,
            max_contribution_per_source=request.max_contribution_per_source,
        )
        try:
            generated = render_traversal(
                request.traversal_id,
                safe_project_path(request.targets),
                safe_project_path(request.output_dir),
                request.target_ids,
                settings,
                root=safe_project_path(request.traversal_root),
            )
            return {"ok": True, "outputs": [output.__dict__ for output in generated]}
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/generate")
    def generate(request: GenerateRequest) -> dict[str, Any]:
        settings = Stage1Settings(
            seed=request.seed,
            fragment_size=request.fragment_size,
            reuse_limit=request.reuse_limit,
            output_width=request.output_width,
            max_contribution_per_source=_normalise_contribution_cap(request.max_contribution_per_source),
            search_scan_frames_per_candidate=request.search_scan_frames_per_candidate,
            search_scan_max_candidates=request.search_scan_max_candidates,
            video_source_layout=request.video_source_layout,
            make_video=request.make_video,
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
