"""The Fold — FastAPI app. Thin handlers; logic lives in app/agents and app/repo."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field

from . import config, db, i18n, llm, pdf, repo
from .agents import ingest, learner, profiler
from .taxonomy import public_topics


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="The Fold", version="1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=config.cors_origins(), allow_methods=["*"], allow_headers=["*"])


# ---------- auth-less identity ----------
def current_user(
    conn: sqlite3.Connection = Depends(db.get_db),
    x_user_id: str | None = Header(default=None),
    uid: str | None = Query(default=None),
) -> dict:
    raw = x_user_id or uid
    if not raw or not raw.isdigit():
        raise HTTPException(401, "Missing X-User-Id")
    user = repo.get_user(conn, int(raw))
    if not user:
        raise HTTPException(401, "Unknown user")
    return user


# ---------- models ----------
class OnboardIn(BaseModel):
    name: str | None = None
    city: str | None = None
    recent_read: str | None = None
    topics: list[str] = Field(default_factory=list)
    other: str | None = None
    budget_min: Literal[5, 12, 20] = 12
    lang: Literal["en", "ur"] = "en"


class EventIn(BaseModel):
    edition_id: int | None = None
    article_id: int | None = None
    type: Literal["open", "skip", "unskip", "dwell", "quiz_correct", "quiz_wrong", "more_challenge", "less_challenge"]
    value: float | None = None


class AdjustIn(BaseModel):
    topic: str
    delta: float = Field(ge=-1, le=1)


class LoginIn(BaseModel):
    email: str
    password: str


class SignUpIn(BaseModel):
    email: str
    password: str
    name: str | None = None
    city: str | None = None
    budget_min: Literal[5, 12, 20] = 12
    region: str | None = None          # e.g. "pakistan", "global", "south_asia", "middle_east"
    topics: list[str] = Field(default_factory=list)  # optional seeded interests


def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.strip().encode()).hexdigest()


# ---------- routes ----------
@app.get("/api/health")
def health(conn: sqlite3.Connection = Depends(db.get_db)):
    n = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    return {"ok": True, "llm": "mock" if llm.is_mock() else llm.provider_name(), "articles": n}


@app.get("/api/topics")
def topics():
    return {"topics": public_topics()}


@app.get("/api/users")
def list_users(conn: sqlite3.Connection = Depends(db.get_db)):
    rows = conn.execute("SELECT id, name, city, budget_min, email FROM users ORDER BY id ASC").fetchall()
    return {"users": [dict(r) for r in rows]}


# Default topic seeds per region
_REGION_TOPICS: dict[str, list[str]] = {
    "pakistan": ["politics_pk", "economy_pk", "ai", "cricket", "startups"],
    "south_asia": ["geopolitics", "economy_pk", "ai", "cricket", "climate"],
    "middle_east": ["geopolitics", "markets", "energy", "ai", "startups"],
    "global": ["ai", "markets", "startups", "geopolitics", "science"],
    "tech": ["ai", "software", "cybersecurity", "startups", "design"],
    "finance": ["markets", "economy_pk", "crypto", "startups", "business"],
    "sports": ["cricket", "football", "f1"],
}


@app.post("/api/auth/signup")
def signup(body: SignUpIn, conn: sqlite3.Connection = Depends(db.get_db)):
    clean_email = body.email.strip().lower()
    existing = conn.execute("SELECT id FROM users WHERE LOWER(email)=?", (clean_email,)).fetchone()
    if existing:
        raise HTTPException(400, "An account with this email already exists")
    # Merge region defaults + explicit topic picks
    seed_topics = list(body.topics) if body.topics else []
    if not seed_topics and body.region:
        seed_topics = _REGION_TOPICS.get(body.region, _REGION_TOPICS["global"])
    if not seed_topics:
        seed_topics = ["ai", "markets", "startups"]
    profile = profiler.build_profile({
        "name": body.name,
        "city": body.city,
        "budget_min": body.budget_min,
        "topics": seed_topics,
        "region": body.region or "global",
    })
    h = _hash_pw(body.password)
    cur = conn.execute(
        "INSERT INTO users (email, password_hash, name, city, budget_min, profile_json) VALUES (?,?,?,?,?,?)",
        (clean_email, h, body.name, body.city, body.budget_min, json.dumps(profile)),
    )
    conn.commit()
    uid = cur.lastrowid
    repo.snapshot(conn, uid, profile, "signup")
    return {"user_id": uid, "name": body.name or clean_email.split("@")[0], "email": clean_email}


@app.post("/api/auth/login")
def login(body: LoginIn, conn: sqlite3.Connection = Depends(db.get_db)):
    clean_email = body.email.strip().lower()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email)=?", (clean_email,)).fetchone()
    if not user:
        # Also allow signing in by username (e.g. 'ayesha' or 'bilal')
        user = conn.execute("SELECT * FROM users WHERE LOWER(name)=?", (clean_email,)).fetchone()
    if not user:
        raise HTTPException(401, "No account found with this email")

    if user["password_hash"]:
        if user["password_hash"] != _hash_pw(body.password):
            raise HTTPException(401, "Incorrect password")
    else:
        # Bind password for demo persona
        conn.execute(
            "UPDATE users SET email=?, password_hash=? WHERE id=?",
            (clean_email if "@" in clean_email else f"{user['name'].lower()}@thefold.app", _hash_pw(body.password), user["id"]),
        )
        conn.commit()

    return {"user_id": user["id"], "name": user["name"] or f"Reader #{user['id']}", "email": user["email"] or clean_email}




@app.post("/api/onboard")
def onboard(body: OnboardIn, conn: sqlite3.Connection = Depends(db.get_db)):
    profile = profiler.build_profile(body.model_dump())
    cur = conn.execute(
        "INSERT INTO users (name,city,budget_min,lang,profile_json) VALUES (?,?,?,?,?)",
        (body.name, body.city, body.budget_min, body.lang, json.dumps(profile)),
    )
    conn.commit()
    uid = cur.lastrowid
    repo.snapshot(conn, uid, profile, "onboarding")
    return {"user_id": uid, "profile": profile}


@app.get("/api/profile")
def get_profile(user: dict = Depends(current_user), conn: sqlite3.Connection = Depends(db.get_db)):
    u = {k: user[k] for k in ("id", "name", "city", "budget_min", "lang")}
    return {"user": u, "profile": user["profile"], "history": repo.snapshots(conn, user["id"])}


@app.post("/api/profile/adjust")
def adjust(body: AdjustIn, user: dict = Depends(current_user), conn: sqlite3.Connection = Depends(db.get_db)):
    p = user["profile"]
    old = p["topics"].get(body.topic, learner.NEW_TOPIC_W)
    p["topics"][body.topic] = round(max(learner.MIN_W, min(learner.MAX_W, old + body.delta)), 4)
    repo.save_profile(conn, user["id"], p)
    return {"profile": p}


@app.post("/api/ingest")
def run_ingest(conn: sqlite3.Connection = Depends(db.get_db)):
    added = ingest.refresh(conn)
    total = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    return {"added": added, "total": total}


@app.post("/api/editions/generate")
def generate(user: dict = Depends(current_user), conn: sqlite3.Connection = Depends(db.get_db)):
    if config.live_ingest():
        try:
            ingest.refresh(conn)
        except Exception:
            pass
    eid = repo.generate_edition(conn, user)
    return repo.edition_json(conn, eid, user["id"])


@app.get("/api/editions")
def editions(user: dict = Depends(current_user), conn: sqlite3.Connection = Depends(db.get_db)):
    return {"editions": repo.list_editions(conn, user["id"])}


@app.get("/api/editions/latest")
def latest(user: dict = Depends(current_user), conn: sqlite3.Connection = Depends(db.get_db)):
    r = conn.execute("SELECT id FROM editions WHERE user_id=? ORDER BY id DESC LIMIT 1", (user["id"],)).fetchone()
    if not r:
        raise HTTPException(404, "No edition yet")
    return repo.edition_json(conn, r["id"], user["id"])


@app.get("/api/editions/{eid}")
def get_edition(eid: int, user: dict = Depends(current_user), conn: sqlite3.Connection = Depends(db.get_db)):
    ed = repo.edition_json(conn, eid, user["id"])
    if not ed:
        raise HTTPException(404, "Edition not found")
    return ed


@app.get("/api/editions/{eid}/pdf")
def edition_pdf(eid: int, user: dict = Depends(current_user), conn: sqlite3.Connection = Depends(db.get_db)):
    ed = repo.edition_json(conn, eid, user["id"])
    if not ed:
        raise HTTPException(404, "Edition not found")
    html = pdf.render_html(ed, user)
    data = pdf.render_pdf(html)
    if data is None:  # WeasyPrint unavailable: serve print-ready HTML instead of a 500
        return HTMLResponse(html.replace("</body>", "<script>window.print()</script></body>"))
    return Response(data, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="the-fold-no-{ed["number"]}.pdf"'})


@app.post("/api/events")
def post_event(body: EventIn, user: dict = Depends(current_user), conn: sqlite3.Connection = Depends(db.get_db)):
    topics: list[str] = []
    if body.article_id:
        r = conn.execute("SELECT topics_json FROM articles WHERE id=?", (body.article_id,)).fetchone()
        if not r:
            raise HTTPException(404, "Unknown article")
        topics = json.loads(r["topics_json"])
    conn.execute("INSERT INTO events (user_id,edition_id,article_id,type,value) VALUES (?,?,?,?,?)",
                 (user["id"], body.edition_id, body.article_id, body.type, body.value))
    new_profile, delta = learner.apply_event(user["profile"], body.type, topics, body.value)
    repo.save_profile(conn, user["id"], new_profile)
    return {"ok": True, "profile_delta": delta}


@app.get("/api/events/recent")
def recent_events(user: dict = Depends(current_user), conn: sqlite3.Connection = Depends(db.get_db)):
    rows = conn.execute("SELECT * FROM events WHERE user_id=? ORDER BY id DESC LIMIT 50", (user["id"],)).fetchall()
    return {"events": [dict(r) for r in rows]}


@app.post("/api/editions/{eid}/translate")
def translate_edition(eid: int, user: dict = Depends(current_user), conn: sqlite3.Connection = Depends(db.get_db)):
    """Translate all headlines in an edition to Urdu (cached). Returns count updated."""
    ed = repo.edition_json(conn, eid, user["id"])
    if not ed:
        raise HTTPException(404, "Edition not found")
    i18n.ensure_table(conn)
    updated = i18n.translate_edition_headlines(eid, conn)
    return {"updated": updated}
