"""Runtime configuration. Values are read lazily so tests can override os.environ."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root


def _load_env() -> None:
    for p in (ROOT / ".env", ROOT / "backend" / ".env"):
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.split(" #")[0].strip())


_load_env()


def gemini_key() -> str:
    return (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()


def grok_key() -> str:
    return (os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY") or "").strip()


def openai_key() -> str:
    return os.environ.get("OPENAI_API_KEY", "").strip()


def anthropic_key() -> str:
    return os.environ.get("ANTHROPIC_API_KEY", "").strip()


def api_key() -> str:
    return gemini_key() or grok_key() or openai_key() or anthropic_key()


def llm_provider() -> str:
    if mock_llm():
        return "mock"
    if gemini_key():
        return "gemini"
    if grok_key():
        return "grok"
    if openai_key():
        return "openai"
    if anthropic_key():
        return "claude"
    return "mock"


def mock_llm() -> bool:
    return os.environ.get("MOCK_LLM", "1") == "1" or not api_key()


def fast_model() -> str:
    p = llm_provider()
    default = {
        "gemini": "gemini-2.5-flash",
        "grok": "grok-beta",
        "openai": "gpt-4o-mini",
        "claude": "claude-haiku-4-5",
    }.get(p, "claude-haiku-4-5")
    return os.environ.get("FAST_MODEL", default)


def smart_model() -> str:
    p = llm_provider()
    default = {
        "gemini": "gemini-2.5-flash",
        "grok": "grok-beta",
        "openai": "gpt-4o",
        "claude": "claude-sonnet-4-5",
    }.get(p, "claude-sonnet-4-5")
    return os.environ.get("SMART_MODEL", default)




def live_ingest() -> bool:
    return os.environ.get("LIVE_INGEST", "0") == "1"


def db_path() -> Path:
    p = Path(os.environ.get("DB_PATH", "backend/data/fold.db"))
    return p if p.is_absolute() else ROOT / p


def cors_origins() -> list[str]:
    return [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
