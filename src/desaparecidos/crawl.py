from __future__ import annotations

import csv
import hashlib
import os
from dataclasses import dataclass, field
from datetime import date
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from PIL import Image

from .manifests import EXPECTED_FIELDS, ManifestKind, read_manifest
from .paths import display_path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}


@dataclass
class CrawlItem:
    id: str
    page_url: str
    image_url: str
    local_path: str
    ok: bool
    bytes_written: int = 0
    error: str | None = None


@dataclass
class CrawlSummary:
    manifest: str
    kind: ManifestKind
    pages: list[str]
    items: list[CrawlItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and any(item.ok for item in self.items)

    def to_api(self) -> dict[str, object]:
        return {
            "manifest": self.manifest,
            "kind": self.kind,
            "pages": self.pages,
            "ok": self.ok,
            "errors": self.errors,
            "items": [item.__dict__ for item in self.items],
        }


class ImageParser(HTMLParser):
    def __init__(self, page_url: str) -> None:
        super().__init__()
        self.page_url = page_url
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "img":
            self._add(values.get("src", ""))
            self._add_srcset(values.get("srcset", ""))
        if tag.lower() == "source":
            self._add_srcset(values.get("srcset", ""))
        if tag.lower() == "meta":
            name = (values.get("property") or values.get("name") or "").lower()
            if name in {"og:image", "og:image:url", "twitter:image", "twitter:image:src"}:
                self._add(values.get("content", ""))
        if tag.lower() == "link" and "image_src" in values.get("rel", "").lower():
            self._add(values.get("href", ""))

    def _add_srcset(self, value: str) -> None:
        for candidate in value.split(","):
            url = candidate.strip().split(" ", 1)[0]
            self._add(url)

    def _add(self, value: str) -> None:
        if not value or value.startswith("data:"):
            return
        parsed = urlparse(value)
        if parsed.scheme and parsed.scheme not in {"http", "https"}:
            return
        resolved = urljoin(self.page_url, value)
        if resolved not in self.urls:
            self.urls.append(resolved)


def crawl_pages(
    pages: list[str],
    kind: ManifestKind,
    manifest: str | Path,
    *,
    output_root: str | Path = "data/raw/crawl",
    max_images_per_page: int = 12,
    label_prefix: str = "",
    timeout: int = 20,
    max_bytes: int = 15 * 1024 * 1024,
    session: requests.Session | None = None,
) -> CrawlSummary:
    if not pages:
        raise ValueError("at least one page URL is required")
    if max_images_per_page < 1 or max_images_per_page > 50:
        raise ValueError("max_images_per_page must be between 1 and 50")

    manifest_path = Path(manifest).expanduser()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir = Path(output_root).expanduser() / kind
    output_dir.mkdir(parents=True, exist_ok=True)

    clean_pages = [page.strip() for page in pages if page.strip()]
    summary = CrawlSummary(
        manifest=display_path(manifest_path),
        kind=kind,
        pages=clean_pages,
    )
    client = session or requests.Session()
    existing_urls = _existing_source_urls(manifest_path, kind)
    rows: list[dict[str, str]] = []
    seen: set[str] = set(existing_urls)

    for page_url in clean_pages:
        parsed_page = urlparse(page_url)
        if parsed_page.scheme not in {"http", "https"}:
            summary.errors.append(f"unsupported page URL: {page_url}")
            continue
        try:
            page_response = client.get(
                page_url,
                timeout=timeout,
                headers={"User-Agent": "desaparecidos.uy-stage1-crawler/0.1"},
            )
            page_response.raise_for_status()
            parser = ImageParser(page_url)
            parser.feed(page_response.text)
        except Exception as exc:
            summary.errors.append(f"{page_url}: {exc}")
            continue

        for image_url in parser.urls[:max_images_per_page]:
            if image_url in seen:
                continue
            seen.add(image_url)
            item, row = _download_candidate(
                client,
                image_url,
                page_url,
                kind,
                manifest_path,
                output_dir,
                len(rows) + 1,
                label_prefix=label_prefix,
                timeout=timeout,
                max_bytes=max_bytes,
            )
            summary.items.append(item)
            if row is not None:
                rows.append(row)

    if rows:
        _append_rows(manifest_path, kind, rows)
    return summary


def _existing_source_urls(manifest_path: Path, kind: ManifestKind) -> set[str]:
    if not manifest_path.exists():
        return set()
    validation = read_manifest(manifest_path, kind)
    return {row.values.get("source_url", "") for row in validation.rows if row.values.get("source_url")}


def _download_candidate(
    client: requests.Session,
    image_url: str,
    page_url: str,
    kind: ManifestKind,
    manifest_path: Path,
    output_dir: Path,
    index: int,
    *,
    label_prefix: str,
    timeout: int,
    max_bytes: int,
) -> tuple[CrawlItem, dict[str, str] | None]:
    row_id = _row_id(page_url, image_url, index)
    try:
        response = client.get(
            image_url,
            timeout=timeout,
            headers={"User-Agent": "desaparecidos.uy-stage1-crawler/0.1"},
        )
        response.raise_for_status()
        payload = response.content
        if len(payload) > max_bytes:
            raise ValueError(f"image exceeds {max_bytes} bytes")
        content_type = response.headers.get("content-type", "")
        suffix = _suffix_for(image_url, content_type)
        if suffix == ".bin" and not content_type.startswith("image/"):
            raise ValueError(f"not an image response: {content_type or 'unknown content type'}")
        Image.open(BytesIO(payload)).verify()

        output_path = output_dir / f"{row_id}{suffix}"
        output_path.write_bytes(payload)
        local_path = display_path(output_path)
        manifest_local_path = _relative_manifest_path(manifest_path, output_path)
        item = CrawlItem(
            id=row_id,
            page_url=page_url,
            image_url=image_url,
            local_path=local_path,
            ok=True,
            bytes_written=len(payload),
        )
        return item, _manifest_row(
            kind,
            row_id,
            image_url,
            page_url,
            manifest_local_path,
            index,
            label_prefix,
        )
    except Exception as exc:
        return CrawlItem(
            id=row_id,
            page_url=page_url,
            image_url=image_url,
            local_path="",
            ok=False,
            error=str(exc),
        ), None


def _suffix_for(url: str, content_type: str) -> str:
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in IMAGE_SUFFIXES:
        return suffix
    lowered = content_type.lower()
    if "png" in lowered:
        return ".png"
    if "webp" in lowered:
        return ".webp"
    if "tiff" in lowered:
        return ".tif"
    if "jpeg" in lowered or "jpg" in lowered:
        return ".jpg"
    return ".bin"


def _row_id(page_url: str, image_url: str, index: int) -> str:
    host = urlparse(page_url).netloc.lower().replace("www.", "")
    host_slug = "".join(char if char.isalnum() else "-" for char in host).strip("-") or "page"
    digest = hashlib.sha256(image_url.encode("utf-8")).hexdigest()[:10]
    return f"crawl-{host_slug}-{index:03d}-{digest}"


def _relative_manifest_path(manifest_path: Path, output_path: Path) -> str:
    return os.path.relpath(output_path.resolve(), manifest_path.parent.resolve())


def _manifest_row(
    kind: ManifestKind,
    row_id: str,
    image_url: str,
    page_url: str,
    local_path: str,
    index: int,
    label_prefix: str,
) -> dict[str, str]:
    label = f"{label_prefix.strip() or 'Crawled image'} {index}".strip()
    common = {
        "id": row_id,
        "source_url": image_url,
        "source_page": page_url,
        "licence_or_terms": "needs rights review before approval",
        "accessed_at": date.today().isoformat(),
        "local_path": local_path,
        "review_status": "pending",
    }
    if kind == "targets":
        return {
            **common,
            "name": label,
            "birth_date": "",
            "disappearance_date": "",
            "disappearance_place": "",
            "notes": "Crawled candidate target image. Review provenance, rights, identity, and crop before approval.",
            "crop_x": "",
            "crop_y": "",
            "crop_width": "",
            "crop_height": "",
        }
    return {
        **common,
        "title": label,
        "location_label": "",
        "notes": "Crawled candidate place/source image. Review provenance and rights before approval.",
    }


def _append_rows(manifest_path: Path, kind: ManifestKind, rows: list[dict[str, str]]) -> None:
    fields = EXPECTED_FIELDS[kind]
    write_header = not manifest_path.exists() or manifest_path.stat().st_size == 0
    with manifest_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
