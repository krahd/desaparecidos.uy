from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from types import SimpleNamespace

from PIL import Image
import pytest

import desaparecidos.traversals as traversal_module
from desaparecidos.manifests import approved_rows
from desaparecidos.traversals import (
    TraversalRenderSettings,
    acquire_traversal,
    assemble_walk,
    discover_traversal,
    parse_route_import,
    render_traversal,
    review_traversal_frames,
)


def image_bytes(colour: tuple[int, int, int]) -> bytes:
    buffer = io.BytesIO()
    image = Image.new("RGB", (400, 320), colour)
    pixels = image.load()
    for y in range(320):
        for x in range(400):
            pixels[x, y] = (
                min(255, colour[0] + x // 4),
                min(255, colour[1] + y // 3),
                min(255, colour[2] + (x + y) // 10),
            )
    for x in range(20, 380, 36):
        for y in range(80, 250):
            if x <= (x // 36) * 36 + 28:
                pixels[x, y] = (45, 50, 55)
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


class FakeProvider:
    name = "mapillary"

    def __init__(self) -> None:
        self.downloads = 0

    def discover(self, geometry: dict[str, object], *, limit: int) -> list[dict[str, object]]:
        del geometry
        items = [
            {
                "provider_id": "two",
                "sequence_id": "sequence-a",
                "longitude": -56.1,
                "latitude": -34.8,
                "compass_angle": 12,
                "captured_at": 2,
                "download_url": "https://example.invalid/two.jpg",
            },
            {
                "provider_id": "one",
                "sequence_id": "sequence-a",
                "longitude": -56.2,
                "latitude": -34.9,
                "compass_angle": 10,
                "captured_at": 1,
                "download_url": "https://example.invalid/one.jpg",
            },
            {
                "provider_id": "one",
                "sequence_id": "sequence-a",
                "longitude": -56.2,
                "latitude": -34.9,
                "compass_angle": 10,
                "captured_at": 1,
                "download_url": "https://example.invalid/duplicate-metadata.jpg",
            },
        ]
        return items[:limit]

    def download(self, frame: dict[str, object]) -> bytes:
        self.downloads += 1
        return image_bytes((90, 120, 150) if frame["provider_id"] == "one" else (150, 100, 70))


class RegionProvider:
    """Two coherent sequences in different halves of the country plus scattered noise frames."""

    name = "mapillary"

    def __init__(self) -> None:
        self.downloads = 0
        self.queried_bboxes: list[tuple[float, float, float, float]] = []
        self.frames: list[dict[str, object]] = []
        for index in range(6):
            self.frames.append({
                "provider_id": f"west-{index}",
                "sequence_id": "sequence-west",
                "longitude": -57.5 + index * 0.01,
                "latitude": -34.5,
                "compass_angle": 0,
                "captured_at": index + 1,
                "download_url": f"https://example.invalid/west-{index}.jpg",
            })
        for index in range(5):
            self.frames.append({
                "provider_id": f"east-{index}",
                "sequence_id": "sequence-east",
                "longitude": -54.0 + index * 0.01,
                "latitude": -33.5,
                "compass_angle": 0,
                "captured_at": index + 1,
                "download_url": f"https://example.invalid/east-{index}.jpg",
            })
        for index in range(3):
            self.frames.append({
                "provider_id": f"noise-{index}",
                "sequence_id": f"sequence-noise-{index}",
                "longitude": -57.0 - index * 0.2,
                "latitude": -34.0,
                "compass_angle": 0,
                "captured_at": 1,
                "download_url": f"https://example.invalid/noise-{index}.jpg",
            })

    def discover(self, geometry: dict[str, object], *, limit: int) -> list[dict[str, object]]:
        west, south, east, north = traversal_module._bbox(geometry)
        self.queried_bboxes.append((west, south, east, north))
        inside = [
            dict(frame) for frame in self.frames
            if west <= float(frame["longitude"]) <= east and south <= float(frame["latitude"]) <= north
        ]
        return inside[:limit]

    def download(self, frame: dict[str, object]) -> bytes:
        self.downloads += 1
        seed = sum(ord(char) for char in str(frame["provider_id"]))
        return image_bytes((seed % 200, (seed * 3) % 200, (seed * 7) % 200))


def region() -> dict[str, object]:
    return {
        "type": "Polygon",
        "coordinates": [[[-58.0, -35.0], [-53.0, -35.0], [-53.0, -33.0], [-58.0, -33.0], [-58.0, -35.0]]],
    }


def test_autonomous_discovery_builds_coherent_walks_per_region(tmp_path: Path) -> None:
    provider = RegionProvider()
    traversal = discover_traversal(
        name="Country walks",
        mode="autonomous",
        geometry=region(),
        duration_seconds=10,
        root=tmp_path,
        provider=provider,
        max_frames=100,
        regions=2,
    )
    assert len(provider.queried_bboxes) == 2
    frames = traversal["frames"]
    # Each walk stays inside one provider sequence; the noise singletons are never selected.
    sequences = [frame["sequence_id"] for frame in frames]
    assert set(sequences) == {"sequence-west", "sequence-east"}
    blocks = [sequences[0]]
    for sequence in sequences[1:]:
        if sequence != blocks[-1]:
            blocks.append(sequence)
    assert len(blocks) == 2
    # Walk order is coherent within each sequence: consecutive captured_at values.
    for sequence_id in set(sequences):
        captured = [int(frame["captured_at"]) for frame in frames if frame["sequence_id"] == sequence_id]
        assert captured == sorted(captured) or captured == sorted(captured, reverse=True)
    assert all(frame["region_index"] in {0, 1} for frame in frames)
    assert {frame["region_index"] for frame in frames} == {0, 1}
    jumps = [frame["id"] for frame in frames if frame["sequence_jump"]]
    assert len(jumps) == 1
    walks = traversal["walks"]
    assert [walk["frame_count"] for walk in walks] == [
        sum(1 for frame in frames if frame["sequence_id"] == walk["sequence_id"]) for walk in walks
    ]
    assert traversal["regions"] == 2


def test_autonomous_discovery_without_coverage_raises(tmp_path: Path) -> None:
    class EmptyProvider:
        name = "mapillary"

        def discover(self, geometry: dict[str, object], *, limit: int) -> list[dict[str, object]]:
            del geometry, limit
            return []

        def download(self, frame: dict[str, object]) -> bytes:
            raise AssertionError("unused")

    with pytest.raises(ValueError, match="no street-level sequences"):
        discover_traversal(
            name="Empty",
            mode="autonomous",
            geometry=region(),
            root=tmp_path,
            provider=EmptyProvider(),
            regions=3,
        )


def route() -> dict[str, object]:
    return {"type": "LineString", "coordinates": [[-56.25, -34.95], [-56.0, -34.7]]}


def test_route_import_supports_geojson_and_gpx() -> None:
    geojson = parse_route_import(json.dumps({"type": "Feature", "properties": {}, "geometry": route()}), "geojson")
    assert geojson["type"] == "LineString"
    gpx = parse_route_import(
        '<gpx xmlns="http://www.topografix.com/GPX/1/1"><trk><trkseg>'
        '<trkpt lat="-34.9" lon="-56.2"/><trkpt lat="-34.8" lon="-56.1"/>'
        '</trkseg></trk></gpx>',
        "gpx",
    )
    assert gpx["coordinates"] == [[-56.2, -34.9], [-56.1, -34.8]]


def test_discovery_deduplicates_and_persists_provider_provenance(tmp_path: Path) -> None:
    traversal = discover_traversal(
        name="Test route",
        mode="manual",
        geometry=route(),
        root=tmp_path,
        provider=FakeProvider(),
        max_frames=10,
    )
    assert [frame["provider_id"] for frame in traversal["frames"]] == ["one", "two"]
    assert traversal["provider"] == "mapillary"
    assert traversal["release_status"] == "internal_unreviewed"
    assert traversal["gap_policy"] == "direct-jump-cut"
    assert (tmp_path / traversal["id"] / "route.json").exists()
    capped = discover_traversal(
        name="Capped", mode="manual", geometry=route(), root=tmp_path, provider=FakeProvider(), max_frames=1
    )
    assert len(capped["frames"]) == 1


def test_acquisition_cache_and_manual_review_gate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        traversal_module, "classify_image",
        lambda _image, _kind: SimpleNamespace(accept=True, label="place-photo", reason="fixture"),
    )
    provider = FakeProvider()
    traversal = discover_traversal(
        name="Test route", mode="manual", geometry=route(), root=tmp_path, provider=provider
    )
    acquired = acquire_traversal(traversal["id"], root=tmp_path, provider=provider)
    assert provider.downloads == 2
    assert all(frame["review_status"] == "pending" for frame in acquired["frames"])
    assert all(frame["local_path"] for frame in acquired["frames"])

    acquire_traversal(traversal["id"], root=tmp_path, provider=provider)
    assert provider.downloads == 2

    reviewed = review_traversal_frames(
        traversal["id"], [acquired["frames"][0]["id"]], "approved", root=tmp_path
    )
    assert reviewed["frames"][0]["review_status"] == "approved"
    with pytest.raises(ValueError, match="unknown traversal frame"):
        review_traversal_frames(traversal["id"], ["no-frame"], "approved", root=tmp_path)


def test_acquisition_rejects_exact_duplicates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        traversal_module, "classify_image",
        lambda _image, _kind: SimpleNamespace(accept=True, label="place-photo", reason="fixture"),
    )

    class DuplicateProvider(FakeProvider):
        def download(self, frame: dict[str, object]) -> bytes:
            del frame
            self.downloads += 1
            return image_bytes((90, 120, 150))

    provider = DuplicateProvider()
    traversal = discover_traversal(
        name="Duplicates", mode="manual", geometry=route(), root=tmp_path, provider=provider
    )
    acquired = acquire_traversal(traversal["id"], root=tmp_path, provider=provider)
    duplicate = acquired["frames"][1]
    assert duplicate["review_status"] == "rejected"
    assert duplicate["duplicate_of"] == acquired["frames"][0]["id"]
    with pytest.raises(ValueError, match="duplicates"):
        review_traversal_frames(traversal["id"], [duplicate["id"]], "approved", root=tmp_path)


def write_target_manifest(tmp_path: Path) -> Path:
    Image.new("RGB", (32, 40), (130, 120, 110)).save(tmp_path / "target.png")
    manifest = tmp_path / "targets.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "id", "name", "source_url", "source_page", "licence_or_terms", "accessed_at",
            "local_path", "review_status", "birth_date", "disappearance_date",
            "disappearance_place", "notes", "crop_x", "crop_y", "crop_width", "crop_height",
        ])
        writer.writerow([
            "target-one", "Target One", "local://target.png", "fixture", "fixture", "2026-06-20",
            "target.png", "approved", "", "1976", "", "", "", "", "", "",
        ])
        writer.writerow([
            "target-two", "Target Two", "local://target.png", "fixture", "fixture", "2026-06-20",
            "target.png", "approved", "", "1977", "", "", "", "", "", "",
        ])
    return manifest


def test_assemble_walk_uses_only_already_found_frames(tmp_path: Path) -> None:
    first = tmp_path / "walk-frame-1.jpg"
    second = tmp_path / "walk-frame-2.jpg"
    Image.open(io.BytesIO(image_bytes((90, 120, 150)))).save(first)
    Image.open(io.BytesIO(image_bytes((150, 100, 70)))).save(second)
    frames = [
        {"id": "walk-frame-1", "local_path": str(first)},
        {"id": "walk-frame-2", "local_path": str(second)},
    ]
    manifest = write_target_manifest(tmp_path)
    target = approved_rows(manifest, "targets", require_files=True)[0]
    walk = assemble_walk(
        target,
        manifest,
        frames,
        TraversalRenderSettings(fragment_size=8, output_width=32),
    )
    tile_count = (walk.result.image.width // 8) * (walk.result.image.height // 8)
    assert len(walk.result.placements) == tile_count
    assert len(walk.placed_after_frame) == tile_count
    assert walk.placed_after_frame == sorted(walk.placed_after_frame)
    assert walk.segment_frame_ids == ["walk-frame-1", "walk-frame-2"]
    # Tiles placed before the second frame is reached can only use bits found in the first frame.
    for placement, placed_after in zip(walk.result.placements, walk.placed_after_frame):
        if placed_after == 0:
            assert placement.source_id == "walk-frame-1"
    # Half of the portrait is scheduled from the first frame, the rest after the second.
    assert sum(1 for value in walk.placed_after_frame if value == 0) == tile_count // 2


@pytest.mark.parametrize(
    ("composition", "target_mode", "target_ids"),
    [
        ("overlay", "single", ["target-one"]),
        ("alternate", "sequence", ["target-one", "target-two"]),
        ("split", "single", ["target-two"]),
    ],
)
def test_render_records_approved_frames_and_never_uses_future_frames(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    composition: str,
    target_mode: str,
    target_ids: list[str],
) -> None:
    monkeypatch.setattr(
        traversal_module, "classify_image",
        lambda _image, _kind: SimpleNamespace(accept=True, label="place-photo", reason="fixture"),
    )
    provider = FakeProvider()
    traversal = discover_traversal(
        name="Test route", mode="manual", geometry=route(), root=tmp_path / "routes", provider=provider
    )
    acquired = acquire_traversal(traversal["id"], root=tmp_path / "routes", provider=provider)
    review_traversal_frames(
        traversal["id"], [frame["id"] for frame in acquired["frames"]], "approved", root=tmp_path / "routes"
    )
    rendered_frames: list[Image.Image] = []

    def fake_render(frames: object, size: tuple[int, int], output_path: Path, *, fps: int) -> bool:
        del size, fps
        rendered_frames.extend(list(frames))  # type: ignore[arg-type]
        output_path.write_bytes(b"mp4")
        return True

    monkeypatch.setattr(traversal_module, "_render_video_ffmpeg", fake_render)
    outputs = render_traversal(
        traversal["id"],
        write_target_manifest(tmp_path),
        tmp_path / "outputs",
        target_ids,
        TraversalRenderSettings(
            composition=composition,  # type: ignore[arg-type]
            target_mode=target_mode,  # type: ignore[arg-type]
            duration_seconds=1,
            fps=2,
            fragment_size=8,
            output_width=32,
        ),
        root=tmp_path / "routes",
    )
    assert len(rendered_frames) == 2
    sidecar = json.loads(Path(outputs[0].sidecar_path).read_text(encoding="utf-8"))
    assert sidecar["artwork"] == "seguimos-buscando"
    assert sidecar["future_source_frames_used"] is False
    assert sidecar["assembly_policy"] == "incremental-found-fragments"
    assert sidecar["approved_frame_ids"] == [frame["id"] for frame in acquired["frames"]]
    assert sidecar["release_status"] == "internal_unreviewed"
    assert sidecar["composition"] == composition
    assert sidecar["target_mode"] == target_mode
    segments = sidecar["target_segments"]
    assert list(segments) == target_ids
    all_segment_frames = [frame_id for ids in segments.values() for frame_id in ids]
    assert all_segment_frames == [frame["id"] for frame in acquired["frames"]]
