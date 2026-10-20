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
- Release gate: a plugin ships only when every requirement below has recorded evidence.
- Requirements: every gate passes, `plugin-reviewer` leaves no confirmed finding, the Claude app check passes (unless Claude Code-only), the README is accurate against the current docs, and the plugin is portable across macOS, Linux and Windows through Git Bash.

## Stack and Development

- Product: Claude Code plugins (skills, agents, hooks, MCP and LSP servers, mods) listed in `.claude-plugin/marketplace.json`, one folder per plugin under `plugins/`.
- Build: no build step and no runtime to maintain; no root `package.json`, `pyproject.toml` or virtual environment.
- Plugin code: Bash and POSIX-style Python 3 that run on whatever `bash` and `python3` the user has on `PATH`, with no version floor; `.mjs` modules type-checked by TypeScript 6.0.3; mods in TypeScript under `hooks/*.ts`.
- Repository tooling: Node scripts in `.github/scripts/` for scaffolding, catalog, version bumps, labels, policy checks and eval targets; Node 26 from `.nvmrc`.
- Formatting and linters: Biome for JavaScript and JSON; ruff, mypy and basedpyright for Python; shfmt and ShellCheck for shell; markdownlint-cli2 for Markdown; actionlint for workflows. Each runs at the version pinned in `.claude/rules/QUALITY_GATE.md` and `validate.yml`.
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
- `.claude/audits/`: repository and project audit reports.
- `.claude/memory/`: project memory (facts, feedback).
- `.claude/session-handoff/`: session handoffs.
- `.claude/specs/`: design specs.
- `.claude/plans/`: implementation plans.
- `.claude/templates/`: templates for plugin files and the root README.
- `.claude/rules/QUALITY_GATE.md`: per-file and pre-push checks.
- `.claude/rules/GITHUB_GATE.md`: PRs, labels, commits, pushes.
- `.claude/rules/MAINTENANCE_GATE.md`: docs kept in sync.
- `.claude/rules/RELEASES.md`: release steps after a plugin merge.
- `.claude/rules/PLUGIN_GATE.md`: building, portability, distribution and evals.
- `.claude/rules/SKILL_GATE.md`: how a skill references files.
- `.claude/rules/HOOKS_GATE.md`: how plugin hooks are declared, filtered, failed, tested and documented.
- `docs/`: the user guides, covering installation, managing plugins, compatibility, FAQ, troubleshooting and tool references.

## Research and Sources

- Claude Code and the Claude app change almost daily: training data, memory and project docs are starting points, not the authority.
- Before any plan, answer, plugin component or scaffold, read the official sources for the installed Claude Code version and the pinned tool versions.
- When components connect or depend on each other, research each one equally, never one side only (e.g. a plugin hook reads the hooks reference, the plugins reference and the Claude app platform support).
- Check the Claude Code changelog and the Claude app release notes for changes the docs have not caught up with yet.
- The same standard applies to the Claude models themselves and to every tool the gates pin: research their current features and check their changelogs.

## Plugin Development

- Do not start a new plugin while a released one lacks its Claude app check.
- Name skills and plugins for what the skill does, not how it is implemented.
- Write plugin Python as portable, POSIX-style code: it runs on whatever `python3` the user has on `PATH`, so there is no version floor. Check it here with our own tools.
- Keep the version in `plugin.json`. Never set `version` on a marketplace entry.
- Change `displayName` to relabel a plugin.
- After moving or creating files, delete `.DS_Store` files and orphaned cache directories.
- Do not set `hooks` in the frontmatter of a plugin agent: it is ignored. Declare the hook in the plugin's `hooks/hooks.json`.
- Test a hook in `settings.json` right after editing it: the file watcher loads it with no restart. A plugin hook needs `/reload-plugins`.
- Resolve `node` and `tsc` across every Node manager: plugin hooks and LSP servers get no shell profile.
- Set `"onFailure": "block"` on a check hook, so a broken hook never passes in silence.
- Report a missing tool as a non-blocking `systemMessage` plus `additionalContext`, never as a silent pass. A guard whose job is to deny is the exception: it denies the commands it guards and says what to install.
- Write one permission rule per hook `if` field. A rule joined with `|` never matches.
- Ship a plugin's Node dependencies only with an npm or Bun lockfile; other lockfiles leave no `node_modules`.
- Pass each strict `tsc` flag with an explicit value. `--strict` does not override an explicit `false` in a tsconfig.
- Test a hook script with `env -i`, an empty `HOME` and a minimal `PATH` for each Node manager.

## Commands

Run from the repository root with the `.nvmrc` runtime selected.

```bash
node .github/scripts/new-plugin.mjs --name <name> --category <id> --description "<sentence>" [--display-name 
"<Name>"] [--emoji <e>] [--min-claude-code <x.y.z>] [--claude-code-only]` - Run when scaffolding and registering a
plugin.
```
- `node .github/scripts/catalog.mjs` - Run when regenerating the generated blocks of the root `README.md`; `--check` only checks them.
- `node .github/scripts/check-repo.mjs` - Run when checking repository policy.
- `node .github/scripts/check-version-bump.mjs <base-ref>` - Run when checking that a changed plugin carries a bump and a changelog entry.
- `node .github/scripts/bump-version.mjs <plugin> <major|minor|patch>` - Run when bumping a plugin in its PR.
- `node .github/scripts/release-notes.mjs <plugin> [--tag]` - Run when previewing a plugin's release notes or tag.
- `node .github/scripts/eval-targets.mjs --changed <base> <head>` or `--only <plugin|all>` - Run when listing the plugins whose evals CI would run.
- `node .github/scripts/sync-labels.mjs [--dry-run]` - Run when syncing the GitHub labels after a plugin is added.
- `.github/scripts/validate-claude.sh` - Run when validating the marketplace, `.claude/` and every plugin with `claude plugin validate --strict`, plus mod tests.
- `ONLY=<plugin> .github/scripts/run-evals.sh` - Run when running a plugin's full eval suite.
- `claude --plugin-dir plugins/<plugin>` - Run when exercising a plugin in a live session.
- For all other commands, read `.github/scripts/` and `.github/workflows/`.

### Command Rules

- Script `sync-labels.mjs` writes GitHub labels; run `--dry-run` first.
- Script `run-evals.sh` spends API money: both arms, 3 runs per case, capped by `evals-config.json`. Run it only on Nery's request.
- Script `bump-version.mjs` rewrites `plugin.json` and the plugin changelog; use it instead of hand edits.
- `gh workflow run release.yml` tags and publishes; run it only per `.claude/rules/RELEASES.md`.
