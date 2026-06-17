from __future__ import annotations

import csv
from pathlib import Path

from desaparecidos.demo import create_demo_fixtures
from desaparecidos.pipeline import Stage1Settings, run_stage1


def test_demo_fixtures_use_local_provenance_and_generate(tmp_path: Path) -> None:
    result = create_demo_fixtures(tmp_path)
    targets = tmp_path / result["targets"]
    sources = tmp_path / result["sources"]

    for manifest in (targets, sources):
        with manifest.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        assert rows
        assert all(row["source_url"].startswith("local://demo/") for row in rows)
        assert all(row["source_page"].startswith("local://demo/") for row in rows)
        assert "example.invalid" not in manifest.read_text(encoding="utf-8")

    outputs = run_stage1(
        targets,
        sources,
        tmp_path / "outputs",
        Stage1Settings(seed=17, fragment_size=24, reuse_limit=1, output_width=720),
    )

    assert Path(outputs[0].still_path).exists()
