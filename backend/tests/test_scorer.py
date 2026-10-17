from conftest import AYESHA, BILAL, onboard


def _ids(ed):
    return {i["article_id"] for i in ed["items"] if not i["is_blind_spot"]}


def test_budget_respected(client):
    for budget in (5, 12, 20):
        _, h = onboard(client, {**AYESHA, "budget_min": budget})
        ed = client.post("/api/editions/generate", headers=h).json()
        assert budget * 0.6 <= ed["read_min"] <= budget * 1.5 + 5, (budget, ed["read_min"])
        assert len(ed["items"]) >= 3


def test_personas_differ(client):
    _, ha = onboard(client, AYESHA)
    _, hb = onboard(client, BILAL)
    a = _ids(client.post("/api/editions/generate", headers=ha).json())
    b = _ids(client.post("/api/editions/generate", headers=hb).json())
    overlap = len(a & b) / max(1, min(len(a), len(b)))
    assert overlap < 0.3, f"personas share {overlap:.0%} of stories"


def test_exactly_one_blind_spot_and_labelled(client):
    _, h = onboard(client, AYESHA)
    ed = client.post("/api/editions/generate", headers=h).json()
    blind = [i for i in ed["items"] if i["is_blind_spot"]]
    assert len(blind) == 1 and blind[0]["section"] == "Blind Spot"


def test_diversity_cap():
    from datetime import datetime, timezone

    from app.agents import scorer

    prof = {"topics": {"cricket": 1.0}, "picked": ["cricket"], "entities": [], "avoid": [], "blind_appetite": 0}
    pool = [{"id": i, "title": f"t{i}", "topics": ["cricket"], "source": f"s{i}", "published_at": datetime.now(timezone.utc).isoformat(),
             "word_count": 460, "summary": ""} for i in range(10)]
    sel = scorer.select(prof, pool, 20)
    assert len(sel["picks"]) <= scorer.MAX_PER_TOPIC or len(sel["picks"]) == scorer.MIN_ITEMS


def test_avoid_topics_excluded():
    from datetime import datetime, timezone

    from app.agents import scorer

    prof = {"topics": {"f1": 1.0, "ai": 0.9}, "picked": [], "entities": [], "avoid": ["f1"], "blind_appetite": 0}
    now = datetime.now(timezone.utc).isoformat()
    pool = [{"id": 1, "title": "a", "topics": ["f1"], "source": "x", "published_at": now, "word_count": 500},
            {"id": 2, "title": "b", "topics": ["ai"], "source": "y", "published_at": now, "word_count": 500}]
    sel = scorer.select(prof, pool, 5)
    assert all("f1" not in a["topics"] for a in sel["picks"])
