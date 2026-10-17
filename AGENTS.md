# AGENTS.md

This repo is built with a multi-agent "orchestrator" workflow.

- **Orchestrator instructions:** [`CLAUDE.md`](CLAUDE.md) — read it first. Cursor, Codex, Windsurf, Aider etc. should treat it as the system prompt.
- **Specialist agents:** [`.claude/agents/`](.claude/agents/) — one markdown file per role, with scope, files owned, and definition of done.
- **Plan:** [`docs/TASKS.md`](docs/TASKS.md) — the ordered backlog. Tick boxes as you go.
- **Git rule:** commit after **every** task with `bash scripts/commit.sh "<type>(<scope>): <summary>"`. See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md).

If your tool does not support sub-agents, play each role in turn: before a task, read that agent's file and follow it as if it were your instructions.
