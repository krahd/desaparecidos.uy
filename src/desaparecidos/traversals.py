from __future__ import annotations

import hashlib
import io
import json
import math
import os
import random
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Protocol
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont

from .cv import classify_image
from .geography import sample_uruguay_cells
from .images import Fragment, crop_from_row, descriptor_for, load_rgb
from .manifests import ManifestRow, approved_rows, row_file_path
from .paths import display_path
from .pipeline import (
    AssemblyResult,
    Stage1Output,
    TilePlacement,
    _feasibility_error,
    _render_video_ffmpeg,
    _target_canvas,
)

TraversalMode = Literal["manual", "import", "autonomous"]
TraversalScope = Literal["drawn", "uruguay"]
CompositionMode = Literal["overlay", "alternate", "split"]
TargetMode = Literal["single", "sequence"]
ReviewStatus = Literal["pending", "approved", "rejected"]

DEFAULT_TRAVERSAL_ROOT = Path("data/raw/traversals")
MAX_DISCOVERY_FRAMES = 1200
MAX_ACQUIRE_FRAMES = 600
MAX_REGIONS = 12
MIN_WALK_FRAMES = 4
MAPILLARY_IMAGES_URL = "https://graph.mapillary.com/images"
MAPILLARY_IMAGE_URL = "https://graph.mapillary.com/{image_id}"
# Minimal search fields. Requesting a thumb_*_url field inside the bbox
# /images search makes graph.mapillary.com return HTTP 500, and heavy fields
# such as creator/organization make dense-city bbox queries time out, so the
# thumbnail URL and contributor attribution are resolved one image at a time
# at download time instead (see below).
MAPILLARY_SEARCH_FIELDS = "id,computed_geometry,compass_angle,captured_at,sequence"
MAPILLARY_IMAGE_FIELDS = "thumb_2048_url,creator,organization"
MAPILLARY_SEARCH_TIMEOUT = 90  # dense-city bbox searches routinely take tens of seconds
# graph.mapillary.com returns HTTP 500 for bbox searches over dense coverage
# (~>1 km in central Montevideo, measured 2026-07-08). Dense boxes are split
# into quadrants and retried within a bounded query budget.
MAPILLARY_MAX_BBOX_DEPTH = 4
MAPILLARY_MAX_BBOX_QUERIES = 40


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


def _grouped_sequences(frames: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for frame in frames:
        groups.setdefault(str(frame.get("sequence_id") or frame.get("provider_id")), []).append(frame)
    for group in groups.values():
        group.sort(key=lambda frame: (int(frame.get("captured_at") or 0), str(frame["provider_id"])))
    return groups


def _chain_groups(groups: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Chain frame groups end-to-start by nearest neighbour, reversing groups when closer."""
    remaining = list(groups)
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


def _ordered_sequences(frames: list[dict[str, Any]], geometry: dict[str, Any]) -> list[dict[str, Any]]:
    groups = _grouped_sequences(frames)
    route = _coordinates(geometry)
    remaining = list(groups.values())
    remaining.sort(key=lambda group: min(
        _route_sort_key([float(endpoint["longitude"]), float(endpoint["latitude"])], route)
        for endpoint in (group[0], group[-1])
    ))
    return _chain_groups(remaining)


def _region_cells(geometry: dict[str, Any], regions: int) -> list[dict[str, Any]]:
    """Partition the region bounding box into a grid of GeoJSON Polygon cells."""
    west, south, east, north = _bbox(geometry)
    columns = max(1, math.ceil(math.sqrt(regions)))
    rows = max(1, math.ceil(regions / columns))
    cell_width = (east - west) / columns
    cell_height = (north - south) / rows
    cells: list[dict[str, Any]] = []
    for row in range(rows):
        for column in range(columns):
            if len(cells) >= regions:
                break
            cell_west = west + column * cell_width
            cell_south = south + row * cell_height
            cells.append({
                "type": "Polygon",
                "coordinates": [[
                    [cell_west, cell_south],
                    [cell_west + cell_width, cell_south],
                    [cell_west + cell_width, cell_south + cell_height],
                    [cell_west, cell_south + cell_height],
                    [cell_west, cell_south],
                ]],
            })
    return cells


def _coherent_region_walks(
    provider: "TraversalProvider",
    cells: list[dict[str, Any]],
    *,
    desired_frames: int,
    query_limit: int,
    max_walks: int | None = None,
) -> list[dict[str, Any]]:
    """One coherent walk per cell: the longest single capture sequence found in each.

    Each walk stays inside one provider sequence so it reads as a continuous
    street-level traversal; walks from different cells are joined with the
    existing direct-jump-cut gap policy. Cells without coverage are skipped;
    when ``max_walks`` is set, remaining candidate cells are not queried once
    enough walks have been found.
    """
    target_walks = max(1, max_walks or len(cells))
    per_region_frames = max(MIN_WALK_FRAMES, desired_frames // target_walks)
    per_region_query = min(MAX_DISCOVERY_FRAMES, max(query_limit // target_walks, per_region_frames * 4))
    seen: set[str] = set()
    walk_groups: list[list[dict[str, Any]]] = []
    for region_index, cell in enumerate(cells):
        if len(walk_groups) >= target_walks:
            break
        candidates = []
        for frame in provider.discover(cell["geometry"], limit=per_region_query):
            provider_id = str(frame.get("provider_id", ""))
            if not provider_id or provider_id in seen:
                continue
            seen.add(provider_id)
            candidates.append(frame)
        groups = list(_grouped_sequences(candidates).values())
        if not groups:
            continue
        coherent = [group for group in groups if len(group) >= MIN_WALK_FRAMES] or groups
        best = max(coherent, key=lambda group: (len(group), str(group[0].get("sequence_id", ""))))
        walk = best[:per_region_frames]
        for frame in walk:
            frame["region_index"] = region_index
            if cell.get("name"):
                frame["place_name"] = cell["name"]
                frame["place_kind"] = cell.get("kind", "locality")
        walk_groups.append(walk)
    if not walk_groups:
        raise ValueError("no street-level sequences were found in the selected region")
    return _chain_groups(walk_groups)[:desired_frames]


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

    def _auth_header(self) -> dict[str, str]:
        return {"Authorization": f"OAuth {self.token}"}

    def discover(self, geometry: dict[str, Any], *, limit: int) -> list[dict[str, Any]]:
        limit = min(MAX_DISCOVERY_FRAMES, max(1, limit))
        boxes: list[tuple[float, float, float, float, int]] = [(*_bbox(geometry), 0)]
        frames: list[dict[str, Any]] = []
        seen: set[str] = set()
        queries = 0
        while boxes and len(frames) < limit and queries < MAPILLARY_MAX_BBOX_QUERIES:
            west, south, east, north, depth = boxes.pop(0)
            queries += 1
            response = self.session.get(
                MAPILLARY_IMAGES_URL,
                params={
                    "bbox": f"{west},{south},{east},{north}",
                    "limit": limit,
                    "fields": MAPILLARY_SEARCH_FIELDS,
                },
                headers=self._auth_header(),
                timeout=MAPILLARY_SEARCH_TIMEOUT,
            )
            if response.status_code == 500 and depth < MAPILLARY_MAX_BBOX_DEPTH:
                # Dense coverage: split into quadrants and retry smaller boxes.
                mid_lon, mid_lat = (west + east) / 2, (south + north) / 2
                boxes.extend([
                    (west, south, mid_lon, mid_lat, depth + 1),
                    (mid_lon, south, east, mid_lat, depth + 1),
                    (west, mid_lat, mid_lon, north, depth + 1),
                    (mid_lon, mid_lat, east, north, depth + 1),
                ])
                continue
            response.raise_for_status()
            payload = response.json()
            for item in payload.get("data", []):
                coordinates = (item.get("computed_geometry") or {}).get("coordinates") or []
                provider_id = str(item.get("id", ""))
                if len(coordinates) < 2 or not provider_id or provider_id in seen:
                    continue
                seen.add(provider_id)
                frames.append({
                    "provider_id": provider_id,
                    "sequence_id": str(item.get("sequence", "")),
                    "longitude": float(coordinates[0]),
                    "latitude": float(coordinates[1]),
                    "compass_angle": float(item.get("compass_angle") or 0),
                    "captured_at": item.get("captured_at"),
                })
        return frames[:limit]

    def _image_details(self, provider_id: str) -> dict[str, Any]:
        """Resolve one image's thumbnail URL and contributor attribution.

        The bbox /images search returns HTTP 500 when a thumb_*_url field is
        requested and slows badly on dense cells with attribution fields, so
        both are fetched a single image at a time when the frame is actually
        downloaded. This also keeps the URL fresh (Mapillary thumbnail URLs
        are short-lived signed links) and attaches contributor attribution to
        exactly the frames that can appear in outputs.
        """
        if not provider_id:
            return {}
        response = self.session.get(
            MAPILLARY_IMAGE_URL.format(image_id=provider_id),
            params={"fields": MAPILLARY_IMAGE_FIELDS},
            headers=self._auth_header(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def download(self, frame: dict[str, Any]) -> bytes:
        # Legacy routes cached a download_url at discovery time; new routes carry
        # only the provider id and resolve fresh image details here.
        url = str(frame.get("download_url") or "")
        if not url:
            details = self._image_details(str(frame.get("provider_id", "")))
            thumb = details.get("thumb_2048_url")
            url = _clean_url(str(thumb)) if thumb else ""
            frame["creator"] = details.get("creator") or frame.get("creator") or {}
            frame["organization"] = details.get("organization") or frame.get("organization") or {}
        if not url:
            raise ValueError(f"no thumbnail available for frame {frame.get('id') or frame.get('provider_id')}")
        response = self.session.get(url, timeout=30)
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


def _walk_summary(frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    walks: list[dict[str, Any]] = []
    for frame in frames:
        sequence = str(frame.get("sequence_id", ""))
        region = frame.get("region_index")
        if not walks or walks[-1]["sequence_id"] != sequence or walks[-1]["region_index"] != region:
            walks.append({
                "region_index": region,
                "sequence_id": sequence,
                "first_frame_id": frame["id"],
                "place_name": frame.get("place_name"),
                "place_kind": frame.get("place_kind"),
                "frame_count": 0,
            })
        walks[-1]["frame_count"] += 1
    return walks


def _walk_line_geometry(frames: list[dict[str, Any]]) -> dict[str, Any]:
    """The chosen national path: a LineString through each walk's start plus the final frame."""
    coordinates: list[list[float]] = []
    previous_region: int | None = None
    for frame in frames:
        region = frame.get("region_index")
        if region != previous_region:
            coordinates.append([float(frame["longitude"]), float(frame["latitude"])])
            previous_region = region
    if frames:
        coordinates.append([float(frames[-1]["longitude"]), float(frames[-1]["latitude"])])
    if len(coordinates) < 2:
        raise ValueError("no street-level sequences were found in the sampled places")
    return {"type": "LineString", "coordinates": coordinates}


def _renumber_walks(frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Renumber region_index in chained walk order and summarise the visited places."""
    mapping: dict[int, int] = {}
    places: list[dict[str, Any]] = []
    for frame in frames:
        original = int(frame.get("region_index", 0))
        if original not in mapping:
            mapping[original] = len(mapping)
            places.append({
                "region_index": mapping[original],
                "name": frame.get("place_name") or "campo",
                "kind": frame.get("place_kind") or "rural",
            })
        frame["region_index"] = mapping[original]
    return places


def discover_traversal(
    *,
    name: str,
    mode: TraversalMode,
    geometry: dict[str, Any] | None = None,
    duration_seconds: int = 60,
    root: str | Path = DEFAULT_TRAVERSAL_ROOT,
    provider: TraversalProvider | None = None,
    max_frames: int = MAX_DISCOVERY_FRAMES,
    regions: int = 1,
    scope: TraversalScope = "drawn",
    rural_probability: float = 0.25,
    seed: int | None = None,
) -> dict[str, Any]:
    if scope == "uruguay" and mode != "autonomous":
        raise ValueError("the uruguay scope requires autonomous mode")
    if scope != "uruguay":
        if geometry is None:
            raise ValueError("route geometry is required for a drawn traversal")
        geometry = normalise_geojson(geometry)
    provider = provider or MapillaryProvider()
    limit = min(MAX_DISCOVERY_FRAMES, max(1, max_frames))
    regions = max(1, min(MAX_REGIONS, regions))
    places: list[dict[str, Any]] | None = None
    if scope == "uruguay":
        desired = min(limit, max(2, duration_seconds * 2))
        # Oversample candidate places: cells without street-level coverage are
        # skipped until `regions` coherent walks are found.
        cells = sample_uruguay_cells(
            regions * 3, rural_probability=rural_probability, rng=random.Random(seed)
        )
        frames = _coherent_region_walks(
            provider, cells, desired_frames=desired, query_limit=limit, max_walks=regions
        )
        places = _renumber_walks(frames)
        geometry = _walk_line_geometry(frames)
    elif mode == "autonomous":
        desired = min(limit, max(2, duration_seconds * 2))
        cells = [{"geometry": cell} for cell in _region_cells(geometry, regions)]
        frames = _coherent_region_walks(
            provider, cells, desired_frames=desired, query_limit=limit
        )
    else:
        raw_frames = provider.discover(geometry, limit=limit)
        deduplicated: dict[str, dict[str, Any]] = {}
        for frame in raw_frames:
            provider_id = str(frame.get("provider_id", ""))
            if provider_id:
                deduplicated.setdefault(provider_id, frame)
        frames = _ordered_sequences(list(deduplicated.values()), geometry)[:limit]
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
        "scope": scope,
        "rural_probability": rural_probability if scope == "uruguay" else None,
        "places": places,
        "regions": regions if mode == "autonomous" else None,
        "walks": _walk_summary(frames) if mode == "autonomous" else None,
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
    auto_approve: bool = False,
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
            manually_reviewed = bool(frame.get("reviewed_at")) and frame.get("review_policy") != "auto-cv-accepted"
            if manually_reviewed:
                pass  # a person's decision always survives re-acquisition
            elif auto_approve and checked.accept:
                # Explicit artist-selected policy: frames passing the local CV
                # place gate are approved automatically and remain reversible
                # through the ordinary frame review.
                frame["review_status"] = "approved"
                frame["reviewed_at"] = _now()
                frame["review_policy"] = "auto-cv-accepted"
            else:
                frame["review_status"] = "pending"
                frame.pop("review_policy", None)
        except Exception as exc:
            errors.append(f"{frame.get('id')}: {exc}")
            frame["acquisition_error"] = str(exc)
    traversal["frames"] = frames
    traversal["acquisition"] = {
        "attempted": len(frames),
        "acquired": sum(bool(frame.get("local_path")) for frame in frames),
        "auto_approve": auto_approve,
        "auto_approved": sum(frame.get("review_policy") == "auto-cv-accepted" for frame in frames),
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
        frame["review_policy"] = "manual"
    return save_traversal(traversal, root)


@dataclass(frozen=True)
class TraversalRenderSettings:
    composition: CompositionMode = "overlay"
    target_mode: TargetMode = "single"
    duration_seconds: int = 60
    fps: int = 24
    seed: int = 17
    fragment_size: int = 24
    output_width: int = 1920
    reuse_limit: int = 10000
    max_contribution_per_source: int = 0


def _fragments_for_frame(frame: dict[str, Any], fragment_size: int, limit: int = 240) -> list[Fragment]:
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
    return candidates


@dataclass(frozen=True)
class WalkAssembly:
    """An assembly built strictly in walk order, with the frame index that supplied each tile."""
    result: AssemblyResult
    placed_after_frame: list[int]
    segment_frame_ids: list[str]


def assemble_walk(
    target_row: ManifestRow,
    target_manifest: str | Path,
    frames: list[dict[str, Any]],
    settings: "TraversalRenderSettings",
) -> WalkAssembly:
    """Assemble the target incrementally from the bits found along the walk.

    Frames are consumed in traversal order. After each frame is reached, its
    fragments join the found pool and a proportional share of the still-empty
    target tiles is filled with the best-matching found fragment, so no tile
    is ever matched against a frame the walk has not reached yet.
    """
    target = crop_from_row(load_rgb(row_file_path(target_row, target_manifest)), target_row)
    target = _target_canvas(target, settings.output_width, settings.fragment_size)
    tile = settings.fragment_size
    positions = [(x, y) for y in range(0, target.height, tile) for x in range(0, target.width, tile)]
    tile_descriptors = np.stack([
        descriptor_for(target.crop((x, y, x + tile, y + tile))) for x, y in positions
    ]).astype(np.float32)

    rng = random.Random(settings.seed + sum(ord(char) for char in target_row.id))
    per_frame: list[list[Fragment]] = []
    for frame in frames:
        fragments = _fragments_for_frame(frame, tile)
        rng.shuffle(fragments)
        per_frame.append(fragments)
    total_fragments = sum(len(fragments) for fragments in per_frame)
    cap = max(0, settings.max_contribution_per_source)
    error = _feasibility_error(len(positions), total_fragments, settings.reuse_limit, len(frames), cap)
    if error:
        raise ValueError(error)

    pool: list[Fragment] = []
    descriptors = np.zeros((total_fragments, tile_descriptors.shape[1]), dtype=np.float32)
    source_of = np.zeros(total_fragments, dtype=np.intp)
    available = np.zeros(total_fragments, dtype=bool)
    frag_use = np.zeros(total_fragments, dtype=np.int64)
    source_use = np.zeros(len(frames), dtype=np.int64)
    best_dist = np.full(len(positions), np.inf, dtype=np.float32)
    best_idx = np.full(len(positions), -1, dtype=np.intp)
    filled = np.zeros(len(positions), dtype=bool)

    output = Image.new("RGB", target.size, (0, 0, 0))
    placements: list[TilePlacement] = []
    placed_after: list[int] = []
    offset = 0
    for frame_index, fragments in enumerate(per_frame):
        count = len(fragments)
        for local_index, fragment in enumerate(fragments):
            descriptors[offset + local_index] = fragment.descriptor
        pool.extend(fragments)
        source_of[offset:offset + count] = frame_index
        available[offset:offset + count] = True
        open_tiles = np.flatnonzero(~filled)
        if open_tiles.size and count:
            distances = np.linalg.norm(
                tile_descriptors[open_tiles][:, None, :] - descriptors[offset:offset + count][None, :, :],
                axis=2,
            )
            new_best = distances.argmin(axis=1)
            new_dist = distances[np.arange(open_tiles.size), new_best]
            better = new_dist < best_dist[open_tiles]
            best_dist[open_tiles[better]] = new_dist[better]
            best_idx[open_tiles[better]] = offset + new_best[better]
        offset += count
        quota = math.ceil(len(positions) * (frame_index + 1) / len(per_frame))
        while len(placements) < quota:
            open_tiles = np.flatnonzero(~filled)
            stale = open_tiles[(best_idx[open_tiles] < 0) | ~available[np.maximum(best_idx[open_tiles], 0)]]
            for tile_index in stale:
                candidates = np.flatnonzero(available[:offset])
                if candidates.size == 0:
                    raise ValueError("fragment reuse / contribution limits exhausted")
                distances = np.linalg.norm(descriptors[candidates] - tile_descriptors[tile_index], axis=1)
                pick = int(np.argmin(distances))
                best_idx[tile_index] = int(candidates[pick])
                best_dist[tile_index] = float(distances[pick])
            tile_index = int(open_tiles[int(np.argmin(best_dist[open_tiles]))])
            pool_index = int(best_idx[tile_index])
            fragment = pool[pool_index]
            x, y = positions[tile_index]
            output.paste(fragment.image, (x, y))
            placements.append(TilePlacement(
                source_id=fragment.source_id,
                fragment_id=fragment.fragment_id,
                image=fragment.image,
                dest_x=x,
                dest_y=y,
                source_x=fragment.x,
                source_y=fragment.y,
            ))
            placed_after.append(frame_index)
            filled[tile_index] = True
            frag_use[pool_index] += 1
            source_index = int(source_of[pool_index])
            source_use[source_index] += 1
            if frag_use[pool_index] >= settings.reuse_limit:
                available[pool_index] = False
            if cap > 0 and source_use[source_index] >= cap:
                available[np.flatnonzero(source_of[:offset] == source_index)] = False

    source_usage = {
        str(frames[index]["id"]): int(count)
        for index, count in enumerate(source_use)
        if count > 0
    }
    fragment_usage: dict[str, int] = {}
    for index, count in enumerate(frag_use):
        if count > 0:
            fragment_usage[pool[index].fragment_id] = int(count)
    result = AssemblyResult(output, target, source_usage, fragment_usage, placements)
    return WalkAssembly(result, placed_after, [str(frame["id"]) for frame in frames])


def _split_segments(frames: list[dict[str, Any]], count: int) -> list[list[dict[str, Any]]]:
    if len(frames) < count:
        raise ValueError(
            f"the ordered target sequence needs at least one approved frame per target: "
            f"{len(frames)} frames for {count} targets"
        )
    bounds = [round(index * len(frames) / count) for index in range(count + 1)]
    return [frames[bounds[index]:bounds[index + 1]] for index in range(count)]


def _fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (0, 0, 0))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def _walk_progress(walk: WalkAssembly, reached_frame: int) -> Image.Image:
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


def _traversal_video_frames(
    segments: list[list[dict[str, Any]]],
    targets: list[ManifestRow],
    walks: list[WalkAssembly],
    settings: TraversalRenderSettings,
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
        frame_count = max(1, math.ceil(len(frames) * progress))
        with Image.open(str(frames[min(len(frames) - 1, frame_count - 1)]["local_path"])) as source_image:
            street = _fit(source_image.convert("RGB"), walk.result.image.size)
        portrait = _walk_progress(walk, frame_count - 1)
        if progress > 0.80:
            portrait = Image.blend(portrait, walk.result.image, min(1.0, (progress - 0.80) / 0.10))
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
    segments = _split_segments(frames, len(selected)) if settings.target_mode == "sequence" else [frames]
    walks = [
        assemble_walk(target, target_manifest, segment, settings)
        for target, segment in zip(selected, segments)
    ]
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    stem = f"seguimos-buscando-{traversal_id}-{settings.seed}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    still_path = output_root / f"{stem}.png"
    video_path = output_root / f"{stem}.mp4"
    sidecar_path = output_root / f"{stem}.json"
    walks[-1].result.image.save(still_path)
    if not _render_video_ffmpeg(
        _traversal_video_frames(segments, selected, walks, settings),
        walks[0].result.image.size,
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
        "regions": traversal.get("regions"),
        "walks": traversal.get("walks"),
        "gap_policy": "direct-jump-cut",
        "sequence_jumps": [frame["id"] for frame in frames if frame.get("sequence_jump")],
        "approved_frame_ids": [frame["id"] for frame in frames],
        "target_ids": [target.id for target in selected],
        "target_id": selected[0].id if len(selected) == 1 else "sequence",
        "target_segments": {target.id: walk.segment_frame_ids for target, walk in zip(selected, walks)},
        "composition": settings.composition,
        "target_mode": settings.target_mode,
        "settings": asdict(settings),
        "source_usage": {target.id: walk.result.source_usage for target, walk in zip(selected, walks)},
        "source_image_display": "approved-traversal-with-contributing-fragments",
        "assembly_policy": "incremental-found-fragments",
        "future_source_frames_used": False,
        "generated_at": _now(),
        "still_path": display_path(still_path),
        "video_path": display_path(video_path),
        "video_format": "h264",
    }
    sidecar_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
    return [Stage1Output(str(sidecar["target_id"]), display_path(still_path), display_path(sidecar_path), display_path(video_path))]


def run_autonomous_uruguay(
    *,
    name: str = "Seguimos buscando · Uruguay",
    regions: int = 4,
    duration_seconds: int = 60,
    max_frames: int = 240,
    rural_probability: float = 0.25,
    seed: int | None = None,
    root: str | Path = DEFAULT_TRAVERSAL_ROOT,
    target_manifest: str | Path,
    output_dir: str | Path,
    target_ids: list[str],
    settings: TraversalRenderSettings | None = None,
    provider: TraversalProvider | None = None,
) -> tuple[dict[str, Any], list[Stage1Output]]:
    """One-shot Seguimos buscando run: sample places across Uruguay, discover
    coherent walks, acquire frames, auto-approve those passing the CV place
    gate, and render the video. Every stage's record stays reviewable on disk
    afterwards, and manual frame review can still amend the traversal.
    """
    traversal = discover_traversal(
        name=name,
        mode="autonomous",
        scope="uruguay",
        duration_seconds=duration_seconds,
        root=root,
        provider=provider,
        max_frames=max_frames,
        regions=regions,
        rural_probability=rural_probability,
        seed=seed,
    )
    traversal = acquire_traversal(
        str(traversal["id"]), root=root, provider=provider,
        max_frames=max_frames, auto_approve=True,
    )
    approved = [
        frame for frame in traversal.get("frames", [])
        if frame.get("review_status") == "approved" and frame.get("local_path")
    ]
    if not approved:
        raise ValueError(
            "no acquired frames passed the CV place gate; open the traversal for manual review"
        )
    outputs = render_traversal(
        str(traversal["id"]), target_manifest, output_dir, target_ids, settings, root=root
    )
    return load_traversal(str(traversal["id"]), root), outputs
