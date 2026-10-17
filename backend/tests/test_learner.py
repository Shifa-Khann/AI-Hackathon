from conftest import CRICKET_FAN, onboard

from app.agents import learner


def _prof(**kw):
    return {"topics": {"ai": 0.7, "cricket": 0.7, "f1": 0.1}, "picked": ["ai", "cricket"], "blind_appetite": 0.5, **kw}


def test_skip_lowers_open_raises():
    p, d = learner.apply_event(_prof(), "skip", ["cricket"])
    assert p["topics"]["cricket"] < 0.7 and d["cricket"] < 0
    p, d = learner.apply_event(_prof(), "open", ["ai"])
    assert p["topics"]["ai"] > 0.7


def test_picked_topics_never_below_floor():
    p = _prof()
    for _ in range(20):
        p, _ = learner.apply_event(p, "skip", ["cricket"])
    assert p["topics"]["cricket"] >= learner.PICKED_FLOOR


def test_new_topic_enters_on_positive_signal_only():
    p, d = learner.apply_event(_prof(), "skip", ["space"])
    assert "space" not in p["topics"]
    p, d = learner.apply_event(_prof(), "open", ["space"])
    assert p["topics"]["space"] >= learner.NEW_TOPIC_W - 0.001


def test_dwell_thresholds():
    _, d_short = learner.apply_event(_prof(), "dwell", ["ai"], 3)
    _, d_mid = learner.apply_event(_prof(), "dwell", ["ai"], 10)
    _, d_long = learner.apply_event(_prof(), "dwell", ["ai"], 45)
    assert not d_short and 0 < d_mid["ai"] < d_long["ai"]


def test_challenge_changes_blind_appetite():
    p, _ = learner.apply_event(_prof(), "more_challenge", [])
    assert p["blind_appetite"] > 0.5
    p, _ = learner.apply_event(_prof(), "less_challenge", [])
    assert p["blind_appetite"] < 0.5


def test_decay_shrinks_weights():
    p = learner.decay(_prof())
    assert p["topics"]["ai"] < 0.7


def test_describe_changes():
    old = {"cricket": 0.7, "ai": 0.5}
    new = {"topics": {"cricket": 0.3, "ai": 0.7}}
    s = learner.describe_changes(old, new)
    assert "less Cricket" in s and "more Artificial intelligence" in s
    assert learner.describe_changes(None, new) == ""


def _cricket_count(ed):
    return sum(1 for i in ed["items"] if "cricket" in i["topics"])


def test_skip_changes_next_edition(client):
    """The demo moment: skip a topic, regenerate, the paper visibly shifts."""
    _, h = onboard(client, CRICKET_FAN)
    ed1 = client.post("/api/editions/generate", headers=h).json()
    w0 = client.get("/api/profile", headers=h).json()["profile"]["topics"]["cricket"]
    crick = [i for i in ed1["items"] if "cricket" in i["topics"]]
    assert len(crick) >= 1, "test persona should get at least one cricket story"
    for it in crick:
        client.post("/api/events", headers=h, json={"edition_id": ed1["id"], "article_id": it["article_id"], "type": "skip"})
    w1 = client.get("/api/profile", headers=h).json()["profile"]["topics"]["cricket"]
    assert w1 < w0

    ed2 = client.post("/api/editions/generate", headers=h).json()
    assert _cricket_count(ed2) < _cricket_count(ed1)
    changed = {i["article_id"] for i in ed2["items"]} - {i["article_id"] for i in ed1["items"]}
    assert len(changed) >= 2
    assert "less" in ed2["editor_note"].lower() and "Cricket" in ed2["editor_note"]


def test_opens_shift_why_this(client):
    _, h = onboard(client, CRICKET_FAN)
    ed1 = client.post("/api/editions/generate", headers=h).json()
    for it in ed1["items"][:2]:
        client.post("/api/events", headers=h, json={"article_id": it["article_id"], "type": "open"})
    ed2 = client.post("/api/editions/generate", headers=h).json()
    assert all(i["why"] for i in ed2["items"])
