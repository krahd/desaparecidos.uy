from __future__ import annotations

from PIL import Image, ImageDraw
import pytest

from desaparecidos.evaluation import (
    evaluate_temporal_causality,
    evaluate_history,
    participation_metrics,
    require_temporal_causality,
    source_reconstitution_metrics,
    target_structure_metrics,
    temporal_causality_metrics,
    visual_grammar_metrics,
)


def _history() -> dict[str, object]:
    placements = []
    sources = ["a", "a", "b", "c"]
    positions = [(0, 0), (24, 0), (0, 24), (24, 24)]
    for index, (source, (x, y)) in enumerate(zip(sources, positions)):
        placements.append({
            "placement_id": f"target:{index}",
            "source_id": source,
            "fragment_id": f"{source}:{index}",
            "source_rect": {"x": 0, "y": 0, "width": 24, "height": 24},
            "matched_target_rect": {"x": x, "y": y, "width": 24, "height": 24},
            "render_geometry": {
                "x": x - 2,
                "y": y - 2,
                "width": 28,
                "height": 28,
                "rotation_degrees": index,
                "opacity": 0.9,
                "z_index": index,
            },
            "time": {
                "encounter_index": [0, 0, 1, 2][index],
                "enter_normalised": index / 4,
                "settle_normalised": (index + 1) / 4,
                "exit_normalised": None,
            },
        })
    return {
        "schema": "desaparecidos.uy/placement-history/1.0",
        "target_id": "target",
        "canvas": {"width": 48, "height": 48},
        "visual_grammar": "overlap",
        "seed": 17,
        "source_sequence": ["a", "b", "c"],
        "placement_count": 4,
        "timeline_unit": "normalised-output-process",
        "placements": placements,
    }


def test_participation_metrics_are_exact() -> None:
    metrics = participation_metrics(_history())
    assert metrics["placement_count"] == 4
    assert metrics["source_count"] == 3
    assert metrics["max_source_share"] == 0.5
    assert metrics["hhi"] == 0.375


def test_source_reconstitution_reports_adjacency_without_anonymity_claim() -> None:
    metrics = source_reconstitution_metrics(_history())
    assert metrics["same_source_adjacency_edges"] == 1
    assert metrics["largest_same_source_component"] == 2
    assert metrics["largest_component_source"] == "a"
    assert metrics["anonymity_determined"] is False
    assert metrics["manual_recognisability_review_required"] is True


def test_visual_grammar_and_temporal_causality_metrics() -> None:
    grammar = visual_grammar_metrics(_history())
    causality = temporal_causality_metrics(_history())

    assert grammar["visual_grammar"] == "overlap"
    assert grammar["overlap_pair_count"] > 0
    assert grammar["minimum_opacity"] == 0.9
    assert causality["causality_violation_count"] == 0
    assert causality["future_sources_used"] is False
    assert evaluate_history(_history())["participation"]["source_count"] == 3


def test_temporal_causality_detects_future_source_use() -> None:
    history = _history()
    history["placements"][2]["time"]["encounter_index"] = 0  # type: ignore[index]
    metrics = temporal_causality_metrics(history)
    assert metrics["future_sources_used"] is True
    assert metrics["causality_violation_count"] == 1
    assert metrics["violation_reasons"]["target:2"] == ["source-used-before-encounter"]


def test_temporal_causality_evaluation_hashes_histories_and_blocks_violation() -> None:
    histories = {"target": _history()}
    valid = evaluate_temporal_causality(histories)

    assert valid["evaluator_schema"] == "desaparecidos.uy/temporal-causality-evaluator/1.0"
    assert valid["valid"] is True
    assert valid["violation_count"] == 0
    assert len(valid["evaluated_history_sha256"]) == 64

    histories["target"]["placements"][2]["time"]["encounter_index"] = 0  # type: ignore[index]
    invalid = evaluate_temporal_causality(histories)
    assert invalid["evaluated_history_sha256"] != valid["evaluated_history_sha256"]
    assert invalid["future_source_frames_used"] is True
    with pytest.raises(ValueError, match="temporal causality evaluation failed"):
        require_temporal_causality(histories)


def test_target_structure_is_low_level_and_distinguishes_change() -> None:
    target = Image.new("RGB", (96, 96), (220, 220, 220))
    ImageDraw.Draw(target).ellipse((20, 12, 76, 86), outline=(20, 20, 20), width=5)
    identical = target.copy()
    changed = Image.new("RGB", target.size, (20, 20, 20))

    same = target_structure_metrics(identical, target)
    different = target_structure_metrics(changed, target)

    assert same["luminance_mae"] == 0.0
    assert same["gradient_mae"] == 0.0
    assert different["luminance_mae"] > same["luminance_mae"]
    assert "not face recognition" in str(same["interpretation"])
