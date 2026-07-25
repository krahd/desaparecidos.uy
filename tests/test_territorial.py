from __future__ import annotations

from dataclasses import dataclass

from desaparecidos.territorial import (
    balance_territorial_sources,
    territorial_group,
    territorial_usage,
)


@dataclass(frozen=True)
class Row:
    id: str
    values: dict[str, str]


def test_territorial_group_prefers_explicit_reviewed_metadata() -> None:
    assert territorial_group(Row("a", {"department": "Rocha"})) == "rocha"
    assert territorial_group(Row("b", {"region": "Litoral"})) == "litoral"
    assert territorial_group(Row("c", {"location_label": "Ruta 5, Tacuarembó"})) == "tacuarembo"
    assert territorial_group(Row("d", {"location_label": "surface study"})) == "unlocated"


def test_balance_territorial_sources_is_deterministic_and_interleaves_groups() -> None:
    rows = [
        *(Row(f"m-{index}", {"department": "Montevideo"}) for index in range(5)),
        Row("r-1", {"department": "Rocha"}),
        Row("a-1", {"department": "Artigas"}),
    ]
    first = balance_territorial_sources(rows, seed=17)
    second = balance_territorial_sources(rows, seed=17)

    assert [row.id for row in first] == [row.id for row in second]
    assert {territorial_group(row) for row in first[:3]} == {"montevideo", "rocha", "artigas"}


def test_territorial_usage_keeps_unlocated_visible() -> None:
    rows = [
        Row("m", {"department": "Montevideo"}),
        Row("u", {"location_label": "unknown surface"}),
    ]
    assert territorial_usage({"m": 3, "u": 2}, rows) == {"montevideo": 3, "unlocated": 2}
