from __future__ import annotations

from io import BytesIO
from pathlib import Path

import numpy as np
import requests
from PIL import Image

from desaparecidos.crawl import crawl_pages
from desaparecidos.manifests import read_manifest, set_review_status


class FakeSession:
    """Serves canned responses and records every GET for download counting."""

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


def response(body: bytes | str, *, content_type: str = "text/html", status_code: int = 200) -> requests.Response:
    result = requests.Response()
    result.status_code = status_code
    result._content = body if isinstance(body, bytes) else body.encode("utf-8")
    result.headers["content-type"] = content_type
    result.url = "https://example.test/"
    return result


def png_bytes(size: tuple[int, int] = (400, 400), *, flat: bool = False, seed: int = 7) -> bytes:
    if flat:
        image = Image.new("RGB", size, (180, 60, 60))
    else:
        arr = np.random.default_rng(seed).integers(0, 255, (size[1], size[0], 3), dtype=np.uint8)
        image = Image.fromarray(arr, "RGB")
    handle = BytesIO()
    image.save(handle, format="PNG")
    return handle.getvalue()


def image_response(body: bytes) -> requests.Response:
    return response(body, content_type="image/png")


def test_crawl_pages_appends_pending_manifest_rows(tmp_path: Path) -> None:
    page = "https://example.test/page"
    image = "https://example.test/photo.png"
    session = FakeSession({
        page: response(f'<html><img src="{image}"></html>'),
        image: image_response(png_bytes((12, 12))),
    })
    manifest = tmp_path / "data" / "manifests" / "crawled-places.csv"

    summary = crawl_pages(
        [page], "places", manifest,
        output_root=tmp_path / "data" / "raw" / "crawl",
        session=session, use_cv=False, delay=0, respect_robots=False,
    )

    assert summary.ok is True
    assert summary.items[0].ok is True
    validation = read_manifest(manifest, "places")
    assert validation.rows[0].review_status == "pending"
    assert validation.rows[0].values["source_url"] == image
    assert (manifest.parent / validation.rows[0].local_path).exists()


def test_review_status_update_allows_approval(tmp_path: Path) -> None:
    page = "https://example.test/page"
    image = "https://example.test/photo.png"
    session = FakeSession({
        page: response(f'<meta property="og:image" content="{image}">'),
        image: image_response(png_bytes((12, 12))),
    })
    manifest = tmp_path / "data" / "manifests" / "crawled-targets.csv"
    crawl_pages(
        [page], "targets", manifest,
        output_root=tmp_path / "data" / "raw" / "crawl",
        session=session, use_cv=False, delay=0, respect_robots=False,
    )
    row_id = read_manifest(manifest, "targets").rows[0].id

    validation = set_review_status(manifest, "targets", row_id, "approved")

    assert validation.ok is True
    assert validation.rows[0].approved is True


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
        max_depth=1, delay=0, respect_robots=False,
    )

    assert summary.pages_crawled == 2
    assert summary.added == 2


def test_crawler_respects_total_image_cap(tmp_path: Path) -> None:
    page = "https://a.test/"
    session = FakeSession({
        page: response('<img src="https://a.test/1.png"><img src="https://a.test/2.png">'),
        "https://a.test/1.png": image_response(png_bytes(seed=1)),
        "https://a.test/2.png": image_response(png_bytes(seed=2)),
    })
    manifest = tmp_path / "crawled-places.csv"

    summary = crawl_pages(
        [page], "places", manifest,
        output_root=tmp_path / "crawl", session=session,
        max_images=1, delay=0, respect_robots=False,
    )

    assert summary.added == 1


def test_crawler_same_domain_only_when_cross_domain_off(tmp_path: Path) -> None:
    page = "https://a.test/"
    other = "https://b.other/"
    session = FakeSession({
        page: response(f'<a href="{other}">x</a><img src="https://a.test/a.png">'),
        other: response('<img src="https://b.other/b.png">'),
        "https://a.test/a.png": image_response(png_bytes(seed=1)),
        "https://b.other/b.png": image_response(png_bytes(seed=2)),
    })
    manifest = tmp_path / "crawled-places.csv"

    summary = crawl_pages(
        [page], "places", manifest,
        output_root=tmp_path / "crawl", session=session,
        max_depth=1, cross_domain=False, delay=0, respect_robots=False,
    )

    assert summary.pages_crawled == 1


def test_crawler_blocks_disallowed_by_robots(tmp_path: Path) -> None:
    page = "https://a.test/page"
    session = FakeSession({
        "https://a.test/robots.txt": response("User-agent: *\nDisallow: /"),
        page: response('<img src="https://a.test/a.png">'),
        "https://a.test/a.png": image_response(png_bytes()),
    })
    manifest = tmp_path / "crawled-places.csv"

    summary = crawl_pages(
        [page], "places", manifest,
        output_root=tmp_path / "crawl", session=session,
        delay=0, respect_robots=True,
    )

    assert summary.pages_crawled == 0
    assert any("robots" in error for error in summary.errors)


def test_cv_filter_rejects_flat_place_image(tmp_path: Path) -> None:
    page = "https://a.test/"
    flat = "https://a.test/logo.png"
    session = FakeSession({
        page: response(f'<img src="{flat}">'),
        flat: image_response(png_bytes(flat=True)),
    })
    manifest = tmp_path / "crawled-places.csv"

    summary = crawl_pages(
        [page], "places", manifest,
        output_root=tmp_path / "crawl", session=session,
        delay=0, respect_robots=False, use_cv=True,
    )

    assert summary.added == 0
    assert summary.cv_rejected == 1
    assert not manifest.exists() or read_manifest(manifest, "places").rows == []


def test_cache_prevents_redownload_across_runs(tmp_path: Path) -> None:
    page = "https://a.test/"
    flat = "https://a.test/logo.png"
    session = FakeSession({
        page: response(f'<img src="{flat}">'),
        flat: image_response(png_bytes(flat=True)),
    })
    manifest = tmp_path / "crawled-places.csv"
    output_root = tmp_path / "crawl"
    kwargs = dict(output_root=output_root, session=session, delay=0, respect_robots=False, use_cv=True)

    crawl_pages([page], "places", manifest, **kwargs)
    second = crawl_pages([page], "places", manifest, **kwargs)

    # The rejected image is downloaded once; the second run is a cache hit.
    assert session.count(flat) == 1
    assert second.from_cache == 1
    assert second.cv_rejected == 1


def test_identical_bytes_share_one_stored_file(tmp_path: Path) -> None:
    page = "https://a.test/"
    payload = png_bytes(seed=3)
    session = FakeSession({
        page: response('<img src="https://a.test/1.png"><img src="https://a.test/2.png">'),
        "https://a.test/1.png": image_response(payload),
        "https://a.test/2.png": image_response(payload),
    })
    manifest = tmp_path / "crawled-places.csv"
    output_root = tmp_path / "crawl"

    summary = crawl_pages(
        [page], "places", manifest,
        output_root=output_root, session=session,
        delay=0, respect_robots=False, use_cv=True,
    )

    assert summary.added == 2
    stored = list((output_root / "store").rglob("*.png"))
    assert len(stored) == 1
