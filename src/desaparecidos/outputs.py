from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import display_path

OUTPUT_MEDIA_SUFFIXES = (".json", ".png", ".mp4", ".webm")


def list_outputs(output_dir: str | Path = "outputs/stage1") -> list[dict[str, Any]]:
    root = Path(output_dir)
    if not root.exists():
        return []
    items: list[dict[str, Any]] = []
    sidecars = sorted(root.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    for sidecar_path in sidecars:
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


def delete_outputs(
    output_dir: str | Path = "outputs/stage1",
    *,
    ids: list[str] | None = None,
    all_outputs: bool = False,
) -> dict[str, Any]:
    root = Path(output_dir)
    selected_ids = set(ids or [])
    if not all_outputs and not selected_ids:
        raise ValueError("select at least one output or request all outputs")
    if not root.exists():
        return {"ok": True, "deleted": [], "errors": []}

    sidecars = sorted(root.glob("*.json"))
    known_ids = {sidecar.stem for sidecar in sidecars}
    requested = known_ids if all_outputs else selected_ids
    missing = sorted(selected_ids - known_ids) if not all_outputs else []
    deleted: list[str] = []
    errors: list[str] = [f"output not found: {output_id}" for output_id in missing]

    for sidecar_path in sidecars:
        if sidecar_path.stem not in requested:
            continue
        output_deleted = False
        for suffix in OUTPUT_MEDIA_SUFFIXES:
            path = sidecar_path.with_suffix(suffix)
            if not path.exists():
                continue
            try:
                path.unlink()
                output_deleted = True
            except OSError as exc:
                errors.append(f"could not delete {display_path(path)}: {exc}")
        if output_deleted:
            deleted.append(sidecar_path.stem)

    return {"ok": not errors, "deleted": deleted, "errors": errors}
