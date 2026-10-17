"""Create two demo personas with two editions each.  Run:  python -m app.seed.make_demo"""
from __future__ import annotations

from .. import db, repo
from ..agents import learner, profiler

PERSONAS = [
    {"name": "Ayesha", "city": "Islamabad", "budget_min": 12,
     "recent_read": "How AI policy and open source are reshaping Pakistan's startup scene",
     "topics": ["ai", "startups", "politics_pk", "software", "design"], "other": "", "lang": "en"},
    {"name": "Bilal", "city": "Karachi", "budget_min": 20,
     "recent_read": "Rupee, remittances and the budget debate",
     "topics": ["markets", "economy_pk", "energy", "f1", "business"], "other": "", "lang": "en"},
]


def main() -> None:
    import json

    db.init_db()
    conn = db.connect()
    for p in PERSONAS:
        profile = profiler.build_profile(p)
        cur = conn.execute("INSERT INTO users (name,city,budget_min,lang,profile_json) VALUES (?,?,?,?,?)",
                           (p["name"], p["city"], p["budget_min"], p["lang"], json.dumps(profile)))
        conn.commit()
        uid = cur.lastrowid
        repo.snapshot(conn, uid, profile, "onboarding")
        user = repo.get_user(conn, uid)
        e1 = repo.generate_edition(conn, user)
        ed1 = repo.edition_json(conn, e1)
        # simulate behaviour: skip the last two stories, open the lead
        prof = repo.get_user(conn, uid)["profile"]
        for it in ed1["items"][-2:]:
            if it["is_blind_spot"]:
                continue
            prof, _ = learner.apply_event(prof, "skip", it["topics"])
            conn.execute("INSERT INTO events (user_id,edition_id,article_id,type) VALUES (?,?,?,?)", (uid, e1, it["article_id"], "skip"))
        prof, _ = learner.apply_event(prof, "open", ed1["items"][0]["topics"])
        conn.execute("INSERT INTO events (user_id,edition_id,article_id,type) VALUES (?,?,?,?)", (uid, e1, ed1["items"][0]["article_id"], "open"))
        repo.save_profile(conn, uid, prof)
        repo.generate_edition(conn, repo.get_user(conn, uid))
        print(f"{p['name']:8s} user_id={uid}   open: http://localhost:3000/?uid={uid}")
    conn.close()


if __name__ == "__main__":
    main()
