"""Ingestor: RSS + Hacker News -> deduped, tagged articles in SQLite. Failing sources never break the run."""
from __future__ import annotations

import html
import json
import re
import sqlite3
from datetime import datetime, timezone
from time import mktime

from . import feeds
from .tagger import tag_articles

TIMEOUT = 8.0


def _clean(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", text or "")).strip()


def _title_tokens(t: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", t.lower()))


def is_duplicate_title(title: str, known: list[set[str]], threshold: float = 0.85) -> bool:
    toks = _title_tokens(title)
    if not toks:
        return True
    for k in known:
        if k and len(toks & k) / len(toks | k) >= threshold:
            return True
    return False


def fetch_rss() -> list[dict]:
    import feedparser
    import httpx

    out: list[dict] = []
    for source, url in feeds.FEEDS:
        try:
            r = httpx.get(url, timeout=TIMEOUT, follow_redirects=True, headers={"User-Agent": "TheFold/1.0"})
            parsed = feedparser.parse(r.content)
        except Exception:
            continue
        for e in parsed.entries[:15]:
            link = getattr(e, "link", None)
            title = _clean(getattr(e, "title", ""))
            if not link or not title:
                continue
            summary = _clean(getattr(e, "summary", ""))[:600]
            ts = getattr(e, "published_parsed", None)
            image_url = None
            if hasattr(e, "media_content") and e.media_content:
                image_url = e.media_content[0].get("url")
            elif hasattr(e, "media_thumbnail") and e.media_thumbnail:
                image_url = e.media_thumbnail[0].get("url")
            elif hasattr(e, "enclosures") and e.enclosures:
                image_url = e.enclosures[0].get("href")
            out.append({"url": link, "title": title, "source": source, "summary": summary,
                        "published_at": pub.isoformat(), "word_count": max(300, len(summary.split()) * 8),
                        "image_url": image_url})
    return out


def fetch_hn(limit: int = 25) -> list[dict]:
    import httpx

    out: list[dict] = []
    try:
        ids = httpx.get(feeds.HN_TOP, timeout=TIMEOUT).json()[:limit]
        for i in ids:
            it = httpx.get(feeds.HN_ITEM.format(id=i), timeout=TIMEOUT).json() or {}
            if it.get("url") and it.get("title"):
                pub = datetime.fromtimestamp(it.get("time", 0), timezone.utc).isoformat()
                out.append({"url": it["url"], "title": it["title"], "source": "Hacker News",
                            "summary": f"Discussed on Hacker News ({it.get('score', 0)} points).",
                            "published_at": pub, "word_count": 700, "image_url": None})
    except Exception:
        pass
    return out


def store(conn: sqlite3.Connection, candidates: list[dict]) -> int:
    """Dedupe against the DB (URL + title similarity), tag, insert. Returns number added."""
    known = [_title_tokens(r["title"]) for r in conn.execute("SELECT title FROM articles")]
    fresh: list[dict] = []
    seen_urls = {r["url"] for r in conn.execute("SELECT url FROM articles")}
    for c in candidates:
        if c["url"] in seen_urls or is_duplicate_title(c["title"], known):
            continue
        seen_urls.add(c["url"])
        known.append(_title_tokens(c["title"]))
        fresh.append(c)
    tag_articles(fresh)
    added = 0
    for a in fresh:
        cur = conn.execute(
            """INSERT OR IGNORE INTO articles
               (url,title,source,summary,content,topics_json,entities_json,published_at,word_count,image_url)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (a["url"], a["title"], a["source"], a["summary"], a["summary"], json.dumps(a["topics"]),
             json.dumps(a["entities"]), a["published_at"], a["word_count"], a.get("image_url")),
        )
        added += cur.rowcount
    conn.commit()
    return added


def refresh(conn: sqlite3.Connection) -> int:
    return store(conn, fetch_rss() + fetch_hn())
