from app.agents import editor, ingest, profiler, quiz, tagger


def test_profiler_chips_and_free_text():
    p = profiler.build_profile({"topics": ["ai", "cricket"], "recent_read": "Nvidia earnings and the stock rally", "other": ""})
    assert p["topics"]["ai"] >= 0.7 and p["topics"]["cricket"] >= 0.7
    assert p["topics"]["markets"] >= 0.5, "free text should imply markets"
    assert p["picked"] == ["ai", "cricket"] and "Nvidia" in p["entities"] or p["entities"] is not None
    assert all(0 <= w <= 1 for w in p["topics"].values())


def test_profiler_ignores_unknown_topics():
    p = profiler.build_profile({"topics": ["ai", "not_a_topic"]})
    assert "not_a_topic" not in p["topics"]


def test_tagger_keywords():
    assert "cricket" in tagger.keyword_topics("Opener hits a century in the Test against bowlers")
    assert tagger.keyword_topics("zzzz qqqq") == []
    assert "Nvidia" in tagger.extract_entities("Nvidia shares rose")


def test_title_dedupe():
    known = [ingest._title_tokens("Opener's unbeaten century puts the home side in control")]
    assert ingest.is_duplicate_title("Opener's unbeaten century puts the home side in control!", known)
    assert not ingest.is_duplicate_title("Rupee holds steady as remittances stay strong", known)


def test_ingest_store_dedupes(client):
    from app import db

    conn = db.connect()
    base = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    cand = [
        {"url": "https://x.test/1", "title": "Quantum chip breakthrough announced by researchers", "source": "T", "summary": "Researchers study physics.",
         "published_at": "2026-10-17T00:00:00+00:00", "word_count": 500},
        {"url": "https://x.test/1", "title": "Same url again", "source": "T", "summary": "", "published_at": "2026-10-17T00:00:00+00:00", "word_count": 500},
        {"url": "https://x.test/2", "title": "Quantum chip breakthrough announced by researchers", "source": "U", "summary": "", "published_at": "2026-10-17T00:00:00+00:00", "word_count": 500},
    ]
    assert ingest.store(conn, [dict(c) for c in cand]) == 1
    assert ingest.store(conn, [dict(c) for c in cand]) == 0, "re-run must add nothing"
    assert conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0] == base + 1
    conn.close()


def test_editor_copy_rules():
    prof = {"topics": {"ai": 0.8}, "picked": ["ai"], "quote": "Pakistan AI policy", "entities": [], "avoid": []}
    art = {"id": 1, "title": "One two three four five six seven eight nine ten eleven twelve thirteen fourteen",
           "summary": "First sentence. Second sentence. Third sentence.", "topics": ["ai"], "source": "S", "read_min": 2, "entities": []}
    sel = {"picks": [art], "blind": None, "total_min": 2}
    ed = editor.write_edition({"name": "A"}, prof, sel, 1, "", None, ["S", "T", "U"])
    it = ed["items"][0]
    assert len(it["headline"].rstrip("…").split()) <= 12
    assert it["dek"] == "First sentence. Second sentence."
    assert "Pakistan AI policy" in it["why"]
    assert ed["plan"]["columns"] in (2, 3) and ed["quiz"]


def test_quiz_grading():
    q = [{"q": "a", "options": ["x", "y"], "answer": 1, "article_id": 5}, {"q": "b", "options": ["x", "y"], "answer": 0, "article_id": 6}]
    g = quiz.grade(q, [1, 1])
    assert g["score"] == 1 and g["events"][1]["type"] == "quiz_wrong"
