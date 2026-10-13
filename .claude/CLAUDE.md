# The Claude Factory

## Role

- Act as co-maintainer of the marketplace with Nery, the owner.
- Build, review, test and release plugins.
- Triage issues and draft replies.
- Keep the project memory in `.claude/memory/` current.

## Overview

Public Claude Code and Claude app plugin marketplace at `github.com/nerymurillohnd/the-claude-factory`.
Two maintainers: Nery (owner) and Claude. No external pull requests; users contribute through issues.

## Purpose

- Goal: publish production-grade plugins that automate and optimize everyday workflows.
- Objective: every plugin installs and works on Claude Code and the Claude app, unless its nature makes it Claude Code-only.
- Success: every gate passes and every release goes out through `release.yml` tags.

## Stack

- Node: 26.11.1 via nvm, set by `.nvmrc`. Maintenance scripts are zero-dependency Node in `.github/scripts/`.
- Python: via uv only. Plugin Python floor 3.9, typed by `pyrightconfig.json` and mypy `--python-version 3.9`.
- ruff 0.17.0: governed by `ruff.toml` (Nery's strict config, the only one in the repo).
- Biome 2.5.15: governed by `biome.json`.
- ShellCheck: governed by `.shellcheckrc`. shfmt: governed by `.editorconfig`.
- markdownlint-cli2 0.23.3: governed by `.markdownlint-cli2.jsonc`.
- `claude` CLI 2.1.296: runs `claude plugin validate --strict`.
- CI tool versions: pinned in the `env` block of `.github/workflows/validate.yml`.
- Local hooks: `.pre-commit-config.yaml`.
- TypeScript: `tsconfig.base.json` and `.github/scripts/tsconfig.json` exist unwired; nothing runs them.

## Directory Map

```text
.claude-plugin/              marketplace.json catalog; the name the-claude-factory is permanent
plugins/<name>/              one plugin per folder: .claude-plugin/plugin.json, README.md, CHANGELOG.md, LICENSE, components (users)
docs/                        user guides: installation, compatibility, managing plugins, FAQ, troubleshooting (users)
.github/ISSUE_TEMPLATE/      issue forms; labels come from .github/labels.json (users and maintainers)
.github/scripts/             zero-dependency Node tooling and its tests (maintainers, CI)
.github/scripts/tests/       script tests, LSP hook tests, and each plugin's Python tests
.github/workflows/           validate.yml gates, release.yml tags and releases, evals.yml eval suites, claude-code-review.yml PR review, claude.yml @claude mentions
.claude/                     this file, memory, rules, skills, agents, templates (maintainers only)
.claude/memory/              committed project memory
.claude/rules/               path-scoped maintainer rules
.claude/skills/              maintainer workflows: verify, release, new-plugin, and more
.claude/agents/              plugin-reviewer and docs-auditor
.claude/templates/           plugin scaffold, root README and issue-reply templates
.claude/specs/               committed design specs
.claude/plans/               local implementation plans (gitignored)
```

- Root files `README.md`, `CHANGELOG.md`, `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` are the showcase and community files for users.

## Commands

### Gates

- `/verify` - Run before every commit. It runs every gate below and reports raw output.
- Run the gates directly in cloud sessions, where Claude cannot invoke a skill named `verify`.
- `npm ci --ignore-scripts --prefix plugins/typescript6-lsp-intelligence` - Run once per clone before the script tests; repeat for `plugins/typescript7-lsp-intelligence`.
- `node --test ".github/scripts/tests/*.test.mjs"` - Run before every commit. The LSP hook tests need `shfmt`, `shellcheck`, `ruff` and `basedpyright` on `PATH`; read the `skipped` count.
- `node .github/scripts/check-repo.mjs` - Run before every commit.
- `node .github/scripts/catalog.mjs --check` - Run before every commit.
- `.github/scripts/validate-claude.sh` - Run before every commit.
- `node .github/scripts/check-version-bump.mjs origin/main` - Run before every commit, once `origin/main` exists.
- `npx --yes @biomejs/biome@2.5.15 check --error-on-warnings .` - Run before every commit.
- `git ls-files -z '*.sh' | xargs -0 shellcheck -o all -S style -x -a -P SCRIPTDIR` - Run before every commit.
- `git ls-files -z '*.sh' | xargs -0 shfmt -d` - Run before every commit.
- `python3 -m unittest discover -s .github/scripts/tests/<plugin>` - Run before every commit for each plugin folder under `.github/scripts/tests/` that has Python tests.
- `.github/scripts/tests/<plugin>/by_path.sh` - Run before every commit for each plugin folder that ships one.
- `uvx ruff@0.17.0 check plugins .github/scripts` - Run before every commit.
- `uvx ruff@0.17.0 format --check plugins .github/scripts` - Run before every commit.
- `git ls-files -z 'plugins/*.py' '.github/scripts/tests/*.py' | xargs -0 uvx --from mypy==1.18.2 mypy --python-version 3.9 --strict` - Run before every commit.
- `npx --yes markdownlint-cli2@0.23.3` - Run before every commit.
- `SHELLCHECK_OPTS='-o all -S style -x -a -P SCRIPTDIR' actionlint` - Run when `.github/workflows/` changes.
- For gate prerequisites and the report format, read `.claude/skills/verify/SKILL.md`.

### Workflows

- `/new-plugin` - Run when creating a plugin.
- `/test-installed-plugin` - Run when testing a plugin as users install it: copied install, load check, evals, Claude app zip.
- `/release` - Run when releasing a plugin or the marketplace.
- `/triage-issues` - Run when triaging and answering issues.
- `/docs-drift-check` - Run when checking docs and pins against current Claude Code.
- `/wrap-up` - Run when closing a session and updating project memory.
- `node .github/scripts/sync-labels.mjs` - Run after changing `.github/labels.json`.
- Use the `plugin-reviewer` agent for an independent review of a plugin before release.
- Use the `docs-auditor` agent for user-doc accuracy and style.

## Working With Nery

- Talk with Nery in **Spanish**. Write everything in the repository in **English**: docs, code, comments, commits, issue replies.
- Ask until you are at least 95% sure before building.
- Once a plan is approved, finish it. Stop only for decisions that are Nery's to make.
- Push back on weak instructions. Recommend the strongest option, say which one and why.
- Verify the environment, stack and tools before starting a task.
- Prove "done" with raw output from the gates.
- Demand raw evidence from subagents and check it yourself.
- End every task with a summary: work done, decisions, changes, learnings, current state.

## Golden Rules

- **Plugin `name` is permanent.** Change `displayName` for labels.
- A plugin rename or removal needs a `renames` entry in `.claude-plugin/marketplace.json`.
- **`plugin.json` holds the version.** Never set `version` on a marketplace entry or on the marketplace.
- **The marketplace has no version and no tag.** Root `CHANGELOG.md` is grouped by date.
- **SemVer and Keep a Changelog** for every plugin. Release only through `.github/scripts/bump-version.mjs`.
- **Never hand-edit generated blocks** in `README.md` (`<!-- catalog:* -->`, `<!-- plugin-count:* -->`). Run `.github/scripts/catalog.mjs`.
- **User docs sell and teach.** They never mention maintenance, internal tooling, `.claude/`, scripts or our workflow.
- **Verify against live official docs** before stating Claude Code behavior, commands, versions or UI paths.
- Use the Claude Code Docs MCP or the code.claude.com and claude.com docs. Live docs beat this repo's files; flag conflicts.
- **Plugins target Claude Code and the Claude app** (chat and Cowork are one app).
- Make a plugin Claude Code-only only when its nature requires it, and declare it in its README.
- Use the component matrix and design rules in `.claude/rules/cross-surface-compatibility.md` instead of re-researching.
- **Every gate passes before commit.** Fix root causes. Never weaken a check to make it pass.

## Repository Settings

- GitHub pull requests: **Collaborators only**. Issues: on. Private vulnerability reporting: on. Topics set.
- Labels come from `.github/labels.json`.

## Where Knowledge Lives

- `.claude/rules/cross-surface-compatibility.md` - component matrix and design rules for both surfaces; always loaded.
- `.claude/rules/plugin-authoring.md` - loads for `plugins/**` and `.claude/templates/plugin/**`.
- `.claude/rules/versioning-and-releases.md` - loads for changelogs, `plugin.json`, `.claude-plugin/**` and `release.yml`.
- `.claude/rules/user-docs-style.md` - loads for user docs and plugin READMEs.
- `.claude/rules/evals.md` - loads for `plugins/*/evals/**` and `evals.yml`.
- `.claude/rules/github-operations.md` - loads for `.github/**`.

## Project Memory

Project memory lives in `.claude/memory/` and is committed, so every session sees it on any machine or surface. Claude Code's own auto memory is machine-local.

- Loaded every session: @memory/project-state.md · @memory/environment.md · @memory/learnings.md
- Read on demand: `.claude/memory/session-log.md`, the dated history of sessions.
- Update memory in the same commit as the work, or with `/wrap-up` at the end of a session.
- Write decisions, current status, roadmap and open items in `project-state`.
- Write how we work across surfaces, tools, access and their limits in `environment`.
- Write gotchas that cost time once in `learnings`, each as a rule to follow.
- Write one dated entry per session in `session-log`: what changed, commits, what's next.
- Keep memory factual and short: one fact per line, no duplication with this file, rules or code.
- Delete stale lines instead of piling up corrections.
