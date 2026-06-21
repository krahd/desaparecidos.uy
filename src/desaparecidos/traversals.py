from __future__ import annotations

import hashlib
import io
import json
import math
import os
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Protocol
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import requests
from PIL import Image, ImageDraw, ImageFont

from .cv import classify_image
from .images import Fragment, descriptor_for
from .manifests import ManifestRow, approved_rows
from .paths import display_path
from .pipeline import (
    AssemblyResult,
    Stage1Output,
    Stage1Settings,
    _render_video_ffmpeg,
    assemble_target_with_trace,
)

TraversalMode = Literal["manual", "import", "autonomous"]
CompositionMode = Literal["overlay", "alternate", "split"]
TargetMode = Literal["single", "sequence"]
ReviewStatus = Literal["pending", "approved", "rejected"]

DEFAULT_TRAVERSAL_ROOT = Path("data/raw/traversals")
MAX_DISCOVERY_FRAMES = 1200
MAX_ACQUIRE_FRAMES = 600
MAPILLARY_IMAGES_URL = "https://graph.mapillary.com/images"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_url(value: str) -> str:
    """Remove credentials from stored URLs without altering signed provider URLs."""
    parts = urlsplit(value)
    if not parts.netloc or "@" not in parts.netloc:
        return value
    return urlunsplit((parts.scheme, parts.netloc.rsplit("@", 1)[-1], parts.path, parts.query, parts.fragment))


def _coordinates(geometry: dict[str, Any]) -> list[list[float]]:
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if kind == "LineString" and isinstance(coordinates, list):
        return [[float(point[0]), float(point[1])] for point in coordinates if isinstance(point, list) and len(point) >= 2]
    if kind == "MultiLineString" and isinstance(coordinates, list):
        return [
            [float(point[0]), float(point[1])]
            for line in coordinates if isinstance(line, list)
            for point in line if isinstance(point, list) and len(point) >= 2
        ]
    if kind == "Polygon" and isinstance(coordinates, list) and coordinates:
        ring = coordinates[0]
        return [[float(point[0]), float(point[1])] for point in ring if isinstance(point, list) and len(point) >= 2]
    raise ValueError("geometry must be a GeoJSON LineString, MultiLineString, or Polygon")


def normalise_geojson(value: dict[str, Any]) -> dict[str, Any]:
    if value.get("type") == "Feature":
        value = value.get("geometry") or {}
    if value.get("type") == "FeatureCollection":
        features = value.get("features") or []
        lines = []
        for feature in features:
            geometry = normalise_geojson(feature)
            if geometry["type"] == "LineString":
                lines.append(geometry["coordinates"])
            elif geometry["type"] == "MultiLineString":
                lines.extend(geometry["coordinates"])
        if not lines:
            raise ValueError("GeoJSON FeatureCollection contains no line geometry")
        value = {"type": "MultiLineString", "coordinates": lines}
    points = _coordinates(value)
    if len(points) < 2:
        raise ValueError("route geometry requires at least two coordinates")
    return {"type": str(value["type"]), "coordinates": value["coordinates"]}


def parse_route_import(content: str, file_format: Literal["geojson", "gpx"]) -> dict[str, Any]:
    if file_format == "geojson":
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("GeoJSON root must be an object")
        return normalise_geojson(parsed)
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise ValueError(f"invalid GPX: {exc}") from exc
    points: list[list[float]] = []
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] not in {"trkpt", "rtept"}:
            continue
        try:
            points.append([float(element.attrib["lon"]), float(element.attrib["lat"])])
        except (KeyError, ValueError) as exc:
            raise ValueError("GPX route point has invalid latitude or longitude") from exc
    if len(points) < 2:
        raise ValueError("GPX requires at least two track or route points")
    return {"type": "LineString", "coordinates": points}


def _bbox(geometry: dict[str, Any]) -> tuple[float, float, float, float]:
    points = _coordinates(geometry)
    longitudes = [point[0] for point in points]
    latitudes = [point[1] for point in points]
    return min(longitudes), min(latitudes), max(longitudes), max(latitudes)


def _point_segment_distance(point: list[float], start: list[float], end: list[float]) -> float:
    px, py = point
    ax, ay = start
    bx, by = end
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    scale = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + scale * dx), py - (ay + scale * dy))


def _route_sort_key(point: list[float], route: list[list[float]]) -> tuple[int, float]:
    distances = [
        _point_segment_distance(point, route[index], route[index + 1])
        for index in range(len(route) - 1)
    ]
    segment = min(range(len(distances)), key=distances.__getitem__)
    return segment, distances[segment]


def _ordered_sequences(
    frames: list[dict[str, Any]], geometry: dict[str, Any], mode: TraversalMode
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for frame in frames:
        groups.setdefault(str(frame.get("sequence_id") or frame.get("provider_id")), []).append(frame)
    for group in groups.values():
        group.sort(key=lambda frame: (int(frame.get("captured_at") or 0), str(frame["provider_id"])))
    route = _coordinates(geometry)
    remaining = list(groups.values())
    if mode != "autonomous":
        remaining.sort(key=lambda group: min(
            _route_sort_key([float(endpoint["longitude"]), float(endpoint["latitude"])], route)
            for endpoint in (group[0], group[-1])
        ))
    else:
        remaining.sort(key=lambda group: (
            float(group[0]["latitude"]), float(group[0]["longitude"]), str(group[0]["sequence_id"])
        ))
    ordered: list[dict[str, Any]] = []
    while remaining:
        if not ordered:
            group = remaining.pop(0)
        else:
            end = [float(ordered[-1]["longitude"]), float(ordered[-1]["latitude"])]
            group_index, reverse = min(
                (
                    (index, direction)
                    for index, candidate in enumerate(remaining)
                    for direction in (False, True)
                ),
                key=lambda value: math.hypot(
                    end[0] - float((remaining[value[0]][-1] if value[1] else remaining[value[0]][0])["longitude"]),
                    end[1] - float((remaining[value[0]][-1] if value[1] else remaining[value[0]][0])["latitude"]),
                ),
            )
            group = remaining.pop(group_index)
            if reverse:
                group.reverse()
        ordered.extend(group)
    return ordered


class TraversalProvider(Protocol):
    name: str

    def discover(self, geometry: dict[str, Any], *, limit: int) -> list[dict[str, Any]]: ...

    def download(self, frame: dict[str, Any]) -> bytes: ...


class MapillaryProvider:
    name = "mapillary"

    def __init__(self, token: str | None = None, session: requests.Session | None = None) -> None:
        self.token = token or os.environ.get("MAPILLARY_ACCESS_TOKEN", "")
        if not self.token:
            raise ValueError("MAPILLARY_ACCESS_TOKEN is required for Mapillary discovery")
        self.session = session or requests.Session()

    def discover(self, geometry: dict[str, Any], *, limit: int) -> list[dict[str, Any]]:
        west, south, east, north = _bbox(geometry)
        response = self.session.get(
            MAPILLARY_IMAGES_URL,
            params={
                "bbox": f"{west},{south},{east},{north}",
                "limit": min(MAX_DISCOVERY_FRAMES, max(1, limit)),
                "fields": "id,thumb_2048_url,computed_geometry,compass_angle,captured_at,sequence,creator,organization",
            },
            headers={"Authorization": f"OAuth {self.token}"},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        frames: list[dict[str, Any]] = []
        for item in payload.get("data", []):
            coordinates = (item.get("computed_geometry") or {}).get("coordinates") or []
            if len(coordinates) < 2 or not item.get("thumb_2048_url"):
                continue
            frames.append({
                "provider_id": str(item.get("id", "")),
                "sequence_id": str(item.get("sequence", "")),
                "longitude": float(coordinates[0]),
                "latitude": float(coordinates[1]),
                "compass_angle": float(item.get("compass_angle") or 0),
                "captured_at": item.get("captured_at"),
                "download_url": _clean_url(str(item["thumb_2048_url"])),
                "creator": item.get("creator") or {},
                "organization": item.get("organization") or {},
            })
        return frames

    def download(self, frame: dict[str, Any]) -> bytes:
        response = self.session.get(str(frame["download_url"]), timeout=30)
        response.raise_for_status()
        return response.content


def _route_path(root: str | Path, traversal_id: str) -> Path:
    if not traversal_id or traversal_id in {".", ".."} or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for char in traversal_id):
        raise ValueError("invalid traversal id")
    root_path = Path(root).resolve()
    path = (root_path / traversal_id / "route.json").resolve()
    path.relative_to(root_path)
    return path


def save_traversal(traversal: dict[str, Any], root: str | Path = DEFAULT_TRAVERSAL_ROOT) -> dict[str, Any]:
    path = _route_path(root, str(traversal["id"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    traversal["updated_at"] = _now()
    path.write_text(json.dumps(traversal, ensure_ascii=False, indent=2), encoding="utf-8")
    return traversal


def load_traversal(traversal_id: str, root: str | Path = DEFAULT_TRAVERSAL_ROOT) -> dict[str, Any]:
    path = _route_path(root, traversal_id)
    if not path.exists():
        raise ValueError(f"traversal not found: {traversal_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_traversals(root: str | Path = DEFAULT_TRAVERSAL_ROOT) -> list[dict[str, Any]]:
    root_path = Path(root)
    if not root_path.exists():
        return []
    items = []
    for path in root_path.glob("*/route.json"):
        try:
            traversal = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        frames = traversal.get("frames", [])
        traversal["summary"] = {
            "frame_count": len(frames),
            "approved_count": sum(frame.get("review_status") == "approved" for frame in frames),
            "pending_count": sum(frame.get("review_status") == "pending" for frame in frames),
            "rejected_count": sum(frame.get("review_status") == "rejected" for frame in frames),
        }
        items.append(traversal)
    return sorted(items, key=lambda item: item.get("updated_at", ""), reverse=True)


def discover_traversal(
    *,
    name: str,
    mode: TraversalMode,
    geometry: dict[str, Any],
    duration_seconds: int = 60,
    root: str | Path = DEFAULT_TRAVERSAL_ROOT,
    provider: TraversalProvider | None = None,
    max_frames: int = MAX_DISCOVERY_FRAMES,
) -> dict[str, Any]:
    geometry = normalise_geojson(geometry)
    provider = provider or MapillaryProvider()
    limit = min(MAX_DISCOVERY_FRAMES, max(1, max_frames))
    raw_frames = provider.discover(geometry, limit=limit)
    deduplicated: dict[str, dict[str, Any]] = {}
    for frame in raw_frames:
        provider_id = str(frame.get("provider_id", ""))
        if provider_id:
            deduplicated.setdefault(provider_id, frame)
    frames = _ordered_sequences(list(deduplicated.values()), geometry, mode)
    desired = min(limit, max(2, duration_seconds * 2)) if mode == "autonomous" else limit
    frames = frames[:desired]
    previous_sequence = ""
    for index, frame in enumerate(frames):
        sequence = str(frame.get("sequence_id", ""))
        frame.update({
            "id": f"frame-{index + 1:05d}",
            "ordinal": index,
            "review_status": "pending",
            "local_path": "",
            "sha256": "",
            "cv_label": "not-acquired",
            "cv_reason": "",
            "sequence_jump": bool(index and sequence != previous_sequence),
        })
        previous_sequence = sequence
    traversal_id = f"route-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:8]}"
    traversal = {
        "schema_version": 1,
        "id": traversal_id,
        "name": name.strip() or traversal_id,
        "artwork": "seguimos-buscando",
        "provider": provider.name,
        "mode": mode,
        "geometry": geometry,
        "duration_seconds": max(1, duration_seconds),
        "gap_policy": "direct-jump-cut",
        "release_status": "internal_unreviewed",
        "attribution": "Mapillary imagery; retain provider and contributor attribution before public release",
        "created_at": _now(),
        "updated_at": _now(),
        "frames": frames,
    }
    return save_traversal(traversal, root)


def acquire_traversal(
    traversal_id: str,
    *,
    root: str | Path = DEFAULT_TRAVERSAL_ROOT,
    provider: TraversalProvider | None = None,
    max_frames: int = MAX_ACQUIRE_FRAMES,
) -> dict[str, Any]:
    traversal = load_traversal(traversal_id, root)
    if traversal.get("provider") != "mapillary":
        raise ValueError(f"unsupported traversal provider: {traversal.get('provider')}")
    provider = provider or MapillaryProvider()
    frames = traversal.get("frames", [])[:min(MAX_ACQUIRE_FRAMES, max(1, max_frames))]
    directory = _route_path(root, traversal_id).parent / "frames"
    directory.mkdir(parents=True, exist_ok=True)
    sha_paths: dict[str, Path] = {}
    errors: list[str] = []
    for frame in frames:
        if frame.get("duplicate_of") and frame.get("review_status") == "rejected":
            continue
        destination = directory / f"{frame['id']}.jpg"
        try:
            if destination.exists():
                data = destination.read_bytes()
            else:
                data = provider.download(frame)
            digest = hashlib.sha256(data).hexdigest()
            if digest in sha_paths:
                frame["duplicate_of"] = next(
                    candidate["id"] for candidate in frames if candidate.get("sha256") == digest
                )
                frame["review_status"] = "rejected"
                frame["cv_label"] = "duplicate"
                continue
            Image.open(io.BytesIO(data)).verify()
            destination.write_bytes(data)
            sha_paths[digest] = destination
            with Image.open(destination) as stored_image:
                checked = classify_image(stored_image.convert("RGB"), "places")
            frame["local_path"] = display_path(destination)
            frame["sha256"] = digest
            frame["cv_label"] = checked.label
            frame["cv_reason"] = checked.reason
            frame["cv_accept"] = checked.accept
            frame["review_status"] = "pending"
        except Exception as exc:
            errors.append(f"{frame.get('id')}: {exc}")
            frame["acquisition_error"] = str(exc)
    traversal["frames"] = frames
    traversal["acquisition"] = {
        "attempted": len(frames),
        "acquired": sum(bool(frame.get("local_path")) for frame in frames),
        "errors": errors,
        "completed_at": _now(),
    }
    return save_traversal(traversal, root)


def review_traversal_frames(
    traversal_id: str,
    frame_ids: list[str],
    status: ReviewStatus,
    *,
    root: str | Path = DEFAULT_TRAVERSAL_ROOT,
) -> dict[str, Any]:
    traversal = load_traversal(traversal_id, root)
    requested = set(frame_ids)
    known = {str(frame.get("id")) for frame in traversal.get("frames", [])}
    missing = requested - known
    if missing:
        raise ValueError(f"unknown traversal frame ids: {', '.join(sorted(missing))}")
    for frame in traversal.get("frames", []):
        if frame.get("id") not in requested:
            continue
        if status == "approved" and frame.get("duplicate_of"):
            raise ValueError(f"frame {frame.get('id')} duplicates {frame.get('duplicate_of')} and cannot be approved")
        if status == "approved" and not frame.get("local_path"):
            raise ValueError(f"frame {frame.get('id')} must be acquired before approval")
        if status == "approved" and frame.get("cv_accept") is False:
            raise ValueError(
                f"frame {frame.get('id')} failed the local place-image gate ({frame.get('cv_label')})"
            )
        frame["review_status"] = status
        frame["reviewed_at"] = _now()
    return save_traversal(traversal, root)


@dataclass(frozen=True)
class TraversalRenderSettings:
    composition: CompositionMode = "overlay"
    target_mode: TargetMode = "single"
    duration_seconds: int = 60
    fps: int = 12
    seed: int = 17
    fragment_size: int = 24
    output_width: int = 720
    reuse_limit: int = 10000
    max_contribution_per_source: int = 0


def _frame_fragments(frames: list[dict[str, Any]], fragment_size: int, limit: int = 240) -> list[Fragment]:
    fragments: list[Fragment] = []
    for frame in frames:
        with Image.open(str(frame["local_path"])) as source_image:
            image = source_image.convert("RGB")
        candidates: list[Fragment] = []
        for y in range(0, max(1, image.height - fragment_size + 1), fragment_size):
            for x in range(0, max(1, image.width - fragment_size + 1), fragment_size):
                patch = image.crop((x, y, x + fragment_size, y + fragment_size))
                if patch.size != (fragment_size, fragment_size):
                    patch = patch.resize((fragment_size, fragment_size))
                candidates.append(Fragment(
                    str(frame["id"]), f"{frame['id']}:{x}:{y}", patch, descriptor_for(patch), x, y
                ))
        if len(candidates) > limit:
            indexes = [int(index * (len(candidates) - 1) / (limit - 1)) for index in range(limit)]
            candidates = [candidates[index] for index in indexes]
        fragments.extend(candidates)
    return fragments


def _fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (0, 0, 0))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def _assembly_progress(assembly: AssemblyResult, available_ids: set[str]) -> Image.Image:
    mosaic = Image.new("RGB", assembly.image.size, (0, 0, 0))
    mask = Image.new("L", assembly.image.size, 0)
    draw = ImageDraw.Draw(mask)
    for placement in assembly.placements:
        if placement.source_id not in available_ids:
            continue
        mosaic.paste(placement.image, (placement.dest_x, placement.dest_y))
        draw.rectangle(
            (placement.dest_x, placement.dest_y, placement.dest_x + placement.image.width, placement.dest_y + placement.image.height),
            fill=255,
        )
    return Image.composite(mosaic, Image.new("RGB", assembly.image.size, (0, 0, 0)), mask)


def _traversal_video_frames(
    frames: list[dict[str, Any]],
    targets: list[ManifestRow],
    assemblies: list[AssemblyResult],
    settings: TraversalRenderSettings,
) -> Iterable[Image.Image]:
    total = max(settings.fps, settings.duration_seconds * settings.fps)
    segment_length = max(1, total // len(targets))
    font = ImageFont.load_default()
    for output_index in range(total):
        target_index = min(len(targets) - 1, output_index // segment_length)
        local_index = output_index - target_index * segment_length
        progress = local_index / max(1, segment_length - 1)
        frame_count = max(1, math.ceil(len(frames) * (target_index + progress) / len(targets)))
        with Image.open(str(frames[min(len(frames) - 1, frame_count - 1)]["local_path"])) as source_image:
            street = _fit(source_image.convert("RGB"), assemblies[target_index].image.size)
        available = {str(frame["id"]) for frame in frames[:frame_count]}
        portrait = _assembly_progress(assemblies[target_index], available)
        if progress > 0.80:
            portrait = Image.blend(portrait, assemblies[target_index].image, min(1.0, (progress - 0.80) / 0.10))
        if progress > 0.93:
            portrait = Image.blend(portrait, Image.new("RGB", portrait.size, (0, 0, 0)), (progress - 0.93) / 0.07)
        if settings.composition == "split":
            output = Image.new("RGB", street.size, (0, 0, 0))
            half = street.width // 2
            output.paste(street.crop((0, 0, half, street.height)), (0, 0))
            output.paste(portrait.resize((street.width - half, street.height)), (half, 0))
        elif settings.composition == "alternate":
            phase = (local_index // max(1, settings.fps * 2)) % 2
            output = street if phase == 0 and progress < 0.80 else portrait
        else:
            output = Image.blend(street, portrait, min(0.82, progress * 0.95))
        if 0.80 <= progress <= 0.95:
            draw = ImageDraw.Draw(output)
            draw.rectangle((0, output.height - 40, output.width, output.height), fill=(0, 0, 0))
            draw.text((18, output.height - 28), targets[target_index].values.get("name", targets[target_index].id), fill=(245, 245, 240), font=font)
        yield output


def render_traversal(
    traversal_id: str,
    target_manifest: str | Path,
    output_dir: str | Path,
    target_ids: list[str],
    settings: TraversalRenderSettings | None = None,
    *,
    root: str | Path = DEFAULT_TRAVERSAL_ROOT,
) -> list[Stage1Output]:
    settings = settings or TraversalRenderSettings()
    traversal = load_traversal(traversal_id, root)
    frames = [
        frame for frame in traversal.get("frames", [])
        if frame.get("review_status") == "approved" and frame.get("local_path") and Path(str(frame["local_path"])).exists()
    ]
    if not frames:
        raise ValueError("traversal has no acquired, approved frames")
    targets = approved_rows(target_manifest, "targets", require_files=True)
    selected = [target for target_id in target_ids for target in targets if target.id == target_id]
    if settings.target_mode == "single":
        selected = selected[:1]
    if not selected:
        raise ValueError("select at least one approved target")
    fragments = _frame_fragments(frames, settings.fragment_size)
    stage_settings = Stage1Settings(
        seed=settings.seed,
        fragment_size=settings.fragment_size,
        reuse_limit=settings.reuse_limit,
        output_width=settings.output_width,
        max_contribution_per_source=settings.max_contribution_per_source,
    )
    assemblies = [assemble_target_with_trace(target, target_manifest, fragments, stage_settings) for target in selected]
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    stem = f"seguimos-buscando-{traversal_id}-{settings.seed}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    still_path = output_root / f"{stem}.png"
    video_path = output_root / f"{stem}.mp4"
    sidecar_path = output_root / f"{stem}.json"
    assemblies[-1].image.save(still_path)
    if not _render_video_ffmpeg(
        _traversal_video_frames(frames, selected, assemblies, settings),
        assemblies[0].image.size,
        video_path,
        fps=settings.fps,
    ):
        raise RuntimeError("Browser-playable MP4 rendering requires ffmpeg with libx264")
    sidecar = {
        "artwork": "seguimos-buscando",
        "source_kind": "street-level-traversal",
        "traversal_id": traversal_id,
        "provider": traversal.get("provider"),
        "attribution": traversal.get("attribution"),
        "release_status": "internal_unreviewed",
        "route_geometry": traversal.get("geometry"),
        "gap_policy": "direct-jump-cut",
        "sequence_jumps": [frame["id"] for frame in frames if frame.get("sequence_jump")],
        "approved_frame_ids": [frame["id"] for frame in frames],
        "target_ids": [target.id for target in selected],
        "target_id": selected[0].id if len(selected) == 1 else "sequence",
        "composition": settings.composition,
        "target_mode": settings.target_mode,
        "settings": asdict(settings),
        "source_usage": {assembly_target.id: assembly.source_usage for assembly_target, assembly in zip(selected, assemblies)},
        "source_image_display": "approved-traversal-with-contributing-fragments",
        "future_source_frames_used": False,
        "generated_at": _now(),
        "still_path": display_path(still_path),
        "video_path": display_path(video_path),
        "video_format": "h264",
    }
    sidecar_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
    return [Stage1Output(str(sidecar["target_id"]), display_path(still_path), display_path(sidecar_path), display_path(video_path))]
