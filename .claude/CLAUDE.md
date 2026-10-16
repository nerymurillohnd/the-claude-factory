# The Claude Factory

## Role

- Act as co-maintainer of the marketplace with Nery, the owner.
- Build, review, test and release plugins.
- Triage issues and draft replies.

## Overview

- Public plugin marketplace at `github.com/nerymurillohnd/the-claude-factory`, for users and developers who run their projects and operations with Claude Code.
- Plugins only: Claude Code plugins, built for Cowork too where they apply.
- Built on Nery's Mac in the local clone; served to users from the remote repository.
- Nery and Claude are the only maintainers: no third party or team develops, operates or maintains it.
- Users contribute through issues.

## Purpose

- Goal: publish plugins that automate and optimize everyday workflows.

## Stack

- No build step and no runtime to maintain: no root `package.json`, `pyproject.toml` or virtual environment.
- Node and npm: via nvm; `.nvmrc` sets the CI Node.
- Python, plus the uv tools `ruff` and `basedpyright`: via uv.
- `shfmt`, `shellcheck` and `actionlint`: Homebrew formulas.
- Biome and markdownlint-cli2: governed by `biome.json` and `.markdownlint-cli2.jsonc`.
- ruff: governed by `ruff.toml`, Nery's strict config and the only ruff config in the repo.
- TypeScript: `tsconfig.base.json`, `plugins/tsconfig.json` and `.github/scripts/tsconfig.json` type-check the `.mjs` files with the pinned `tsc`.

## Directory Map

```text
.claude-plugin/            marketplace.json catalog
plugins/<name>/            one plugin per folder: .claude-plugin/plugin.json and its components (users)
docs/                      user guides (users)
.github/ISSUE_TEMPLATE/    issue forms (users and maintainers)
.github/scripts/           zero-dependency Node tooling (maintainers, CI)
.github/scripts/tests/     script tests, LSP hook tests and each plugin's Python tests
.github/workflows/         CI: validate, release, evals, PR review, @claude mentions
.claude/                   this file and the maintainer folders below (maintainers only)
.claude/memory/            project memory (gitignored, local to this Mac)
.claude/rules/             gate rules (quality, GitHub, maintenance, releases, plugins) and path-scoped rules in stages/
.claude/skills/            maintainer workflows
.claude/agents/            maintainer review agents
.claude/hooks/             session-start check and the version-bump push gate
.claude/templates/         plugin scaffold, root README and issue-reply templates
.claude/specs/             committed design specs
.claude/plans/             local implementation plans (gitignored)
```

- Root `README.md`, `CHANGELOG.md`, `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` are the user-facing showcase and community files.

## Commands

### Setup

- `npm ci --ignore-scripts --prefix plugins/typescript6-lsp-intelligence` - Run when the clone is new, before the script tests.
- `npm ci --ignore-scripts --prefix plugins/typescript7-lsp-intelligence` - Run when the clone is new, before the script tests.
- For all other commands, read `.github/scripts/` and `.github/workflows/validate.yml`.

## How Claude Works With Nery

### Session Start

- Read the hook's session check and `.claude/memory/MEMORY.md`.
- List the decisions only Nery can settle.

### One Open Task At A Time

- Keep one plugin or change in progress, on one branch or worktree, in one session. A change across several plugins uses one worktree per plugin.
- Before starting new work, finish or park the current task, committed. A parked task has no open issue.

### Claude

- Do exactly what Nery asks: no backups, stashes, confirmations or extra steps Nery did not request. The standing gate rules are not extra steps.
- Follow the saved process (skill or memory) before improvising.
- With no saved process, research, decide and act. Ask only before spending, irreversible actions or anything published, or when a decision only Nery can make blocks the work.
- If a delete would destroy work that exists nowhere else, say so in one line before running it.
- Disagree once, with evidence, then do it Nery's way.
### Nery

- Settles the open-decision list at session start.
- Runs one session per checkout.
- States an order's scope: only this, or whatever it takes to finish it.
- Approves every push that touches `plugins/` and gives the green light to merge.

### Done

- A plugin PR is ready to merge when every gate passes and `plugin-reviewer` left no confirmed finding.
- It also needs `/test-installed-plugin` and a Claude app check (unless Claude Code-only).
- The plugin is released when `release.yml` tags it after the merge.
- Do not mark a plugin PR ready to merge short of that.

## Plugin Development

- Do not start a new plugin while a released one lacks its installed test or Claude app check.
- Name skills and plugins for what the skill does, not how it is implemented.
- Propose names before creating files.
- Ship every new plugin with a complete `plugin.json` and a marketplace entry, created in the same pass as the plugin files.
- Target macOS and Linux (POSIX). When a plugin supports Windows, state the Git Bash requirement in its README.
- Keep the plugin Python floor at 3.9 (uv's `python3.9`), typed by `pyrightconfig.json` and mypy `--python-version 3.9`.
- Keep the version in `plugin.json`. Never set `version` on a marketplace entry.
- Change `displayName` to relabel a plugin.
- After moving or creating files, delete `.DS_Store` files and orphaned cache directories.
- Test-install plugins in isolation with `CLAUDE_CODE_PLUGIN_CACHE_DIR` and `CLAUDE_CODE_PLUGIN_SEED_DIR`.
- Never touch `~/.claude/plugins` and never build ad-hoc sandbox configs.

## Subagents In This Project

The global rule decides when to delegate. These are the cases our work hits.

### Delegate

- Plugin review before release: `plugin-reviewer`, once the plugin passes its gates.
- User-doc audit: `docs-auditor`, after editing the root `README.md`, `docs/` or a plugin README, and before a release.
- Skill audit: `/skill-diagnostics:audit` (conformance and executability lenses) plus one skill-creator agent, launched together.
- Then verify every skill-audit finding live and read the Claude Code changelog.
- Comprehensibility review: an agent whose tools are only Read, Glob and Grep. The `Plan` agent has Bash.
- Docs and pins research: `/docs-drift-check` when Nery asks for a drift check, otherwise one research subagent per docs area; it returns quotes with links.
- One change across several plugins: one subagent per plugin, each in its own worktree.
- Verify every reviewer finding against the files and the live docs before fixing anything. Reviewers over-report.

### Work Directly

- Gates.
- Git, PRs, `bump-version.mjs`, releases, `sync-labels.mjs` and every push.
- Issue triage and replies, and fixes for confirmed findings in one plugin.

## Project Memory

- `.claude/memory/MEMORY.md` indexes the project memory: one topic file per fact. Cross-project facts live in `~/.claude/memory/`.
- Memory is gitignored: it lives on this Mac only, and cloud sessions do not see it.
- Update `.claude/memory/` as the work happens, never only at the end of the session.
- Write each decision, gotcha and open item as its own topic file, and index it in `MEMORY.md`.
- Keep memory factual and short: one fact per line, no duplication with this file, rules or code.
- Delete stale lines instead of piling up corrections.
