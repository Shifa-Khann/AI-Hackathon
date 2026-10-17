#!/usr/bin/env bash
# Install deps (idempotent) and run the backend test suite. Optionally type-check the frontend.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "▶ backend deps"
(cd backend && python -m pip install -q -r requirements.txt --break-system-packages 2>/dev/null || python -m pip install -q -r requirements.txt)

echo "▶ backend tests"
(cd backend && MOCK_LLM=1 python -m pytest -q)

if [ -d frontend/node_modules ] && [ "${CHECK_FRONTEND:-0}" = "1" ]; then
  echo "▶ frontend build"
  (cd frontend && npm run build)
fi
echo "DEV CHECK OK"
