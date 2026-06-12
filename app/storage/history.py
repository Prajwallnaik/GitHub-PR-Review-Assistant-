"""SQLite-based review history storage."""

import sqlite3
import json
import os
from datetime import datetime
from dataclasses import asdict
from typing import Optional, List

from app.models.review import ReviewResult
from config.settings import SQLITE_DB_PATH


def _get_connection() -> sqlite3.Connection:
    """Get a database connection, creating the data directory if needed."""
    os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the reviews table if it does not exist."""
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pr_url TEXT NOT NULL,
                owner TEXT NOT NULL,
                repo TEXT NOT NULL,
                pr_number INTEGER NOT NULL,
                review_date TEXT NOT NULL,
                severity TEXT NOT NULL,
                bugs_count INTEGER NOT NULL,
                review_json TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_review(
    pr_url: str,
    owner: str,
    repo: str,
    pr_number: int,
    review: ReviewResult,
):
    """Insert a new review row into the database."""
    conn = _get_connection()
    try:
        conn.execute(
            """
            INSERT INTO reviews (pr_url, owner, repo, pr_number, review_date, severity, bugs_count, review_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pr_url,
                owner,
                repo,
                pr_number,
                datetime.now().isoformat(),
                review.severity,
                len(review.bugs),
                json.dumps(asdict(review), ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_history() -> List[dict]:
    """Return all reviews ordered by date descending."""
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM reviews ORDER BY review_date DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_review_by_id(review_id: int) -> Optional[dict]:
    """Return a single review row by its ID."""
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM reviews WHERE id = ?", (review_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
