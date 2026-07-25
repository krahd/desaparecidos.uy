from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from typing import Any, Iterable, Literal, Protocol, Sequence

from PIL import Image

PlacementGrammar = Literal["grid", "irregular", "overlap"]
TargetSalience = Literal["uniform", "portrait"]
PLACEMENT_HISTORY_SCHEMA = "desaparecidos.uy/placement-history/1.0"


class PlacementLike(Protocol):
    source_id: str
    fragment_id: str
    image: Image.Image
    dest_x: int
    dest_y: int
    source_x: int
    source_y: int


@dataclass(frozen=True)
class PlacementGeometry:
    x: int
    y: int
    width: int
    height: int
    rotation_degrees: float
    opacity: float
    z_index: int

    def to_dict(self) -> dict[str, int | float]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "rotation_degrees": round(self.rotation_degrees, 4),
            "opacity": round(self.opacity, 4),
            "z_index": self.z_index,
        }


def _stable_seed(seed: int, *parts: object) -> int:
    payload = "\x1f".join([str(seed), *(str(part) for part in parts)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big", signed=False)


def ordered_target_positions(
    width: int,
    height: int,
    tile: int,
    mode: TargetSalience,
) -> list[tuple[int, int]]:
    """Return deterministic target-tile order.

    ``uniform`` preserves row-major order. ``portrait`` allocates scarce source
    material first to an intentionally simple set of target-side facial regions.
    It does not inspect or identify source persons and does not claim biometric
    landmark detection; it is an explicit visual-priority control for reviewed,
    portrait-oriented target images.
    """
    positions = [(x, y) for y in range(0, height, tile) for x in range(0, width, tile)]
    if mode == "uniform":
        return positions
    if mode != "portrait":
        raise ValueError(f"unsupported target salience mode: {mode}")

    regions = (
        (0.34, 0.38, 0.09, 1.00),  # left eye
        (0.66, 0.38, 0.09, 1.00),  # right eye
        (0.50, 0.64, 0.12, 0.92),  # mouth
        (0.50, 0.50, 0.26, 0.42),  # central facial structure
        (0.50, 0.30, 0.36, 0.16),  # upper silhouette / forehead
    )

    def score(position: tuple[int, int]) -> tuple[float, int, int]:
        x, y = position
        nx = (x + tile / 2) / max(1, width)
        ny = (y + tile / 2) / max(1, height)
        salience = 0.0
        for cx, cy, radius, weight in regions:
            distance2 = (nx - cx) ** 2 + (ny - cy) ** 2
            salience += weight * math.exp(-distance2 / max(1e-9, 2 * radius * radius))
        return (-salience, y, x)

    return sorted(positions, key=score)


def geometry_for_placement(
    placement: PlacementLike,
    *,
    grammar: PlacementGrammar,
    canvas_size: tuple[int, int],
    seed: int,
    target_id: str,
    index: int,
) -> PlacementGeometry:
    width, height = canvas_size
    base_width, base_height = placement.image.size
    if grammar == "grid":
        return PlacementGeometry(
            placement.dest_x,
            placement.dest_y,
            base_width,
            base_height,
            0.0,
            1.0,
            index,
        )

    rng = random.Random(_stable_seed(seed, target_id, placement.fragment_id, index, grammar))
    if grammar == "irregular":
        scale = rng.uniform(0.90, 1.12)
        rotation = rng.uniform(-5.0, 5.0)
        jitter = 0.20
        opacity = 1.0
    elif grammar == "overlap":
        scale = rng.uniform(1.18, 1.52)
        rotation = rng.uniform(-9.0, 9.0)
        jitter = 0.34
        opacity = rng.uniform(0.86, 1.0)
    else:
        raise ValueError(f"unsupported placement grammar: {grammar}")

    fragment_width = max(1, int(round(base_width * scale)))
    fragment_height = max(1, int(round(base_height * scale)))
    x = int(round(placement.dest_x + rng.uniform(-base_width * jitter, base_width * jitter)))
    y = int(round(placement.dest_y + rng.uniform(-base_height * jitter, base_height * jitter)))
    x = max(-fragment_width // 2, min(width - fragment_width // 2, x))
    y = max(-fragment_height // 2, min(height - fragment_height // 2, y))
    return PlacementGeometry(x, y, fragment_width, fragment_height, rotation, opacity, index)


def geometries_for(
    placements: Sequence[PlacementLike],
    *,
    grammar: PlacementGrammar,
    canvas_size: tuple[int, int],
    seed: int,
    target_id: str,
) -> list[PlacementGeometry]:
    return [
        geometry_for_placement(
            placement,
            grammar=grammar,
            canvas_size=canvas_size,
            seed=seed,
            target_id=target_id,
            index=index,
        )
        for index, placement in enumerate(placements)
    ]


def _transformed_fragment(image: Image.Image, geometry: PlacementGeometry) -> Image.Image:
    fragment = image.convert("RGBA")
    if fragment.size != (geometry.width, geometry.height):
        fragment = fragment.resize((geometry.width, geometry.height), Image.Resampling.LANCZOS)
    if geometry.opacity < 1.0:
        alpha = fragment.getchannel("A").point(lambda value: int(round(value * geometry.opacity)))
        fragment.putalpha(alpha)
    if geometry.rotation_degrees:
        fragment = fragment.rotate(
            geometry.rotation_degrees,
            resample=Image.Resampling.BICUBIC,
            expand=True,
        )
    return fragment


def render_placements(
    placements: Sequence[PlacementLike],
    canvas_size: tuple[int, int],
    *,
    grammar: PlacementGrammar,
    seed: int,
    target_id: str,
    background: tuple[int, int, int],
) -> Image.Image:
    """Render a deterministic final composition from matched fragments."""
    if grammar == "grid":
        output = Image.new("RGB", canvas_size, background)
        for placement in placements:
            output.paste(placement.image, (placement.dest_x, placement.dest_y))
        return output

    output = Image.new("RGBA", canvas_size, (*background, 255))
    geometries = geometries_for(
        placements,
        grammar=grammar,
        canvas_size=canvas_size,
        seed=seed,
        target_id=target_id,
    )
    for placement, geometry in sorted(
        zip(placements, geometries), key=lambda item: item[1].z_index
    ):
        fragment = _transformed_fragment(placement.image, geometry)
        x = geometry.x - (fragment.width - geometry.width) // 2
        y = geometry.y - (fragment.height - geometry.height) // 2
        output.alpha_composite(fragment, (x, y))
    return output.convert("RGB")


def _source_sequence(placements: Sequence[PlacementLike]) -> list[str]:
    sequence: list[str] = []
    for placement in placements:
        if placement.source_id not in sequence:
            sequence.append(placement.source_id)
    return sequence


def build_placement_history(
    placements: Sequence[PlacementLike],
    canvas_size: tuple[int, int],
    *,
    grammar: PlacementGrammar,
    seed: int,
    target_id: str,
    source_sequence: Sequence[str] | None = None,
    placed_after_frame: Sequence[int] | None = None,
) -> dict[str, Any]:
    """Build a versioned, replayable account of how an output was constituted."""
    if placed_after_frame is not None and len(placed_after_frame) != len(placements):
        raise ValueError("placed_after_frame must contain one entry per placement")
    sequence = list(source_sequence or _source_sequence(placements))
    source_index = {source_id: index for index, source_id in enumerate(sequence)}
    geometries = geometries_for(
        placements,
        grammar=grammar,
        canvas_size=canvas_size,
        seed=seed,
        target_id=target_id,
    )
    count = max(1, len(placements))
    records: list[dict[str, Any]] = []
    for index, (placement, geometry) in enumerate(zip(placements, geometries)):
        encounter_index = (
            int(placed_after_frame[index])
            if placed_after_frame is not None
            else source_index.get(placement.source_id, 0)
        )
        enter = index / count
        settle = min(1.0, (index + 1) / count)
        records.append(
            {
                "placement_id": f"{target_id}:{index:06d}",
                "source_id": placement.source_id,
                "fragment_id": placement.fragment_id,
                "source_rect": {
                    "x": placement.source_x,
                    "y": placement.source_y,
                    "width": placement.image.width,
                    "height": placement.image.height,
                },
                "matched_target_rect": {
                    "x": placement.dest_x,
                    "y": placement.dest_y,
                    "width": placement.image.width,
                    "height": placement.image.height,
                },
                "render_geometry": geometry.to_dict(),
                "time": {
                    "encounter_index": encounter_index,
                    "enter_normalised": round(enter, 6),
                    "settle_normalised": round(settle, 6),
                    "exit_normalised": None,
                },
            }
        )
    return {
        "schema": PLACEMENT_HISTORY_SCHEMA,
        "target_id": target_id,
        "canvas": {"width": canvas_size[0], "height": canvas_size[1]},
        "visual_grammar": grammar,
        "seed": seed,
        "source_sequence": sequence,
        "placement_count": len(records),
        "timeline_unit": "normalised-output-process",
        "placements": records,
    }


def placements_visible_after(
    placements: Sequence[PlacementLike],
    placed_after_frame: Sequence[int],
    reached_frame: int,
) -> list[PlacementLike]:
    if len(placements) != len(placed_after_frame):
        raise ValueError("placed_after_frame must contain one entry per placement")
    return [
        placement
        for placement, frame_index in zip(placements, placed_after_frame)
        if frame_index <= reached_frame
    ]
