# The Claude Factory

Nery and Claude Code are the only two parties responsible for this marketplace. Claude Code, with Anthropic's services, is integrated at every level of it: design, development, review, testing, release and issue triage.

- No third-party team reviews our work between this repository and the users who install it. Every push, release and reply is the last check before the public; take each one with that responsibility.
- Prefer automation and process optimization wherever they keep quality: CI, evals, hooks, agents and scheduled tasks for validation, review, releases, drift checks and issue handling. Where none exists yet, propose building it.
- This project also follows the guidelines and way of working in the `@~/.claude/CLAUDE.md` and the global cross-projects lessons in `@~/.claude/LESSONS.md`.

## Overview

A public Claude Code plugin marketplace at `github.com/nerymurillohnd/the-claude-factory`, for users and developers who run their projects and operations with Claude. It ships plugins only, built for Claude Code and for the Claude app wherever they apply. It is built on Nery's Mac in the local clone and served to users from the remote repository. Users contribute through issues.

Plugins are for third parties whose setups are unknown: every plugin works from what its README declares, never from what is installed on Nery's machine.

## Purpose and Goal

This project carries one item of the global North Star: multiply execution capacity with AI, and share it as public plugins.

- Goal: publish plugins that automate and optimize everyday workflows.
- Differentiator: completeness, not complexity. Elsewhere, users combine several plugins and skills to cover one domain; here one plugin covers the whole domain (knowledge, enforcement, tooling, review and proof that it works), so users find everything in one place.
- Release gate: a plugin ships only when every requirement below has recorded evidence.
- Requirements: every gate passes, the plugin review leaves no confirmed finding, the Claude app check passes (unless Claude Code-only), the README is accurate against the current docs, and the plugin is portable across macOS, Linux and Windows through Git Bash.

## Stack and Development

- Product: Claude Code plugins (skills, agents, hooks, MCP and LSP servers, mods) listed in `.claude-plugin/marketplace.json`, one folder per plugin under `plugins/`.
- Build: no build step and no runtime to maintain; no root `pyproject.toml` or virtual environment.
- Root `package.json` (ADR_2026-10-21_maintainer-only-root-package-json): maintainer tooling only, never a runtime of any plugin. A user receives only `plugins/<name>/`, but Node resolves imports by walking up the folders, so anything in the root `node_modules` would let a plugin pass here and fail for users.
  - It holds only exact `@types/*` devDependencies, today `@types/node` on the Node major of `.nvmrc`, so `tsc`, the post-edit hook and the language server read `scripts/tsconfig.json` the same way. It sets `"private": true` and never `dependencies`, `main`, `exports`, `bin`, `type` or `workspaces`; a `"type"` would change how Node and `tsc` read the plugins' `.js` and `.ts` files.
  - The CLIs stay out of it: TypeScript, Biome, ruff, mypy and every other tool run as installed on the machine, by bare name, never through `npx` or `uvx` (ADR_2026-10-21_gates-run-installed-tools). CI installs the latest release of each; only TypeScript is pinned, to 6.0.3 (ADR_2026-10-21_ci-installs-latest-tools).
  - `check-repo.mjs` enforces all of it, including the `.nvmrc` major. When `.nvmrc` changes major, change `@types/node` in the same commit with `npm install --save-dev --save-exact @types/node@<major>.x.y`.
  - A plugin that needs packages ships its own `package.json` and npm or Bun lockfile in `plugins/<name>/`, which Claude Code installs into that plugin's cache; it never relies on the root one.
- Plugin code: Bash and POSIX-style Python 3 that run on whatever `bash` and `python3` the user has on `PATH`, with no version floor; `.mjs` modules type-checked by TypeScript 6.0.3; mods in TypeScript under `hooks/*.ts`.
- Repository tooling: Node scripts in `scripts/` for scaffolding, catalog, version bumps, labels, policy checks and eval targets, with their tests in `scripts/tests/`; Node 26 from `.nvmrc`. Maintainer code lives at the root, never under `.github/` (ADR_2026-10-21_maintainer-scripts-at-root): basedpyright and other tools skip folders whose name starts with a dot, so code there goes unchecked. `.github/` holds only GitHub's own files.
- Formatting and linters: Biome for JavaScript and JSON; ruff, mypy and basedpyright for Python; shfmt and ShellCheck for shell; actionlint for workflows. Markdown has no linter (ADR_2026-10-21_remove-markdownlint). Each runs as installed on the machine; CI installs the latest release of each, TypeScript excepted.
- Testing: `node --test` for script and hook tests, `unittest` and `by_path.sh` for plugin scripts, `claude plugin validate --strict` and `claude plugin test` for plugins and mods, `claude plugin eval` for plugins that have evals.
- CI/CD and GitHub Actions: `validate.yml` on every push and PR, `evals.yml` for changed plugins that have evals, `release.yml` tags each plugin after merge, and Claude reviewers run on pull requests.
- Tool sources: Node, npm and a global TypeScript via nvm, and the root `node_modules` via `npm ci` after a fresh clone; Python, ruff, mypy and basedpyright via uv (`uv tool install <tool>@latest`); Biome and Claude Code via their official installers; shfmt, ShellCheck and actionlint via Homebrew. A tool that is missing is installed from its source, never run through `npx` or `uvx`. Global configs are never overridden here; `ruff.toml` is the only ruff config in the repo.

## Authority, Limits and Permissions

- Push only on Nery's instruction; when one is needed, ask for approval.
- Type-check every `.mjs` and mod with strict `tsc`, and Python with `mypy --strict` and basedpyright: no `any`, unsafe casts, ignore comments or loosened configs.
- Make each script and hook that receives critical input require the fields it needs, or fail loudly.
- Prefer avoiding technical debt: resolve at its root every issue the task touches directly or indirectly, or needs to work.
- Record as technical debt only a completely separate scope.
- Fix every issue a hook, script, formatter, linter or diagnostic reports; never skip or suppress it.
- Build every plugin for third parties: never depend on, cite or fold in what is installed on Nery's machine.
- When designing, planning or proposing a plugin, justify every choice (name, skills, agents, structure) on its own merits.
- Never name other plugins of the marketplace as precedent ("follows X", "like Y does") or as a blocker.

## Documentation, Maintenance, and Gates

- `.claude/maintainer/decisions/`: ADRs for important decisions.
- `.claude/maintainer/technical-debt/`: pending and closed debt.
- `.claude/memory/`: project memory (facts, feedback).
- `.claude/session-handoff/`: session handoffs.
- `.claude/skills/`: project skills (`plugin-development`, `plugin-consistency`, `github-workflow`, `release-and-versioning`, `plugin-hooks-guidance`, `plugin-mcp-guidance`).
- `.claude/specs/`: design specs.
- `.claude/plans/`: implementation plans.
- `.claude/templates/`: templates for plugin files and the root README.
- `.claude/rules/WORKFLOW.md`: how to work by task: quality checks, maintenance, plugins, hooks, versioning, GitHub, releases, skills and user docs.
- `docs/`: the user guides, covering installation, managing plugins, compatibility, FAQ, troubleshooting and tool references.

## Research and Sources

- Claude Code and the Claude app change almost daily: training data, memory and project docs are starting points, not the authority.
- Before any plan, answer, plugin component or scaffold, read the official sources for the installed Claude Code version and the installed tool versions.
- When components connect or depend on each other, research each one equally, never one side only (e.g. a plugin hook reads the hooks reference, the plugins reference and the Claude app platform support).
- Check the Claude Code changelog and the Claude app release notes for changes the docs have not caught up with yet.
- The same standard applies to the Claude models themselves and to every tool the gates run: research their current features and check their changelogs.

## Commands

Run from the repository root with the `.nvmrc` runtime selected and `npm ci` run once after a fresh clone, so `node_modules/@types/node` exists. The commands run the tools installed on the machine by bare name; CI installs the latest release of each, except TypeScript, pinned in the `env` block of `.github/workflows/validate.yml`.

### Project

- `node scripts/new-plugin.mjs --name <name> --category <id> --description "<sentence>" [--display-name "<Name>"] [--emoji <e>] [--min-claude-code <x.y.z>] [--claude-code-only]` - Run when scaffolding and registering a plugin.
- `node scripts/catalog.mjs` - Run when regenerating the generated blocks of the root `README.md`.
- `node scripts/bump-version.mjs <plugin> <major|minor|patch>` - Run when bumping a plugin in its PR.
- `node scripts/release-notes.mjs <plugin> [--tag]` - Run when previewing a plugin's release notes or tag.
- `node scripts/eval-targets.mjs --changed <base> <head>` or `--only <plugin|all>` - Run when listing the plugins whose evals CI would run.
- `node scripts/sync-labels.mjs [--dry-run]` - Run when syncing the GitHub labels after a plugin is added.
- `ONLY=<plugin> scripts/run-evals.sh` - Run when running a plugin's full eval suite.
- `claude --plugin-dir plugins/<plugin>` - Run when exercising a plugin in a live session.
- `git push origin <branch>` - Run when Nery orders a push. Never run a bare `git push`.
- For all other commands, read `scripts/` and `.github/workflows/`.

### After Editing a File

Python:

- `ruff format <file>` - Run first, after every `.py` edit.
- `ruff check <file>` - Run after the formatter.
- `mypy --strict <file>` - Run after ruff.
- `basedpyright --warnings <file>` - Run after mypy.
- `python3 -m unittest discover -s scripts/tests/<plugin>` - Run when the file belongs to a plugin with Python tests.
- `scripts/tests/<plugin>/by_path.sh` - Run when that plugin folder ships one.

JavaScript modules (`tsc` checks the whole project):

- `biome check --write --error-on-warnings <file>` - Run first, after every `.mjs` edit.
- `tsc -p scripts/tsconfig.json --noEmit` - Run after Biome, for a file under `scripts/`; `-p scripts/tsconfig.plugins.json` for a file under `plugins/`.
- `node --test "scripts/tests/*.test.mjs"` - Run after the type check, and `node --test scripts/tests/<plugin>/*.test.mjs` when the file belongs to a plugin with Node tests. A skipped test means a missing tool: install it.
- `node scripts/check-repo.mjs` - Run after the tests.

Mods (code in `hooks/*.ts`, tests in `tests/*.test.ts`):

- `biome check --write --error-on-warnings <file>` - Run first, after every `.ts` edit.
- `tsc -p plugins/<plugin>/tsconfig.json --noEmit` - Run after Biome. The config extends the declarations the engine writes into `plugins/<plugin>/.claude-plugin/types/` when it loads the mod. Git ignores that folder, so after a fresh clone load the plugin once in an interactive session from a trusted folder (`claude --plugin-dir plugins/<plugin>`, then `/exit`) to write it. CI cannot run this gate for that reason.
- `claude plugin validate --strict plugins/<plugin>` - Run after tsc. It reads the mod the way the engine will. Pass `$` only inside `register.ts`: validation fails when `$` goes to a function imported from another file.
- `claude plugin test plugins/<plugin>` - Run last. Break the rule under test on purpose once and confirm its tests fail.

Shell:

- `shfmt -w <file>` - Run first, after every `.sh` edit.
- `shellcheck -o all -S style -x -a -P SCRIPTDIR <file>` - Run after shfmt.
- `scripts/tests/<plugin>/by_path.sh` - Run when the script belongs to a plugin that ships one.

### Before Every Push

Run `npm run gates` with the `.nvmrc` Node and after `npm ci` (ADR_2026-10-21_gates-run-from-one-script). `scripts/gates.mjs` is the one list of gates, the source of the commands below: it runs them in order, without a shell, stops at the first failure with that gate's exit code, and fails any gate whose tests skipped a case, since a skip means a tool is missing. Fix the cause and run it again from the start. No git hook runs it or `.pre-commit-config.yaml`.

| Group | Runs in | Gates |
| :-- | :-- | :-- |
| (before anything) | local | the branch, `git status`, every commit since `origin/main` signed `G` |
| `policy` | CI and local | the maintainer Node tests (`scripts/tests/*.test.mjs`), `check-repo.mjs`, `catalog.mjs --check`, `check-version-bump.mjs`, `tsc` on `scripts/`, ShellCheck and shfmt on `scripts/` |
| `python` | CI and local | ruff check, ruff format, `mypy --strict` and basedpyright on `scripts/` |
| `claude` | CI and local | `claude plugin validate --strict` on the marketplace and on every plugin |
| `lint` | CI and local | Biome outside `plugins/`, actionlint |
| `local` | local only | the plugins' behavior: the tests in `scripts/tests/<plugin>/` (Node, Python and `by_path.sh`), `claude plugin test` for every mod, the mods' `tsc`; and the analysis of plugin code: `tsc -p scripts/tsconfig.plugins.json`, Biome, ShellCheck, shfmt, ruff, mypy and basedpyright on `plugins/` |

CI runs only the `policy`, `python`, `claude` and `lint` groups, one per job, with `npm run gates:ci -- --group <group>` (ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure): what is ours and what no user's machine changes. The plugins' behavior depends on the interpreter and tools of whoever installs them, so it is proven here before the push and, for a plugin that has them, by its evals in `evals.yml`. `--ci` changes only three things: it leaves out the `local` group, the version-bump base comes from `--base`, and the run goes on after a failure to list every failing gate.

The mods' `tsc` needs the declarations the engine writes into `plugins/<plugin>/.claude-plugin/types/`; after a fresh clone, load the plugin once in an interactive session (`claude --plugin-dir plugins/<plugin>`, then `/exit`).

Report the run as `.claude/rules/WORKFLOW.md` → When Checking Quality says: gate, result and key output line.

### Command Rules

- Script `sync-labels.mjs` writes GitHub labels; run `--dry-run` first.
- Script `run-evals.sh` spends API money: both arms, 3 runs per case, capped by `evals-config.json`. Run it only on Nery's request.
- Script `bump-version.mjs` rewrites `plugin.json` and the plugin changelog; use it instead of hand edits.
- `gh workflow run release.yml` tags and publishes; run it only per the `release-and-versioning` skill.
