from __future__ import annotations

import random
import re
from collections import defaultdict
from typing import Protocol, Sequence, TypeVar


class SourceRowLike(Protocol):
    id: str
    values: dict[str, str]


RowT = TypeVar("RowT", bound=SourceRowLike)

URUGUAY_DEPARTMENTS = (
    "artigas",
    "canelones",
    "cerro largo",
    "colonia",
    "durazno",
    "flores",
    "florida",
    "lavalleja",
    "maldonado",
    "montevideo",
    "paysandu",
    "rio negro",
    "rivera",
    "rocha",
    "salto",
    "san jose",
    "soriano",
    "tacuarembo",
    "treinta y tres",
)


def _fold(value: str) -> str:
    table = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")
    return re.sub(r"\s+", " ", value.translate(table).strip().lower())


def territorial_group(row: SourceRowLike) -> str:
    """Return a reviewable territorial grouping, without geocoding or inference.

    Explicit ``department`` and ``region`` fields take precedence. Existing
    ``location_label`` text is matched only against Uruguay's department names;
    unmatched material remains visibly ``unlocated`` rather than being guessed.
    """
    for field in ("department", "region"):
        value = _fold(row.values.get(field, ""))
        if value:
            return value
    label = _fold(row.values.get("location_label", ""))
    for department in URUGUAY_DEPARTMENTS:
        if re.search(rf"\b{re.escape(department)}\b", label):
            return department
    return "unlocated"


def balance_territorial_sources(rows: Sequence[RowT], *, seed: int) -> list[RowT]:
    """Round-robin reviewed sources across declared territorial groups.

    This does not assert that all departments are represented. It prevents a
    large group from exhausting the source order before smaller reviewed groups
    can participate, while preserving deterministic variability within groups.
    """
    grouped: dict[str, list[RowT]] = defaultdict(list)
    for row in rows:
        grouped[territorial_group(row)].append(row)
    rng = random.Random(seed)
    for group_rows in grouped.values():
        rng.shuffle(group_rows)
    group_names = sorted(grouped)
    rng.shuffle(group_names)
    balanced: list[RowT] = []
    while any(grouped.values()):
        for name in group_names:
            if grouped[name]:
                balanced.append(grouped[name].pop())
    return balanced


def territorial_usage(
    source_usage: dict[str, int],
    rows: Sequence[SourceRowLike],
) -> dict[str, int]:
    row_by_id = {row.id: row for row in rows}
    result: dict[str, int] = defaultdict(int)
    for source_id, count in source_usage.items():
        row = row_by_id.get(source_id)
        result[territorial_group(row) if row is not None else "unknown"] += int(count)
    return dict(sorted(result.items()))
