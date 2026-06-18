from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .cv import CV_POLICY_VERSION, hamming_distance
from .paths import display_path


@dataclass(frozen=True)
class CachedImage:
    url: str
    sha256: str
    path: str
    bytes: int
    width: int
    height: int
    content_type: str
    phash: str = ""
    cv_label: str = ""
    cv_score: float = 0.0
    cv_accept: bool = False


@dataclass(frozen=True)
class CachedClassification:
    url: str
    kind: str
    cv_label: str
    cv_score: float
    cv_accept: bool
    face_x: int | None = None
    face_y: int | None = None
    face_width: int | None = None
    face_height: int | None = None
    cv_policy_version: int = CV_POLICY_VERSION


class CrawlCache:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.store = self.root / "store"
        self.runs = self.root / "runs"
        self.store.mkdir(parents=True, exist_ok=True)
        self.runs.mkdir(parents=True, exist_ok=True)
        self.db_path = self.root / "cache.sqlite"
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS images (
                url TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL,
                phash TEXT NOT NULL,
                path TEXT NOT NULL,
                bytes INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                content_type TEXT NOT NULL,
                cv_label TEXT NOT NULL DEFAULT '',
                cv_score REAL NOT NULL DEFAULT 0,
                cv_accept INTEGER NOT NULL DEFAULT 0,
                first_seen REAL NOT NULL,
                last_seen REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS image_classifications (
                url TEXT NOT NULL,
                kind TEXT NOT NULL,
                cv_label TEXT NOT NULL,
                cv_score REAL NOT NULL,
                cv_accept INTEGER NOT NULL,
                face_x INTEGER,
                face_y INTEGER,
                face_width INTEGER,
                face_height INTEGER,
                cv_policy_version INTEGER NOT NULL DEFAULT 1,
                classified_at REAL NOT NULL,
                PRIMARY KEY (url, kind)
            );

            CREATE TABLE IF NOT EXISTS crawl_runs (
                run_id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                manifest TEXT NOT NULL,
                seeds_json TEXT NOT NULL,
                settings_json TEXT NOT NULL,
                started_at REAL NOT NULL,
                finished_at REAL,
                summary_json TEXT
            );

            CREATE TABLE IF NOT EXISTS crawl_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                ordinal INTEGER NOT NULL,
                url TEXT NOT NULL,
                depth INTEGER NOT NULL,
                parent_url TEXT,
                status INTEGER,
                result TEXT NOT NULL,
                error TEXT,
                fetched_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS crawl_image_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                ordinal INTEGER NOT NULL,
                page_url TEXT NOT NULL,
                image_url TEXT NOT NULL,
                decision TEXT NOT NULL,
                row_id TEXT,
                sha256 TEXT,
                phash TEXT,
                path TEXT,
                cv_label TEXT,
                error TEXT,
                created_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                depth INTEGER,
                status INTEGER,
                fetched_at REAL
            );
            """
        )
        self._ensure_column("images", "phash", "TEXT NOT NULL DEFAULT ''")
        self._ensure_column("images", "cv_label", "TEXT NOT NULL DEFAULT ''")
        self._ensure_column("images", "cv_score", "REAL NOT NULL DEFAULT 0")
        self._ensure_column("images", "cv_accept", "INTEGER NOT NULL DEFAULT 0")
        self._ensure_column("image_classifications", "cv_policy_version", "INTEGER NOT NULL DEFAULT 1")
        self.conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS images_sha256 ON images(sha256);
            CREATE INDEX IF NOT EXISTS images_phash ON images(phash);
            """
        )
        self.conn.commit()

    def _ensure_column(self, table: str, column: str, definition: str) -> None:
        columns = {
            row["name"]
            for row in self.conn.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column not in columns:
            self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    @staticmethod
    def _row_to_image(row: sqlite3.Row) -> CachedImage:
        return CachedImage(
            url=row["url"],
            sha256=row["sha256"],
            path=row["path"],
            bytes=int(row["bytes"]),
            width=int(row["width"]),
            height=int(row["height"]),
            content_type=row["content_type"],
            phash=row["phash"],
            cv_label=row["cv_label"],
            cv_score=float(row["cv_score"]),
            cv_accept=bool(row["cv_accept"]),
        )

    @staticmethod
    def _row_to_classification(row: sqlite3.Row) -> CachedClassification:
        return CachedClassification(
            url=row["url"],
            kind=row["kind"],
            cv_label=row["cv_label"],
            cv_score=float(row["cv_score"]),
            cv_accept=bool(row["cv_accept"]),
            face_x=row["face_x"],
            face_y=row["face_y"],
            face_width=row["face_width"],
            face_height=row["face_height"],
            cv_policy_version=int(row["cv_policy_version"]),
        )

    def get_image(self, url: str) -> CachedImage | None:
        row = self.conn.execute("SELECT * FROM images WHERE url = ?", (url,)).fetchone()
        return self._row_to_image(row) if row else None

    def get_by_hash(self, sha256: str) -> CachedImage | None:
        row = self.conn.execute(
            "SELECT * FROM images WHERE sha256 = ? AND path != '' LIMIT 1", (sha256,)
        ).fetchone()
        return self._row_to_image(row) if row else None

    def find_similar_phash(self, phash: str, threshold: int) -> CachedImage | None:
        rows = self.conn.execute("SELECT * FROM images WHERE phash != ''").fetchall()
        for row in rows:
            if hamming_distance(phash, row["phash"]) <= threshold:
                return self._row_to_image(row)
        return None

    def store_path(self, sha256: str, suffix: str) -> Path:
        bucket = self.store / sha256[:2]
        bucket.mkdir(parents=True, exist_ok=True)
        return bucket / f"{sha256}{suffix}"

    def put_image(self, record: CachedImage) -> None:
        now = time.time()
        self.conn.execute(
            """
            INSERT INTO images (url, sha256, phash, path, bytes, width, height,
                                content_type, cv_label, cv_score, cv_accept,
                                first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                sha256=excluded.sha256,
                phash=excluded.phash,
                path=excluded.path,
                bytes=excluded.bytes,
                width=excluded.width,
                height=excluded.height,
                content_type=excluded.content_type,
                cv_label=excluded.cv_label,
                cv_score=excluded.cv_score,
                cv_accept=excluded.cv_accept,
                last_seen=excluded.last_seen
            """,
            (
                record.url,
                record.sha256,
                record.phash,
                record.path,
                record.bytes,
                record.width,
                record.height,
                record.content_type,
                record.cv_label,
                record.cv_score,
                int(record.cv_accept),
                now,
                now,
            ),
        )
        self.conn.commit()

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
                status=excluded.status,
                fetched_at=excluded.fetched_at
            """,
            (url, depth, status, time.time()),
        )
        self.conn.commit()

    def get_classification(
        self,
        url: str,
        kind: str,
        *,
        cv_policy_version: int | None = CV_POLICY_VERSION,
    ) -> CachedClassification | None:
        row = self.conn.execute(
            "SELECT * FROM image_classifications WHERE url = ? AND kind = ?",
            (url, kind),
        ).fetchone()
        if row is None:
            return None
        record = self._row_to_classification(row)
        if cv_policy_version is not None and record.cv_policy_version != cv_policy_version:
            return None
        return record

    def put_classification(self, record: CachedClassification) -> None:
        self.conn.execute(
            """
            INSERT INTO image_classifications
                (url, kind, cv_label, cv_score, cv_accept, face_x, face_y,
                 face_width, face_height, cv_policy_version, classified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url, kind) DO UPDATE SET
                cv_label=excluded.cv_label,
                cv_score=excluded.cv_score,
                cv_accept=excluded.cv_accept,
                face_x=excluded.face_x,
                face_y=excluded.face_y,
                face_width=excluded.face_width,
                face_height=excluded.face_height,
                cv_policy_version=excluded.cv_policy_version,
                classified_at=excluded.classified_at
            """,
            (
                record.url,
                record.kind,
                record.cv_label,
                record.cv_score,
                int(record.cv_accept),
                record.face_x,
                record.face_y,
                record.face_width,
                record.face_height,
                record.cv_policy_version,
                time.time(),
            ),
        )
        self.conn.commit()

    def start_run(
        self,
        run_id: str,
        kind: str,
        manifest: str,
        seeds: list[str],
        settings: dict[str, Any],
    ) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO crawl_runs
                (run_id, kind, manifest, seeds_json, settings_json, started_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                kind,
                manifest,
                json.dumps(seeds, ensure_ascii=False),
                json.dumps(settings, ensure_ascii=False, sort_keys=True),
                time.time(),
            ),
        )
        self.conn.commit()

    def finish_run(self, run_id: str, summary: dict[str, Any]) -> None:
        self.conn.execute(
            "UPDATE crawl_runs SET finished_at = ?, summary_json = ? WHERE run_id = ?",
            (time.time(), json.dumps(summary, ensure_ascii=False, sort_keys=True), run_id),
        )
        self.conn.commit()

    def put_page_event(
        self,
        run_id: str,
        ordinal: int,
        url: str,
        depth: int,
        parent_url: str | None,
        status: int | None,
        result: str,
        error: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO crawl_pages
                (run_id, ordinal, url, depth, parent_url, status, result, error, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, ordinal, url, depth, parent_url, status, result, error, time.time()),
        )
        self.conn.commit()

    def put_image_event(
        self,
        run_id: str,
        ordinal: int,
        page_url: str,
        image_url: str,
        decision: str,
        *,
        row_id: str | None = None,
        sha256: str | None = None,
        phash: str | None = None,
        path: str | None = None,
        cv_label: str | None = None,
        error: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO crawl_image_events
                (run_id, ordinal, page_url, image_url, decision, row_id, sha256,
                 phash, path, cv_label, error, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                ordinal,
                page_url,
                image_url,
                decision,
                row_id,
                sha256,
                phash,
                path,
                cv_label,
                error,
                time.time(),
            ),
        )
        self.conn.commit()

    def page_trail(self, run_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT ordinal, url, depth, parent_url, status, result, error, fetched_at
            FROM crawl_pages
            WHERE run_id = ?
            ORDER BY ordinal ASC, id ASC
            """,
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def export_run_jsonl(self, run_id: str) -> Path:
        output = self.runs / f"{run_id}.jsonl"
        with output.open("w", encoding="utf-8") as handle:
            run = self.conn.execute(
                "SELECT * FROM crawl_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if run:
                handle.write(json.dumps({"type": "run", **dict(run)}, ensure_ascii=False) + "\n")
            for row in self.page_trail(run_id):
                handle.write(json.dumps({"type": "page", **row}, ensure_ascii=False) + "\n")
            events = self.conn.execute(
                """
                SELECT ordinal, page_url, image_url, decision, row_id, sha256, phash,
                       path, cv_label, error, created_at
                FROM crawl_image_events
                WHERE run_id = ?
                ORDER BY ordinal ASC, id ASC
                """,
                (run_id,),
            ).fetchall()
            for event in events:
                handle.write(json.dumps({"type": "image", **dict(event)}, ensure_ascii=False) + "\n")
        return output

    def image_events(self, run_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT ordinal, page_url, image_url, decision, row_id, sha256, phash,
                   path, cv_label, error, created_at
            FROM crawl_image_events
            WHERE run_id = ?
            ORDER BY ordinal ASC, id ASC
            """,
            (run_id,),
        ).fetchall()
        return [{"run_id": run_id, **dict(row)} for row in rows]

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "CrawlCache":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def page_trail_for_runs(root: str | Path, run_ids: list[str]) -> list[dict[str, Any]]:
    if not (Path(root) / "cache.sqlite").exists():
        return []
    seen: set[str] = set()
    trail: list[dict[str, Any]] = []
    with CrawlCache(root) as cache:
        for run_id in run_ids:
            for row in cache.page_trail(run_id):
                url = str(row.get("url", ""))
                if not url or url in seen:
                    continue
                seen.add(url)
                trail.append({"run_id": run_id, **row})
    return trail


def image_events_for_runs(root: str | Path, run_ids: list[str]) -> list[dict[str, Any]]:
    if not (Path(root) / "cache.sqlite").exists():
        return []
    events: list[dict[str, Any]] = []
    with CrawlCache(root) as cache:
        for run_id in run_ids:
            events.extend(cache.image_events(run_id))
    return events


def display_optional_path(path: Path | None) -> str | None:
    return display_path(path) if path else None
