---
paths:
  - ".claude/**"
---

# Claude's project setup

Claude Code's configuration for this repository and the maintainer records; nothing here ships to users.

## Where a new file goes
- Put project instructions and the core commands in `CLAUDE.md`, and the commands of each lifecycle stage in `WORKFLOW.md`, which `CLAUDE.md` points to without importing it.
- Put project settings (permissions, plugins, MCP servers, auto memory) in `settings.json`. Register this project's hooks there, with their scripts in `hooks/`, as `rules/hook-scripts.md` sets out.
- Put a convention for one area or file type in `rules/<topic>.md`, with a quoted `paths` list so it loads only with those files.
- Put a subagent in `agents/<group>/<agent>.md`: `auditors/` for read-only checks, `docs-maintainers/` for `plugin-readme-writer` (a plugin README written in full for the first time), `testers/` for test runs. Set `model` in its frontmatter (Sonnet for executors and simple auditors; Opus for adversarial reviewers, orchestrators, and reviewers of critical, complex or broad work) and `effort` from the official recommendations for that model and task.
- Leave `agent-memory/<agent>/` to the subagents that set `memory: project`; they write it themselves.
- Put a project skill in `skills/<skill>/` as a procedure that calls `scripts/`, with no scripts inside the skill folder.
- Put a document's template in the `docs-maintenance` skill's `assets/<name>-template.md` and its fill procedure in its `references/documents/<name>.md`, and list the pair in that skill's Documents table. Put a template that isn't a document (plugin manifest, skill, agent, evals workflow) in `templates/<name>-template.md` with its procedure in `references/<name>.md`, listed in `references/README.md`.
- Record decisions and technical debt in `maintainer/` through the `project-maintainer:write-records` skill: one ADR per decision in `decisions/ADR_<YYYY-MM-DD>_<slug>.md`, debt in `technical-debt/pending-debt.md` and `technical-debt/closed-debt.md`.
- Put design specs in `maintainer/specs/<topic>-spec.md`, implementation plans in `maintainer/plans/<YYYY-MM-DD>-<topic>.md`, and audit reports in `maintainer/audits/<YYYY-MM-DD>-<topic>-audit.md`.
- Write end-of-session handoffs through the `project-maintainer:write-handoff` skill, which saves them in `session-handoff/`.
- Put each redesign draft in `architecture/` at the path it will replace (`CLAUDE.draft.md`, `rules/<topic>.md`). Move it to its target once the owner approves it, and delete `architecture/` when it is empty.

## Working here
- When you add a folder of instruction Markdown here, add it to the `.claude/` entries under `files.includes` in `biome.jsonc`, so Biome leaves the Markdown Claude reads unformatted.
- When a write here asks for permission, wait for the owner's answer; `.claude/` is a protected folder, so never write to it through Bash instead.
- After changing a skill, run `npm run lint:skills -- .claude/skills/<skill>`. Report each defect it finds to the owner, one question per rule id, and fix it or record it as debt only after the owner decides.
