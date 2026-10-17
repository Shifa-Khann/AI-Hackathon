"""Editor: turn selected articles into edition copy — headlines, deks, why-this, note, layout plan, quiz."""
from __future__ import annotations

import re

from .. import config, llm
from ..taxonomy import label


def _sentences(text: str, n: int = 2) -> str:
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return " ".join(parts[:n])


def _trim_words(text: str, n: int = 12) -> str:
    words = text.split()
    return text if len(words) <= n else " ".join(words[:n]).rstrip(",;:") + "…"


def why_this(a: dict, profile: dict, blind: bool = False, baseline: dict | None = None) -> str:
    """One sentence tracing the story back to the reader's words or behaviour."""
    topic = a["topics"][0]
    lab = label(topic).lower()
    if blind:
        return f"Outside your usual reading ({lab}) — included on purpose to widen your view."
    quote = (profile.get("quote") or "").strip()
    if quote:
        from .tagger import keyword_topics

        if topic in keyword_topics(quote, limit=4):
            snippet = quote if len(quote) <= 60 else quote[:57].rstrip() + "…"
            return f"You told us you read about “{snippet}” — this follows that thread."
    if topic in profile.get("picked", []):
        learned = baseline and profile["topics"].get(topic, 0) > baseline.get(topic, 0) + 0.05
        if learned:
            return f"You picked {lab} at the start and have been opening these lately."
        return f"You picked {lab} when setting up your paper."
    if baseline and profile["topics"].get(topic, 0) > baseline.get(topic, 0) + 0.05:
        return f"You've been opening {lab} stories lately, so we're giving you more."
    ents = {e.lower() for e in profile.get("entities", [])}
    hit = next((e for e in a.get("entities", []) if e.lower() in ents), None)
    if hit:
        return f"Mentions {hit}, which you said you follow."
    return f"Ranked highly for {lab} and fresh today."


def _layout_plan(items: list[dict]) -> dict:
    n = len(items)
    columns = 3 if n >= 7 else 2
    style = "wide" if n >= 6 else "split"
    sections = []
    for it in items:
        if it["section"] not in sections:
            sections.append(it["section"])
    return {"hero": items[0]["article_id"], "columns": columns, "hero_style": style, "sections": sections}


def _fallback_quiz(items: list[dict], all_sources: list[str]) -> list[dict]:
    quiz = []
    for it in [i for i in items if not i["is_blind_spot"]][:3]:
        wrong = [s for s in all_sources if s != it["source"]][:2]
        options = sorted({it["source"], *wrong})
        quiz.append({
            "q": f"Which outlet reported: “{it['headline']}”?",
            "options": options,
            "answer": options.index(it["source"]),
            "article_id": it["article_id"],
        })
    return quiz


def write_edition(
    user: dict,
    profile: dict,
    selection: dict,
    number: int,
    changes: str = "",
    baseline: dict | None = None,
    all_sources: list[str] | None = None,
) -> dict:
    """Return {items, editor_note, todo, plan, quiz, read_min}. Falls back to deterministic copy."""
    picks = selection["picks"]
    blind = selection.get("blind")
    ordered = [(a, False) for a in picks] + ([(blind, True)] if blind else [])
    items = []
    for slot, (a, is_blind) in enumerate(ordered):
        items.append({
            "article_id": a["id"], "slot": slot,
            "section": "Blind Spot" if is_blind else ("Front Page" if slot == 0 else label(a["topics"][0])),
            "headline": _trim_words(a["title"]), "dek": _sentences(a.get("summary", "")),
            "why": why_this(a, profile, is_blind, baseline),
            "is_blind_spot": is_blind, "read_min": a["read_min"], "source": a.get("source", ""),
        })
    lead = items[0]["headline"] if items else ""
    note = (
        f"Edition No. {number}: {len(items)} stories, about {selection['total_min']} minutes — then you're done. "
        f"I led with “{lead}” because it matched what you care about most today. {changes}"
    ).strip()
    todo = f"Pick one story from today and read the original in full: “{lead}”." if lead else ""
    quiz = _fallback_quiz(items, all_sources or [i["source"] for i in items])

    if not llm.is_mock() and items:
        payload = {
            "reader": {"name": user.get("name"), "profile_summary": profile.get("summary"), "quote": profile.get("quote"),
                       "top_topics": sorted(profile["topics"], key=profile["topics"].get, reverse=True)[:5]},
            "changes_since_last_edition": changes,
            "articles": [{"article_id": it["article_id"], "title": a["title"], "summary": a.get("summary", ""),
                          "source": a.get("source", ""), "blind_spot": it["is_blind_spot"]}
                         for it, (a, _) in zip(items, ordered)],
        }
        import json

        res = llm.complete_json(
            "You are the editor of 'The Fold', a calm, finite personal newspaper. For each article write: headline (<=12 words, "
            "no clickbait, no question marks), dek (2 factual sentences using ONLY the provided summary), why (one sentence telling "
            "the reader why it is in their paper, citing their quote or behaviour if provided). Also write editor_note (2-3 sentences, "
            "first person), todo (one concrete thing to do today, or empty), and 3 multiple-choice quiz questions answerable from the deks. "
            'Return {"items":[{"article_id":1,"headline":"","dek":"","why":""}],"editor_note":"","todo":"",'
            '"quiz":[{"q":"","options":["","",""],"answer":0,"article_id":1}]}.',
            json.dumps(payload),
            fallback=lambda: {},
            model=config.smart_model(),
        )
        by_id = {r.get("article_id"): r for r in res.get("items", []) if isinstance(r, dict)}
        for it in items:
            r = by_id.get(it["article_id"])
            if r:
                it["headline"] = r.get("headline") or it["headline"]
                it["dek"] = r.get("dek") or it["dek"]
                it["why"] = r.get("why") or it["why"]
        note = res.get("editor_note") or note
        todo = res.get("todo", todo) or todo
        q = res.get("quiz")
        if isinstance(q, list) and q and all({"q", "options", "answer"} <= set(x) for x in q):
            quiz = q[:3]

    return {
        "items": items, "editor_note": note, "todo": todo,
        "plan": _layout_plan(items) if items else {}, "quiz": quiz, "read_min": selection["total_min"],
    }
