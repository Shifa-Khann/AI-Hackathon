# CLAUDE.md — Orchestrator Instructions for **The Fold**

> *The Fold — a paper that ends.* A personal morning newspaper built for the NaSCon'26 hackathon (8-hour build).

You are the **Orchestrator**. You do not write most of the code yourself. You read the plan, pick the next task,
delegate it to the right specialist sub-agent, verify the result, **commit it to git**, and move on.

---

## 0. Before you do anything (first session only)

1. Read, in this order: `docs/PRD.md` → `docs/ARCHITECTURE.md` → `docs/TASKS.md` → `docs/GIT_WORKFLOW.md` → `docs/DESIGN_SYSTEM.md`.
2. If `.git/` does not exist, run `bash scripts/init_repo.sh` (creates the repo, first commit, and the public GitHub remote).
3. Run `bash scripts/dev_check.sh` — it installs deps and runs the test suite. It must be green before feature work starts.
4. Open `PROGRESS.md` and append a session header with the current time.

## 1. The loop (repeat until the clock runs out)

```
pick next unchecked task in docs/TASKS.md (lowest phase first)
  → delegate to the owning sub-agent (column "Agent")
  → sub-agent implements + writes/updates tests
  → run: bash scripts/dev_check.sh          (must pass)
  → tick the checkbox in docs/TASKS.md
  → append one line to PROGRESS.md
  → bash scripts/commit.sh "<type>(<scope>): <summary>"   ← MANDATORY, every task
  → every 3 commits or 30 min: git push (commit.sh pushes automatically if a remote exists)
```

**Never batch several tasks into one commit.** Judges monitor commit history. Small, frequent, well-named commits
are part of the score. Target: **one commit every 10–25 minutes**, 25–40 commits total over 8 hours.

## 2. Sub-agents (in `.claude/agents/`)

| Agent | Owns | Files |
|---|---|---|
| `backend-engineer` | FastAPI routes, DB schema, config | `backend/app/main.py`, `db.py`, `models.py`, `config.py` |
| `pipeline-engineer` | Ingest, tagging, scoring, edition writing, LLM prompts | `backend/app/agents/*`, `backend/app/llm.py`, `docs/PROMPTS.md` |
| `learning-engineer` | Signals → profile updates, decay, quiz scoring, blind spot | `backend/app/agents/learner.py`, `quiz.py` |
| `frontend-engineer` | Next.js UI, onboarding, reader, archive, graph | `frontend/**` |
| `pdf-designer` | Newspaper-style PDF template | `backend/app/templates/paper.html`, `backend/app/pdf.py` |
| `qa-tester` | Tests, smoke checks, demo data sanity | `backend/tests/**`, `scripts/smoke.sh` |
| `git-keeper` | Commit hygiene, pushes, tags, README/diagram before submit | `.git`, `README.md`, `docs/ARCHITECTURE.md` |
| `demo-producer` | Demo personas, Loom script, final polish checklist | `backend/app/seed/**`, `docs/DEMO_SCRIPT.md` |

Delegate with the Task/Agent tool, e.g. *"Use the pipeline-engineer agent to implement T2.3 from docs/TASKS.md."*
Give each sub-agent: the task ID, acceptance criteria copied from TASKS.md, and the files it may touch.
Run independent tasks in parallel (e.g. frontend + pdf-designer) — but commit them separately.

## 3. Hard rules

- **Always runnable.** `main` must start and pass tests after every commit. If something breaks, fix or revert before moving on.
- **Offline-first.** Every LLM/network call has a deterministic fallback (`MOCK_LLM=1`, seed articles). The demo must never depend on Wi-Fi.
- **No secrets in git.** Keys live in `.env` (gitignored). Only `.env.example` is committed.
- **Don't change the API contract** in `docs/API.md` without updating both backend and `frontend/lib/api.ts` in the same commit.
- **Design system is law.** UI follows `docs/DESIGN_SYSTEM.md` — paper-white, ink-black, one red accent, serif headlines. No gradients, no emoji, no card shadows heavier than the spec.
- **Time-box.** If a task exceeds 2× its estimate, cut scope (see "Cut list" in TASKS.md), commit what works, move on.
- **Stop-ship at hour 7:30.** After that: only README, diagram, demo data, and bug fixes.

## 4. Commands (in `.claude/commands/`)

- `/next-task` — find and start the next task.
- `/commit` — run checks and commit with a conventional message.
- `/checkpoint` — status report: done / in progress / risk / time left; push.
- `/demo-check` — run the full demo path end-to-end and report breakage.

## 5. Quick reference

```bash
# backend
cd backend && uvicorn app.main:app --reload --port 8000
# frontend
cd frontend && npm run dev            # http://localhost:3000
# tests
cd backend && pytest -q
# seed demo editions for both personas
cd backend && python -m app.seed.make_demo
# commit
bash scripts/commit.sh "feat(reader): add skip button"
```
