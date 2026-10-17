# TASKS — 8-hour build plan

The scaffold in this repo already contains a **working baseline** (mock LLM, seed articles, reader, PDF, tests).
Tasks below are about verifying, wiring real data, and adding the wow features. Tick each box and **commit after each task**.

Legend: `BE` backend-engineer · `PL` pipeline-engineer · `LE` learning-engineer · `FE` frontend-engineer · `PDF` pdf-designer · `QA` qa-tester · `GIT` git-keeper · `DEMO` demo-producer

## Phase 0 — Setup (0:00–0:30)

| ✓ | ID | Task | Agent | Acceptance | Commit message |
|---|---|---|---|---|---|
| [x] | T0.1 | Run `scripts/init_repo.sh`, create public GitHub repo, push scaffold | GIT | Remote exists, first commit pushed | `chore: scaffold The Fold` |
| [x] | T0.2 | Copy `.env.example` → `.env`, add `ANTHROPIC_API_KEY` | BE | `MOCK_LLM=0` health check shows `llm: claude` | *(no commit — .env is ignored)* |
| [x] | T0.3 | `scripts/dev_check.sh` green; backend + frontend boot | QA | pytest passes, :3000 renders landing | `chore: verify dev environment` |

## Phase 1 — Core pipeline real data (0:30–2:30)

| ✓ | ID | Task | Agent | Acceptance | Commit message |
|---|---|---|---|---|---|
| [x] | T1.1 | Live RSS ingest via feedparser; HN top stories; dedupe | PL | `POST /api/ingest` adds ≥ 80 articles; re-run adds 0 dupes | `feat(ingest): live RSS and Hacker News ingest` |
| [x] | T1.2 | LLM tagging in batches of 15 (Haiku), keyword fallback | PL | Each article has ≥ 1 topic from taxonomy | `feat(tagger): batch LLM topic tagging` |
| [x] | T1.3 | Profiler: real LLM extraction from onboarding answers | PL | Free-text "I read about Gaza ceasefire and Nvidia earnings" → geopolitics + ai/markets weights | `feat(profiler): LLM interest extraction` |
| [x] | T1.4 | Editor: real LLM headlines/dek/why/note/quiz in one JSON call | PL | Schema-valid output; fallback on failure | `feat(editor): LLM edition writer` |
| [x] | T1.5 | Tests for ingest dedupe + editor schema | QA | New tests pass | `test: ingest and editor coverage` |

## Phase 2 — Reader & PDF polish (2:30–4:30)

| ✓ | ID | Task | Agent | Acceptance | Commit message |
|---|---|---|---|---|---|
| [x] | T2.1 | Onboarding polish: chip animation, progress line, loader showing pipeline steps | FE | < 60 s flow, no layout jank | `feat(onboarding): polished 3-step flow` |
| [x] | T2.2 | Reader: layout plan drives hero/column count; reading progress bar | FE | Two editions with different plans render differently | `feat(reader): plan-driven newspaper layout` |
| [x] | T2.3 | Skip/open/dwell tracking (IntersectionObserver for dwell) | FE | Events visible in `GET /api/events/recent` | `feat(reader): engagement signals` |
| [x] | T2.4 | PDF: masthead, 3 columns, drop cap, QR per story, end panel | PDF | PDF opens, 2–4 pages, no overflow | `feat(pdf): broadsheet edition PDF` |
| [x] | T2.5 | Archive page with edition thumbnails | FE | Past editions listed newest-first | `feat(archive): edition archive` |

## Phase 3 — Wow features (4:30–6:45)

| ✓ | ID | Task | Agent | Acceptance | Commit message |
|---|---|---|---|---|---|
| [x] | T3.1 | Learning loop verified: skip 2 → regenerate → ≥ 2 stories change | LE | `tests/test_learner.py::test_skip_changes_next_edition` passes | `feat(learning): signal-weighted profile updates` |
| [x] | T3.2 | Blind Spot story + more/less challenge | LE | Exactly 1 blind spot per edition, labelled | `feat(learning): blind spot column` |
| [x] | T3.3 | Recall quiz at End of paper, answers posted as events | FE | Score shown; weights move | `feat(quiz): end-of-paper recall quiz` |
| [x] | T3.4 | Interest graph (D3 force) with before/after toggle, click to boost/mute | FE | Nodes resize after events | `feat(profile): interactive interest graph` |
| [x] | T3.5 | "Why this?" references onboarding quote or recent behaviour | PL | Every item `why` non-empty, cites a reason | `feat(editor): explainable why-this traces` |

## Phase 4 — Polish & submit (6:45–8:00)

| ✓ | ID | Task | Agent | Acceptance | Commit message |
|---|---|---|---|---|---|
| [x] | T4.1 | Two demo personas pre-generated (`python -m app.seed.make_demo`) | DEMO | Overlap < 30 % | `chore(demo): seed personas Ayesha and Bilal` |
| [x] | T4.2 | Urdu headline toggle (LLM translate, cached) | PL | Toggle switches headlines | `feat(i18n): Urdu headline toggle` |
| [x] | T4.3 | README with screenshots + architecture PNG | GIT | Renders well on GitHub | `docs: README and architecture diagram` |
| [x] | T4.4 | `/demo-check` full run, fix bugs | QA | No console errors on demo path | `fix: demo path polish` |
| [ ] | T4.5 | Tag release, push, record Loom | GIT/DEMO | `git tag v1.0-nascon` pushed | `chore: release v1.0` |

## Cut list (in order — cut from the top when behind)

1. Urdu toggle (T4.2)
2. Graph click-to-boost (keep read-only graph)
3. Dynamic layout plan (use fixed hero + 3 cols)
4. Live RSS (stay on seed pool + HN only)
5. Dwell tracking (keep open/skip)

**Never cut:** onboarding, reader, PDF, archive, learning visible change, End of paper, commits.
