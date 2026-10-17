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
    """Translate all headlines, story summaries (deks), and reasons (whys) in an edition in a single batch call."""
    ensure_table(conn)
    rows = conn.execute(
        "SELECT id, headline, dek, why FROM edition_items WHERE edition_id=? AND (headline_ur IS NULL OR headline_ur='' OR dek_ur IS NULL OR dek_ur='')",
        (edition_id,),
    ).fetchall()
    if not rows:
        return 0

    from app import config, llm

    to_translate: list[sqlite3.Row] = []
    updated = 0
    for r in rows:
        cached_h = _get_cached(conn, _cache_key("h:" + r["headline"]))
        cached_d = _get_cached(conn, _cache_key("d:" + (r["dek"] or "")))
        cached_w = _get_cached(conn, _cache_key("w:" + (r["why"] or "")))
        if cached_h and cached_d:
            conn.execute("UPDATE edition_items SET headline_ur=?, dek_ur=?, why_ur=? WHERE id=?", (cached_h, cached_d, cached_w or "", r["id"]))
            updated += 1
        else:
            to_translate.append(r)

    if not to_translate:
        if updated:
            conn.commit()
        return updated

    if llm.is_mock():
        for r in to_translate:
            ur_h = f"[اردو] {r['headline']}"
            ur_d = f"[اردو خلاصہ] {r['dek']}"
            ur_w = f"[اردو وجہ] {r['why']}" if r["why"] else ""
            conn.execute("UPDATE edition_items SET headline_ur=?, dek_ur=?, why_ur=? WHERE id=?", (ur_h, ur_d, ur_w, r["id"]))
            _set_cached(conn, _cache_key("h:" + r["headline"]), ur_h)
            _set_cached(conn, _cache_key("d:" + (r["dek"] or "")), ur_d)
            if ur_w:
                _set_cached(conn, _cache_key("w:" + (r["why"] or "")), ur_w)
            updated += 1
        conn.commit()
        return updated

    # Batch translate all headlines, summaries, and why reasons in one single prompt
    items_input = [{"id": r["id"], "headline": r["headline"], "summary": r["dek"], "why": r["why"]} for r in to_translate]
    system = (
        "You are an expert Urdu news editor. Translate each English news story headline, summary, and editorial reason ('why') into fluent, natural journalistic Urdu. "
        'Return JSON format: {"translations": [{"id": <number>, "headline_ur": "<Urdu headline>", "dek_ur": "<Urdu summary>", "why_ur": "<Urdu why>"}, ...]}'
    )
    user_prompt = f"Translate these news stories:\n{json.dumps(items_input, ensure_ascii=False)}"

    result = llm.complete_json(
        system,
        user_prompt,
        fallback=lambda: {"translations": []},
        model=config.fast_model(),
        max_tokens=3500,
    )

    tr_map: dict[int, dict] = {}
    for t in result.get("translations", []):
        if isinstance(t, dict) and t.get("id") is not None:
            tr_map[int(t["id"])] = {
                "headline_ur": (t.get("headline_ur") or t.get("ur") or "").strip(),
                "dek_ur": (t.get("dek_ur") or "").strip(),
                "why_ur": (t.get("why_ur") or "").strip(),
            }

    for r in to_translate:
        item_tr = tr_map.get(r["id"], {})
        ur_h = item_tr.get("headline_ur") or translate_headline(r["headline"], conn)
        ur_d = item_tr.get("dek_ur") or ""
        ur_w = item_tr.get("why_ur") or ""
        if ur_h and ur_h != r["headline"]:
            conn.execute("UPDATE edition_items SET headline_ur=?, dek_ur=?, why_ur=? WHERE id=?", (ur_h, ur_d, ur_w, r["id"]))
            _set_cached(conn, _cache_key("h:" + r["headline"]), ur_h)
            if ur_d:
                _set_cached(conn, _cache_key("d:" + (r["dek"] or "")), ur_d)
            if ur_w:
                _set_cached(conn, _cache_key("w:" + (r["why"] or "")), ur_w)
            updated += 1

    conn.commit()
    return updated


