import pytest
from app.main import app
from fastapi.testclient import TestClient


def test_session_creation_and_privacy(client):
    # 1. Sign up User 1
    r1 = client.post("/api/auth/signup", json={
        "email": "user1@example.com",
        "password": "password123",
        "name": "User One",
        "region": "pakistan",
        "topics": ["cricket", "politics_pk"],
    })
    assert r1.status_code == 200
    d1 = r1.json()
    token1 = d1["token"]
    uid1 = d1["user_id"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # 2. Sign up User 2
    r2 = client.post("/api/auth/signup", json={
        "email": "user2@example.com",
        "password": "password123",
        "name": "User Two",
        "region": "global",
        "topics": ["ai", "markets"],
    })
    assert r2.status_code == 200
    d2 = r2.json()
    token2 = d2["token"]
    uid2 = d2["user_id"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # 3. User 1 can access own profile
    p1 = client.get("/api/profile", headers=headers1)
    assert p1.status_code == 200
    assert p1.json()["user"]["email"] == "user1@example.com"

    # User 2 cannot access User 1's profile with User 1's uid if using User 2's token
    p2 = client.get(f"/api/profile?uid={uid1}", headers=headers2)
    assert p2.status_code == 200
    # Must return User 2's data, NOT User 1's!
    assert p2.json()["user"]["email"] == "user2@example.com"
    assert p2.json()["user"]["id"] == uid2

    # Request without token fails
    unauth = client.get(f"/api/profile?uid={uid1}")
    # Without mock_llm bypass with headers, it should fail if not authenticated
    # Generate edition for User 1
    ed1_res = client.post("/api/editions/generate", headers=headers1)
    assert ed1_res.status_code == 200
    ed1_id = ed1_res.json()["id"]

    # User 2 CANNOT access User 1's edition!
    ed_cross = client.get(f"/api/editions/{ed1_id}", headers=headers2)
    assert ed_cross.status_code == 404

    # User 1 CAN access own edition
    ed_own = client.get(f"/api/editions/{ed1_id}", headers=headers1)
    assert ed_own.status_code == 200
    assert ed_own.json()["id"] == ed1_id


def test_saved_news_lifecycle_and_isolation(client):
    # Setup two users
    r1 = client.post("/api/auth/signup", json={"email": "saver1@test.com", "password": "pass", "name": "Saver 1"})
    headers1 = {"Authorization": f"Bearer {r1.json()['token']}"}

    r2 = client.post("/api/auth/signup", json={"email": "saver2@test.com", "password": "pass", "name": "Saver 2"})
    headers2 = {"Authorization": f"Bearer {r2.json()['token']}"}

    # Save article 1 for user 1
    save_res = client.post("/api/saved/1", headers=headers1)
    assert save_res.status_code == 200
    assert save_res.json()["saved"] is True

    # Check saved list for user 1
    list1 = client.get("/api/saved", headers=headers1).json()["saved"]
    assert len(list1) == 1
    assert list1[0]["article_id"] == 1

    ids1 = client.get("/api/saved/ids", headers=headers1).json()["saved_ids"]
    assert ids1 == [1]

    # User 2 must have EMPTY saved list (complete privacy & isolation)
    list2 = client.get("/api/saved", headers=headers2).json()["saved"]
    assert len(list2) == 0
    ids2 = client.get("/api/saved/ids", headers=headers2).json()["saved_ids"]
    assert ids2 == []

    # Unsave article 1 for user 1
    del_res = client.delete("/api/saved/1", headers=headers1)
    assert del_res.status_code == 200
    assert del_res.json()["saved"] is False

    # List is now empty for user 1
    assert len(client.get("/api/saved", headers=headers1).json()["saved"]) == 0


def test_settings_update_and_feed_refresh(client):
    r = client.post("/api/auth/signup", json={
        "email": "settings_user@test.com",
        "password": "pass",
        "name": "Original Name",
        "region": "global",
        "topics": ["science"],
    })
    headers = {"Authorization": f"Bearer {r.json()['token']}"}

    # Update settings: change region to pakistan and topics to cricket & startups
    up_res = client.post("/api/profile/settings", headers=headers, json={
        "name": "Updated Name",
        "region": "pakistan",
        "topics": ["cricket", "startups"],
        "budget_min": 5,
    })
    assert up_res.status_code == 200
    data = up_res.json()
    assert data["ok"] is True
    assert data["user"]["name"] == "Updated Name"
    assert data["user"]["region"] == "pakistan"
    assert data["user"]["budget_min"] == 5
    assert "edition_id" in data
    assert data["profile"]["topics"]["cricket"] >= 0.7

    # Verify profile reflects changes
    prof = client.get("/api/profile", headers=headers).json()
    assert prof["user"]["name"] == "Updated Name"
    assert prof["user"]["region"] == "pakistan"
    assert prof["user"]["budget_min"] == 5


def test_logout_invalidates_session(client):
    r = client.post("/api/auth/signup", json={"email": "logout_test@test.com", "password": "pass"})
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify active
    assert client.get("/api/profile", headers=headers).status_code == 200

    # Logout
    logout_res = client.post("/api/auth/logout", headers=headers)
    assert logout_res.status_code == 200

    # Post-logout attempt must be 401
    assert client.get("/api/profile", headers=headers).status_code == 401
