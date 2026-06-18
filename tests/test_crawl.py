from __future__ import annotations

from io import BytesIO
from pathlib import Path

import numpy as np
import requests
from PIL import Image

from desaparecidos.cache import CrawlCache
from desaparecidos.crawl import _best_srcset_candidate, crawl_pages
from desaparecidos.manifests import read_manifest, set_review_status


class FakeSession:
    def __init__(self, responses: dict[str, requests.Response]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def get(self, url: str, **_: object) -> requests.Response:
        self.calls.append(url)
        if url not in self.responses:
            raise requests.exceptions.ConnectionError(f"no response for {url}")
        return self.responses[url]

    def count(self, url: str) -> int:
        return sum(1 for call in self.calls if call == url)


def response(
    body: bytes | str,
    *,
    content_type: str = "text/html",
    status_code: int = 200,
) -> requests.Response:
    result = requests.Response()
    result.status_code = status_code
    result._content = body if isinstance(body, bytes) else body.encode("utf-8")
    result.headers["content-type"] = content_type
    result.url = "https://example.test/"
    return result


def png_bytes(size: tuple[int, int] = (240, 240), *, seed: int = 7) -> bytes:
    arr = np.random.default_rng(seed).integers(0, 255, (size[1], size[0], 3), dtype=np.uint8)
    image = Image.fromarray(arr, "RGB")
    handle = BytesIO()
    image.save(handle, format="PNG")
    return handle.getvalue()


def image_response(body: bytes) -> requests.Response:
    return response(body, content_type="image/png")


def test_srcset_selects_one_largest_candidate() -> None:
    assert _best_srcset_candidate("small.jpg 320w, large.jpg 1280w") == "large.jpg"
    assert _best_srcset_candidate("one.jpg 1x, two.jpg 2x") == "two.jpg"


def test_crawl_pages_appends_pending_manifest_rows_and_trail(tmp_path: Path) -> None:
    page = "https://example.test/page"
    image = "https://example.test/photo.png"
    session = FakeSession({
        page: response(f'<html><img src="{image}"></html>'),
        image: image_response(png_bytes()),
    })
    manifest = tmp_path / "data" / "manifests" / "crawled-places.csv"
    output_root = tmp_path / "data" / "raw" / "crawl"

    summary = crawl_pages(
        [page],
        "places",
        manifest,
        output_root=output_root,
        session=session,
        use_cv=False,
        delay=0,
        respect_robots=False,
    )

    assert summary.ok is True
    assert summary.run_id
    assert summary.trail_path
    assert summary.pages_crawled == 1
    assert summary.items[0].ok is True
    validation = read_manifest(manifest, "places")
    row = validation.rows[0]
    assert row.review_status == "pending"
    assert row.values["source_url"] == image
    assert row.values["crawl_run_id"] == summary.run_id
    assert row.values["content_sha256"]
    assert row.values["perceptual_hash"]
    assert (manifest.parent / row.local_path).exists()
    with CrawlCache(output_root) as cache:
        trail = cache.page_trail(summary.run_id)
    assert [entry["url"] for entry in trail] == [page]


def test_review_status_update_allows_people_approval(tmp_path: Path) -> None:
    page = "https://example.test/page"
    image = "https://example.test/person.png"
    session = FakeSession({
        page: response(f'<meta property="og:image" content="{image}">'),
        image: image_response(png_bytes()),
    })
    manifest = tmp_path / "data" / "manifests" / "crawled-people.csv"
    crawl_pages(
        [page],
        "people",
        manifest,
        output_root=tmp_path / "data" / "raw" / "crawl",
        session=session,
        use_cv=True,
        delay=0,
        respect_robots=False,
    )
    row = read_manifest(manifest, "people").rows[0]

    validation = set_review_status(manifest, "people", row.id, "approved")

    assert validation.ok is True
    assert validation.rows[0].approved is True
    assert validation.rows[0].values["face_width"]


def test_perceptual_duplicate_rejects_resized_variant(tmp_path: Path) -> None:
    page = "https://example.test/page"
    image_a = "https://example.test/a.png"
    image_b = "https://example.test/b.png"
    base = Image.open(BytesIO(png_bytes((260, 260), seed=12))).convert("RGB")
    a_handle = BytesIO()
    b_handle = BytesIO()
    base.save(a_handle, format="PNG")
    base.resize((240, 240), Image.Resampling.LANCZOS).save(b_handle, format="PNG")
    session = FakeSession({
        page: response(f'<img src="{image_a}"><img src="{image_b}">'),
        image_a: image_response(a_handle.getvalue()),
        image_b: image_response(b_handle.getvalue()),
    })
    manifest = tmp_path / "crawled-places.csv"

    summary = crawl_pages(
        [page],
        "places",
        manifest,
        output_root=tmp_path / "crawl",
        session=session,
        use_cv=False,
        delay=0,
        respect_robots=False,
    )

    assert summary.added == 1
    assert summary.duplicates == 1
    assert len(read_manifest(manifest, "places").rows) == 1


def test_cache_reuses_url_but_classifies_per_kind(tmp_path: Path) -> None:
    page = "https://example.test/page"
    image = "https://example.test/photo.png"
    session = FakeSession({
        page: response(f'<img src="{image}">'),
        image: image_response(png_bytes()),
    })
    output_root = tmp_path / "crawl"

    first = crawl_pages(
        [page],
        "places",
        tmp_path / "places.csv",
        output_root=output_root,
        session=session,
        use_cv=False,
        delay=0,
        respect_robots=False,
    )
    second = crawl_pages(
        [page],
        "people",
        tmp_path / "people.csv",
        output_root=output_root,
        session=session,
        use_cv=True,
        delay=0,
        respect_robots=False,
    )

    assert session.count(image) == 1
    assert first.added == 1
    assert second.from_cache == 1
    assert second.added == 1
    with CrawlCache(output_root) as cache:
        assert cache.get_classification(image, "places") is not None
        assert cache.get_classification(image, "people") is not None


def test_crawler_follows_links_to_depth(tmp_path: Path) -> None:
    page_a = "https://a.test/"
    page_b = "https://a.test/b"
    img_a = "https://a.test/a.png"
    img_b = "https://a.test/b.png"
    session = FakeSession({
        page_a: response(f'<a href="{page_b}">next</a><img src="{img_a}">'),
        page_b: response(f'<img src="{img_b}">'),
        img_a: image_response(png_bytes(seed=1)),
        img_b: image_response(png_bytes(seed=2)),
    })
    manifest = tmp_path / "crawled-places.csv"

    summary = crawl_pages(
        [page_a], "places", manifest,
        output_root=tmp_path / "crawl", session=session,
        max_depth=1, delay=0, respect_robots=False, use_cv=False,
    )

    assert summary.pages_crawled == 2
    assert summary.added == 2
