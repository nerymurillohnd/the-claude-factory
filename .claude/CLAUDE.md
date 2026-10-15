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
- TypeScript: `tsconfig.base.json` and `.github/scripts/tsconfig.json` exist unwired; nothing runs them.

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
.claude/memory/            committed project memory
.claude/rules/             always-loaded rules; stages/ holds the path-scoped ones
.claude/skills/            maintainer workflows
.claude/agents/            maintainer review agents
.claude/hooks/             session-start check
.claude/templates/         plugin scaffold, root README and issue-reply templates
.claude/specs/             committed design specs
.claude/plans/             local implementation plans (gitignored)
```

- Root `README.md`, `CHANGELOG.md`, `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` are the user-facing showcase and community files.

## Commands

### Gate Rules

- Read `.claude/skills/verify/SKILL.md` for gate prerequisites and the report format.
- Run the gates directly in cloud sessions, where Claude cannot invoke a skill named `verify`.
- Quote raw gate output from this session only.
- Gates run pinned versions (`npx`, `uvx`); CI pins them in the `env` block of `.github/workflows/validate.yml`.
- No git hook runs `.pre-commit-config.yaml`.

### Setup

- `npm ci --ignore-scripts --prefix plugins/typescript6-lsp-intelligence` - Run when the clone is new, before the script tests.
- `npm ci --ignore-scripts --prefix plugins/typescript7-lsp-intelligence` - Run when the clone is new, before the script tests.

### Gates

- `/verify` - Run before every commit. It runs every gate below and reports raw output.
- `node --test ".github/scripts/tests/*.test.mjs"` - Run before every commit. Read the `skipped` count.
- `node .github/scripts/check-repo.mjs` - Run before every commit.
- `node .github/scripts/catalog.mjs --check` - Run before every commit.
- `.github/scripts/validate-claude.sh` - Run before every commit.
- `node .github/scripts/check-version-bump.mjs origin/main` - Run before every commit, once `origin/main` exists.
- `npx --yes @biomejs/biome@2.5.15 check --error-on-warnings .` - Run before every commit.
- `git ls-files -z '*.sh' | xargs -0 shellcheck -o all -S style -x -a -P SCRIPTDIR` - Run before every commit.
- `git ls-files -z '*.sh' | xargs -0 shfmt -d` - Run before every commit.
- `python3 -m unittest discover -s .github/scripts/tests/<plugin>` - Run before every commit, for each plugin test folder with Python tests.
- `.github/scripts/tests/<plugin>/by_path.sh` - Run before every commit, for each plugin folder that ships one.
- `uvx ruff@0.17.0 check plugins .github/scripts` - Run before every commit.
- `uvx ruff@0.17.0 format --check plugins .github/scripts` - Run before every commit.
- `git ls-files -z 'plugins/*.py' '.github/scripts/tests/*.py' | xargs -0 uvx --from mypy==1.20.2 mypy --python-version 3.9 --strict` - Run before every commit.
- `npx --yes markdownlint-cli2@0.23.3` - Run before every commit.
- `SHELLCHECK_OPTS='-o all -S style -x -a -P SCRIPTDIR' actionlint` - Run when `.github/workflows/` changes.
- The LSP hook tests need `shfmt`, `shellcheck`, `ruff` and `basedpyright` on `PATH`.
- For all other commands, read `.github/scripts/` and `.github/workflows/validate.yml`.

## Rules

- Push changes to maintainer docs and tooling straight to `main`, unless Nery says otherwise.
- Send the creation of a plugin, or any change to its components, through a PR.
- Never rename the marketplace: the name `the-claude-factory` is permanent.
- Never hand-edit generated blocks in `README.md` (`<!-- catalog:* -->`, `<!-- plugin-count:* -->`). Run `.github/scripts/catalog.mjs`.
- Add a line to this file only when Claude makes the same mistake twice, or Nery repeats a correction from an earlier session.
- Put procedures in skills, and rules for one part of the repo in a path-scoped rule.

## How Claude Works With Nery

### Session Start

- Read the hook's session check and the Open items in `.claude/memory/project-state.md`.
- List the decisions only Nery can settle.

### One Open Task At A Time

- Keep one plugin or change in progress, on one branch or worktree, in one session.
- Before starting new work, finish or park the current work: committed, with one line in `project-state`.
- Never leave uncommitted work in a folder.

### Claude

- Do exactly what Nery asks: no backups, stashes, confirmations or extra steps he did not request.
- Follow the saved process (skill or memory) before improvising.
- With no saved process, research, decide and act. Ask only before spending, irreversible actions or anything published.
- If a delete would destroy work that exists nowhere else, say so in one line before running it.
- Disagree once, with evidence, then do it Nery's way.
- State the expected cost before paid runs: evals, `claude -p`, `claude plugin eval`, workflows, agent fan-outs.

### Nery

- Settles the open-decision list at session start.
- Runs one session per checkout.
- States an order's scope: only this, or whatever it takes to finish it.
- Closes each task: commit and push, commit locally, or park it.

### Done

- A plugin change is done when every gate passes and `plugin-reviewer` left no confirmed finding.
- It also needs `/test-installed-plugin`, a Claude app check (unless Claude Code-only), a merged PR and a `release.yml` tag.
- Do not release a plugin short of done.

## Plugin Development

- Do not start a new plugin while a released one lacks its installed test or Claude app check.
- Name skills and plugins for what the skill does, not how it is implemented.
- Propose names before creating files.
- Ship every new plugin with a complete `plugin.json`, a `README.md`, a `CHANGELOG.md`, a `LICENSE` and a marketplace entry, created in the same pass as the plugin files.
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
- Skill audit: one skill-creator agent plus the conformance and executability lenses, launched together.
- Then verify every skill-audit finding live and read the Claude Code changelog.
- Comprehensibility review: an agent whose tools are only Read, Glob and Grep. The `Plan` agent has Bash.
- Docs and pins research: `/docs-drift-check`, or one research subagent per docs area; it returns quotes with links.
- One change across several plugins: one subagent per plugin, each in its own worktree.
- Verify every reviewer finding against the files and the live docs before fixing anything. Reviewers over-report.

### Work Directly

- Gates and `/verify`.
- Git, PRs, `bump-version.mjs`, `/release`, `sync-labels.mjs` and every push.
- `/test-installed-plugin`, `claude -p` and `claude plugin eval` runs. They use Nery's sign-in and plan.
- Edits to memory, `CLAUDE.md`, rules and maintainer skills. They carry this session's decisions.
- Issue triage and replies, and fixes for confirmed findings in one plugin.

## Project Memory

- Loaded every session: @memory/environment.md · @memory/learnings.md
- Read `.claude/memory/project-state.md` at session start and `.claude/memory/session-log.md` on demand.
- Memory is committed, so every session sees it on any machine. Claude Code's own auto memory is machine-local.
- Update `.claude/memory/` in the same commit as the work, never only at the end of the session.
- Write decisions, current status, roadmap and open items in `project-state`.
- Write how we work across surfaces, tools, access and their limits in `environment`.
- Write gotchas that cost time once in `learnings`, each as a rule to follow.
- Write one dated entry per session in `session-log`: what changed, commits, what's next.
- Keep memory factual and short: one fact per line, no duplication with this file, rules or code.
- Delete stale lines instead of piling up corrections.
