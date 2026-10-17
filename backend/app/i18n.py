"""Urdu translation: translate headlines via LLM (cached in DB). Falls back to English silently."""
from __future__ import annotations

import hashlib
import sqlite3


def _cache_key(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def _get_cached(conn: sqlite3.Connection, key: str) -> str | None:
    """Try to fetch a cached Urdu translation from a simple KV table."""
    try:
        r = conn.execute(
            "SELECT value FROM translation_cache WHERE key=?", (key,)
        ).fetchone()
        return r[0] if r else None
    except Exception:
        return None


def _set_cached(conn: sqlite3.Connection, key: str, value: str) -> None:
    try:
        conn.execute(
            "INSERT OR REPLACE INTO translation_cache (key, value) VALUES (?,?)",
            (key, value),
        )
        conn.commit()
    except Exception:
        pass


def ensure_table(conn: sqlite3.Connection) -> None:
    """Create translation_cache if it does not exist."""
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS translation_cache (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        conn.commit()
    except Exception:
        pass


def translate_headline(headline: str, conn: sqlite3.Connection | None = None) -> str:
    """Return Urdu translation of headline, or the original on any failure."""
    from app import config, llm  # lazy import so tests can patch env before import
    if not headline:
        return headline
    key = _cache_key(headline)
    if conn is not None:
        cached = _get_cached(conn, key)
        if cached:
            return cached
    if llm.is_mock():
        return f"[اردو] {headline}"
    result = llm.complete_json(
        "You are a professional Urdu journalist. Translate the English headline into fluent, natural Urdu. "
        'Return {"ur": "..."}. Do not add transliteration or explanation.',
        f'Headline: "{headline}"',
        fallback=lambda: {},
        model=config.fast_model(),
        max_tokens=200,
    )
    translated = result.get("ur", "").strip()
    if not translated:
        return headline
    if conn is not None:
        _set_cached(conn, key, translated)
    return translated


def translate_edition_headlines(edition_id: int, conn: sqlite3.Connection) -> int:
    """Translate all headlines in an edition that lack a Urdu translation. Returns count updated."""
    ensure_table(conn)
    rows = conn.execute(
        "SELECT id, headline FROM edition_items WHERE edition_id=? AND (headline_ur IS NULL OR headline_ur='')",
        (edition_id,),
    ).fetchall()
    updated = 0
    for row in rows:
        ur = translate_headline(row["headline"], conn)
        if ur and ur != row["headline"]:
            conn.execute(
                "UPDATE edition_items SET headline_ur=? WHERE id=?", (ur, row["id"])
            )
            updated += 1
    if updated:
        conn.commit()
    return updated
