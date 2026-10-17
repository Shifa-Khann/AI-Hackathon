from conftest import AYESHA, onboard


def test_health_and_topics(client):
    h = client.get("/api/health").json()
    assert h["ok"] and h["llm"] == "mock" and h["articles"] >= 60
    assert len(client.get("/api/topics").json()["topics"]) >= 20


def test_auth_required(client):
    assert client.get("/api/editions").status_code == 401
    assert client.get("/api/editions", headers={"X-User-Id": "999"}).status_code == 401


def test_full_flow(client):
    uid, h = onboard(client, AYESHA)
    assert client.get("/api/editions/latest", headers=h).status_code == 404

    ed = client.post("/api/editions/generate", headers=h).json()
    assert ed["number"] == 1 and len(ed["items"]) >= 3
    assert all(it["why"] for it in ed["items"]), "every story needs a Why this?"
    assert all(it["url"].startswith("http") for it in ed["items"])
    assert len(ed["quiz"]) >= 1 and ed["editor_note"]

    assert client.get(f"/api/editions/{ed['id']}", headers=h).json()["id"] == ed["id"]
    assert client.get("/api/editions/latest", headers=h).json()["id"] == ed["id"]

    art = ed["items"][1]["article_id"]
    r = client.post("/api/events", headers=h, json={"edition_id": ed["id"], "article_id": art, "type": "skip"})
    assert r.status_code == 200 and r.json()["profile_delta"]
    assert client.get("/api/events/recent", headers=h).json()["events"][0]["type"] == "skip"

    ed2 = client.post("/api/editions/generate", headers=h).json()
    assert ed2["number"] == 2 and ed2["id"] != ed["id"]
    assert art not in [i["article_id"] for i in ed2["items"]], "skipped story must not come back"

    lst = client.get("/api/editions", headers=h).json()["editions"]
    assert [e["number"] for e in lst] == [2, 1]


def test_editions_are_private(client):
    _, h1 = onboard(client, AYESHA)
    _, h2 = onboard(client, {**AYESHA, "name": "Other"})
    ed = client.post("/api/editions/generate", headers=h1).json()
    assert client.get(f"/api/editions/{ed['id']}", headers=h2).status_code == 404


def test_profile_and_adjust(client):
    _, h = onboard(client, AYESHA)
    client.post("/api/editions/generate", headers=h)
    p = client.get("/api/profile", headers=h).json()
    assert len(p["history"]) == 2  # onboarding + edition-1
    before = p["profile"]["topics"]["ai"]
    after = client.post("/api/profile/adjust", headers=h, json={"topic": "ai", "delta": -0.3}).json()["profile"]["topics"]["ai"]
    assert after < before


def test_bad_event_type_rejected(client):
    _, h = onboard(client, AYESHA)
    assert client.post("/api/events", headers=h, json={"type": "explode"}).status_code == 422


def test_pdf_or_html_fallback(client):
    _, h = onboard(client, AYESHA)
    ed = client.post("/api/editions/generate", headers=h).json()
    r = client.get(f"/api/editions/{ed['id']}/pdf", headers=h)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith(("application/pdf", "text/html"))
    # browsers can't send headers on a plain link, so ?uid= must work too
    uid = h["X-User-Id"]
    assert client.get(f"/api/editions/{ed['id']}/pdf?uid={uid}").status_code == 200
