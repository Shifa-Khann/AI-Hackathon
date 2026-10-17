"""Data-access helpers: articles, editions, profile snapshots."""
from __future__ import annotations

import json
import sqlite3
from datetime import date

from .agents import editor, learner, scorer


def article_row(r: sqlite3.Row) -> dict:
    d = dict(r)
    d["topics"] = json.loads(d.pop("topics_json") or "[]")
    d["entities"] = json.loads(d.pop("entities_json") or "[]")
    return d


def all_articles(conn: sqlite3.Connection) -> list[dict]:
    return [article_row(r) for r in conn.execute("SELECT * FROM articles")]


def get_user(conn: sqlite3.Connection, uid: int) -> dict | None:
    r = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not r:
        return None
    d = dict(r)
    d["profile"] = json.loads(d.pop("profile_json"))
    return d


def save_profile(conn: sqlite3.Connection, uid: int, profile: dict) -> None:
    conn.execute("UPDATE users SET profile_json=? WHERE id=?", (json.dumps(profile), uid))
    conn.commit()


def snapshot(conn: sqlite3.Connection, uid: int, profile: dict, label: str) -> None:
    conn.execute("INSERT INTO profile_snapshots (user_id,label,profile_json) VALUES (?,?,?)",
                 (uid, label, json.dumps(profile)))
    conn.commit()


def snapshots(conn: sqlite3.Connection, uid: int) -> list[dict]:
    rows = conn.execute("SELECT * FROM profile_snapshots WHERE user_id=? ORDER BY id", (uid,)).fetchall()
    return [{"label": r["label"], "created_at": r["created_at"], "topics": json.loads(r["profile_json"])["topics"]} for r in rows]


def seen_article_ids(conn: sqlite3.Connection, uid: int) -> set[int]:
    shown = conn.execute(
        """SELECT DISTINCT i.article_id FROM edition_items i JOIN editions e ON e.id=i.edition_id WHERE e.user_id=?""",
        (uid,),
    ).fetchall()
    skipped = conn.execute("SELECT DISTINCT article_id FROM events WHERE user_id=? AND type='skip'", (uid,)).fetchall()
    return {r[0] for r in shown} | {r[0] for r in skipped if r[0]}


def generate_edition(conn: sqlite3.Connection, user: dict) -> int:
    uid = user["id"]
    profile = user["profile"]
    snaps = snapshots(conn, uid)
    prev_topics = snaps[-1]["topics"] if snaps else None
    changes = learner.describe_changes(prev_topics, profile)
    baseline = snaps[0]["topics"] if snaps else None

    profile = learner.decay(profile)
    pool = all_articles(conn)
    exclude = seen_article_ids(conn, uid)
    selection = scorer.select(profile, pool, user["budget_min"], exclude_ids=exclude)
    if len(selection["picks"]) < scorer.MIN_ITEMS:  # pool exhausted: allow repeats except skipped
        skipped = {r[0] for r in conn.execute("SELECT article_id FROM events WHERE user_id=? AND type='skip'", (uid,))}
        selection = scorer.select(profile, pool, user["budget_min"], exclude_ids=skipped)

    number = conn.execute("SELECT COUNT(*) FROM editions WHERE user_id=?", (uid,)).fetchone()[0] + 1
    sources = sorted({a["source"] for a in pool})
    ed = editor.write_edition(user, profile, selection, number, changes, baseline, sources)

    cur = conn.execute(
        "INSERT INTO editions (user_id,number,date,plan_json,editor_note,todo,quiz_json,read_min) VALUES (?,?,?,?,?,?,?,?)",
        (uid, number, date.today().isoformat(), json.dumps(ed["plan"]), ed["editor_note"], ed["todo"],
         json.dumps(ed["quiz"]), ed["read_min"]),
    )
    eid = cur.lastrowid
    for it in ed["items"]:
        conn.execute(
            """INSERT INTO edition_items (edition_id,article_id,slot,section,headline,dek,why,is_blind_spot,read_min)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (eid, it["article_id"], it["slot"], it["section"], it["headline"], it["dek"], it["why"],
             int(it["is_blind_spot"]), it["read_min"]),
        )
    conn.commit()
    save_profile(conn, uid, profile)
    snapshot(conn, uid, profile, f"edition-{number}")
    return eid


def edition_json(conn: sqlite3.Connection, eid: int, uid: int | None = None) -> dict | None:
    e = conn.execute("SELECT * FROM editions WHERE id=?", (eid,)).fetchone()
    if not e or (uid is not None and e["user_id"] != uid):
        return None
    rows = conn.execute(
        """SELECT i.*, a.url, a.source, a.image_url, a.topics_json FROM edition_items i
           JOIN articles a ON a.id=i.article_id WHERE i.edition_id=? ORDER BY i.slot""", (eid,),
    ).fetchall()
    items = []
    for r in rows:
        items.append({
            "id": r["id"], "article_id": r["article_id"], "slot": r["slot"], "section": r["section"],
            "headline": r["headline"], "dek": r["dek"], "why": r["why"], "source": r["source"], "url": r["url"],
            "image_url": r["image_url"], "topics": json.loads(r["topics_json"]), "read_min": r["read_min"],
            "is_blind_spot": bool(r["is_blind_spot"]), "headline_ur": r["headline_ur"],
            "dek_ur": r["dek_ur"] if "dek_ur" in r.keys() else None,
            "why_ur": r["why_ur"] if "why_ur" in r.keys() else None,
        })
    return {
        "id": e["id"], "number": e["number"], "date": e["date"], "editor_note": e["editor_note"], "todo": e["todo"],
        "read_min": e["read_min"], "plan": json.loads(e["plan_json"] or "{}"), "items": items,
        "quiz": json.loads(e["quiz_json"] or "[]"),
    }


def list_editions(conn: sqlite3.Connection, uid: int) -> list[dict]:
    rows = conn.execute("SELECT * FROM editions WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
    out = []
    for e in rows:
        items = conn.execute("SELECT headline FROM edition_items WHERE edition_id=? ORDER BY slot", (e["id"],)).fetchall()
        out.append({"id": e["id"], "number": e["number"], "date": e["date"], "story_count": len(items),
                    "read_min": e["read_min"], "lead_headline": items[0]["headline"] if items else ""})
    return out
