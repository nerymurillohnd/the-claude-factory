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
- Migrate existing code on touch, not in a dedicated sweep: Mypy to Basedpyright, unittest to pytest, and bare `python3` maintainer entry points to the uv shebang. Plugin scripts keep `#!/usr/bin/env python3`.
- Migrate the whole touched unit at once (a script with its tests and its gate), never half of it. Until then, its current gates keep running and must pass.

## Quality gates

Consolidated here until Nery orders a rule file for them.

- After you edit, write or create a `.py`, `.mjs`, `.ts` or `.sh` file, run the commands for its type below right away, before the next task, in this order: formatter, linter, type checker, tests.
- Fix every finding before you advance to the next step, file or task. An issue stays open only when it waits on a decision or a spend only Nery can make: then stop and ask.
- After a delegated review, verify every finding against the files and the live docs before fixing it, then apply the confirmed ones in one coherent pass per file and re-read each touched file and its references (memory `apply-fixes-holistically`).

### After editing a file

Python:

- `ruff format <file>` - Run first, after every `.py` edit.
- `ruff check <file>` - Run after the formatter.
- `basedpyright --warnings <file>` - Run after ruff.
- The tests of the unit the file belongs to: the PEP 723 pytest runner for migrated code; `python3 -m unittest discover -s scripts/tests/<plugin>` until a plugin's tests are migrated.
- `scripts/tests/<plugin>/by_path.sh` - Run when that plugin folder ships one.
- Never run mypy on new or migrated code. The `mypy-scripts` and `mypy-plugins` gates run only over the unmigrated `.py` files and must pass until those migrate; `mypy-scripts` leaves out `scripts/schemas/`, `scripts/generators/` and `scripts/validators/` (`MIGRATED_PYTHON` in `scripts/gates.mjs`).

JavaScript modules (`tsc` checks the whole project):

- `biome check --write --error-on-warnings <file>` - Run first, after every `.mjs` edit.
- `tsc -p scripts/tsconfig.json --noEmit` - Run after Biome, for a file under `scripts/`; `-p scripts/tsconfig.plugins.json` for a file under `plugins/`.
- `node --test "scripts/tests/*.test.mjs"` - Run after the type check, and `node --test scripts/tests/<plugin>/*.test.mjs` when the file belongs to a plugin with Node tests. A skipped test means a missing tool: install it.
- `node scripts/check-repo.mjs` - Run after the tests.

Mods (code in `hooks/*.ts`, tests in `tests/*.test.ts`):

- `biome check --write --error-on-warnings <file>` - Run first, after every `.ts` edit.
- `head -1 plugins/<plugin>/.claude-plugin/types/claude-code/index.d.ts` - Run before trusting the mod's `tsc`: its `Written by Claude Code` version must equal `claude --version`; if not, reload the plugin interactively (`claude -p` never rewrites it).
- `tsc -p plugins/<plugin>/tsconfig.json --noEmit` - Run after Biome. The config extends the declarations the engine writes into `plugins/<plugin>/.claude-plugin/types/` when it loads the mod. Git ignores that folder, so after a fresh clone load the plugin once in an interactive session from a trusted folder (`claude --plugin-dir plugins/<plugin>`, then `/exit`) to write it. CI cannot run this gate for that reason.
- `claude plugin validate --strict plugins/<plugin>` - Run after tsc. It reads the mod the way the engine will. Pass `$` only inside `register.ts`: validation fails when `$` goes to a function imported from another file.
- `claude plugin test plugins/<plugin>` - Run last. Break the rule under test on purpose once and confirm its tests fail.

Shell:

- `shfmt -w <file>` - Run first, after every `.sh` edit.
- `shellcheck -o all -S style -x -a -P SCRIPTDIR <file>` - Run after shfmt.
- `scripts/tests/<plugin>/by_path.sh` - Run when the script belongs to a plugin that ships one.

### Before every push

Run `npm run gates` with the `.nvmrc` Node and after `npm ci` (ADR_2026-10-21_gates-run-from-one-script). `scripts/gates.mjs` is the one list of gates, the source of the commands below: it runs them in order, without a shell, stops at the first failure with that gate's exit code, and fails any gate whose tests skipped a case, since a skip means a tool is missing. Fix the cause and run it again from the start. No git hook runs it or `.pre-commit-config.yaml`.

| Group | Runs in | Gates |
| :-- | :-- | :-- |
| (before anything) | local | the branch, `git status`, every commit since `origin/main` signed `G` |
| `policy` | CI and local | the maintainer Node tests (`scripts/tests/*.test.mjs`), `check-repo.mjs`, `catalog.mjs --check`, `check-version-bump.mjs`, `tsc` on `scripts/`, ShellCheck and shfmt on `scripts/` |
| `python` | CI and local | ruff check, ruff format and basedpyright on `scripts/`; `mypy --strict` on its unmigrated `.py` |
| `claude` | CI and local | `claude plugin validate --strict` on the marketplace and on every plugin |
| `lint` | CI and local | Biome outside `plugins/`, actionlint |
| `local` | local only | the plugins' behavior: the tests in `scripts/tests/<plugin>/` (Node, Python and `by_path.sh`), `claude plugin test` for every mod, the mods' `tsc`; and the analysis of plugin code: `tsc -p scripts/tsconfig.plugins.json`, Biome, ShellCheck, shfmt, ruff, mypy and basedpyright on `plugins/` |

CI runs only the `policy`, `python`, `claude` and `lint` groups, one per job, with `npm run gates:ci -- --group <group>` (ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure): what is ours and what no user's machine changes. The plugins' behavior depends on the interpreter and tools of whoever installs them, so it is proven here before the push and, for a plugin that has them, by its evals in `evals.yml`. `--ci` changes only three things: it leaves out the `local` group, the version-bump base comes from `--base`, and the run goes on after a failure to list every failing gate.

The mods' `tsc` needs the declarations the engine writes into `plugins/<plugin>/.claude-plugin/types/`; after a fresh clone, load the plugin once in an interactive session (`claude --plugin-dir plugins/<plugin>`, then `/exit`).

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
