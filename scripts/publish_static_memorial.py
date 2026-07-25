from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from desaparecidos.paths import display_path, safe_project_path

WORKS = (
    "todos-somos-familiares",
    "estan-en-todas-partes",
    "seguimos-buscando",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def publish(
    exhibition_manifest: Path,
    publication_config: Path,
    destination: Path,
    *,
    acknowledge_review: bool,
) -> Path:
    if not acknowledge_review:
        raise ValueError(
            "publishing requires --acknowledge-review to confirm that rights, source, "
            "recognisability, historical metadata, and full-duration video review are complete"
        )
    exhibition = _load(exhibition_manifest)
    publication = _load(publication_config)
    if exhibition.get("schema") != "desaparecidos.uy/exhibition-triptych/2.0":
        raise ValueError("unsupported or stale exhibition manifest schema")
    if publication.get("schema") != "desaparecidos.uy/web-publication/1.0":
        raise ValueError("unsupported publication configuration schema")
    exhibition_videos = exhibition.get("videos", {})
    publication_works = publication.get("works", {})
    if not isinstance(exhibition_videos, dict) or not isinstance(publication_works, dict):
        raise ValueError("manifest video and publication work records must be objects")

    source_web = safe_project_path("web")
    destination.mkdir(parents=True, exist_ok=True)
    media = destination / "media"
    media.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "method.html", "style.css", "app.js"):
        shutil.copy2(source_web / name, destination / name)

    emitted: dict[str, Any] = {
        "schema": "desaparecidos.uy/web-publication/1.0",
        "note": str(publication.get("note", "")),
        "works": {},
    }
    audit: dict[str, Any] = {
        "schema": "desaparecidos.uy/web-publication-audit/1.0",
        "exhibition_manifest": display_path(exhibition_manifest),
        "publication_config": display_path(publication_config),
        "works": {},
    }
    for work in WORKS:
        requested = publication_works.get(work, {})
        if not isinstance(requested, dict):
            raise ValueError(f"publication record for {work} must be an object")
        publish_work = requested.get("publish") is True
        emitted_record = {
            "publish": publish_work,
            "path": f"./media/{work}.mp4",
            "poster": str(requested.get("poster", "")),
            "controls": bool(requested.get("controls", False)),
        }
        audit_record: dict[str, Any] = {"publish": publish_work}
        if publish_work:
            source_record = exhibition_videos.get(work)
            if not isinstance(source_record, dict):
                raise ValueError(f"exhibition manifest has no video record for {work}")
            source = safe_project_path(str(source_record.get("path", "")))
            if not source.exists() or not source.is_file():
                raise ValueError(f"reviewed video is missing for {work}: {source}")
            expected = str(source_record.get("sha256", ""))
            actual = _sha256(source)
            if not expected or actual != expected:
                raise ValueError(f"video digest mismatch for {work}")
            target = media / f"{work}.mp4"
            shutil.copy2(source, target)
            audit_record.update({
                "source": display_path(source),
                "published": display_path(target),
                "sha256": actual,
                "bytes": target.stat().st_size,
            })
        emitted["works"][work] = emitted_record
        audit["works"][work] = audit_record

    (destination / "publication.json").write_text(
        json.dumps(emitted, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    audit_path = destination / "publication-audit.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    return audit_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish a reviewed, static desaparecidos.uy memorial site."
    )
    parser.add_argument("exhibition_manifest", type=Path)
    parser.add_argument("publication_config", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--acknowledge-review", action="store_true")
    args = parser.parse_args()
    audit = publish(
        safe_project_path(args.exhibition_manifest),
        safe_project_path(args.publication_config),
        safe_project_path(args.destination),
        acknowledge_review=args.acknowledge_review,
    )
    print(display_path(audit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
