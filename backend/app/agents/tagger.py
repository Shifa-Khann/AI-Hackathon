"""Tagger: assign topics + entities to articles. Keyword fallback; batched LLM when live."""
from __future__ import annotations

import re

from .. import config, llm
from ..taxonomy import TOPICS, TOPIC_IDS

KNOWN_ENTITIES = [
    "Nvidia", "OpenAI", "Anthropic", "Google", "Microsoft", "Apple", "Meta", "Tesla", "Amazon",
    "IMF", "SBP", "PSX", "OPEC", "NASA", "Karachi", "Lahore", "Islamabad", "Pakistan",
]


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def keyword_topics(text: str, limit: int = 3) -> list[str]:
    toks = _tokens(text)
    scored = []
    for t in TOPICS:
        hits = sum(1 for k in t["keywords"] if k in toks)
        if hits:
            scored.append((hits, t["id"]))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [tid for _, tid in scored[:limit]]


def extract_entities(text: str) -> list[str]:
    low = text.lower()
    return [e for e in KNOWN_ENTITIES if e.lower() in low][:4]


def tag_articles(articles: list[dict]) -> list[dict]:
    """Each article dict gets `topics` and `entities`. Uses the LLM in batches of 15 when live."""
    for a in articles:
        text = f"{a['title']} {a.get('summary', '')}"
        a["topics"] = keyword_topics(text) or ["culture"]
        a["entities"] = extract_entities(text)
    if llm.is_mock():
        return articles
    for i in range(0, len(articles), 15):
        batch = articles[i : i + 15]
        payload = "\n".join(f"{j}. {a['title']} — {a.get('summary', '')[:200]}" for j, a in enumerate(batch))
        res = llm.complete_json(
            f"Tag each article with 1-3 topic ids from {TOPIC_IDS} and up to 4 named entities. "
            'Return {"items":[{"i":0,"topics":["ai"],"entities":["OpenAI"]}]}.',
            payload,
            fallback=lambda: {"items": []},
            model=config.fast_model(),
        )
        for it in res.get("items", []):
            try:
                a = batch[int(it["i"])]
            except (KeyError, ValueError, IndexError):
                continue
            topics = [t for t in it.get("topics", []) if t in TOPIC_IDS]
            if topics:
                a["topics"] = topics[:3]
            a["entities"] = [str(e) for e in it.get("entities", [])][:4] or a["entities"]
    return articles
