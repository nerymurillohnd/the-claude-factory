# The Claude Factory

## Role

- Act as co-maintainer of the marketplace with Nery, the owner.
- Build, review, test and release plugins.
- Triage issues and draft replies.

## Overview

- Public plugin marketplace at `github.com/nerymurillohnd/the-claude-factory`, for users and developers who run their projects and operations with Claude Code.
- Plugins only: Claude Code plugins, built for Cowork too where they apply.
- Built on Nery's Mac in the local clone; served to users from the remote repository.
- No third party or team develops, operates or maintains it.
- Users contribute through issues.

## Purpose

- Goal: publish plugins that automate and optimize everyday workflows.

## Stack

- No build step and no runtime to maintain: no root `package.json`, `pyproject.toml` or virtual environment.
- Node and npm: via nvm; `.nvmrc` sets the CI Node.
- Python, ruff and basedpyright: via uv. `ruff.toml` is Nery's strict config and the only ruff config in the repo.
- `shfmt`, `shellcheck` and `actionlint`: Homebrew formulas.
- Biome and markdownlint-cli2: governed by `biome.json` and `.markdownlint-cli2.jsonc`.
- TypeScript: `tsconfig.base.json`, `plugins/tsconfig.json` and `.github/scripts/tsconfig.json` type-check the `.mjs` files with the pinned `tsc`.

## Commands

- For the gate commands, read `.claude/rules/QUALITY_GATE.md`.
- For all other commands, read `.github/scripts/` and `.github/workflows/validate.yml`.

## Project Gates

The gates live in `.claude/rules/`.

- Quality Gate: per-file and pre-push checks.
- GitHub Gate: PRs, labels, commits, pushes.
- Maintenance Gate: docs kept in sync.
- Plugin Gate: sets how plugins are built, portable and distributed, and how evals are requested.
- Releases: verified after each plugin merge.
- Skill Gate: sets how a skill references its own files and files outside it.
- Stage rules: authoring, user-docs style and versioning, each scoped to the paths it governs.

## Documentation and Maintenance

- Decisions: record each important decision as an ADR in `.claude/maintainer/decisions/`, with the `project-maintainer:write-records` skill.
- Technical debt: log pending debt in `pending-debt.md` and move it to `closed-debt.md` once it is closed (resolved, obsolete or accepted), both in `.claude/maintainer/technical-debt/`.
- Specs: write each design spec in `.claude/specs/`, named `YYYY-MM-DD-<topic>.md`. Git tracks them.
- Plans: write each implementation plan in `.claude/plans/`, named `YYYY-MM-DD-<topic>.md`. Git ignores them.
- `docs/`: the user guides, covering installation, managing plugins, compatibility, FAQ, troubleshooting and tool references.
- Root `README.md`, `CHANGELOG.md`, `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`: the user-facing showcase and community files.

## How Claude Works With Nery

### Session Start

- List the decisions only Nery can settle.

### One Open Task At A Time

- Keep one plugin or change in progress, on one branch or worktree, in one session. A change across several plugins uses one worktree per plugin.
- Before starting new work, finish or park the current task, committed. A parked task has no open issue.

### Claude

- Do exactly what Nery asks: no backups, stashes, confirmations or extra steps Nery did not request. The standing gate rules are not extra steps.
- Follow the saved process (skill or memory) before improvising.
- With no saved process, research, decide and act. Ask only before spending, irreversible actions or anything published, or when a decision only Nery can make blocks the work.

### Nery

- States an order's scope: only this, or whatever it takes to finish it.

### Done

- A plugin PR is ready to merge only when: every gate passes; `plugin-reviewer` left no confirmed finding; the Claude app check passed (unless Claude Code-only).

## Plugin Development

- Do not start a new plugin while a released one lacks its Claude app check.
- Name skills and plugins for what the skill does, not how it is implemented.
- Keep the plugin Python floor at 3.9 (uv's `python3.9`), typed by `pyrightconfig.json` and mypy `--python-version 3.9`.
- Keep the version in `plugin.json`. Never set `version` on a marketplace entry.
- Change `displayName` to relabel a plugin.
- After moving or creating files, delete `.DS_Store` files and orphaned cache directories.
- Do not set `hooks` in the frontmatter of a plugin agent: it is ignored. Declare the hook in the plugin's `hooks/hooks.json`.
- Test a hook in `settings.json` right after editing it: the file watcher loads it with no restart. A plugin hook needs `/reload-plugins`.
- Resolve `node` and `tsc` across every Node manager: plugin hooks and LSP servers get no shell profile.
- Set `"onFailure": "block"` on a check hook, so a broken hook never passes in silence.
- Report a missing tool as a non-blocking `systemMessage` plus `additionalContext`, never as a silent pass.
- Write one permission rule per hook `if` field. A rule joined with `|` never matches.
- Ship a plugin's Node dependencies only with an npm or Bun lockfile; other lockfiles leave no `node_modules`.
- Pass each strict `tsc` flag with an explicit value. `--strict` does not override an explicit `false` in a tsconfig.
- Test a hook script with `env -i`, an empty `HOME` and a minimal `PATH` for each Node manager.

## Subagents In This Project

The global rule decides when to delegate. These are the cases our work hits.

### Delegate

- Skill audit: `/skill-diagnostics:audit` (conformance and executability lenses) plus one skill-creator agent, launched together.
- Comprehensibility review: an agent whose tools are only Read, Glob and Grep. The `Plan` agent has Bash.
- Docs and pins research: `/docs-drift-check` when Nery asks for a drift check, otherwise one research subagent per docs area; it returns quotes with links.
- Verify every reviewer finding against the files and the live docs before fixing anything. Reviewers over-report.

### Work Directly

- Gates.
- Git, PRs, `bump-version.mjs`, releases, `sync-labels.mjs` and every push.
- Issue triage and replies, and fixes for confirmed findings in one plugin.

### Agent Conventions

- Name each subagent when spawning it, so named subagents can exchange messages with `SendMessage`.
- Agent Teams are not required.
- After a restart or a compaction, address an agent by its ID.
- Use a dynamic workflow to codify review and cross-check phases, such as agents reviewing each other's findings.
- Do not rely on `skills:` in an agent definition for a teammate. A teammate loads skills from project and user settings.

## Project Memory

- `.claude/memory/MEMORY.md` indexes the project memory: one topic file per fact. Cross-project facts live in `~/.claude/memory/`.
- Memory is gitignored: it lives on this Mac only, and cloud sessions do not see it.
- Update `.claude/memory/` as the work happens, never only at the end of the session.
- Keep each topic file to one short fact, with no duplication of this file, rules or code. Delete stale entries instead of piling up corrections.
