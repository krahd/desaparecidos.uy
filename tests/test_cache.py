from __future__ import annotations

from pathlib import Path

from desaparecidos.cache import CachedImage, CrawlCache


def make_record(url: str, sha: str, path: str) -> CachedImage:
    return CachedImage(
        url=url, sha256=sha, path=path, bytes=10, width=400, height=300,
        content_type="image/png", cv_label="place", cv_score=0.1, cv_accept=True,
    )


def test_image_roundtrip_and_hash_dedupe(tmp_path: Path) -> None:
    cache = CrawlCache(tmp_path)
    record = make_record("https://x.test/a.png", "abc123", str(tmp_path / "a.png"))
    cache.put_image(record)

    got = cache.get_image("https://x.test/a.png")
    assert got is not None and got.sha256 == "abc123" and got.cv_accept is True
    assert cache.get_image("https://x.test/missing.png") is None
    by_hash = cache.get_by_hash("abc123")
    assert by_hash is not None and by_hash.url == "https://x.test/a.png"
    cache.close()


def test_store_path_is_bucketed(tmp_path: Path) -> None:
    cache = CrawlCache(tmp_path)
    path = cache.store_path("abcdef0123", ".jpg")
    assert path.parent.name == "ab"
    assert path.name == "abcdef0123.jpg"
    assert path.parent.exists()
    cache.close()


def test_page_depth_keeps_minimum(tmp_path: Path) -> None:
    cache = CrawlCache(tmp_path)
    assert cache.page_depth("https://x.test/p") is None
    cache.put_page("https://x.test/p", 2, 200)
    assert cache.page_depth("https://x.test/p") == 2
    cache.put_page("https://x.test/p", 1, 200)
    assert cache.page_depth("https://x.test/p") == 1
    cache.close()
