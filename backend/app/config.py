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


def api_key() -> str:
    return os.environ.get("ANTHROPIC_API_KEY", "").strip()


def mock_llm() -> bool:
    return os.environ.get("MOCK_LLM", "1") == "1" or not api_key()


def fast_model() -> str:
    return os.environ.get("FAST_MODEL", "claude-haiku-4-5")


def smart_model() -> str:
    return os.environ.get("SMART_MODEL", "claude-sonnet-4-5")


def live_ingest() -> bool:
    return os.environ.get("LIVE_INGEST", "0") == "1"


def db_path() -> Path:
    p = Path(os.environ.get("DB_PATH", "backend/data/fold.db"))
    return p if p.is_absolute() else ROOT / p


def cors_origins() -> list[str]:
    return [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
