from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from desaparecidos.evaluation import evaluate_sidecar, target_structure_metrics
from desaparecidos.manifests import approved_rows, row_file_path
from desaparecidos.paths import display_path, safe_project_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate an artwork output using artwork-derived structural measures."
    )
    parser.add_argument("sidecar", type=Path)
    parser.add_argument("--target-manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    sidecar_path = safe_project_path(args.sidecar)
    report = evaluate_sidecar(sidecar_path)
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    if args.target_manifest:
        target_manifest = safe_project_path(args.target_manifest)
        target_by_id = {
            row.id: row for row in approved_rows(target_manifest, "targets", require_files=True)
        }
        still_path = safe_project_path(str(sidecar.get("still_path", "")))
        if still_path.exists():
            with Image.open(still_path) as generated:
                for target_id, target_report in report["targets"].items():
                    target = target_by_id.get(target_id)
                    if target is None:
                        target_report["target_structure"] = {
                            "error": "target not found in approved target manifest"
                        }
                        continue
                    with Image.open(row_file_path(target, target_manifest)) as reference:
                        target_report["target_structure"] = target_structure_metrics(
                            generated.convert("RGB"), reference.convert("RGB")
                        )

    output = safe_project_path(args.output) if args.output else sidecar_path.with_suffix(".evaluation.json")
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(display_path(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
