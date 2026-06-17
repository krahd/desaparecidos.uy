from __future__ import annotations

from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

from desaparecidos.crawl import crawl_pages
from desaparecidos.manifests import read_manifest, set_review_status


class FakeSession:
    def __init__(self, responses: dict[str, requests.Response]) -> None:
        self.responses = responses

    def get(self, url: str, **_: object) -> requests.Response:
        return self.responses[url]


def response(
    body: bytes,
    *,
    content_type: str = "text/html",
    status_code: int = 200,
) -> requests.Response:
    result = requests.Response()
    result.status_code = status_code
    result._content = body
    result.headers["content-type"] = content_type
    result.url = "https://example.test/"
    return result


def png_bytes() -> bytes:
    handle = BytesIO()
    Image.new("RGB", (12, 12), (120, 130, 140)).save(handle, format="PNG")
    return handle.getvalue()


def test_crawl_pages_appends_pending_manifest_rows(tmp_path: Path) -> None:
    page = "https://example.test/page"
    image = "https://example.test/photo.png"
    session = FakeSession({
        page: response(f'<html><img src="{image}"></html>'.encode("utf-8")),
        image: response(png_bytes(), content_type="image/png"),
    })
    manifest = tmp_path / "data" / "manifests" / "crawled-places.csv"

    summary = crawl_pages(
        [page],
        "places",
        manifest,
        output_root=tmp_path / "data" / "raw" / "crawl",
        session=session,
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
        page: response(f'<meta property="og:image" content="{image}">'.encode("utf-8")),
        image: response(png_bytes(), content_type="image/png"),
    })
    manifest = tmp_path / "data" / "manifests" / "crawled-targets.csv"
    crawl_pages(
        [page],
        "targets",
        manifest,
        output_root=tmp_path / "data" / "raw" / "crawl",
        session=session,
    )
    row_id = read_manifest(manifest, "targets").rows[0].id

    validation = set_review_status(manifest, "targets", row_id, "approved")

    assert validation.ok is True
    assert validation.rows[0].approved is True
