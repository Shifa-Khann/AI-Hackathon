"""Profiler: onboarding answers -> weighted interest profile."""
from __future__ import annotations

import re

from .. import llm
from ..taxonomy import TOPIC_IDS
from .tagger import keyword_topics


def _entities_from_text(text: str) -> list[str]:
    # Capitalised words that are not sentence starters are likely names.
    words = re.findall(r"(?<![.!?]\s)(?<!^)\b([A-Z][a-zA-Z]{2,})\b", text)
    stop = {"The", "And", "But", "This", "That", "What", "When", "How"}
    out: list[str] = []
    for w in words:
        if w not in stop and w not in out:
            out.append(w)
    return out[:6]


def fallback_profile(answers: dict) -> dict:
    chips = [t for t in answers.get("topics", []) if t in TOPIC_IDS]
    weights: dict[str, float] = {t: 0.7 for t in chips}
    free = f"{answers.get('recent_read') or ''} {answers.get('other') or ''}".strip()
    for t in keyword_topics(free, limit=4):
        weights[t] = max(weights.get(t, 0.0), 0.55)
    # keep every taxonomy topic present at a low baseline so the graph and learner have something to move
    for t in TOPIC_IDS:
        weights.setdefault(t, 0.08)
    return {
        "topics": weights,
        "picked": chips,
        "entities": _entities_from_text(free),
        "tone": "mixed",
        "avoid": [],
        "summary": f"Reads about {', '.join(chips[:3]) or 'a bit of everything'}.",
        "quote": (answers.get("recent_read") or "").strip()[:140],
        "blind_appetite": 0.5,
    }


def build_profile(answers: dict) -> dict:
    base = fallback_profile(answers)
    if llm.is_mock():
        return base
    free = f"Recently read: {answers.get('recent_read')}\nOther interests: {answers.get('other')}\nPicked: {answers.get('topics')}"
    res = llm.complete_json(
        "You are the intake editor of a personal newspaper. Convert the reader's answers into a weighted interest profile. "
        f"Use only topic ids from {TOPIC_IDS}. Weights 0-1; picked chips >= 0.6. "
        'Return {"topics":{"ai":0.8},"entities":["Nvidia"],"tone":"analytical|light|mixed","avoid":[],"summary":"one line"}.',
        free,
        fallback=lambda: {},
    )
    for t, w in (res.get("topics") or {}).items():
        if t in TOPIC_IDS and isinstance(w, (int, float)):
            base["topics"][t] = max(base["topics"].get(t, 0.0), min(1.0, float(w)))
    base["entities"] = (res.get("entities") or base["entities"])[:8]
    base["tone"] = res.get("tone") or base["tone"]
    base["avoid"] = [t for t in res.get("avoid", []) if t in TOPIC_IDS]
    base["summary"] = res.get("summary") or base["summary"]
    return base
