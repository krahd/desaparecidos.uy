from __future__ import annotations

from desaparecidos.cli import build_parser


def test_cli_contribution_cap_default_and_unlimited_flag() -> None:
    parser = build_parser()

    defaults = parser.parse_args(["run-stage1"])
    unlimited = parser.parse_args(["run-stage1", "--max-contribution-per-source", "0"])

    assert defaults.max_contribution_per_source == 1
    assert unlimited.max_contribution_per_source == 0
