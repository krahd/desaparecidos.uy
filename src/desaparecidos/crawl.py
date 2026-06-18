from __future__ import annotations

import csv
import hashlib
import os
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import date
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from PIL import Image

from .cache import CrawlCache, sha256_hex
from .cv import CVResult, classify_image
from .manifests import EXPECTED_FIELDS, ManifestKind, read_manifest
from .paths import display_path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
USER_AGENT = "desaparecidos.uy-stage1-crawler/0.2"


@dataclass
class CrawlItem:
    id: str
    page_url: str
    image_url: str
    local_path: str
    ok: bool
    bytes_written: int = 0
    from_cache: bool = False
    cv_label: str = ""
    cv_score: float = 0.0
    cv_accept: bool = False
    error: str | None = None


@dataclass
class CrawlSummary:
    manifest: str
    kind: ManifestKind
    pages: list[str]
    items: list[CrawlItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    pages_crawled: int = 0
    images_seen: int = 0
    from_cache: int = 0
    cv_rejected: int = 0
    added: int = 0

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
            "pages_crawled": self.pages_crawled,
            "images_seen": self.images_seen,
            "from_cache": self.from_cache,
            "cv_rejected": self.cv_rejected,
            "added": self.added,
            "items": [item.__dict__ for item in self.items],
        }


class PageParser(HTMLParser):
    """Collects image URLs and anchor links from a page."""

    def __init__(self, page_url: str) -> None:
        super().__init__()
        self.page_url = page_url
        self.urls: list[str] = []
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        name = tag.lower()
        if name == "img":
            self._add_image(values.get("src", ""))
            self._add_srcset(values.get("srcset", ""))
        elif name == "source":
            self._add_srcset(values.get("srcset", ""))
        elif name == "meta":
            prop = (values.get("property") or values.get("name") or "").lower()
            if prop in {"og:image", "og:image:url", "twitter:image", "twitter:image:src"}:
                self._add_image(values.get("content", ""))
        elif name == "link" and "image_src" in values.get("rel", "").lower():
            self._add_image(values.get("href", ""))
        elif name == "a":
            self._add_link(values.get("href", ""))

    def _add_srcset(self, value: str) -> None:
        for candidate in value.split(","):
            url = candidate.strip().split(" ", 1)[0]
            self._add_image(url)

    def _resolve(self, value: str) -> str | None:
        if not value or value.startswith("data:"):
            return None
        parsed = urlparse(value)
        if parsed.scheme and parsed.scheme not in {"http", "https"}:
            return None
        resolved, _ = urldefrag(urljoin(self.page_url, value))
        return resolved or None

    def _add_image(self, value: str) -> None:
        resolved = self._resolve(value)
        if resolved and resolved not in self.urls:
            self.urls.append(resolved)

    def _add_link(self, value: str) -> None:
        resolved = self._resolve(value)
        if resolved and resolved not in self.links:
            self.links.append(resolved)


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
    max_depth: int = 2,
    max_pages: int = 60,
    max_images: int = 80,
    cross_domain: bool = True,
    delay: float = 0.7,
    respect_robots: bool = True,
    use_cv: bool = True,
) -> CrawlSummary:
    if not pages:
        raise ValueError("at least one page URL is required")
    if max_images_per_page < 1 or max_images_per_page > 50:
        raise ValueError("max_images_per_page must be between 1 and 50")
    if max_depth < 0 or max_depth > 4:
        raise ValueError("max_depth must be between 0 and 4")
    if max_pages < 1 or max_pages > 500:
        raise ValueError("max_pages must be between 1 and 500")
    if max_images < 1 or max_images > 1000:
        raise ValueError("max_images must be between 1 and 1000")

    manifest_path = Path(manifest).expanduser()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    cache_root = Path(output_root).expanduser()
    cache_root.mkdir(parents=True, exist_ok=True)

    clean_pages = [page.strip() for page in pages if page.strip()]
    summary = CrawlSummary(manifest=display_path(manifest_path), kind=kind, pages=clean_pages)
    client = session or requests.Session()
    cache = CrawlCache(cache_root)

    seen_images: set[str] = set(_existing_source_urls(manifest_path, kind))
    seed_domains = {urlparse(page).netloc for page in clean_pages}
    visited_pages: set[str] = set()
    robots: dict[str, RobotFileParser] = {}
    last_fetch: dict[str, float] = {}
    rows: list[dict[str, str]] = []
    queue: deque[tuple[str, int]] = deque((page, 0) for page in clean_pages)

    try:
        while queue:
            if summary.pages_crawled >= max_pages or summary.added >= max_images:
                break
            page_url, depth = queue.popleft()
            page_url, _ = urldefrag(page_url)
            if page_url in visited_pages:
                continue
            parsed_page = urlparse(page_url)
            if parsed_page.scheme not in {"http", "https"}:
                summary.errors.append(f"unsupported page URL: {page_url}")
                continue
            if respect_robots and not _robots_allowed(client, robots, page_url, timeout):
                visited_pages.add(page_url)
                summary.errors.append(f"{page_url}: blocked by robots.txt")
                continue

            _throttle(last_fetch, parsed_page.netloc, delay)
            try:
                page_response = client.get(
                    page_url, timeout=timeout, headers={"User-Agent": USER_AGENT}
                )
                page_response.raise_for_status()
                parser = PageParser(page_url)
                parser.feed(page_response.text)
            except Exception as exc:
                summary.errors.append(f"{page_url}: {exc}")
                continue

            visited_pages.add(page_url)
            summary.pages_crawled += 1
            cache.put_page(page_url, depth, getattr(page_response, "status_code", 0))

            for image_url in parser.urls[:max_images_per_page]:
                if summary.added >= max_images:
                    break
                item, row = _handle_image(
                    client, cache, image_url, page_url, kind, manifest_path,
                    summary, seen_images, len(rows) + 1,
                    label_prefix=label_prefix, timeout=timeout, max_bytes=max_bytes,
                    use_cv=use_cv,
                )
                if item is None:
                    continue
                summary.items.append(item)
                if row is not None:
                    rows.append(row)

            if depth < max_depth:
                for link in parser.links:
                    if link in visited_pages:
                        continue
                    netloc = urlparse(link).netloc
                    if not cross_domain and netloc not in seed_domains:
                        continue
                    queue.append((link, depth + 1))

        if rows:
            _append_rows(manifest_path, kind, rows)
    finally:
        cache.close()
    return summary


def _throttle(last_fetch: dict[str, float], host: str, delay: float) -> None:
    if delay <= 0:
        return
    now = time.monotonic()
    previous = last_fetch.get(host)
    if previous is not None:
        wait = delay - (now - previous)
        if wait > 0:
            time.sleep(wait)
    last_fetch[host] = time.monotonic()


def _robots_allowed(
    client: requests.Session,
    robots: dict[str, RobotFileParser],
    url: str,
    timeout: int,
) -> bool:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    parser = robots.get(base)
    if parser is None:
        parser = RobotFileParser()
        try:
            response = client.get(
                urljoin(base, "/robots.txt"), timeout=timeout, headers={"User-Agent": USER_AGENT}
            )
            if response.status_code >= 400:
                parser.parse([])
            else:
                parser.parse(response.text.splitlines())
        except Exception:
            parser.parse([])  # on any error, do not block
        robots[base] = parser
    return parser.can_fetch(USER_AGENT, url)


def _handle_image(
    client: requests.Session,
    cache: CrawlCache,
    image_url: str,
    page_url: str,
    kind: ManifestKind,
    manifest_path: Path,
    summary: CrawlSummary,
    seen_images: set[str],
    index: int,
    *,
    label_prefix: str,
    timeout: int,
    max_bytes: int,
    use_cv: bool,
) -> tuple[CrawlItem | None, dict[str, str] | None]:
    if image_url in seen_images:
        return None, None
    seen_images.add(image_url)
    summary.images_seen += 1
    row_id = _row_id(page_url, image_url, index)

    cached = cache.get_image(image_url)
    if cached is not None and cached.path and Path(cached.path).exists():
        summary.from_cache += 1
        return _finalise(
            summary, kind, row_id, image_url, page_url, manifest_path, index,
            label_prefix, Path(cached.path), bytes_written=0, from_cache=True,
            cv=CVResult(cached.cv_accept, cached.cv_label, cached.cv_score, "cached"),
        )

    try:
        response = client.get(image_url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        payload = response.content
        if len(payload) > max_bytes:
            raise ValueError(f"image exceeds {max_bytes} bytes")
        content_type = response.headers.get("content-type", "")
        suffix = _suffix_for(image_url, content_type)
        if suffix == ".bin" and not content_type.startswith("image/"):
            raise ValueError(f"not an image response: {content_type or 'unknown content type'}")
        try:
            image = Image.open(BytesIO(payload))
            image.load()
        except Exception as exc:
            raise ValueError(f"not a decodable image: {exc}") from exc
        width, height = image.size
        sha = sha256_hex(payload)

        duplicate = cache.get_by_hash(sha)
        if duplicate is not None and Path(duplicate.path).exists():
            stored_path = Path(duplicate.path)
            cv = CVResult(duplicate.cv_accept, duplicate.cv_label, duplicate.cv_score, "deduped")
        else:
            cv = classify_image(image, kind) if use_cv else CVResult(True, "cv-off", 0.0, "cv disabled")
            stored_path = cache.store_path(sha, suffix)
            if not stored_path.exists():
                stored_path.write_bytes(payload)

        cache.put_image(
            _cached_record(image_url, sha, stored_path, payload, width, height, content_type, cv)
        )
        return _finalise(
            summary, kind, row_id, image_url, page_url, manifest_path, index,
            label_prefix, stored_path, bytes_written=len(payload), from_cache=False, cv=cv,
        )
    except Exception as exc:
        return CrawlItem(
            id=row_id, page_url=page_url, image_url=image_url, local_path="",
            ok=False, error=str(exc),
        ), None


def _finalise(
    summary: CrawlSummary,
    kind: ManifestKind,
    row_id: str,
    image_url: str,
    page_url: str,
    manifest_path: Path,
    index: int,
    label_prefix: str,
    stored_path: Path,
    *,
    bytes_written: int,
    from_cache: bool,
    cv: CVResult,
) -> tuple[CrawlItem, dict[str, str] | None]:
    item = CrawlItem(
        id=row_id, page_url=page_url, image_url=image_url,
        local_path=display_path(stored_path), ok=cv.accept, bytes_written=bytes_written,
        from_cache=from_cache, cv_label=cv.label, cv_score=cv.score, cv_accept=cv.accept,
        error=None if cv.accept else f"cv rejected: {cv.reason}",
    )
    if not cv.accept:
        summary.cv_rejected += 1
        return item, None
    summary.added += 1
    manifest_local_path = _relative_manifest_path(manifest_path, stored_path)
    row = _manifest_row(kind, row_id, image_url, page_url, manifest_local_path, index, label_prefix)
    return item, row


def _cached_record(image_url, sha, stored_path, payload, width, height, content_type, cv):
    from .cache import CachedImage

    return CachedImage(
        url=image_url, sha256=sha, path=str(stored_path), bytes=len(payload),
        width=width, height=height, content_type=content_type,
        cv_label=cv.label, cv_score=cv.score, cv_accept=cv.accept,
    )


def _existing_source_urls(manifest_path: Path, kind: ManifestKind) -> set[str]:
    if not manifest_path.exists():
        return set()
    validation = read_manifest(manifest_path, kind)
    return {row.values.get("source_url", "") for row in validation.rows if row.values.get("source_url")}


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
