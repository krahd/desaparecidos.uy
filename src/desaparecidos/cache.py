"""Persistent crawl cache so images are fetched and classified only once.

Backed by a SQLite database plus a content-addressed file store under
``data/raw/crawl/``. The cache lets the crawler:

- skip URLs already seen (no re-download, no re-classification);
- deduplicate identical bytes fetched from different URLs (one stored file);
- skip pages already fetched at the same or shallower depth.

Everything lives under ignored ``data/raw/`` and persists across runs.
"""

from __future__ import annotations

import hashlib
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CachedImage:
    url: str
    sha256: str
    path: str
    bytes: int
    width: int
    height: int
    content_type: str
    cv_label: str
    cv_score: float
    cv_accept: bool


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class CrawlCache:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.store = self.root / "store"
        self.store.mkdir(parents=True, exist_ok=True)
        self.db_path = self.root / "cache.sqlite"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS images (
                url TEXT PRIMARY KEY,
                sha256 TEXT,
                path TEXT,
                bytes INTEGER,
                width INTEGER,
                height INTEGER,
                content_type TEXT,
                cv_label TEXT,
                cv_score REAL,
                cv_accept INTEGER,
                first_seen REAL,
                last_seen REAL
            );
            CREATE INDEX IF NOT EXISTS images_sha ON images(sha256);
            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                depth INTEGER,
                status INTEGER,
                fetched_at REAL
            );
            """
        )
        self.conn.commit()

    # -- images -----------------------------------------------------------

    @staticmethod
    def _row_to_image(row: sqlite3.Row) -> CachedImage:
        return CachedImage(
            url=row["url"],
            sha256=row["sha256"],
            path=row["path"],
            bytes=row["bytes"],
            width=row["width"],
            height=row["height"],
            content_type=row["content_type"],
            cv_label=row["cv_label"],
            cv_score=row["cv_score"],
            cv_accept=bool(row["cv_accept"]),
        )

    def get_image(self, url: str) -> CachedImage | None:
        row = self.conn.execute("SELECT * FROM images WHERE url = ?", (url,)).fetchone()
        return self._row_to_image(row) if row else None

    def get_by_hash(self, sha256: str) -> CachedImage | None:
        row = self.conn.execute(
            "SELECT * FROM images WHERE sha256 = ? AND path != '' LIMIT 1", (sha256,)
        ).fetchone()
        return self._row_to_image(row) if row else None

    def store_path(self, sha256: str, suffix: str) -> Path:
        bucket = self.store / sha256[:2]
        bucket.mkdir(parents=True, exist_ok=True)
        return bucket / f"{sha256}{suffix}"

    def put_image(self, record: CachedImage) -> None:
        now = time.time()
        self.conn.execute(
            """
            INSERT INTO images (url, sha256, path, bytes, width, height, content_type,
                                cv_label, cv_score, cv_accept, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                sha256=excluded.sha256, path=excluded.path, bytes=excluded.bytes,
                width=excluded.width, height=excluded.height,
                content_type=excluded.content_type, cv_label=excluded.cv_label,
                cv_score=excluded.cv_score, cv_accept=excluded.cv_accept,
                last_seen=excluded.last_seen
            """,
            (
                record.url, record.sha256, record.path, record.bytes, record.width,
                record.height, record.content_type, record.cv_label, record.cv_score,
                int(record.cv_accept), now, now,
            ),
        )
        self.conn.commit()

    # -- pages ------------------------------------------------------------

    def page_depth(self, url: str) -> int | None:
        row = self.conn.execute("SELECT depth FROM pages WHERE url = ?", (url,)).fetchone()
        return int(row["depth"]) if row else None

    def put_page(self, url: str, depth: int, status: int) -> None:
        self.conn.execute(
            """
            INSERT INTO pages (url, depth, status, fetched_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                depth=min(pages.depth, excluded.depth),
                status=excluded.status, fetched_at=excluded.fetched_at
            """,
            (url, depth, status, time.time()),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "CrawlCache":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
