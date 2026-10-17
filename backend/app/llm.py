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


def provider_name() -> str:
    return config.llm_provider()


def _call_gemini_native(
    api_key: str,
    model: str,
    system: str,
    user: str,
) -> str:
    import httpx

    m = model.replace("models/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
    prompt = f"{system}\n\nIMPORTANT: Respond with valid JSON only. Do not wrap in markdown or prose.\n\nInput:\n{user}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.3,
        },
    }
    r = httpx.post(url, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    candidates = data.get("candidates", [])
    if candidates and "content" in candidates[0]:
        return candidates[0]["content"]["parts"][0]["text"]
    return "{}"


def _call_openai_compatible(
    endpoint: str,
    api_key: str,
    model: str,
    system: str,
    user: str,
    max_tokens: int = 4000,
) -> str:
    import httpx

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system + "\nRespond with valid JSON only. No prose, no markdown code fences."},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
    }
    r = httpx.post(endpoint, headers=headers, json=payload, timeout=45)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def complete_json(
    system: str,
    user: str,
    fallback: Callable[[], Any],
    *,
    model: str | None = None,
    validate: Callable[[Any], bool] | None = None,
    max_tokens: int = 4000,
) -> Any:
    """Return parsed JSON from Gemini, Grok, OpenAI, or Claude, or `fallback()` in mock mode / on failure."""
    provider = config.llm_provider()
    if provider == "mock":
        return fallback()

    chosen_model = model or config.smart_model()

    for _ in range(2):
        try:
            raw_text = ""
            if provider == "gemini":
                raw_text = _call_gemini_native(
                    config.gemini_key(),
                    chosen_model,
                    system,
                    user,
                )
            elif provider == "grok":
                raw_text = _call_openai_compatible(
                    "https://api.x.ai/v1/chat/completions",
                    config.grok_key(),
                    chosen_model,
                    system,
                    user,
                    max_tokens=max_tokens,
                )
            elif provider == "openai":
                raw_text = _call_openai_compatible(
                    "https://api.openai.com/v1/chat/completions",
                    config.openai_key(),
                    chosen_model,
                    system,
                    user,
                    max_tokens=max_tokens,
                )
            elif provider == "claude":
                import anthropic

                client = anthropic.Anthropic(api_key=config.anthropic_key(), timeout=45)
                msg = client.messages.create(
                    model=chosen_model,
                    max_tokens=max_tokens,
                    system=system + "\nRespond with valid JSON only. No prose, no code fences.",
                    messages=[{"role": "user", "content": user}],
                )
                raw_text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")

            if raw_text:
                data = _extract_json(raw_text)
                if validate is None or validate(data):
                    return data
        except Exception:
            continue

    return fallback()

