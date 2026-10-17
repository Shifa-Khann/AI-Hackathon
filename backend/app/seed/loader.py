"""Load the offline sample article pool into SQLite."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..agents.tagger import extract_entities

SEED_FILE = Path(__file__).with_name("articles.json")


def load_seed_articles(conn: sqlite3.Connection) -> int:
    if not SEED_FILE.exists():
        from .build_articles import build

        data = build()
    else:
        data = json.loads(SEED_FILE.read_text())
    now = datetime.now(timezone.utc)
    added = 0
    for a in data:
        published = (now - timedelta(hours=a.get("hours_ago", 12))).isoformat()
        cur = conn.execute(
            """INSERT OR IGNORE INTO articles
               (url,title,source,summary,content,topics_json,entities_json,published_at,word_count)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (a["url"], a["title"], a["source"], a["summary"], a["summary"],
             json.dumps(a["topics"]), json.dumps(extract_entities(a["title"] + " " + a["summary"])),
             published, a.get("word_count", 600)),
        )
        added += cur.rowcount
    conn.commit()
    return added
