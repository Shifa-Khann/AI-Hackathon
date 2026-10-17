# API contract

Base URL: `http://localhost:8000`. User identified by `X-User-Id` header (frontend stores it in `localStorage` as `fold_uid`).
Changing this contract requires updating `frontend/lib/api.ts` in the same commit.

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/api/health` | — | `{ok, llm: "claude"|"mock", articles: n}` |
| GET | `/api/topics` | — | `{topics: [{id,label}]}` — onboarding chips |
| POST | `/api/onboard` | `{name?, city?, recent_read?, topics: string[], other?, budget_min: 5|12|20, lang?: "en"|"ur"}` | `{user_id, profile}` |
| GET | `/api/profile` | — | `{user, profile, history: [{created_at, topics}]}` |
| POST | `/api/profile/adjust` | `{topic, delta}` | `{profile}` — graph boost/mute |
| POST | `/api/ingest` | — | `{added, total}` |
| POST | `/api/editions/generate` | — | `Edition` |
| GET | `/api/editions` | — | `{editions: [{id, number, date, story_count, read_min, lead_headline}]}` |
| GET | `/api/editions/latest` | — | `Edition` or 404 |
| GET | `/api/editions/{id}` | — | `Edition` |
| GET | `/api/editions/{id}/pdf` | — | `application/pdf` (or `text/html` print fallback) |
| POST | `/api/events` | `{edition_id?, article_id?, type, value?}` | `{ok, profile_delta}` |
| GET | `/api/events/recent` | — | `{events: [...]}` |

`type` ∈ `open | skip | unskip | dwell | quiz_correct | quiz_wrong | more_challenge | less_challenge`

### Edition

```json
{
  "id": 3, "number": 3, "date": "2026-10-17",
  "editor_note": "Today I leaned into AI policy because you skipped two markets stories yesterday…",
  "todo": "Pakistan vs England 2nd Test starts 10:00 PKT — first session worth catching.",
  "read_min": 11,
  "plan": {"hero": 41, "columns": 3, "sections": ["Front", "Technology", "Business", "Blind Spot"]},
  "items": [{
    "id": 12, "article_id": 41, "slot": 0, "section": "Front",
    "headline": "…", "dek": "…", "why": "You told us …",
    "source": "Dawn", "url": "https://…", "image_url": null,
    "topics": ["ai", "policy"], "read_min": 3, "is_blind_spot": false
  }],
  "quiz": [{"q": "…", "options": ["a","b","c"], "answer": 1, "article_id": 41}]
}
```
