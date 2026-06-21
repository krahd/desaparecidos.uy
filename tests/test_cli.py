from __future__ import annotations

from desaparecidos.cli import build_parser


def test_cli_contribution_cap_default_and_unlimited_flag() -> None:
    parser = build_parser()

    defaults = parser.parse_args(["run-stage1"])
    unlimited = parser.parse_args(["run-stage1", "--max-contribution-per-source", "0"])
    match_layout = parser.parse_args(["run-stage1", "--video-source-layout", "match"])

    assert defaults.max_contribution_per_source == 1
    assert defaults.video_source_layout == "grid"
    assert unlimited.max_contribution_per_source == 0
    assert match_layout.video_source_layout == "match"


def test_cli_traversal_render_options() -> None:
    args = build_parser().parse_args([
        "run-traversal", "--traversal", "route-one", "--target-id", "person-one",
        "--target-id", "person-two", "--target-mode", "sequence", "--composition", "split",
    ])

    assert args.target_id == ["person-one", "person-two"]
    assert args.target_mode == "sequence"
    assert args.composition == "split"
