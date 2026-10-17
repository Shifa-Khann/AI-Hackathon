"""Thin LLM wrapper. Every call has a deterministic fallback so the demo never needs the network."""
from __future__ import annotations

import json
import re
from typing import Any, Callable

from . import config


def is_mock() -> bool:
    return config.mock_llm()


def _extract_json(text: str) -> Any:
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"(\{.*\}|\[.*\])", text, flags=re.DOTALL)
        if m:
            return json.loads(m.group(1))
        raise


def complete_json(
    system: str,
    user: str,
    fallback: Callable[[], Any],
    *,
    model: str | None = None,
    validate: Callable[[Any], bool] | None = None,
    max_tokens: int = 4000,
) -> Any:
    """Return parsed JSON from Claude, or `fallback()` in mock mode / on any failure (one retry first)."""
    if is_mock():
        return fallback()
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=config.api_key(), timeout=45)
    except Exception:
        return fallback()
    for _ in range(2):
        try:
            msg = client.messages.create(
                model=model or config.smart_model(),
                max_tokens=max_tokens,
                system=system + "\nRespond with valid JSON only. No prose, no code fences.",
                messages=[{"role": "user", "content": user}],
            )
            data = _extract_json("".join(b.text for b in msg.content if getattr(b, "type", "") == "text"))
            if validate is None or validate(data):
                return data
        except Exception:
            continue
    return fallback()
