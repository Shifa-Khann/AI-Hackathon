#!/usr/bin/env bash
# End-to-end smoke test against a RUNNING backend (default http://localhost:8000).
set -euo pipefail
API="${API:-http://localhost:8000}"
j() { python3 -c "import sys,json; d=json.load(sys.stdin); print($1)"; }

echo "health…";   curl -sf "$API/api/health" | j "d['ok']"
UID_=$(curl -sf -X POST "$API/api/onboard" -H 'content-type: application/json' \
  -d '{"name":"Smoke","recent_read":"AI policy and cricket","topics":["ai","cricket","startups"],"budget_min":12}' | j "d['user_id']")
echo "user $UID_"
H="X-User-Id: $UID_"
E1=$(curl -sf -X POST "$API/api/editions/generate" -H "$H" | j "d['id']")
echo "edition $E1"
FIRST=$(curl -sf "$API/api/editions/$E1" -H "$H" | j "d['items'][1]['article_id']")
curl -sf -X POST "$API/api/events" -H "$H" -H 'content-type: application/json' -d "{\"edition_id\":$E1,\"article_id\":$FIRST,\"type\":\"skip\"}" >/dev/null
E2=$(curl -sf -X POST "$API/api/editions/generate" -H "$H" | j "d['id']")
echo "edition $E2 (after skip)"
curl -sf "$API/api/editions" -H "$H" | j "len(d['editions'])"
curl -sf -o /dev/null -w "pdf: %{http_code} %{content_type}\n" "$API/api/editions/$E2/pdf" -H "$H"
echo "SMOKE OK"
