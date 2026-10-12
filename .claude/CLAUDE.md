# The Claude Factory — maintainer instructions

Public Claude Code / Cowork plugin marketplace at `github.com/nerymurillohnd/the-claude-factory`.
Two maintainers: Nery (owner) and Claude. No external pull requests; users contribute through issues.

## Working with Nery

- Talk with Nery in **Spanish**. Write everything in the repository in **English**: docs, code, comments, commits, issue replies.
- Ask until you are ≥95% sure before building; once a plan is approved, finish it and stop only for decisions that are Nery's to make.
- Push back on weak instructions and recommend the strongest option, saying which one and why.
- Verify the environment, stack and tools before starting a task.
- Prove "done" with raw output from the gates. Demand raw evidence from subagents and check it yourself.
- End every task with a summary: work done, decisions, changes, learnings, current state.

## Layout

| Path | Purpose | Audience |
| :-- | :-- | :-- |
| `.claude-plugin/marketplace.json` | Catalog. Name `the-claude-factory` is permanent | Claude Code |
| `plugins/<name>/` | One plugin per folder: `.claude-plugin/plugin.json`, `README.md`, `CHANGELOG.md`, `LICENSE`, components | Users |
| `README.md`, `CHANGELOG.md`, `docs/` | Showcase and user guides | Users |
| `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` | Community files | Users |
| `.github/ISSUE_TEMPLATE/`, `.github/labels.json` | Issue forms and labels | Users / maintainers |
| `.github/scripts/` | Zero-dependency Node tooling + tests | Maintainers, CI |
| `.github/workflows/` | `validate.yml` (gates), `release.yml` (tags + releases), `evals.yml` (full plugin eval suites, billed) | CI |
| `.claude/` | This file, memory, rules, skills, agents, templates | Maintainers only |

## Golden rules

1. **Plugin `name` is permanent.** Change `displayName` for labels. A rename or removal needs a `renames` entry in `marketplace.json` and a major marketplace bump.
2. **`plugin.json` holds the version** — never set `version` on a marketplace entry.
3. **SemVer + Keep a Changelog** for every plugin and for the marketplace. Release only through `bump-version.mjs`.
4. **Never hand-edit generated blocks** in `README.md` (`<!-- catalog:* -->`, `<!-- plugin-count:* -->`). Run `catalog.mjs`.
5. **User docs sell and teach; they never mention maintenance**, internal tooling, `.claude/`, scripts or our workflow.
6. **Verify against live official docs** before stating Claude Code behavior, commands, versions or UI paths. Use the Claude Code Docs MCP or code.claude.com / claude.com docs. Live docs beat this repo's files; flag conflicts.
7. **Plugins target Claude Code and Cowork.** Claude Code-only only when a plugin's nature requires it, declared in its README. The verified component matrix and design rules are in `.claude/rules/cross-surface-compatibility.md` (always loaded) — use it instead of re-researching.
8. **Every gate passes before commit.** Fix root causes; never weaken a check to make it pass.

## Quality gates

Run the `verify` skill, or directly:

```bash
node --test ".github/scripts/tests/*.test.mjs"
node .github/scripts/check-repo.mjs
node .github/scripts/catalog.mjs --check
.github/scripts/validate-claude.sh
npx --yes markdownlint-cli2@0.23.3
```

## Workflows → skills

| Task | Skill |
| :-- | :-- |
| Create a plugin | `/new-plugin` |
| Release a plugin or the marketplace | `/release` |
| Triage and answer issues | `/triage-issues` |
| Run all gates | `/verify` |
| Check docs and pins against current Claude Code | `/docs-drift-check` |
| Close a session and update project memory | `/wrap-up` |

Agents: `plugin-reviewer` (independent review of a plugin before release), `docs-auditor` (user-doc accuracy and style).

## Repository settings (GitHub)

- Pull requests: **Collaborators only**. Issues: on. Private vulnerability reporting: on. Topics set.
- Labels come from `.github/labels.json` via `node .github/scripts/sync-labels.mjs`.

## Project memory

Project memory lives in `.claude/memory/` and is committed, so every session sees it on any machine or surface (Claude Code's own auto memory is machine-local).

- Loaded every session: @memory/project-state.md · @memory/environment.md · @memory/learnings.md
- Read on demand: `.claude/memory/session-log.md` (dated history of sessions).
- Update memory in the same commit as the work, or with `/wrap-up` at the end of a session:
  - **project-state** — decisions, current status, roadmap, open items.
  - **environment** — how we work across surfaces, tools, access and their limits.
  - **learnings** — gotchas that cost time once; write each as a rule to follow.
  - **session-log** — one dated entry per session: what changed, commits, what's next.
- Keep memory factual and short: one fact per line, no duplication with this file, rules or code. Delete stale lines instead of piling up corrections.
