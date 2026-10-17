# PRD — The Fold

**Tagline:** *A paper that ends.*
**Event:** NaSCon'26 hackathon — "Build a personal morning paper". Build window: 8 hours.
**Owner:** Sana

---

## 1. Problem

News is scattered across dozens of sites, apps and newsletters. Social media unified its feed; news never did.
People hop from link to link and still can't name three things they learned.

## 2. Insight / positioning

Every competitor will ship "RSS + AI summaries + infinite list". The Fold wins on three things judges can *see*:

1. **It ends.** A finite edition sized to the reader's time budget, closing on an "End of paper — you're done" page. The opposite of a feed.
2. **It explains itself.** Every story has a *Why this?* line tracing back to the reader's own words and behaviour.
3. **It visibly learns.** Skip two stories, regenerate, and the paper changes in front of the judges. The interest graph grows.

## 3. Users

- **Primary persona — "Ayesha", 24, CS grad in Islamabad.** Follows AI, startups, cricket. Reads on phone at breakfast, 10 min.
- **Demo persona 2 — "Bilal", 41, finance manager in Karachi.** Markets, energy, Pakistani economy, F1. Wants 20 min and a PDF to print.

The two personas receive different papers from **the same news pool** — this is the core demo.

## 4. Goals & success metrics (for the demo)

| Goal | Metric in demo |
|---|---|
| Onboarding is fast | < 60 s from landing to first paper |
| Personal | Two personas share < 30 % of stories |
| Finite | Edition read time within ±15 % of chosen budget |
| Learns | After 2 skips + regenerate, ≥ 2 stories change and skipped topic weight drops |
| Explainable | 100 % of stories have a non-empty *Why this?* |
| Robust | Full demo runs with `MOCK_LLM=1` and no internet |

## 5. Scope

### 5.1 Must ship (Tier 1 — required by the brief)

**F1 Onboarding (≈60 s).** Three steps on one page with a progress line:
1. Open question: *"What did you read recently that stuck with you?"* (free text, optional).
2. Topic chips (multi-select, ~24 chips) plus a "something else" text field.
3. Reading budget: 5 / 12 / 20 minutes. Optional: name, city, language (English/Urdu headlines).
An LLM turns answers into a weighted interest profile (JSON: `topics{name:weight}`, `entities[]`, `tone`, `avoid[]`).

**F2 Ingest.** RSS feeds (list in `backend/app/agents/feeds.py`) + Hacker News API. Dedupe by URL and title similarity.
Tag each article with topics/entities (LLM, keyword fallback). Store in SQLite. Offline fallback: `seed/articles.json`.

**F3 Scoring & selection.** `score = 0.55·relevance + 0.20·recency + 0.15·source_quality + 0.10·novelty`, minus a diversity
penalty for repeated topic/source. Greedy fill until estimated read time (words ÷ 230 wpm, capped per story) meets the budget.

**F4 Edition writer.** For each chosen article the LLM writes: headline (≤ 12 words), 2-sentence summary, *Why this?* (1 sentence),
and for the edition: editor's note, layout plan (hero, columns, sections), 3 quiz questions, "One thing to do today".

**F5 Web reader.** Newspaper layout: masthead with edition number/date/weather-free tagline, hero story, 2–3 columns, section rules.
Each story: read original (opens source, logs click), Skip (fades + logs), Why this? toggle. Reading progress bar. Ends on the
"End of paper" page with quiz. Archive page lists previous editions.

**F6 PDF.** Same edition rendered via Jinja → WeasyPrint: broadsheet-inspired A4/A3, masthead, rules, columns, drop cap, QR code
per story linking to the original, closing "End of paper" panel. Downloaded via `GET /api/editions/{id}/pdf`.

**F7 Learning loop.** Events (`open`, `skip`, `dwell`, `quiz_correct`, `quiz_wrong`, `more_challenge`, `less_challenge`) update topic
weights with decay (×0.97 per edition) and clamping. Next edition reflects it. Profile page shows weights before/after.

### 5.2 Differentiators (Tier 2 — pick at least 4)

- **D1 Finite edition** — End-of-paper page (web + PDF). *(cheap, do it)*
- **D2 Why this?** — on every story. *(cheap, do it)*
- **D3 Blind Spot** — one story from a topic the reader under-indexes on, labelled, with "more/less challenge" buttons.
- **D4 Interest graph** — D3 force graph of topics sized by weight; click a node to boost/mute.
- **D5 Recall quiz** — 3 questions at the end; results feed learning. Directly answers "can't name three things they learned".
- **D6 Dynamic layout** — LLM layout plan changes hero/columns by edition (busy vs light day).

### 5.3 Polish (Tier 3)

- One thing to do today box. Urdu headline toggle. Two pre-generated demo personas. README + architecture diagram + Loom.

### 5.4 Out of scope

Auth/accounts (single cookie `fold_uid`), email delivery, real cron (button + optional APScheduler), mobile apps, payments,
full-text scraping of paywalled sites.

## 6. User flows

1. **First run:** Landing → *Make my paper* → onboarding (3 steps) → "Setting your type…" loader (shows pipeline steps live) → Edition No. 1.
2. **Read:** scroll through → open/skip/why → End of paper → quiz → "See you tomorrow".
3. **Learn:** Profile → graph shows changed weights → *Print tomorrow's edition now* → Edition No. 2 differs.
4. **Archive:** Archive → any past edition → web view or PDF.

## 7. Non-functional

- p95 edition generation < 25 s with real LLM, < 2 s in mock mode.
- Works on a 1280px laptop for demo; acceptable on 390px mobile.
- All text sourced from articles is summarised, never reproduced in full; every story links to the original.

## 8. Risks

| Risk | Mitigation |
|---|---|
| Feeds slow / blocked at venue | Seed article pool, `MOCK_LLM=1`, pre-generated demo editions |
| WeasyPrint system deps | Dockerfile + documented `apt` line; fallback route returns print-ready HTML |
| LLM JSON breaks | `llm.complete_json` with schema check + 1 retry + deterministic fallback |
| Running out of time | Strict tiering, cut list in TASKS.md, commit every task |

## 9. Submission checklist

- [ ] Public GitHub repo, steady commit history
- [ ] Loom ≤ 5 min following `docs/DEMO_SCRIPT.md`
- [ ] Architecture diagram (`docs/ARCHITECTURE.md` → export PNG to `docs/architecture.png`)
- [ ] README with setup, screenshots, features, architecture image
