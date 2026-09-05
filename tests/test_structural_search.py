from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import pytest

from desaparecidos.structural_search import search_regions, structure_descriptor
from desaparecidos.traversals import TraversalRenderSettings


def pattern() -> Image.Image:
    image = Image.new('L', (64, 64), 30)
    draw = ImageDraw.Draw(image)
    draw.rectangle((8, 10, 21, 50), fill=210)
    draw.line((10, 49, 52, 39), fill=160, width=6)
    draw.ellipse((38, 6, 57, 25), fill=245)
    return image.convert('RGB')


def frames_at(root: Path, *images: Image.Image) -> list[dict]:
    frames = []
    for index, image in enumerate(images):
        path = root / f'frame-{index}.png'
        image.save(path)
        frames.append({'id': f'frame-{index}', 'local_path': str(path)})
    return frames


def settings(**kwargs) -> TraversalRenderSettings:
    return replace(TraversalRenderSettings(fragment_size=32, max_region_size=64,
                   output_width=64, contribution_interval=1, search_similarity=0, min_structure=0.02, structure_threshold=0.8, structure_scale="fine"), **kwargs)


def test_descriptor_rejects_same_tone_different_structure_and_ignores_brightness() -> None:
    original = pattern()
    a, strength = structure_descriptor(original)
    b, _ = structure_descriptor(original.transpose(Image.Transpose.ROTATE_90))
    c, _ = structure_descriptor(original.point(lambda value: value * 0.6 + 30))
    flat, flat_strength = structure_descriptor(Image.new('RGB', (64, 64), (130, 130, 130)))
    assert strength > 0.02
    assert float(a @ b) < 0.8
    assert float(a @ c) > 0.99
    assert flat_strength == 0 and np.linalg.norm(flat) == 0


def test_current_frame_only_single_region_skips_and_largest_first(tmp_path: Path) -> None:
    target = pattern()
    frames = frames_at(tmp_path, Image.new('RGB', target.size, 120), target)
    result, encounters, decisions, coverage = search_regions(target, frames, settings())
    assert encounters == [1]
    assert [d['action'] for d in decisions] == ['skip', 'place']
    assert len(result.placements) == 1
    assert result.placements[0].image.size == (64, 64)
    assert result.source_usage == {'frame-1': 1}
    assert coverage == 1


def test_later_better_candidate_refines_but_equal_or_worse_does_not(tmp_path: Path) -> None:
    target = pattern()
    approximate = target.filter(ImageFilter.GaussianBlur(2))
    frames = frames_at(tmp_path, approximate, target, approximate, target)
    result, encounters, decisions, _ = search_regions(target, frames, settings(refinement_margin=0.005))
    assert encounters == [0, 1]
    assert [d['action'] for d in decisions] == ['place', 'refine', 'skip', 'skip']
    assert decisions[1]['score'] > decisions[0]['score']
    assert np.array_equal(np.asarray(result.image), np.asarray(target))
    frozen, after, _, _ = search_regions(target, frames, settings(reconstruction_mode='largest-first'))
    assert after == [0] and len(frozen.placements) == 1


def test_fixed_regions_variable_regions_and_partial_results(tmp_path: Path) -> None:
    target = pattern()
    frames = frames_at(tmp_path, target)
    fixed, _, _, coverage = search_regions(target, frames, settings(reconstruction_mode='fixed'))
    assert len(fixed.placements) == 1 and fixed.placements[0].image.size == (32, 32)
    assert coverage == 0.25
    blank, encounters, decisions, coverage = search_regions(target, frames_at(tmp_path, Image.new('RGB', (64, 64), 0)), settings())
    assert not blank.placements and not encounters and coverage == 0
    assert decisions[0]['action'] == 'skip' and blank.image.getbbox() is None


def test_smaller_later_region_refines_only_part_of_a_large_match(tmp_path: Path) -> None:
    target = pattern()
    approximate = target.filter(ImageFilter.GaussianBlur(2))
    source = Image.new('RGB', target.size, 0)
    source.paste(target.crop((0, 0, 32, 32)), (0, 0))
    result, encounters, decisions, _ = search_regions(target, frames_at(tmp_path, approximate, source), settings(refinement_margin=0.005))
    assert encounters == [0, 1]
    assert result.placements[0].image.size == (64, 64)
    assert result.placements[1].image.size != (64, 64)
    assert decisions[1]['action'] == 'refine'


def test_source_cannot_contribute_again_and_source_rect_stays_in_bounds(tmp_path: Path) -> None:
    frames = frames_at(tmp_path, pattern().resize((32, 32)))
    result, _, decisions, _ = search_regions(pattern(), frames * 2, settings())
    assert len(result.placements) <= 1
    if result.placements:
        p = result.placements[0]
        assert p.source_x + p.source_width <= 32
        assert p.source_y + p.source_height <= 32
        assert decisions[-1]['reason'] == 'source-already-contributed'


def test_invalid_size_range_fails(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match='minimum'):
        search_regions(pattern(), frames_at(tmp_path, pattern()), settings(fragment_size=96))


def test_missing_region_precedes_refining_an_already_good_region(tmp_path: Path) -> None:
    target = Image.new('RGB', (128, 64))
    target.paste(pattern(), (0, 0))
    target.paste(pattern(), (64, 0))
    frames = frames_at(tmp_path, pattern().filter(ImageFilter.GaussianBlur(2)), pattern(), pattern())
    result, encounters, decisions, coverage = search_regions(target, frames,
        settings(fragment_size=64, max_region_size=64, refinement_margin=0.005))
    assert encounters == [0, 1, 2]
    assert [p.dest_x for p in result.placements] == [0, 64, 0]
    assert [d['action'] for d in decisions] == ['place', 'place', 'refine']
    assert coverage == 1


@pytest.mark.parametrize('scale', ['broad', 'fine'])
def test_exposure_adjustment_follows_structural_acceptance_and_records_transform(tmp_path: Path, scale: str) -> None:
    target = pattern()
    dark = target.point(lambda v: v * 0.5 + 10)
    frames = frames_at(tmp_path, Image.new('RGB', target.size, (130,)*3), dark)
    result, encounters, decisions, coverage = search_regions(target, frames,
        settings(structure_scale=scale, tone_mode='match-region'))
    assert encounters == [1] and coverage == 1
    assert decisions[0]['action'] == 'skip' and 'tone_transform' not in decisions[0]
    transform = decisions[1]['tone_transform']
    pixels = np.asarray(dark.convert('L'),dtype=np.float32)*transform['gain']+transform['offset']
    assert np.array_equal(np.asarray(result.image)[:,:,0], np.clip(pixels,0,255).round().astype(np.uint8))
    assert abs(np.asarray(result.image).mean() - np.asarray(target).mean()) < 2
    assert result.image != target  # The adjusted source crop remains the material.


def test_contributions_are_spaced_without_replaying_earlier_sources(tmp_path: Path) -> None:
    target = Image.new('RGB', (256, 64))
    for x in range(0, 256, 64):
        target.paste(pattern(), (x, 0))
    frames = frames_at(tmp_path, *[pattern() for _ in range(12)])
    result, encounters, decisions, coverage = search_regions(target, frames,
        settings(fragment_size=64, max_region_size=64, contribution_interval=3))
    assert encounters == [2, 5, 8, 11]
    assert coverage == 1
    assert [p.source_id for p in result.placements] == [f'frame-{i}' for i in encounters]
    assert all(d['reason'] == 'contribution-spacing' for d in decisions if d['action'] == 'skip')


def test_quality_target_stops_only_with_coverage_and_actual_image_similarity(tmp_path: Path) -> None:
    target = pattern()
    dark = target.point(lambda v: v * 0.4)
    frames = frames_at(tmp_path, dark, target, target)
    _, encounters, decisions, coverage = search_regions(target, frames,
        settings(search_similarity=0.99, refinement_margin=0))
    assert coverage == 1
    # Normalised structural correlation alone cannot declare the dark image complete.
    assert decisions[0]['reconstruction_similarity'] < 0.99
    assert decisions[-1]['stop_reason'] == 'quality-target-reached'
    assert len(decisions) == 2 and encounters == [0, 1]


def test_unattainable_quality_reports_exhaustion_without_smaller_regions(tmp_path: Path) -> None:
    result, _, decisions, coverage = search_regions(pattern(),
        frames_at(tmp_path, pattern().filter(ImageFilter.GaussianBlur(2))),
        settings(search_similarity=1, fragment_size=64, max_region_size=64))
    assert coverage == 1
    assert decisions[-1]['stop_reason'] == 'approved-frames-exhausted'
    assert all(p.image.size == (64, 64) for p in result.placements)


def test_assembly_truncates_encounter_history_at_quality_stop(tmp_path: Path) -> None:
    from desaparecidos.manifests import ManifestRow
    from desaparecidos.traversals import assemble_walk
    frames = frames_at(tmp_path, pattern(), pattern(), pattern())
    target = ManifestRow(kind='targets', line_number=2,
        values={'id':'target', 'local_path': frames[0]['local_path']})
    walk = assemble_walk(target, tmp_path/'targets.csv', frames,
        settings(fragment_size=64, max_region_size=64, search_similarity=0.99))
    assert walk.segment_frame_ids == ['frame-0']
    assert walk.placed_after_frame == [0]
    assert walk.search_summary['stop_reason'] == 'quality-target-reached'
    assert walk.search_summary['encounter_count'] == 1
