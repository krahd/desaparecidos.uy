"""Approximate gazetteer of Uruguay for autonomous traversal sampling.

The locality list and boundary polygon are deliberately coarse. They exist only
to decide *where the autonomous walk looks next* — favouring inhabited places
while sometimes wandering elsewhere — and are not authoritative geographic or
demographic data. Populations are rounded 2011 INE census figures used purely
as sampling weights; coordinates are town centres to within a couple of
kilometres. Nothing here refers to persons.
"""
from __future__ import annotations

import random
from typing import Any

# west, south, east, north
URUGUAY_BBOX = (-58.44, -34.98, -53.35, -30.09)

# Coarse land boundary (lon, lat), clockwise from Bella Unión. Used to keep
# rural samples on Uruguayan territory rather than in the river, the ocean, or
# a neighbouring country. Border-adjacent error of a few kilometres is accepted.
URUGUAY_BOUNDARY: list[tuple[float, float]] = [
    (-57.65, -30.20),  # Bella Unión
    (-56.47, -30.30),  # Cuareim / Artigas
    (-56.00, -30.75),
    (-55.55, -30.85),  # Rivera
    (-54.90, -31.35),
    (-54.16, -31.87),  # Aceguá
    (-53.75, -32.05),
    (-53.37, -32.57),  # Río Branco
    (-53.20, -32.80),  # Laguna Merín shore
    (-53.37, -33.74),  # Chuy
    (-53.55, -34.10),  # Atlantic coast
    (-54.15, -34.65),  # La Paloma
    (-54.95, -34.95),  # Punta del Este
    (-56.20, -34.90),  # Montevideo
    (-57.85, -34.46),  # Colonia
    (-58.42, -33.88),  # Nueva Palmira
    (-58.35, -33.10),  # Fray Bentos
    (-58.12, -32.30),  # Paysandú
    (-57.97, -31.40),  # Salto
]

# (name, longitude, latitude, approximate population)
URUGUAY_LOCALITIES: list[tuple[str, float, float, int]] = [
    ("Montevideo", -56.1645, -34.9011, 1319000),
    ("Salto", -57.9667, -31.3833, 104000),
    ("Ciudad de la Costa", -55.9500, -34.8167, 95000),
    ("Paysandú", -58.0756, -32.3214, 76000),
    ("Las Piedras", -56.2192, -34.7302, 71000),
    ("Rivera", -55.5508, -30.9053, 64000),
    ("Maldonado", -54.9500, -34.9000, 63000),
    ("Tacuarembó", -55.9833, -31.7333, 55000),
    ("Melo", -54.1833, -32.3667, 52000),
    ("Mercedes", -58.0308, -33.2458, 42000),
    ("Artigas", -56.4667, -30.4000, 41000),
    ("Minas", -55.2333, -34.3667, 38000),
    ("San José de Mayo", -56.7136, -34.3375, 37000),
    ("Durazno", -56.5167, -33.3833, 34000),
    ("Florida", -56.2147, -34.0954, 34000),
    ("Barros Blancos", -56.0043, -34.7541, 32000),
    ("Ciudad del Plata", -56.3833, -34.7667, 31000),
    ("San Carlos", -54.9167, -34.8000, 27000),
    ("Colonia del Sacramento", -57.8400, -34.4626, 26000),
    ("Pando", -55.9583, -34.7167, 26000),
    ("Treinta y Tres", -54.3833, -33.2333, 25000),
    ("Rocha", -54.3333, -34.4833, 25000),
    ("Fray Bentos", -58.3000, -33.1333, 24000),
    ("Trinidad", -56.9000, -33.5167, 21000),
    ("La Paz", -56.2233, -34.7597, 21000),
    ("Canelones", -56.2778, -34.5228, 20000),
    ("Carmelo", -58.2833, -34.0000, 18000),
    ("Dolores", -58.2167, -33.5333, 17000),
    ("Young", -57.6333, -32.6833, 17000),
    ("Santa Lucía", -56.3908, -34.4528, 17000),
    ("Progreso", -56.2194, -34.6667, 16000),
    ("Paso de Carrasco", -56.0500, -34.8600, 16000),
    ("Río Branco", -53.3833, -32.5667, 15000),
    ("Paso de los Toros", -56.5167, -32.8167, 13000),
    ("Juan Lacaze", -57.4333, -34.4333, 13000),
    ("Bella Unión", -57.5833, -30.2500, 12000),
    ("Libertad", -56.6167, -34.6333, 10000),
    ("Rosario", -57.3500, -34.3167, 10000),
    ("Nueva Helvecia", -57.2333, -34.3000, 10000),
    ("Nueva Palmira", -58.4167, -33.8667, 10000),
    ("Chuy", -53.4500, -33.6833, 10000),
    ("Punta del Este", -54.9500, -34.9667, 9000),
    ("Piriápolis", -55.2667, -34.8667, 9000),
    ("Lascano", -54.2000, -33.6667, 8000),
    ("Castillos", -53.8333, -34.1667, 8000),
    ("Sarandí del Yí", -55.6333, -33.3500, 7000),
    ("Tranqueras", -55.7500, -31.2000, 7000),
    ("Tarariras", -57.6167, -34.2667, 7000),
    ("Sarandí Grande", -56.3333, -33.7333, 6000),
    ("José Pedro Varela", -54.5333, -33.4500, 5000),
    ("Guichón", -57.2000, -32.3500, 5000),
    ("Aiguá", -54.7500, -34.2000, 2500),
]


def point_in_uruguay(longitude: float, latitude: float) -> bool:
    """Ray-cast the coarse boundary polygon."""
    inside = False
    points = URUGUAY_BOUNDARY
    for index in range(len(points)):
        lon_a, lat_a = points[index]
        lon_b, lat_b = points[(index + 1) % len(points)]
        if (lat_a > latitude) == (lat_b > latitude):
            continue
        crossing = (lon_b - lon_a) * (latitude - lat_a) / (lat_b - lat_a) + lon_a
        if longitude < crossing:
            inside = not inside
    return inside


def _cell(longitude: float, latitude: float, size: float) -> dict[str, Any]:
    half = size / 2
    west, south = longitude - half, latitude - half
    east, north = longitude + half, latitude + half
    return {
        "type": "Polygon",
        "coordinates": [[
            [west, south], [east, south], [east, north], [west, north], [west, south],
        ]],
    }


def _weighted_locality(rng: random.Random, exclude: set[str]) -> tuple[str, float, float, int]:
    candidates = [entry for entry in URUGUAY_LOCALITIES if entry[0] not in exclude] or URUGUAY_LOCALITIES
    total = sum(entry[3] for entry in candidates)
    pick = rng.random() * total
    for entry in candidates:
        pick -= entry[3]
        if pick <= 0:
            return entry
    return candidates[-1]


def sample_uruguay_cells(
    count: int,
    *,
    rural_probability: float = 0.25,
    rng: random.Random | None = None,
    locality_cell_degrees: float = 0.012,
    rural_cell_degrees: float = 0.05,
) -> list[dict[str, Any]]:
    """Sample small search cells across Uruguay.

    Each cell is a GeoJSON Polygon. Cells centre on localities chosen with
    population-proportional weight (without repetition until all are used),
    except that with ``rural_probability`` a cell is instead placed at a
    uniform point on Uruguayan land — the walk sometimes searches away from
    inhabited places. Locality cells are ~1.2 km because Mapillary's bbox
    search rejects larger boxes over dense city coverage; rural cells are
    ~5 km because sparse areas need more reach. Deterministic for a seeded
    ``rng``.
    """
    rng = rng or random.Random()
    rural_probability = min(1.0, max(0.0, rural_probability))
    used: set[str] = set()
    cells: list[dict[str, Any]] = []
    west, south, east, north = URUGUAY_BBOX
    for _ in range(max(0, count)):
        if rng.random() < rural_probability:
            for _attempt in range(200):
                longitude = rng.uniform(west, east)
                latitude = rng.uniform(south, north)
                if point_in_uruguay(longitude, latitude):
                    break
            else:  # pathological rng; fall back to a weighted locality
                name, longitude, latitude, _population = _weighted_locality(rng, used)
                used.add(name)
                cells.append({"name": name, "kind": "locality",
                              "geometry": _cell(longitude, latitude, locality_cell_degrees)})
                continue
            cells.append({"name": "campo", "kind": "rural",
                          "geometry": _cell(longitude, latitude, rural_cell_degrees)})
        else:
            name, longitude, latitude, _population = _weighted_locality(rng, used)
            used.add(name)
            jitter = locality_cell_degrees / 2
            cells.append({"name": name, "kind": "locality",
                          "geometry": _cell(longitude + rng.uniform(-jitter, jitter),
                                            latitude + rng.uniform(-jitter, jitter),
                                            locality_cell_degrees)})
    return cells
