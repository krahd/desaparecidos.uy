"""Shared command-line presentation and structural-search options."""
from __future__ import annotations

import argparse

from .search_video import VideoSettings
from .structural_search import StructuralSettings


def add_render_options(parser: argparse.ArgumentParser, *, structural: bool = False) -> None:
    parser.add_argument('--split-orientation', choices=['side-by-side', 'stacked'], default='side-by-side')
    parser.add_argument('--playback-mode', choices=['continuous', 'hold'], default='continuous')
    for name in ('contribution_seconds', 'scan_seconds', 'final_hold_seconds', 'details_hold_seconds', 'text_hold_seconds', 'fade_seconds'):
        parser.add_argument('--' + name.replace('_', '-'), type=float, default=getattr(VideoSettings(), name))
    parser.add_argument('--closing-text', default='')
    parser.add_argument('--hide-match-marks', action='store_true')
    if structural:
        parser.set_defaults(scan_seconds=0.33)
        parser.add_argument('--allow-incomplete', dest='require_complete', action='store_false', default=True)
        parser.add_argument('--max-search-batches', type=int, default=8)
        parser.add_argument('--search-budget-seconds', type=int, default=300)
        parser.add_argument('--contribution-interval', type=int, default=6)
        parser.add_argument('--search-similarity', type=float, default=0.95)
        parser.add_argument('--structure-scale', choices=['broad', 'fine'], default='broad')
        parser.add_argument('--tone-mode', choices=['source', 'match-region'], default='source')
        parser.add_argument('--reconstruction-mode', choices=['fixed', 'largest-first', 'refine'], default='refine')
        parser.add_argument('--max-region-size', type=int, default=384)
        parser.add_argument('--structure-threshold', type=float, default=0.82)
        parser.add_argument('--min-structure', type=float, default=0.035)
        parser.add_argument('--refinement-margin', type=float, default=0.04)


def render_options(args: argparse.Namespace, *, structural: bool = False) -> dict:
    options = {name: getattr(args, name) for name in VideoSettings.__dataclass_fields__ if name != 'show_match_marks'}
    options['show_match_marks'] = not args.hide_match_marks
    if structural:
        options.update({name: getattr(args, name) for name in StructuralSettings.__dataclass_fields__})
    return options
