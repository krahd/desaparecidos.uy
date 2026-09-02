from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from PIL import Image

from .placement_history import PLACEMENT_HISTORY_SCHEMA

TEMPORAL_CAUSALITY_EVALUATOR_SCHEMA = "desaparecidos.uy/temporal-causality-evaluator/1.0"


def _placements(history: dict[str, Any]) -> list[dict[str, Any]]:
    placements = history.get("placements")
    if not isinstance(placements, list):
        raise ValueError("placement history has no placements list")
    if any(not isinstance(placement, dict) for placement in placements):
        raise ValueError("placement history contains a non-object placement")
    return placements


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
    if history.get("schema") != PLACEMENT_HISTORY_SCHEMA:
        raise ValueError("unsupported or missing placement history schema")
    placements = _placements(history)
    if not placements:
        raise ValueError("placement history contains no placements")
    declared_count = history.get("placement_count")
    if isinstance(declared_count, bool) or not isinstance(declared_count, int):
        raise ValueError("placement history has no valid placement_count")
    if declared_count != len(placements):
        raise ValueError("placement history placement_count does not match placements")
    raw_sequence = history.get("source_sequence")
    if not isinstance(raw_sequence, list) or not raw_sequence:
        raise ValueError("placement history has no source_sequence list")
    if any(not isinstance(value, str) or not value for value in raw_sequence):
        raise ValueError("placement history source_sequence contains an invalid source id")
    sequence = list(raw_sequence)
    if len(set(sequence)) != len(sequence):
        raise ValueError("placement history source_sequence contains duplicate source ids")
    source_index = {source: index for index, source in enumerate(sequence)}
    violations: dict[str, list[str]] = {}
    encounter_indexes: list[int] = []
    placement_ids: set[str] = set()
    for index, placement in enumerate(placements):
        placement_id = placement.get("placement_id")
        if not isinstance(placement_id, str) or not placement_id:
            raise ValueError(f"placement history placement[{index}] has no stable id")
        if placement_id in placement_ids:
            raise ValueError(f"placement history contains duplicate placement id: {placement_id}")
        placement_ids.add(placement_id)
        source = placement.get("source_id")
        if not isinstance(source, str) or not source:
            raise ValueError(f"placement {placement_id} has no valid source id")
        time = placement.get("time", {})
        reasons: list[str] = []
        if not isinstance(time, dict):
            encounter = -1
            reasons.append("missing-time-record")
        else:
            raw_encounter = time.get("encounter_index")
            if isinstance(raw_encounter, bool) or not isinstance(raw_encounter, int):
                encounter = -1
                reasons.append("invalid-encounter-index")
            else:
                encounter = raw_encounter
        encounter_indexes.append(encounter)
        known = source_index.get(source)
        if encounter < 0:
            reasons.append("negative-encounter-index")
        if encounter >= len(sequence):
            reasons.append("encounter-index-out-of-range")
        if known is None:
            reasons.append("source-not-in-sequence")
        elif encounter < known:
            reasons.append("source-used-before-encounter")
        if reasons:
            violations[placement_id] = sorted(set(reasons))
    return {
        "source_sequence_length": len(sequence),
        "maximum_encounter_index": max(encounter_indexes, default=-1),
        "causality_violation_count": len(violations),
        "violating_placement_ids": sorted(violations),
        "violation_reasons": dict(sorted(violations.items())),
        "future_sources_used": bool(violations),
    }


def histories_from_sidecar(sidecar: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if "placement_history" in sidecar and "placement_histories" in sidecar:
        raise ValueError("sidecar must not contain both placement history forms")
    if "placement_history" in sidecar:
        history = sidecar["placement_history"]
        if not isinstance(history, dict):
            raise ValueError("sidecar placement_history must be an object")
        return {str(sidecar.get("target_id", "target")): history}
    histories = sidecar.get("placement_histories")
    if not isinstance(histories, dict) or not histories:
        raise ValueError("sidecar contains no placement history")
    if any(not isinstance(history, dict) for history in histories.values()):
        raise ValueError("sidecar placement_histories must contain objects")
    return {str(target_id): history for target_id, history in histories.items()}


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def evaluate_temporal_causality(
    histories: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate and hash a complete set of placement histories."""
    if not histories:
        raise ValueError("temporal causality evaluation requires at least one history")
    ordered = {target_id: histories[target_id] for target_id in sorted(histories)}
    targets: dict[str, dict[str, Any]] = {}
    for target_id, history in ordered.items():
        if not target_id:
            raise ValueError("temporal causality history has an empty target id")
        if history.get("target_id") != target_id:
            raise ValueError(f"placement history target id does not match mapping key: {target_id}")
        targets[target_id] = temporal_causality_metrics(history)
    violation_count = sum(
        int(metrics["causality_violation_count"])
        for metrics in targets.values()
    )
    return {
        "evaluator_schema": TEMPORAL_CAUSALITY_EVALUATOR_SCHEMA,
        "evaluated_history_sha256": _canonical_sha256(ordered),
        "history_count": len(ordered),
        "placement_count": sum(len(_placements(history)) for history in ordered.values()),
        "violation_count": violation_count,
        "future_source_frames_used": violation_count > 0,
        "valid": violation_count == 0,
        "targets": targets,
    }


def require_temporal_causality(
    histories: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    evaluation = evaluate_temporal_causality(histories)
    if not evaluation["valid"]:
        raise ValueError(
            "temporal causality evaluation failed: "
            f"{evaluation['violation_count']} placement violation(s)"
        )
    return evaluation


def recorded_temporal_causality_matches(
    sidecar: dict[str, Any],
    computed: dict[str, Any],
) -> bool:
    recorded = sidecar.get("temporal_causality")
    if not isinstance(recorded, dict):
        return False
    fields = (
        "evaluator_schema",
        "evaluated_history_sha256",
        "history_count",
        "placement_count",
        "violation_count",
        "future_source_frames_used",
        "valid",
        "targets",
    )
    return all(recorded.get(field) == computed.get(field) for field in fields)


def require_sidecar_temporal_causality(sidecar: dict[str, Any]) -> dict[str, Any]:
    computed = require_temporal_causality(histories_from_sidecar(sidecar))
    if not recorded_temporal_causality_matches(sidecar, computed):
        raise ValueError("recorded temporal causality evaluation does not match placement histories")
    if sidecar.get("artwork") == "seguimos-buscando":
        if sidecar.get("future_source_frames_used") != computed["future_source_frames_used"]:
            raise ValueError("future_source_frames_used does not match temporal causality evaluation")
    return computed


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
    histories = histories_from_sidecar(sidecar)
    causality = evaluate_temporal_causality(histories)
    return {
        "evaluation_schema": "desaparecidos.uy/artwork-evaluation/2.0",
        "sidecar": str(sidecar_path),
        "artwork": sidecar.get("artwork"),
        "temporal_causality": {
            **causality,
            "recorded_evaluation_matches": recorded_temporal_causality_matches(
                sidecar, causality
            ),
        },
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
