from __future__ import annotations

import csv
import hashlib
import os
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from PIL import Image

from .cache import CachedClassification, CachedImage, CrawlCache
from .cv import CVResult, classify_image, hamming_distance, perceptual_hash
from .manifests import EXPECTED_FIELDS, ManifestKind, read_manifest
from .paths import display_path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
USER_AGENT = "desaparecidos.uy-crawler/0.3"
PHASH_DUPLICATE_THRESHOLD = 6


@dataclass
class CrawlItem:
    id: str
    page_url: str
    image_url: str
    local_path: str
    ok: bool
    bytes_written: int = 0
    from_cache: bool = False
    duplicate: bool = False
    cv_label: str = ""
    cv_score: float = 0.0
    cv_accept: bool = False
    content_sha256: str = ""
    perceptual_hash: str = ""
    crawl_run_id: str = ""
    error: str | None = None


@dataclass
class CrawlSummary:
    manifest: str
    kind: ManifestKind
    pages: list[str]
    run_id: str
    trail_path: str | None = None
    items: list[CrawlItem] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    pages_crawled: int = 0
    images_seen: int = 0
    from_cache: int = 0
    cv_rejected: int = 0
    duplicates: int = 0
    added: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors and self.added > 0

    def to_api(self) -> dict[str, object]:
        return {
            "manifest": self.manifest,
            "kind": self.kind,
            "pages": self.pages,
            "run_id": self.run_id,
            "trail_path": self.trail_path,
            "ok": self.ok,
            "errors": self.errors,
            "pages_crawled": self.pages_crawled,
            "images_seen": self.images_seen,
            "from_cache": self.from_cache,
            "cv_rejected": self.cv_rejected,
            "duplicates": self.duplicates,
            "added": self.added,
            "items": [item.__dict__ for item in self.items],
        }


@dataclass
class CombinedCrawlSummary:
    pages: list[str]
    pages_crawled: int
    images_seen: int
    places: CrawlSummary
    people: CrawlSummary
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_api(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "pages": self.pages,
            "pages_crawled": self.pages_crawled,
            "images_seen": self.images_seen,
            "errors": self.errors,
            "results": {
                "places": self.places.to_api(),
                "people": self.people.to_api(),
            },
        }


class PageParser(HTMLParser):
    def __init__(self, page_url: str) -> None:
        super().__init__()
        self.page_url = page_url
        self.urls: list[str] = []
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        name = tag.lower()
        if name == "img":
            srcset = _best_srcset_candidate(values.get("srcset", ""))
            self._add_image(srcset or values.get("src", ""))
        elif name == "source":
            self._add_image(_best_srcset_candidate(values.get("srcset", "")))
        elif name == "meta":
            prop = (values.get("property") or values.get("name") or "").lower()
            if prop in {"og:image", "og:image:url", "twitter:image", "twitter:image:src"}:
                self._add_image(values.get("content", ""))
        elif name == "link" and "image_src" in values.get("rel", "").lower():
            self._add_image(values.get("href", ""))
        elif name == "a":
            self._add_link(values.get("href", ""))

    def _resolve(self, value: str | None) -> str | None:
        if not value or value.startswith("data:"):
            return None
        parsed = urlparse(value)
        if parsed.scheme and parsed.scheme not in {"http", "https"}:
            return None
        resolved, _ = urldefrag(urljoin(self.page_url, value))
        return resolved or None

    def _add_image(self, value: str | None) -> None:
        resolved = self._resolve(value)
        if resolved and resolved not in self.urls:
            self.urls.append(resolved)

    def _add_link(self, value: str | None) -> None:
        resolved = self._resolve(value)
        if resolved and resolved not in self.links:
            self.links.append(resolved)


def _best_srcset_candidate(value: str) -> str | None:
    candidates: list[tuple[float, str]] = []
    for raw in value.split(","):
        parts = raw.strip().split()
        if not parts:
            continue
        url = parts[0]
        score = 1.0
        for descriptor in parts[1:]:
            if descriptor.endswith("w"):
                score = _float_or_default(descriptor[:-1], score)
            elif descriptor.endswith("x"):
                score = _float_or_default(descriptor[:-1], score) * 1000
        candidates.append((score, url))
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[0])[1]


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
    cross_domain: bool = False,
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
    run_id = _run_id(kind, clean_pages)
    summary = CrawlSummary(
        manifest=display_path(manifest_path),
        kind=kind,
        pages=clean_pages,
        run_id=run_id,
    )
    client = session or requests.Session()
    rows: list[dict[str, str]] = []
    seen_urls = set(_existing_source_urls(manifest_path, kind))
    seen_sha, seen_phashes = _existing_dedupe_values(manifest_path, kind)
    seed_domains = {urlparse(page).netloc for page in clean_pages}
    visited_pages: set[str] = set()
    queued_pages: set[str] = set(clean_pages)
    robots: dict[str, RobotFileParser] = {}
    last_fetch: dict[str, float] = {}
    page_ordinal = 0
    image_ordinal = 0
    queue: deque[tuple[str, int, str | None]] = deque((page, 0, None) for page in clean_pages)

    settings = {
        "max_images_per_page": max_images_per_page,
        "max_depth": max_depth,
        "max_pages": max_pages,
        "max_images": max_images,
        "cross_domain": cross_domain,
        "delay": delay,
        "respect_robots": respect_robots,
        "use_cv": use_cv,
    }

    with CrawlCache(cache_root) as cache:
        cache.start_run(run_id, kind, display_path(manifest_path), clean_pages, settings)
        try:
            while queue and summary.pages_crawled < max_pages and summary.added < max_images:
                page_url, depth, parent_url = queue.popleft()
                page_url, _ = urldefrag(page_url)
                if page_url in visited_pages:
                    continue
                parsed_page = urlparse(page_url)
                if parsed_page.scheme not in {"http", "https"}:
                    summary.errors.append(f"unsupported page URL: {page_url}")
                    page_ordinal += 1
                    cache.put_page_event(run_id, page_ordinal, page_url, depth, parent_url, None, "unsupported")
                    continue
                if respect_robots and not _robots_allowed(client, robots, page_url, timeout):
                    visited_pages.add(page_url)
                    page_ordinal += 1
                    cache.put_page_event(run_id, page_ordinal, page_url, depth, parent_url, None, "robots-blocked")
                    continue

                _throttle(last_fetch, parsed_page.netloc, delay)
                status: int | None = None
                try:
                    page_response = client.get(
                        page_url, timeout=timeout, headers={"User-Agent": USER_AGENT}
                    )
                    status = getattr(page_response, "status_code", None)
                    page_response.raise_for_status()
                    parser = PageParser(page_url)
                    parser.feed(page_response.text)
                except Exception as exc:
                    visited_pages.add(page_url)
                    page_ordinal += 1
                    message = str(exc)
                    summary.errors.append(f"{page_url}: {message}")
                    cache.put_page_event(run_id, page_ordinal, page_url, depth, parent_url, status, "error", message)
                    continue

                visited_pages.add(page_url)
                summary.pages_crawled += 1
                page_ordinal += 1
                cache.put_page_event(run_id, page_ordinal, page_url, depth, parent_url, status, "fetched")

                for image_url in parser.urls[:max_images_per_page]:
                    if summary.added >= max_images:
                        break
                    image_ordinal += 1
                    item, row = _handle_image(
                        client,
                        cache,
                        run_id,
                        image_ordinal,
                        image_url,
                        page_url,
                        kind,
                        manifest_path,
                        summary,
                        seen_urls,
                        seen_sha,
                        seen_phashes,
                        len(rows) + 1,
                        label_prefix=label_prefix,
                        timeout=timeout,
                        max_bytes=max_bytes,
                        use_cv=use_cv,
                    )
                    if item is not None:
                        summary.items.append(item)
                    if row is not None:
                        rows.append(row)

                if depth < max_depth:
                    for link in parser.links:
                        if link in visited_pages or link in queued_pages:
                            continue
                        netloc = urlparse(link).netloc
                        if not cross_domain and netloc not in seed_domains:
                            continue
                        queued_pages.add(link)
                        queue.append((link, depth + 1, page_url))

            if rows:
                _append_rows(manifest_path, kind, rows)
        finally:
            cache.finish_run(run_id, summary.to_api())
            summary.trail_path = display_path(cache.export_run_jsonl(run_id))
    return summary


def crawl_pages_combined(
    pages: list[str],
    places_manifest: str | Path,
    people_manifest: str | Path,
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
    cross_domain: bool = False,
    delay: float = 0.7,
    respect_robots: bool = True,
    use_cv: bool = True,
) -> CombinedCrawlSummary:
    """Traverse once and classify every candidate independently for both source kinds."""
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

    manifest_paths = {
        "places": Path(places_manifest).expanduser(),
        "people": Path(people_manifest).expanduser(),
    }
    if manifest_paths["places"].resolve() == manifest_paths["people"].resolve():
        raise ValueError("place and people manifests must use different paths")
    for manifest_path in manifest_paths.values():
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
    cache_root = Path(output_root).expanduser()
    cache_root.mkdir(parents=True, exist_ok=True)
    clean_pages = [page.strip() for page in pages if page.strip()]
    summaries = {
        kind: CrawlSummary(
            manifest=display_path(manifest_paths[kind]),
            kind=kind,
            pages=clean_pages,
            run_id=_run_id(kind, clean_pages),
        )
        for kind in ("places", "people")
    }
    rows: dict[str, list[dict[str, str]]] = {"places": [], "people": []}
    seen_urls = {
        kind: set(_existing_source_urls(manifest_paths[kind], kind))
        for kind in ("places", "people")
    }
    dedupe = {
        kind: _existing_dedupe_values(manifest_paths[kind], kind)
        for kind in ("places", "people")
    }
    client = session or requests.Session()
    seed_domains = {urlparse(page).netloc for page in clean_pages}
    visited_pages: set[str] = set()
    queued_pages: set[str] = set(clean_pages)
    candidate_urls: set[str] = set()
    robots: dict[str, RobotFileParser] = {}
    last_fetch: dict[str, float] = {}
    page_ordinal = 0
    image_ordinal = 0
    pages_crawled = 0
    errors: list[str] = []
    queue: deque[tuple[str, int, str | None]] = deque((page, 0, None) for page in clean_pages)
    settings = {
        "combined": True,
        "max_images_per_page": max_images_per_page,
        "max_depth": max_depth,
        "max_pages": max_pages,
        "max_images": max_images,
        "cross_domain": cross_domain,
        "delay": delay,
        "respect_robots": respect_robots,
        "use_cv": use_cv,
    }

    with CrawlCache(cache_root) as cache:
        for kind, summary in summaries.items():
            cache.start_run(summary.run_id, kind, summary.manifest, clean_pages, settings)
        try:
            while queue and pages_crawled < max_pages and len(candidate_urls) < max_images:
                page_url, depth, parent_url = queue.popleft()
                page_url, _ = urldefrag(page_url)
                if page_url in visited_pages:
                    continue
                parsed_page = urlparse(page_url)
                if parsed_page.scheme not in {"http", "https"}:
                    message = f"unsupported page URL: {page_url}"
                    errors.append(message)
                    page_ordinal += 1
                    for summary in summaries.values():
                        cache.put_page_event(summary.run_id, page_ordinal, page_url, depth, parent_url, None, "unsupported")
                    continue
                if respect_robots and not _robots_allowed(client, robots, page_url, timeout):
                    visited_pages.add(page_url)
                    page_ordinal += 1
                    for summary in summaries.values():
                        cache.put_page_event(summary.run_id, page_ordinal, page_url, depth, parent_url, None, "robots-blocked")
                    continue

                _throttle(last_fetch, parsed_page.netloc, delay)
                status: int | None = None
                try:
                    page_response = client.get(page_url, timeout=timeout, headers={"User-Agent": USER_AGENT})
                    status = getattr(page_response, "status_code", None)
                    page_response.raise_for_status()
                    parser = PageParser(page_url)
                    parser.feed(page_response.text)
                except Exception as exc:
                    visited_pages.add(page_url)
                    page_ordinal += 1
                    message = f"{page_url}: {exc}"
                    errors.append(message)
                    for summary in summaries.values():
                        cache.put_page_event(summary.run_id, page_ordinal, page_url, depth, parent_url, status, "error", str(exc))
                    continue

                visited_pages.add(page_url)
                pages_crawled += 1
                page_ordinal += 1
                for summary in summaries.values():
                    summary.pages_crawled = pages_crawled
                    cache.put_page_event(summary.run_id, page_ordinal, page_url, depth, parent_url, status, "fetched")

                for image_url in parser.urls[:max_images_per_page]:
                    if image_url in candidate_urls:
                        continue
                    if len(candidate_urls) >= max_images:
                        break
                    candidate_urls.add(image_url)
                    image_ordinal += 1
                    for kind in ("places", "people"):
                        summary = summaries[kind]
                        sha_seen, phash_seen = dedupe[kind]
                        item, row = _handle_image(
                            client, cache, summary.run_id, image_ordinal, image_url, page_url,
                            kind, manifest_paths[kind], summary, seen_urls[kind], sha_seen,
                            phash_seen, len(rows[kind]) + 1, label_prefix=label_prefix,
                            timeout=timeout, max_bytes=max_bytes, use_cv=use_cv,
                        )
                        if item is not None:
                            summary.items.append(item)
                        if row is not None:
                            rows[kind].append(row)

                if depth < max_depth:
                    for link in parser.links:
                        if link in visited_pages or link in queued_pages:
                            continue
                        if not cross_domain and urlparse(link).netloc not in seed_domains:
                            continue
                        queued_pages.add(link)
                        queue.append((link, depth + 1, page_url))

            for kind in ("places", "people"):
                if rows[kind]:
                    _append_rows(manifest_paths[kind], kind, rows[kind])
        finally:
            for summary in summaries.values():
                summary.errors.extend(errors)
                cache.finish_run(summary.run_id, summary.to_api())
                summary.trail_path = display_path(cache.export_run_jsonl(summary.run_id))

    return CombinedCrawlSummary(
        pages=clean_pages,
        pages_crawled=pages_crawled,
        images_seen=len(candidate_urls),
        places=summaries["places"],
        people=summaries["people"],
        errors=errors,
    )


def _handle_image(
    client: requests.Session,
    cache: CrawlCache,
    run_id: str,
    ordinal: int,
    image_url: str,
    page_url: str,
    kind: ManifestKind,
    manifest_path: Path,
    summary: CrawlSummary,
    seen_urls: set[str],
    seen_sha: set[str],
    seen_phashes: set[str],
    index: int,
    *,
    label_prefix: str,
    timeout: int,
    max_bytes: int,
    use_cv: bool,
) -> tuple[CrawlItem | None, dict[str, str] | None]:
    row_id = _row_id(page_url, image_url, index)
    if image_url in seen_urls:
        summary.duplicates += 1
        cache.put_image_event(run_id, ordinal, page_url, image_url, "duplicate-url", row_id=row_id)
        return None, None
    seen_urls.add(image_url)
    summary.images_seen += 1

    try:
        cached = cache.get_image(image_url)
        if cached is not None and cached.path and Path(cached.path).exists():
            summary.from_cache += 1
            return _finalise_cached(
                cache, run_id, ordinal, row_id, image_url, page_url, kind, manifest_path,
                summary, seen_sha, seen_phashes, index, label_prefix, cached, use_cv,
            )

        response = client.get(image_url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        payload = response.content
        if len(payload) > max_bytes:
            raise ValueError(f"image exceeds {max_bytes} bytes")
        content_type = response.headers.get("content-type", "")
        suffix = _suffix_for(image_url, content_type)
        if suffix == ".bin" and not content_type.startswith("image/"):
            raise ValueError(f"not an image response: {content_type or 'unknown content type'}")
        image = Image.open(BytesIO(payload)).convert("RGB")
        width, height = image.size
        sha = hashlib.sha256(payload).hexdigest()
        phash = perceptual_hash(image)

        stored_path = cache.store_path(sha, suffix)
        exact = cache.get_by_hash(sha)
        if exact is not None and Path(exact.path).exists():
            stored_path = Path(exact.path)
        elif not stored_path.exists():
            stored_path.write_bytes(payload)

        cached_record = CachedImage(
            url=image_url,
            sha256=sha,
            phash=phash,
            path=str(stored_path),
            bytes=len(payload),
            width=width,
            height=height,
            content_type=content_type,
        )
        cache.put_image(cached_record)
        duplicate = _duplicate_reason(sha, phash, seen_sha, seen_phashes)
        if duplicate is not None:
            summary.duplicates += 1
            cache.put_image_event(
                run_id, ordinal, page_url, image_url, duplicate,
                row_id=row_id, sha256=sha, phash=phash, path=str(stored_path),
            )
            return CrawlItem(
                row_id, page_url, image_url, "", False, duplicate=True,
                content_sha256=sha, perceptual_hash=phash, crawl_run_id=run_id,
                error=duplicate,
            ), None
        cv = _classify(cache, cached_record, kind, image, use_cv)
        return _finalise(
            cache, run_id, ordinal, row_id, image_url, page_url, kind, manifest_path,
            summary, seen_sha, seen_phashes, index, label_prefix, cached_record, cv,
            bytes_written=len(payload), from_cache=False,
        )
    except Exception as exc:
        message = str(exc)
        cache.put_image_event(run_id, ordinal, page_url, image_url, "error", row_id=row_id, error=message)
        return CrawlItem(
            row_id, page_url, image_url, "", False, crawl_run_id=run_id, error=message,
        ), None


def _finalise_cached(
    cache: CrawlCache,
    run_id: str,
    ordinal: int,
    row_id: str,
    image_url: str,
    page_url: str,
    kind: ManifestKind,
    manifest_path: Path,
    summary: CrawlSummary,
    seen_sha: set[str],
    seen_phashes: set[str],
    index: int,
    label_prefix: str,
    cached: CachedImage,
    use_cv: bool,
) -> tuple[CrawlItem, dict[str, str] | None]:
    duplicate = _duplicate_reason(cached.sha256, cached.phash, seen_sha, seen_phashes)
    if duplicate is not None:
        summary.duplicates += 1
        cache.put_image_event(
            run_id, ordinal, page_url, image_url, duplicate,
            row_id=row_id, sha256=cached.sha256, phash=cached.phash, path=cached.path,
        )
        return CrawlItem(
            row_id, page_url, image_url, "", False, from_cache=True, duplicate=True,
            content_sha256=cached.sha256, perceptual_hash=cached.phash, crawl_run_id=run_id,
            error=duplicate,
        ), None
    image = Image.open(cached.path).convert("RGB")
    cv = _classify(cache, cached, kind, image, use_cv)
    return _finalise(
        cache, run_id, ordinal, row_id, image_url, page_url, kind, manifest_path,
        summary, seen_sha, seen_phashes, index, label_prefix, cached, cv,
        bytes_written=0, from_cache=True,
    )


def _finalise(
    cache: CrawlCache,
    run_id: str,
    ordinal: int,
    row_id: str,
    image_url: str,
    page_url: str,
    kind: ManifestKind,
    manifest_path: Path,
    summary: CrawlSummary,
    seen_sha: set[str],
    seen_phashes: set[str],
    index: int,
    label_prefix: str,
    cached: CachedImage,
    cv: CVResult,
    *,
    bytes_written: int,
    from_cache: bool,
) -> tuple[CrawlItem, dict[str, str] | None]:
    item = CrawlItem(
        id=row_id,
        page_url=page_url,
        image_url=image_url,
        local_path=display_path(cached.path) if cv.accept else "",
        ok=cv.accept,
        bytes_written=bytes_written,
        from_cache=from_cache,
        cv_label=cv.label,
        cv_score=cv.score,
        cv_accept=cv.accept,
        content_sha256=cached.sha256,
        perceptual_hash=cached.phash,
        crawl_run_id=run_id,
        error=None if cv.accept else f"cv rejected: {cv.reason}",
    )
    if not cv.accept:
        summary.cv_rejected += 1
        cache.put_image_event(
            run_id, ordinal, page_url, image_url, "cv-rejected",
            row_id=row_id, sha256=cached.sha256, phash=cached.phash,
            path=cached.path, cv_label=cv.label, error=cv.reason,
        )
        return item, None

    summary.added += 1
    seen_sha.add(cached.sha256)
    seen_phashes.add(cached.phash)
    cache.put_image_event(
        run_id, ordinal, page_url, image_url, "accepted",
        row_id=row_id, sha256=cached.sha256, phash=cached.phash,
        path=cached.path, cv_label=cv.label,
    )
    manifest_local_path = _relative_manifest_path(manifest_path, Path(cached.path))
    row = _manifest_row(
        kind, row_id, image_url, page_url, manifest_local_path, index, label_prefix,
        run_id=run_id, sha=cached.sha256, phash=cached.phash, face_box=cv.face_box,
    )
    return item, row


def _classify(
    cache: CrawlCache,
    cached: CachedImage,
    kind: ManifestKind,
    image: Image.Image,
    use_cv: bool,
) -> CVResult:
    existing = cache.get_classification(cached.url, kind)
    if existing is not None and (not use_cv or existing.cv_label != "cv-off"):
        face_box = None
        if None not in (existing.face_x, existing.face_y, existing.face_width, existing.face_height):
            face_box = (
                int(existing.face_x or 0),
                int(existing.face_y or 0),
                int(existing.face_width or 0),
                int(existing.face_height or 0),
            )
        return CVResult(
            existing.cv_accept,
            existing.cv_label,
            existing.cv_score,
            "cached classification",
            face_box,
        )
    cv = classify_image(image, kind) if use_cv else CVResult(True, "cv-off", 0.0, "cv disabled")
    face = cv.face_box
    cache.put_classification(
        CachedClassification(
            url=cached.url,
            kind=kind,
            cv_label=cv.label,
            cv_score=cv.score,
            cv_accept=cv.accept,
            face_x=face[0] if face else None,
            face_y=face[1] if face else None,
            face_width=face[2] if face else None,
            face_height=face[3] if face else None,
        )
    )
    return cv


def _duplicate_reason(
    sha: str,
    phash: str,
    seen_sha: set[str],
    seen_phashes: set[str],
) -> str | None:
    if sha in seen_sha:
        return "duplicate-content"
    for existing in seen_phashes:
        if hamming_distance(phash, existing) <= PHASH_DUPLICATE_THRESHOLD:
            return "duplicate-visual"
    return None


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
            parser.parse([])
        robots[base] = parser
    return parser.can_fetch(USER_AGENT, url)


def _existing_source_urls(manifest_path: Path, kind: ManifestKind) -> set[str]:
    if not manifest_path.exists():
        return set()
    validation = read_manifest(manifest_path, kind)
    return {row.values.get("source_url", "") for row in validation.rows if row.values.get("source_url")}


def _existing_dedupe_values(manifest_path: Path, kind: ManifestKind) -> tuple[set[str], set[str]]:
    if not manifest_path.exists():
        return set(), set()
    validation = read_manifest(manifest_path, kind)
    shas = {row.values.get("content_sha256", "") for row in validation.rows if row.values.get("content_sha256")}
    phashes = {row.values.get("perceptual_hash", "") for row in validation.rows if row.values.get("perceptual_hash")}
    return shas, phashes


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


def _run_id(kind: ManifestKind, pages: list[str]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest = hashlib.sha256("\n".join(pages).encode("utf-8")).hexdigest()[:8]
    return f"{now}-{kind}-{digest}"


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
    *,
    run_id: str,
    sha: str,
    phash: str,
    face_box: tuple[int, int, int, int] | None,
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
    if kind == "people":
        x, y, width, height = face_box or ("", "", "", "")
        return {
            **common,
            "title": label,
            "location_label": "",
            "notes": "Crawled candidate contemporary people image. Internal Stage 2 review only; no identity matching has been performed.",
            "crawl_run_id": run_id,
            "content_sha256": sha,
            "perceptual_hash": phash,
            "face_x": str(x),
            "face_y": str(y),
            "face_width": str(width),
            "face_height": str(height),
        }
    return {
        **common,
        "title": label,
        "location_label": "",
        "notes": "Crawled candidate place/source image. Review provenance and rights before approval.",
        "crawl_run_id": run_id,
        "content_sha256": sha,
        "perceptual_hash": phash,
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


def _float_or_default(value: str, default: float) -> float:
    try:
        return float(value)
    except ValueError:
        return default
