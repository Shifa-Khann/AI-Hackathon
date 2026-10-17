#!/usr/bin/env bash
# Initialise git, make the first commit, and (if gh is available) create a PUBLIC GitHub repo and push.
set -euo pipefail
cd "$(dirname "$0")/.."

REPO_NAME="${1:-the-fold}"

if [ ! -d .git ]; then
  git init -b main
  echo "Initialised git repository."
fi

git config user.name  >/dev/null 2>&1 || git config user.name  "${GIT_AUTHOR_NAME:-Sana}"
git config user.email >/dev/null 2>&1 || git config user.email "${GIT_AUTHOR_EMAIL:-sana@example.com}"

if [ -z "$(git log --oneline 2>/dev/null | head -1)" ]; then
  git add -A
  git commit -m "chore: scaffold The Fold (docs, agents, backend, frontend, tests)"
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
    echo "Created public repo and pushed."
  else
    cat <<EOF

No GitHub remote yet and 'gh' is not logged in. Do this manually:
  1. Create an EMPTY PUBLIC repo named "$REPO_NAME" on github.com
  2. git remote add origin https://github.com/<your-username>/$REPO_NAME.git
  3. git push -u origin main
EOF
  fi
fi

git log --oneline | head -5
