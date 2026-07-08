from __future__ import annotations

import random

from desaparecidos.geography import (
    URUGUAY_LOCALITIES,
    point_in_uruguay,
    sample_uruguay_cells,
)


def test_point_in_uruguay_accepts_interior_and_rejects_neighbours() -> None:
    assert point_in_uruguay(-56.52, -33.38)  # Durazno
    assert point_in_uruguay(-55.98, -31.73)  # Tacuarembó
    assert not point_in_uruguay(-58.38, -34.60)  # Buenos Aires
    assert not point_in_uruguay(-54.50, -35.50)  # Atlantic Ocean
    assert not point_in_uruguay(-55.00, -29.50)  # Brazil


def test_locality_sampling_is_deterministic_and_without_repetition() -> None:
    first = sample_uruguay_cells(6, rural_probability=0.0, rng=random.Random(3))
    second = sample_uruguay_cells(6, rural_probability=0.0, rng=random.Random(3))
    assert first == second
    names = [cell["name"] for cell in first]
    assert len(set(names)) == 6
    known = {entry[0] for entry in URUGUAY_LOCALITIES}
    assert all(name in known for name in names)
    assert all(cell["kind"] == "locality" for cell in first)


def test_population_weighting_prefers_inhabited_places() -> None:
    # Montevideo holds roughly half the total weight, so across a handful of
    # independent seeded draws it must appear far more often than small towns.
    hits = sum(
        "Montevideo" in [cell["name"] for cell in sample_uruguay_cells(3, rural_probability=0.0, rng=random.Random(seed))]
        for seed in range(20)
    )
    assert hits >= 12


def test_rural_cells_fall_on_uruguayan_land() -> None:
    cells = sample_uruguay_cells(12, rural_probability=1.0, rng=random.Random(5))
    assert all(cell["kind"] == "rural" for cell in cells)
    for cell in cells:
        ring = cell["geometry"]["coordinates"][0]
        longitude = sum(point[0] for point in ring[:4]) / 4
        latitude = sum(point[1] for point in ring[:4]) / 4
        assert point_in_uruguay(longitude, latitude)


def test_cells_are_closed_small_polygons() -> None:
    cells = sample_uruguay_cells(4, rural_probability=0.5, rng=random.Random(9))
    assert len(cells) == 4
    for cell in cells:
        ring = cell["geometry"]["coordinates"][0]
        assert ring[0] == ring[-1]
        assert abs(ring[1][0] - ring[0][0]) < 0.06
