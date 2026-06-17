from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

from .manifests import ManifestKind, read_manifest


@dataclass
class DownloadItem:
    id: str
    url: str
    output_path: str
    ok: bool
    status_code: int | None = None
    sha256: str | None = None
    bytes_written: int = 0
    error: str | None = None


@dataclass
class DownloadSummary:
    manifest: str
    kind: ManifestKind
    output_root: str
    items: list[DownloadItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and all(item.ok for item in self.items)

    def to_api(self) -> dict[str, object]:
        return {
            "manifest": self.manifest,
            "kind": self.kind,
            "output_root": self.output_root,
            "ok": self.ok,
            "errors": self.errors,
            "items": [item.__dict__ for item in self.items],
        }


def _suffix_for(url: str, content_type: str | None) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}:
        return suffix
    if content_type:
        if "png" in content_type:
            return ".png"
        if "webp" in content_type:
            return ".webp"
        if "tiff" in content_type:
            return ".tif"
        if "jpeg" in content_type or "jpg" in content_type:
            return ".jpg"
    return ".bin"


def download_manifest(
    manifest: str | Path,
    kind: ManifestKind,
    *,
    output_root: str | Path = "data/raw",
    timeout: int = 30,
) -> DownloadSummary:
    manifest_path = Path(manifest)
    validation = read_manifest(manifest_path, kind)
    summary = DownloadSummary(
        manifest=str(manifest_path),
        kind=kind,
        output_root=str(output_root),
    )
    if validation.errors:
        summary.errors.extend(validation.errors)
        return summary

    kind_root = Path(output_root) / kind
    kind_root.mkdir(parents=True, exist_ok=True)
    provenance_dir = Path(output_root) / "provenance"
    provenance_dir.mkdir(parents=True, exist_ok=True)
    provenance_path = provenance_dir / f"{kind}-downloads.jsonl"

    for row in validation.rows:
        url = row.values.get("source_url", "")
        if not url:
            item = DownloadItem(
                id=row.id,
                url=url,
                output_path="",
                ok=False,
                error="source_url is empty",
            )
            summary.items.append(item)
            continue

        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": "desaparecidos.uy-stage1/0.1"},
            )
            suffix = _suffix_for(url, response.headers.get("content-type"))
            output_path = kind_root / f"{row.id}{suffix}"
            response.raise_for_status()
            payload = response.content
            digest = hashlib.sha256(payload).hexdigest()
            output_path.write_bytes(payload)
            item = DownloadItem(
                id=row.id,
                url=url,
                output_path=str(output_path),
                ok=True,
                status_code=response.status_code,
                sha256=digest,
                bytes_written=len(payload),
            )
        except Exception as exc:  # network failures should be reported per row
            item = DownloadItem(
                id=row.id,
                url=url,
                output_path="",
                ok=False,
                error=str(exc),
            )
        summary.items.append(item)

        with provenance_path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    {
                        **item.__dict__,
                        "manifest": str(manifest_path),
                        "kind": kind,
                        "downloaded_at": datetime.now(timezone.utc).isoformat(),
                        "source_page": row.values.get("source_page", ""),
                        "licence_or_terms": row.values.get("licence_or_terms", ""),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )

    return summary
