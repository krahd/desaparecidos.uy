from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import display_path


def list_outputs(output_dir: str | Path = "outputs/stage1") -> list[dict[str, Any]]:
    root = Path(output_dir)
    if not root.exists():
        return []
    items: list[dict[str, Any]] = []
    for sidecar_path in sorted(root.glob("*.json")):
        try:
            sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            sidecar = {}
        still_path = sidecar_path.with_suffix(".png")
        video_path = sidecar_path.with_suffix(".mp4")
        items.append(
            {
                "id": sidecar_path.stem,
                "target_id": sidecar.get("target_id", ""),
                "still_path": display_path(still_path) if still_path.exists() else None,
                "video_path": display_path(video_path) if video_path.exists() else None,
                "sidecar_path": display_path(sidecar_path),
                "sidecar": sidecar,
            }
        )
    return items
