# Git workflow — commits are judged

The brief says: *"Make your own GitHub repository at the start of the hackathon. All commits will be monitored."*
So the commit history is part of the submission. Every agent follows these rules.

## 1. Start of hackathon (do this in the first 10 minutes)

```bash
bash scripts/init_repo.sh            # git init, first commit, creates PUBLIC repo "the-fold" via gh, pushes
```
If `gh` isn't installed/logged in: create an empty public repo on github.com, then
```bash
git remote add origin https://github.com/<you>/the-fold.git
git push -u origin main
```

## 2. When to commit — ALWAYS after:

- finishing any task in `docs/TASKS.md` (one task = one commit, minimum)
- any working sub-step that took > 15 minutes
- fixing a bug
- before starting a risky refactor (so you can `git revert`)

Target cadence: **every 10–25 minutes**. Never let more than 30 minutes pass without a commit.
Never commit a broken build — run `bash scripts/dev_check.sh` first (`scripts/commit.sh` does this for you).

## 3. How to commit

```bash
bash scripts/commit.sh "feat(reader): add skip button with fade"
```
`commit.sh` will: run backend tests → `git add -A` → refuse if `.env` is staged → commit → push if a remote exists.
Use `SKIP_TESTS=1 bash scripts/commit.sh "docs: ..."` only for docs-only commits.

## 4. Message format (Conventional Commits)

```
<type>(<scope>): <imperative summary, ≤ 72 chars>

[optional body: what & why, bullet points]
```
Types: `feat` `fix` `refactor` `test` `docs` `style` `chore` `perf`
Scopes: `ingest` `tagger` `profiler` `scorer` `editor` `learning` `quiz` `api` `db` `reader` `onboarding` `archive` `profile` `pdf` `demo` `i18n`

Good: `feat(scorer): add source diversity penalty`
Bad: `update`, `fixes`, `wip stuff`, `final final v2`

## 5. Branching

Keep it simple for an 8-hour solo build: **commit directly to `main`**, small and green.
If two agents work in parallel on overlapping files, use short branches `feat/<scope>` and merge with `--no-ff` within 30 minutes.

## 6. Pushing

`commit.sh` pushes every commit when `origin` exists. If offline, commits queue locally — run `git push` when back online.
Run `/checkpoint` every hour: it pushes and summarises progress in `PROGRESS.md`.

## 7. Final

```bash
git tag -a v1.0-nascon -m "NaSCon'26 submission"
git push origin main --tags
```
Make sure the repo is **public** before submitting the link.
