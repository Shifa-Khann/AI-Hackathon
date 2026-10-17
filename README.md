# The Fold — *a paper that ends.*

A personal morning newspaper. It learns what you care about, gathers the articles that matter from across the web,
and prints **one finite edition** — on the web and as a broadsheet-style PDF. Built for NaSCon'26 (8-hour hackathon).

## Why it's different

- **It ends.** No infinite scroll. The edition is sized to your reading budget and closes on *"That's the paper."*
- **It explains itself.** Every story has a *Why this?* tracing back to your own words and behaviour.
- **It visibly learns.** Skips, opens, reading time and a daily recall quiz reshape tomorrow's paper. See it in the interest graph.
- **Blind Spot.** One story a day from outside your bubble — and you control how much challenge you want.

## Quick start

```bash
cp .env.example .env                 # MOCK_LLM=1 works with no API key
# backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed.make_demo         # optional: personas Ayesha + Bilal
uvicorn app.main:app --reload --port 8000
# frontend (new terminal)
cd frontend && npm install && npm run dev      # http://localhost:3000
```

PDF export uses WeasyPrint. On Debian/Ubuntu: `sudo apt install libpango-1.0-0 libpangoft2-1.0-0`. Without it the app serves a print-ready HTML page instead.

Real LLM: set `ANTHROPIC_API_KEY` and `MOCK_LLM=0`. Live feeds: `LIVE_INGEST=1`.

## Tests

```bash
cd backend && pytest -q
```

## Project layout

```
CLAUDE.md            orchestrator instructions (start here if vibe-coding with agents)
.claude/agents/      8 specialist sub-agents      .claude/commands/  slash commands
docs/                PRD, architecture, tasks, API, design system, prompts, git workflow, demo script
backend/app/         FastAPI + pipeline agents (ingest, tagger, profiler, scorer, editor, learner, quiz, pdf)
backend/tests/       pytest suite
frontend/            Next.js 14 reader, onboarding, archive, interest graph
scripts/             init_repo.sh, commit.sh, dev_check.sh, smoke.sh
```

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) (Mermaid diagrams).

## Building this with an AI agent team

Open the folder in Claude Code and say: **"Read CLAUDE.md and start the loop."** The orchestrator delegates to the sub-agents and commits after every task
(`scripts/commit.sh`) so the GitHub history shows steady progress.

## What's in the scaffold vs. what's left to build

**Working out of the box (tested, `MOCK_LLM=1`, offline):** onboarding → profile, scoring/selection to a time budget, edition writer
(headlines, deks, *Why this?*, editor's note, quiz, layout plan), blind spot, learning loop with decay, web reader, archive, interest graph,
PDF (WeasyPrint) with QR codes, 30 backend tests, `scripts/smoke.sh`.

**Written but not exercised without keys/network:** the Claude-backed paths (`MOCK_LLM=0`) and live ingest (`LIVE_INGEST=1`: RSS + Hacker News).
Run them once early (tasks T0.2, T1.1–T1.4) and fix anything the real data shakes loose.

**Not built yet (see `docs/TASKS.md`):** Urdu headline toggle (DB column exists), dwell-driven demo polish, README screenshots, architecture PNG export.

**Sample content:** the offline article pool (`backend/app/seed/articles.json`) is invented, from fictional outlets, with `example.com` links.
Live ingest brings real articles.
