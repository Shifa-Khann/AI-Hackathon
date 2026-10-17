"""SQLite schema and connection helpers."""
from __future__ import annotations

import sqlite3
from typing import Iterator

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE, password_hash TEXT,
  name TEXT, city TEXT, budget_min INTEGER DEFAULT 12, lang TEXT DEFAULT 'en',
  profile_json TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT UNIQUE NOT NULL, title TEXT NOT NULL, source TEXT, summary TEXT, content TEXT,
  topics_json TEXT DEFAULT '[]', entities_json TEXT DEFAULT '[]',
  published_at TEXT, word_count INTEGER DEFAULT 600, image_url TEXT,
  fetched_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS editions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  number INTEGER NOT NULL, date TEXT NOT NULL, plan_json TEXT, editor_note TEXT, todo TEXT,
  quiz_json TEXT, read_min INTEGER, created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS edition_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  edition_id INTEGER NOT NULL REFERENCES editions(id),
  article_id INTEGER NOT NULL REFERENCES articles(id),
  slot INTEGER, section TEXT, headline TEXT, dek TEXT, why TEXT,
  is_blind_spot INTEGER DEFAULT 0, read_min INTEGER DEFAULT 2,
  headline_ur TEXT, dek_ur TEXT, why_ur TEXT
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL, edition_id INTEGER, article_id INTEGER,
  type TEXT NOT NULL, value REAL, created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS profile_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL, label TEXT, profile_json TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_items_edition ON edition_items(edition_id);
CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id);
CREATE TABLE IF NOT EXISTS user_sessions (
  token TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);
CREATE TABLE IF NOT EXISTS saved_articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(user_id, article_id)
);
CREATE INDEX IF NOT EXISTS idx_saved_user ON saved_articles(user_id);
"""


def connect() -> sqlite3.Connection:
    path = config.db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = connect()
    try:
        conn.executescript(SCHEMA)
        # Migrate columns if existing DB
        for col, tbl in [
            ("email TEXT", "users"),
            ("password_hash TEXT", "users"),
            ("region TEXT DEFAULT 'global'", "users"),
            ("dek_ur TEXT", "edition_items"),
            ("why_ur TEXT", "edition_items"),
        ]:
            try:
                conn.execute(f"ALTER TABLE {tbl} ADD COLUMN {col}")
            except Exception:
                pass
        conn.commit()
        n = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        if n == 0:
            from .seed.loader import load_seed_articles

            load_seed_articles(conn)
    finally:
        conn.close()



def get_db() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency."""
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()
