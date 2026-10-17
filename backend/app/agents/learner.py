"""Learning loop: engagement signals -> profile weights. Pure functions, no I/O."""
from __future__ import annotations

import copy

from ..taxonomy import label

DECAY = 0.97
MIN_W, MAX_W, PICKED_FLOOR, NEW_TOPIC_W = 0.02, 1.0, 0.10, 0.25

# event type -> delta applied to every topic of the article
SIGNALS: dict[str, float] = {
    "open": 0.12,
    "skip": -0.18,
    "unskip": 0.18,
    "quiz_correct": 0.05,
    "quiz_wrong": 0.02,
}
DWELL_LONG, DWELL_SHORT = 0.08, 0.03
CHALLENGE_STEP = 0.15


def _clamp(profile: dict, topic: str, value: float) -> float:
    floor = PICKED_FLOOR if topic in profile.get("picked", []) else MIN_W
    return round(max(floor, min(MAX_W, value)), 4)


def apply_event(profile: dict, etype: str, topics: list[str], value: float | None = None) -> tuple[dict, dict]:
    """Return (new_profile, delta) where delta maps topic -> change (and 'blind_appetite')."""
    p = copy.deepcopy(profile)
    delta: dict[str, float] = {}
    if etype in ("more_challenge", "less_challenge"):
        step = CHALLENGE_STEP if etype == "more_challenge" else -CHALLENGE_STEP
        old = p.get("blind_appetite", 0.5)
        p["blind_appetite"] = round(max(0.0, min(1.0, old + step)), 3)
        return p, {"blind_appetite": round(p["blind_appetite"] - old, 3)}
    if etype == "dwell":
        secs = value or 0
        d = DWELL_LONG if secs >= 30 else DWELL_SHORT if secs >= 8 else 0.0
    else:
        d = SIGNALS.get(etype, 0.0)
    if d == 0.0:
        return p, delta
    for t in topics:
        old = p["topics"].get(t)
        if old is None:
            if d < 0:
                continue
            old = NEW_TOPIC_W - d  # new topics enter at NEW_TOPIC_W after the first positive signal
        new = _clamp(p, t, old + d)
        p["topics"][t] = new
        delta[t] = round(new - (profile["topics"].get(t, old)), 4)
    return p, delta


def decay(profile: dict) -> dict:
    """Applied once per edition: slowly forget, but never below floors."""
    p = copy.deepcopy(profile)
    for t, w in p["topics"].items():
        p["topics"][t] = _clamp(p, t, w * DECAY)
    return p


def describe_changes(old: dict | None, new: dict, min_change: float = 0.05) -> str:
    """Human sentence about how the profile shifted since the last edition."""
    if not old:
        return ""
    diffs = [(t, new["topics"].get(t, 0) - old.get(t, 0)) for t in new["topics"]]
    ups = sorted([d for d in diffs if d[1] >= min_change], key=lambda x: -x[1])[:2]
    downs = sorted([d for d in diffs if d[1] <= -min_change], key=lambda x: x[1])[:2]
    parts = []
    if ups:
        parts.append("more " + " and ".join(label(t) for t, _ in ups))
    if downs:
        parts.append("less " + " and ".join(label(t) for t, _ in downs))
    return ("Based on what you read and skipped, today has " + ", ".join(parts) + ".") if parts else ""
