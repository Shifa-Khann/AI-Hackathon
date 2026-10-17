#!/usr/bin/env bash
# Usage: bash scripts/commit.sh "feat(scope): message"
# Runs backend tests (unless SKIP_TESTS=1), blocks secrets, commits everything, pushes if a remote exists.
set -euo pipefail
cd "$(dirname "$0")/.."

MSG="${1:-}"
if [ -z "$MSG" ]; then
  echo "Usage: bash scripts/commit.sh \"<type>(<scope>): <summary>\"" >&2
  exit 1
fi

if ! echo "$MSG" | grep -Eq '^(feat|fix|refactor|test|docs|style|chore|perf)(\([a-z0-9_-]+\))?: .+'; then
  echo "Commit message must follow Conventional Commits, e.g. feat(reader): add skip button" >&2
  exit 1
fi

[ -d .git ] || { echo "Not a git repo. Run: bash scripts/init_repo.sh" >&2; exit 1; }

if [ "${SKIP_TESTS:-0}" != "1" ]; then
  echo "▶ running backend tests…"
  (cd backend && MOCK_LLM=1 python -m pytest -q)
fi

git add -A
if git diff --cached --name-only | grep -Eq '(^|/)\.env$'; then
  echo "Refusing to commit .env" >&2
  git reset -q .env 2>/dev/null || true
  exit 1
fi

if git diff --cached --quiet; then
  echo "Nothing to commit."
  exit 0
fi

git commit -q -m "$MSG"
echo "✔ committed: $(git log --oneline -1)"

if git remote get-url origin >/dev/null 2>&1; then
  git push -q origin HEAD && echo "✔ pushed" || echo "⚠ push failed (offline?) — run 'git push' later"
else
  echo "ℹ no remote configured; run scripts/init_repo.sh"
fi
