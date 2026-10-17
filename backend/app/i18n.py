"""Urdu translation: translate headlines via LLM (cached in DB). Falls back to English silently."""
from __future__ import annotations

import hashlib
import json
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
    """Translate all headlines in an edition in a single batch call. Fast and reliable."""
    ensure_table(conn)
    rows = conn.execute(
        "SELECT id, headline FROM edition_items WHERE edition_id=? AND (headline_ur IS NULL OR headline_ur='')",
        (edition_id,),
    ).fetchall()
    if not rows:
        return 0

    from app import config, llm

    to_translate: list[sqlite3.Row] = []
    updated = 0
    for r in rows:
        cached = _get_cached(conn, _cache_key(r["headline"]))
        if cached:
            conn.execute("UPDATE edition_items SET headline_ur=? WHERE id=?", (cached, r["id"]))
            updated += 1
        else:
            to_translate.append(r)

    if not to_translate:
        if updated:
            conn.commit()
        return updated

    if llm.is_mock():
        for r in to_translate:
            ur = f"[اردو] {r['headline']}"
            conn.execute("UPDATE edition_items SET headline_ur=? WHERE id=?", (ur, r["id"]))
            _set_cached(conn, _cache_key(r["headline"]), ur)
            updated += 1
        conn.commit()
        return updated

    # Batch translate all remaining headlines in one single prompt
    items_input = [{"id": r["id"], "headline": r["headline"]} for r in to_translate]
    system = (
        "You are an expert Urdu news editor. Translate each English headline into fluent, natural journalistic Urdu. "
        'Return JSON format: {"translations": [{"id": <number>, "ur": "<Urdu headline>"}, ...]}'
    )
    user_prompt = f"Translate these headlines:\n{json.dumps(items_input, ensure_ascii=False)}"

    result = llm.complete_json(
        system,
        user_prompt,
        fallback=lambda: {"translations": []},
        model=config.fast_model(),
        max_tokens=2000,
    )

    tr_map: dict[int, str] = {}
    for t in result.get("translations", []):
        if isinstance(t, dict) and t.get("id") is not None and t.get("ur"):
            tr_map[int(t["id"])] = t["ur"].strip()

    for r in to_translate:
        ur = tr_map.get(r["id"]) or translate_headline(r["headline"], conn)
        if ur and ur != r["headline"]:
            conn.execute("UPDATE edition_items SET headline_ur=? WHERE id=?", (ur, r["id"]))
            _set_cached(conn, _cache_key(r["headline"]), ur)
            updated += 1

    conn.commit()
    return updated

