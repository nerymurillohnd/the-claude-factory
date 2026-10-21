# The Claude Factory

Nery and Claude Code are the only two parties responsible for this marketplace. Claude Code, with Anthropic's services, is integrated at every level of it: design, development, review, testing, release and issue triage.

- No third-party team reviews our work between this repository and the users who install it. Every push, release and reply is the last check before the public; take each one with that responsibility.
- Prefer automation and process optimization wherever they keep quality: CI, evals, hooks, agents and scheduled tasks for validation, review, releases, drift checks and issue handling. Where none exists yet, propose building it.
- This project also follows the guidelines and way of working in the `@~/.claude/CLAUDE.md`, the global cross-projects memory `@~/.claude/memory/MEMORY.md`, and all of its indexed memory files.

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
- Build: no build step and no runtime to maintain; no root `package.json`, `pyproject.toml` or virtual environment.
- Plugin code: Bash and POSIX-style Python 3 that run on whatever `bash` and `python3` the user has on `PATH`, with no version floor; `.mjs` modules type-checked by TypeScript 6.0.3; mods in TypeScript under `hooks/*.ts`.
- Repository tooling: Node scripts in `.github/scripts/` for scaffolding, catalog, version bumps, labels, policy checks and eval targets; Node 26 from `.nvmrc`.
- Formatting and linters: Biome for JavaScript and JSON; ruff, mypy and basedpyright for Python; shfmt and ShellCheck for shell; markdownlint-cli2 for Markdown; actionlint for workflows. Each runs at the version pinned in Commands below and in `validate.yml`.
- Testing: `node --test` for script and hook tests, `unittest` and `by_path.sh` for plugin scripts, `claude plugin validate --strict` and `claude plugin test` for plugins and mods, `claude plugin eval` for plugins that have evals.
- CI/CD and GitHub Actions: `validate.yml` on every push and PR, `evals.yml` for changed plugins that have evals, `release.yml` tags each plugin after merge, and Claude reviewers run on pull requests.
- Tool sources: Node and npm via nvm; Python, ruff and basedpyright via uv; shfmt, ShellCheck and actionlint via Homebrew. Global configs are never overridden here; `ruff.toml` is the only ruff config in the repo.

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
- `.claude/skills/`: project skills (`plugin-development`, `plugin-consistency`, `github-workflow`).
- `.claude/specs/`: design specs.
- `.claude/plans/`: implementation plans.
- `.claude/templates/`: templates for plugin files and the root README.
- `.claude/rules/WORKFLOW.md`: how to work by task: quality checks, maintenance, plugins, hooks, versioning, GitHub, releases, skills and user docs.
- `docs/`: the user guides, covering installation, managing plugins, compatibility, FAQ, troubleshooting and tool references.

## Research and Sources

- Claude Code and the Claude app change almost daily: training data, memory and project docs are starting points, not the authority.
- Before any plan, answer, plugin component or scaffold, read the official sources for the installed Claude Code version and the pinned tool versions.
- When components connect or depend on each other, research each one equally, never one side only (e.g. a plugin hook reads the hooks reference, the plugins reference and the Claude app platform support).
- Check the Claude Code changelog and the Claude app release notes for changes the docs have not caught up with yet.
- The same standard applies to the Claude models themselves and to every tool the gates pin: research their current features and check their changelogs.

## Commands

Run from the repository root with the `.nvmrc` runtime selected. The gate commands run the versions CI pins in the `env` block of `.github/workflows/validate.yml`.

### Project

- `node .github/scripts/new-plugin.mjs --name <name> --category <id> --description "<sentence>" [--display-name "<Name>"] [--emoji <e>] [--min-claude-code <x.y.z>] [--claude-code-only]` - Run when scaffolding and registering a plugin.
- `node .github/scripts/catalog.mjs` - Run when regenerating the generated blocks of the root `README.md`.
- `node .github/scripts/bump-version.mjs <plugin> <major|minor|patch>` - Run when bumping a plugin in its PR.
- `node .github/scripts/release-notes.mjs <plugin> [--tag]` - Run when previewing a plugin's release notes or tag.
- `node .github/scripts/eval-targets.mjs --changed <base> <head>` or `--only <plugin|all>` - Run when listing the plugins whose evals CI would run.
- `node .github/scripts/sync-labels.mjs [--dry-run]` - Run when syncing the GitHub labels after a plugin is added.
- `ONLY=<plugin> .github/scripts/run-evals.sh` - Run when running a plugin's full eval suite.
- `claude --plugin-dir plugins/<plugin>` - Run when exercising a plugin in a live session.
- `git push origin <branch>` - Run when Nery orders a push. Never run a bare `git push`.
- For all other commands, read `.github/scripts/` and `.github/workflows/`.

### After Editing a File

Python:

- `uvx ruff@0.17.1 format <file>` - Run first, after every `.py` edit.
- `uvx ruff@0.17.1 check <file>` - Run after the formatter.
- `uvx --from mypy==1.20.2 mypy --strict <file>` - Run after ruff.
- `basedpyright --warnings <file>` - Run after mypy.
- `python3 -m unittest discover -s .github/scripts/tests/<plugin>` - Run when the file belongs to a plugin with Python tests.
- `.github/scripts/tests/<plugin>/by_path.sh` - Run when that plugin folder ships one.

JavaScript modules (`tsc` checks the whole project):

- `npx --yes @biomejs/biome@2.5.15 check --write --error-on-warnings <file>` - Run first, after every `.mjs` edit.
- `npx --yes --package typescript@6.0.3 tsc -p plugins/tsconfig.json --noEmit --typeRoots "$(npm root -g)/@types"` - Run when the file is under `plugins/`.
- `npx --yes --package typescript@6.0.3 tsc -p .github/scripts/tsconfig.json --noEmit --typeRoots "$(npm root -g)/@types"` - Run when the file is under `.github/scripts/`.
- `node --test ".github/scripts/tests/*.test.mjs"` - Run after the type check. Read the `skipped` count.
- `node .github/scripts/check-repo.mjs` - Run after the tests.

Mods (code in `hooks/*.ts`, tests in `tests/*.test.ts`):

- `npx --yes @biomejs/biome@2.5.15 check --write --error-on-warnings <file>` - Run first, after every `.ts` edit.
- `npx --yes --package typescript@6.0.3 tsc -p plugins/<plugin>/tsconfig.json --noEmit` - Run after Biome. The config extends the declarations the engine writes into `plugins/<plugin>/.claude-plugin/types/` when it loads the mod. Git ignores that folder, so after a fresh clone load the plugin once in an interactive session from a trusted folder (`claude --plugin-dir plugins/<plugin>`, then `/exit`) to write it. CI cannot run this gate for that reason.
- `claude plugin validate --strict plugins/<plugin>` - Run after tsc. It reads the mod the way the engine will. Pass `$` only inside `register.ts`: validation fails when `$` goes to a function imported from another file.
- `claude plugin test plugins/<plugin>` - Run last. Break the rule under test on purpose once and confirm its tests fail.

Shell:

- `shfmt -w <file>` - Run first, after every `.sh` edit.
- `shellcheck -o all -S style -x -a -P SCRIPTDIR <file>` - Run after shfmt.
- `.github/scripts/tests/<plugin>/by_path.sh` - Run when the script belongs to a plugin that ships one.

### Before Every Push

No git hook runs `.pre-commit-config.yaml`, and CI does not run `basedpyright`, the plugins' Python tests or the `by_path.sh` scripts: steps 12, 13 and 17 are local. CI installs `tsc` only so the TypeScript hook tests run; it does not type-check the `.mjs` files.

1. `git branch --show-current` - Confirm it is the intended branch, not a stale or merged one.
2. `git status --short` - Confirm no path is staged that you did not change.
3. `git log --format='%h %G? %s' origin/main..HEAD` - Confirm every commit shows `G`.
4. `node --test ".github/scripts/tests/*.test.mjs"` - Runs the script tests and the LSP hook tests. They need `shfmt`, `shellcheck`, `ruff` and `basedpyright` on `PATH`. Read the `skipped` count: a missing tool skips its cases.
5. `node .github/scripts/check-repo.mjs` - Checks the repository policy: manifests, required plugin files and sections, changelog entries, and the root `README.md` and `CHANGELOG.md`.
6. `node .github/scripts/catalog.mjs --check` - Fails when the generated blocks of the root `README.md` are out of date.
7. `.github/scripts/validate-claude.sh` - Runs `claude plugin validate --strict` on the marketplace and on every plugin, and `claude plugin test` on every plugin that ships mod tests.
8. `node .github/scripts/check-version-bump.mjs origin/main` - Fails when a plugin changed since `origin/main` without a version bump and a changelog entry. Skip it when `origin/main` does not exist.
9. `npx --yes @biomejs/biome@2.5.15 check --error-on-warnings .` - Checks the format, lint and imports of the JavaScript and JSON files.
10. `git ls-files -z '*.sh' | xargs -0 shellcheck -o all -S style -x -a -P SCRIPTDIR` - Lints every tracked shell script.
11. `git ls-files -z '*.sh' | xargs -0 shfmt -d` - Shows the formatting drift of every tracked shell script.
12. `python3 -m unittest discover -s .github/scripts/tests/<plugin>` - Runs the Python tests of one plugin. Repeat for each test folder with `test_*.py` files.
13. `.github/scripts/tests/<plugin>/by_path.sh` - Runs the plugin scripts by path, as Claude Code does. Repeat for each plugin folder that ships one.
14. `uvx ruff@0.17.1 check plugins .github/scripts` - Lints the Python files.
15. `uvx ruff@0.17.1 format --check plugins .github/scripts` - Checks the formatting of the Python files.
16. `git ls-files -z 'plugins/*.py' '.github/scripts/tests/*.py' | xargs -0 uvx --from mypy==1.20.2 mypy --strict` - Type-checks the Python files.
17. `basedpyright --warnings` - Type-checks the project's Python files outside hidden folders (DEBT-003).
18. `npx --yes --package typescript@6.0.3 tsc -p plugins/tsconfig.json --noEmit --typeRoots "$(npm root -g)/@types"` - Type-checks the `.mjs` files under `plugins/`.
19. `npx --yes --package typescript@6.0.3 tsc -p .github/scripts/tsconfig.json --noEmit --typeRoots "$(npm root -g)/@types"` - Type-checks the `.mjs` files under `.github/scripts/`.
20. `npx --yes --package typescript@6.0.3 tsc -p plugins/<plugin>/tsconfig.json --noEmit` - Type-checks the mod of each plugin that ships one. Run it locally: it needs the declarations the engine writes, which CI does not have.
21. `npx --yes markdownlint-cli2@0.23.3` - Lints the Markdown that people read.
22. `SHELLCHECK_OPTS='-o all -S style -x -a -P SCRIPTDIR' actionlint` - Lints the workflows. Run it only when `.github/workflows/` changed.

### Command Rules

- Script `sync-labels.mjs` writes GitHub labels; run `--dry-run` first.
- Script `run-evals.sh` spends API money: both arms, 3 runs per case, capped by `evals-config.json`. Run it only on Nery's request.
- Script `bump-version.mjs` rewrites `plugin.json` and the plugin changelog; use it instead of hand edits.
- `gh workflow run release.yml` tags and publishes; run it only per "When Releasing" in `.claude/rules/WORKFLOW.md`.
