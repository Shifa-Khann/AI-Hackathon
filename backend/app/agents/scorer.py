"""Scoring & selection: pick the smallest set of stories that fills the reader's time budget. Pure, no I/O."""
from __future__ import annotations

import math
from datetime import datetime, timezone

SOURCE_QUALITY = {  # default 0.75
    "Karachi Ledger": 0.85, "Indus Business Review": 0.85, "The Meridian": 0.9, "Harbor Science": 0.9,
    "Circuit Wire": 0.8, "Pitchside": 0.8,
}
W_REL, W_REC, W_SRC, W_NOV = 0.55, 0.20, 0.15, 0.10
WPM = 230
MIN_ITEMS, MAX_ITEMS = 3, 14
MIN_RELEVANCE = 0.2
MAX_PER_TOPIC = 3


def read_minutes(article: dict) -> int:
    return max(1, min(3, round(article.get("word_count", 600) / WPM * 0.6)))  # skim + decide; originals are a click away


def relevance(profile: dict, a: dict) -> float:
    w = profile["topics"]
    vals = [w.get(t, 0.0) for t in a["topics"]]
    if not vals:
        return 0.0
    base = max(vals) * 0.75 + (sum(vals) / len(vals)) * 0.25
    ents = {e.lower() for e in profile.get("entities", [])}
    bonus = 0.12 if ents and any(e.lower() in ents for e in a.get("entities", [])) else 0.0
    return min(1.0, base + bonus)


def recency(a: dict, now: datetime) -> float:
    try:
        pub = datetime.fromisoformat(a["published_at"])
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        hours = max(0.0, (now - pub).total_seconds() / 3600)
    except Exception:
        hours = 48.0
    return math.exp(-hours / 48)


def base_score(profile: dict, a: dict, now: datetime) -> float:
    return (
        W_REL * relevance(profile, a)
        + W_REC * recency(a, now)
        + W_SRC * SOURCE_QUALITY.get(a.get("source", ""), 0.75)
        + W_NOV * 1.0
    )


def pick_blind_spot(profile: dict, pool: list[dict], now: datetime, exclude: set[int]) -> dict | None:
    """One quality story from a topic the reader under-indexes on."""
    if profile.get("blind_appetite", 0.5) < 0.1:
        return None
    avoid = set(profile.get("avoid", []))
    cands = [
        a for a in pool
        if a["id"] not in exclude and not (set(a["topics"]) & avoid)
        and max(profile["topics"].get(t, 0.0) for t in a["topics"]) <= 0.2
    ]
    if not cands:
        return None
    cands.sort(key=lambda a: (-(SOURCE_QUALITY.get(a.get("source", ""), 0.75) + recency(a, now)), a["id"]))
    return cands[0]


def select(
    profile: dict,
    pool: list[dict],
    budget_min: int,
    now: datetime | None = None,
    exclude_ids: set[int] | None = None,
) -> dict:
    """Return {'picks': [article...], 'blind': article|None, 'total_min': int}. Articles get 'score' and 'read_min'."""
    now = now or datetime.now(timezone.utc)
    exclude = set(exclude_ids or ())
    avoid = set(profile.get("avoid", []))
    cands = [a for a in pool if a["id"] not in exclude and not (set(a["topics"]) & avoid)]
    for a in cands:
        a["score"] = base_score(profile, a, now)
        a["read_min"] = read_minutes(a)
        a["relevance"] = relevance(profile, a)

    relevant = [a for a in cands if a["relevance"] >= MIN_RELEVANCE]
    picks: list[dict] = []
    topic_count: dict[str, int] = {}
    source_count: dict[str, int] = {}
    total = 0
    remaining = sorted(relevant, key=lambda a: a["id"])

    def adjusted(a: dict) -> float:
        pen = 0.10 * max(0, topic_count.get(a["topics"][0], 0) - 1)
        pen += 0.06 * max(0, source_count.get(a.get("source", ""), 0) - 1)
        return a["score"] - pen

    while remaining and len(picks) < MAX_ITEMS:
        if total >= budget_min * 0.9 and len(picks) >= MIN_ITEMS:
            break
        remaining.sort(key=lambda a: (-adjusted(a), a["id"]))
        chosen = None
        for a in remaining:
            if topic_count.get(a["topics"][0], 0) >= MAX_PER_TOPIC:
                continue
            if total + a["read_min"] > budget_min * 1.15 and len(picks) >= MIN_ITEMS:
                continue
            chosen = a
            break
        if not chosen:
            break
        remaining.remove(chosen)
        picks.append(chosen)
        total += chosen["read_min"]
        topic_count[chosen["topics"][0]] = topic_count.get(chosen["topics"][0], 0) + 1
        source_count[chosen.get("source", "")] = source_count.get(chosen.get("source", ""), 0) + 1

    if len(picks) < MIN_ITEMS:  # thin pool: top up with best remaining of anything
        extra = sorted([a for a in cands if a not in picks], key=lambda a: (-a["score"], a["id"]))
        for a in extra[: MIN_ITEMS - len(picks)]:
            picks.append(a)
            total += a["read_min"]

    picks.sort(key=lambda a: (-a["score"], a["id"]))
    blind = pick_blind_spot(profile, cands, now, {a["id"] for a in picks})
    if blind:
        total += blind["read_min"]
    return {"picks": picks, "blind": blind, "total_min": total}
