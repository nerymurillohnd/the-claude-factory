# The Claude Factory

Public Claude Code plugin marketplace (`github.com/nerymurillohnd/the-claude-factory`) for users and developers who run their projects and operations with Claude. It ships plugins only, built for Claude Code and, where they apply, for the Claude app. It is built in Nery's local clone and served to users from the remote repository. Users contribute through issues.

This project also follows the guidelines and way of working in the `@~/.claude/CLAUDE.md` and the global cross-projects lessons in `@~/.claude/LESSONS.md`.

The order of work, stage by stage, is a map whose steps each name the skill or rule that governs it: @WORKFLOW.md

## Responsibility

- Nery and Claude Code are the only parties who work on this marketplace. Claude Code acts only with Nery's authorization. There are no outside collaborators, and pull requests from users are not accepted.
- Users take part only through issues. Triaging, confirming, fixing, verifying and releasing the fix for every issue is Nery's and Claude Code's work, never the reporter's.
- No third-party team reviews our work before users install it, so every push, release and issue reply is the last check before the public: verify it before it goes out.
- Automate recurring work (validation, review, releases, drift checks, issue handling) with CI, evals, hooks, agents and scheduled tasks. Where none exists yet, propose building it.

## Current Claude Code features, capabilities, and guidance enforcement

Claude Code, the Claude app, the Claude models and every tool the gates run change faster than training data, recall or project docs. Before any plan, plugin component or scaffold, and before any answer about how they behave, read the current official documentation and release notes.

- When docs and release notes differ, the release notes win: docs lag releases.
- When components depend on each other, research each side. For example, a plugin hook needs the hooks reference, the plugins reference and the Claude app platform-support page.

## Purpose and release gate

- Goal: publish plugins that automate and optimize everyday workflows.
- One plugin covers its whole domain: knowledge, enforcement, tooling, review and proof that it works.
- Plugins are for third parties whose setups are unknown. Every plugin works from what its README declares, never from what is installed on Nery's machine.
- A plugin ships only when each of these has recorded evidence:
  - every gate passes;
  - the plugin review leaves no confirmed finding;
  - the README's Claude app claims match `docs/compatibility.md` and the official Claude app pages (not needed for Claude Code-only plugins);
  - the README is accurate against the current official docs;
  - the plugin runs on macOS and Linux, and on Windows through Git Bash when its README declares Windows support.

## Scopes

This repository has two distinct scopes: maintainer infrastructure and distributable plugins.

- Plugins are self-contained, portable within their declared requirements, and independent of maintainer tooling. They run on the user's machine, where the maintainer toolchain (uv, PEP 723 execution, the maintainer's Python version, the root `package.json`) does not exist.
- Maintainer scripts, dependencies and execution requirements stay separate from plugin runtimes. Maintainer tooling runs only in maintainer and development environments and in CI.
- Maintainer code and plugin code have separate runtimes and separate Basedpyright configurations.

## Working rules

- Fix technical debt inside the task's scope as part of the task. Record it as pending only when fixing it would change the task's scope substantially or cannot be done.
- Fix every issue a hook, script, formatter, linter or diagnostic reports; never skip or suppress it.
- Justify each choice in a plugin's design (name, skills, agents, structure) individually; precedent in another plugin is not a justification.

## Tooling

The rules live in `.claude/rules/maintainer-tooling.md`, `.claude/rules/plugin-tooling.md` and `.claude/rules/node-tooling.md`, which load in every session. This is the context their decisions rely on:

- Basedpyright is the only type checker, for maintainer and plugin Python. Mypy is not used.
- `tsc` and Biome are to JavaScript and TypeScript what Basedpyright and Ruff are to Python: maintainer tools that check both maintainer and plugin code, installed on the machine and never declared in the root `package.json`. Biome also formats and lints JSON; `biome.json` decides which file types it covers.
- The CLI gate is the authority for diagnostics. The editor and hooks are views of it and must match it.
- Diagnostics from any additional checker fall into one of three classes: implementation defects, policy checks, inference limitations. Another checker is justified only by documented defects that the current stack misses.
- `PYTHONSAFEPATH=1` only prevents automatic prepending of the script directory to the import path. It is not a sandbox.
- `uv python find --script <file>` returns the base interpreter, without the script's dependencies, until `uv sync --script <file>` has run.
- `requires-python` is what bounds the Python version, including in CI.

## Migration

- New code follows the tooling rules from the start.
- Migrate existing code on touch, not in a dedicated sweep: Mypy to Basedpyright, unittest to pytest, and maintainer entry points that need third-party dependencies to the uv shebang; standard-library-only ones keep `#!/usr/bin/env python3`. Plugin scripts keep `#!/usr/bin/env python3`.
- Migrate the whole touched unit at once (a script with its tests and its gate), never half of it. Until then, its current gates keep running and must pass.

## Quality gates

Consolidated here until Nery orders a rule file for them.

- Format, lint, and typecheck your work after each edit, in the order below, then run the tests of the unit you touched.
- Fix every finding before you advance to the next step, file or task.
- A skipped test means a missing tool: install it, never skip it.

### After editing a file

Python:

- `ruff format <file>`, then `ruff check <file>`, then `basedpyright --warnings <file>`.
- The unit's tests: the PEP 723 pytest runner for migrated code; `python3 -m unittest discover -s scripts/tests/<plugin>` until a plugin's tests migrate.
- Never run mypy on new or migrated code; `MIGRATED_PYTHON` in `scripts/gates.mjs` lists the folders the `mypy-scripts` gate leaves out.

JavaScript modules (`tsc` checks the whole project):

- `biome check --write --error-on-warnings <file>`.
- `tsc -p scripts/tsconfig.json --noEmit` for a file under `scripts/`; `-p scripts/tsconfig.plugins.json` for one under `plugins/`.
- `node --test "scripts/tests/*.test.mjs"`, plus `node --test scripts/tests/<plugin>/*.test.mjs` for a plugin with Node tests.
- `node scripts/check-repo.mjs`.

Mods (code in `hooks/*.ts`, tests in `tests/*.test.ts`):

- `biome check --write --error-on-warnings <file>`.
- `head -1 plugins/<plugin>/.claude-plugin/types/claude-code/index.d.ts`: its `Written by Claude Code` version must equal `claude --version` before you trust `tsc`; refresh the declarations as `.claude/rules/mods.md` says. CI cannot run the next gate, because git ignores them.
- `tsc -p plugins/<plugin>/tsconfig.json --noEmit`.
- `claude plugin validate --strict plugins/<plugin>`. Pass `$` only inside `register.ts`: validation fails when `$` goes to a function imported from another file.
- `claude plugin test plugins/<plugin>`.

Shell:

- `shfmt -w <file>`, then `shellcheck -o all -S style -x -a -P SCRIPTDIR <file>`.

Any type: `scripts/tests/<plugin>/by_path.sh` when the plugin you edited ships one.

### Before every push

Run `npm run gates` (ADR_2026-10-21_gates-run-from-one-script). `scripts/gates.mjs` is the one list of gates: it runs them in order without a shell, stops at the first failure with that gate's exit code, and fails a gate whose tests skipped a case. Fix the cause and run it again from the start. No git hook or `.pre-commit-config.yaml` runs it.

| Group | Runs in | Gates |
| :-- | :-- | :-- |
| (before anything) | local | the branch, `git status`, every commit since `origin/main` signed `G` |
| `policy` | CI and local | the maintainer Node tests (`scripts/tests/*.test.mjs`), `check-repo.mjs`, `catalog.mjs --check`, `check-version-bump.mjs`, `tsc` on `scripts/`, ShellCheck and shfmt on `scripts/` |
| `python` | CI and local | ruff check, ruff format and basedpyright on `scripts/`; `mypy --strict` on its unmigrated `.py` |
| `claude` | CI and local | `claude plugin validate --strict` on the marketplace and on every plugin |
| `lint` | CI and local | Biome outside `plugins/`, actionlint |
| `local` | local only | the plugins' behavior: the tests in `scripts/tests/<plugin>/` (Node, Python and `by_path.sh`), `claude plugin test` for every mod, the mods' `tsc`; and the analysis of plugin code: `tsc -p scripts/tsconfig.plugins.json`, Biome, ShellCheck, shfmt, ruff, mypy and basedpyright on `plugins/` |

CI runs one group per job with `npm run gates:ci -- --group <group>`, every group but `local`: plugin behavior depends on the user's machine, so it is proven here and by each plugin's evals (ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure). `--ci` also takes the version-bump base from `--base` and keeps going after a failure to list every failing gate.

Report the run as a table: gate, result and key output line.

## Versioning and Releases

Rules for this area live in `.claude/rules/plugins/versioning-and-releases.md`. Context they rely on:

- Claude Code treats a plugin's `version` in `plugin.json` as a pin and does not check it against SemVer. Users stay on that version until it changes, and commits pushed without a bump never reach them. SemVer is this project's convention, and it is why every functional plugin change needs a bump.
- A `0.x` version makes no interface-stability promise; `1.0.0` does.
- The next green push to `main` tags every plugin whose `plugin.json` version has no tag yet, so a version left pending ships on that push. `release.yml` can also be run by hand.

## Documentation and Maintenance

- `.claude/WORKFLOW.md`: the stage map, imported above.
- `.claude/rules/`: the rules; those without `paths` load in every session, the rest when Claude reads or edits a matching file.
- `.claude/maintainer/decisions/`: ADRs for important decisions.
- `.claude/maintainer/technical-debt/`: pending and closed debt.
- `.claude/memory/`: project memory (facts, feedback).
- `.claude/session-handoff/`: session handoffs.
- `.claude/skills/`: project skills, the procedures for work on this repository.
- `.claude/specs/`: design specs.
- `.claude/plans/`: implementation plans.
- `.claude/templates/`: templates for plugin files, the root README and the plugin review brief.
- `docs/`: the user guides, covering installation, managing plugins, compatibility, FAQ, troubleshooting and tool references.

## Commands

**Command Rules:**

1. Script `sync-labels.mjs` writes GitHub labels; run `--dry-run` first.
2. Script `run-evals.sh` spends API money: both arms, 3 runs per case, capped by `evals-config.json`. Run it only on Nery's request.
3. Script `bump-version.mjs` rewrites `plugin.json` and the plugin changelog; use it instead of hand edits.
4. `gh workflow run release.yml` tags and publishes; run it only per the `release-and-versioning` skill.
5. Run from the repository root with the `.nvmrc` runtime selected (`npm ci` per `node-tooling.md`).

- `node scripts/new-plugin.mjs --name <name> --category <id> --description "<sentence>" [--display-name "<Name>"] [--emoji <e>] [--min-claude-code <x.y.z>] [--claude-code-only]` - Run when scaffolding and registering a plugin.
- `node scripts/catalog.mjs` - Run when regenerating the generated blocks of the root `README.md`.
- `node scripts/bump-version.mjs <plugin> <major|minor|patch>` - Run when bumping a plugin in its PR.
- `node scripts/release-notes.mjs <plugin> [--tag]` - Run when previewing a plugin's release notes or tag.
- `node scripts/eval-targets.mjs --changed <base> <head>` or `--only <plugin|all>` - Run when listing the plugins whose evals CI would run.
- `node scripts/sync-labels.mjs [--dry-run]` - Run when syncing the GitHub labels after a plugin is added.
- `ONLY=<plugin> scripts/run-evals.sh` - Run when running a plugin's full eval suite.
- `claude --plugin-dir plugins/<plugin>` - Run when exercising a plugin in a live session.
- `git push origin <branch>` - Run when Nery orders a push. Never run a bare `git push`.
