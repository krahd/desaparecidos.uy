from __future__ import annotations

import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image


def _placements(history: dict[str, Any]) -> list[dict[str, Any]]:
    placements = history.get("placements")
    if not isinstance(placements, list):
        raise ValueError("placement history has no placements list")
    return [placement for placement in placements if isinstance(placement, dict)]


def participation_metrics(history: dict[str, Any]) -> dict[str, Any]:
    placements = _placements(history)
    counts = Counter(str(item.get("source_id", "")) for item in placements)
    counts.pop("", None)
    total = sum(counts.values())
    shares = {source: count / total for source, count in counts.items()} if total else {}
    hhi = sum(share * share for share in shares.values())
    entropy = -sum(share * math.log(share) for share in shares.values() if share > 0)
    effective_sources = math.exp(entropy) if shares else 0.0
    return {
        "placement_count": total,
        "source_count": len(counts),
        "source_counts": dict(sorted(counts.items())),
        "max_source_share": max(shares.values(), default=0.0),
        "hhi": hhi,
        "effective_source_count": effective_sources,
    }


def _rect(item: dict[str, Any], field: str) -> tuple[int, int, int, int]:
    value = item.get(field, {})
    x = int(value.get("x", 0))
    y = int(value.get("y", 0))
    width = int(value.get("width", 0))
    height = int(value.get("height", 0))
    return x, y, width, height


def _touches(first: tuple[int, int, int, int], second: tuple[int, int, int, int]) -> bool:
    ax, ay, aw, ah = first
    bx, by, bw, bh = second
    horizontal = (ax + aw == bx or bx + bw == ax) and max(ay, by) < min(ay + ah, by + bh)
    vertical = (ay + ah == by or by + bh == ay) and max(ax, bx) < min(ax + aw, bx + bw)
    return horizontal or vertical


def source_reconstitution_metrics(history: dict[str, Any]) -> dict[str, Any]:
    """Measure structural risks without claiming biometric anonymity.

    The metrics quantify whether fragments from one source become adjacent or
    form a connected target-side region. They do not determine whether a living
    source person is recognisable and therefore cannot replace human review.
    """
    placements = _placements(history)
    by_source: dict[str, list[int]] = defaultdict(list)
    for index, placement in enumerate(placements):
        by_source[str(placement.get("source_id", ""))].append(index)
    same_source_edges = 0
    largest_component = 0
    largest_component_source = ""
    components_by_source: dict[str, int] = {}
    rects = [_rect(item, "matched_target_rect") for item in placements]
    for source, indexes in by_source.items():
        neighbours: dict[int, list[int]] = {index: [] for index in indexes}
        for offset, first in enumerate(indexes):
            for second in indexes[offset + 1 :]:
                if _touches(rects[first], rects[second]):
                    same_source_edges += 1
                    neighbours[first].append(second)
                    neighbours[second].append(first)
        seen: set[int] = set()
        source_largest = 0
        for start in indexes:
            if start in seen:
                continue
            queue: deque[int] = deque([start])
            seen.add(start)
            size = 0
            while queue:
                current = queue.popleft()
                size += 1
                for neighbour in neighbours[current]:
                    if neighbour not in seen:
                        seen.add(neighbour)
                        queue.append(neighbour)
            source_largest = max(source_largest, size)
        components_by_source[source] = source_largest
        if source_largest > largest_component:
            largest_component = source_largest
            largest_component_source = source
    return {
        "same_source_adjacency_edges": same_source_edges,
        "largest_same_source_component": largest_component,
        "largest_component_source": largest_component_source,
        "largest_component_by_source": dict(sorted(components_by_source.items())),
        "manual_recognisability_review_required": True,
        "anonymity_determined": False,
    }


def _overlap(first: tuple[int, int, int, int], second: tuple[int, int, int, int]) -> int:
    ax, ay, aw, ah = first
    bx, by, bw, bh = second
    width = max(0, min(ax + aw, bx + bw) - max(ax, bx))
    height = max(0, min(ay + ah, by + bh) - max(ay, by))
    return width * height


def visual_grammar_metrics(history: dict[str, Any]) -> dict[str, Any]:
    placements = _placements(history)
    geometries = [_rect(item, "render_geometry") for item in placements]
    overlap_pairs = 0
    overlap_area = 0
    for index, first in enumerate(geometries):
        for second in geometries[index + 1 :]:
            area = _overlap(first, second)
            if area:
                overlap_pairs += 1
                overlap_area += area
    rotations = [
        abs(float(item.get("render_geometry", {}).get("rotation_degrees", 0.0)))
        for item in placements
    ]
    opacities = [
        float(item.get("render_geometry", {}).get("opacity", 1.0))
        for item in placements
    ]
    return {
        "visual_grammar": history.get("visual_grammar"),
        "overlap_pair_count": overlap_pairs,
        "summed_overlap_area": overlap_area,
        "mean_absolute_rotation_degrees": float(np.mean(rotations)) if rotations else 0.0,
        "minimum_opacity": min(opacities, default=1.0),
    }


def temporal_causality_metrics(history: dict[str, Any]) -> dict[str, Any]:
    placements = _placements(history)
    sequence = [str(value) for value in history.get("source_sequence", [])]
    source_index = {source: index for index, source in enumerate(sequence)}
    violations: list[str] = []
    encounter_indexes: list[int] = []
    for placement in placements:
        placement_id = str(placement.get("placement_id", ""))
        source = str(placement.get("source_id", ""))
        time = placement.get("time", {})
        encounter = int(time.get("encounter_index", -1))
        encounter_indexes.append(encounter)
        known = source_index.get(source)
        if known is not None and encounter < known:
            violations.append(placement_id)
        if encounter < 0:
            violations.append(placement_id)
    return {
        "source_sequence_length": len(sequence),
        "maximum_encounter_index": max(encounter_indexes, default=-1),
        "causality_violation_count": len(set(violations)),
        "violating_placement_ids": sorted(set(violations)),
        "future_sources_used": bool(violations),
    }


def _luminance(image: Image.Image, size: tuple[int, int]) -> np.ndarray:
    return np.asarray(image.convert("L").resize(size, Image.Resampling.LANCZOS), dtype=np.float32) / 255.0


def target_structure_metrics(
    generated: Image.Image,
    target: Image.Image,
    *,
    evaluation_size: tuple[int, int] = (192, 256),
) -> dict[str, float | str]:
    """Compare low-level target structure without making identity claims."""
    output = _luminance(generated, evaluation_size)
    reference = _luminance(target, evaluation_size)
    mae = float(np.mean(np.abs(output - reference)))
    output_dx = np.diff(output, axis=1)
    output_dy = np.diff(output, axis=0)
    reference_dx = np.diff(reference, axis=1)
    reference_dy = np.diff(reference, axis=0)
    gradient_mae = float(
        (np.mean(np.abs(output_dx - reference_dx)) + np.mean(np.abs(output_dy - reference_dy))) / 2
    )
    output_flat = output.ravel() - float(output.mean())
    reference_flat = reference.ravel() - float(reference.mean())
    denominator = float(np.linalg.norm(output_flat) * np.linalg.norm(reference_flat))
    correlation = float(np.dot(output_flat, reference_flat) / denominator) if denominator else 0.0
    return {
        "luminance_mae": mae,
        "gradient_mae": gradient_mae,
        "luminance_correlation": correlation,
        "interpretation": "low-level structural comparison only; not face recognition or identity verification",
    }


def evaluate_history(history: dict[str, Any]) -> dict[str, Any]:
    return {
        "participation": participation_metrics(history),
        "source_reconstitution": source_reconstitution_metrics(history),
        "visual_grammar": visual_grammar_metrics(history),
        "temporal_causality": temporal_causality_metrics(history),
    }


def evaluate_sidecar(path: str | Path) -> dict[str, Any]:
    sidecar_path = Path(path)
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    if "placement_history" in sidecar:
        histories = {str(sidecar.get("target_id", "target")): sidecar["placement_history"]}
    else:
        histories = sidecar.get("placement_histories", {})
    if not isinstance(histories, dict) or not histories:
        raise ValueError("sidecar contains no placement history")
    return {
        "evaluation_schema": "desaparecidos.uy/artwork-evaluation/1.0",
        "sidecar": str(sidecar_path),
        "artwork": sidecar.get("artwork"),
        "targets": {
            target_id: evaluate_history(history)
            for target_id, history in histories.items()
            if isinstance(history, dict)
        },
        "limits": [
            "structural metrics do not determine memorial adequacy",
            "target comparison does not verify identity",
            "source-fragment metrics do not guarantee anonymity",
            "public release still requires full human, rights, and contextual review",
        ],
    }
