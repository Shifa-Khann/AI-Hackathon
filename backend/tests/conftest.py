import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["MOCK_LLM"] = "1"
os.environ["LIVE_INGEST"] = "0"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


AYESHA = {"name": "Ayesha", "city": "Islamabad", "budget_min": 12, "topics": ["ai", "startups", "software", "politics_pk"],
          "recent_read": "AI policy and open source"}
BILAL = {"name": "Bilal", "city": "Karachi", "budget_min": 20, "topics": ["markets", "economy_pk", "energy", "f1", "business"],
         "recent_read": "Rupee and the budget"}
CRICKET_FAN = {"name": "Cricket", "budget_min": 12, "topics": ["cricket", "ai", "startups", "football"]}


def onboard(client, payload):
    r = client.post("/api/onboard", json=payload)
    assert r.status_code == 200, r.text
    uid = r.json()["user_id"]
    return uid, {"X-User-Id": str(uid)}
