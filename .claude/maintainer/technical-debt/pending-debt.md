# 🧾 Pending Debt

> [!NOTE]
> Unresolved technical or maintenance conditions that cannot be fixed now. Each one has evidence, an owner and a way out. Closed items move to `closed-debt.md`.

## 🎯 Entry criteria

Add an item only when all of these hold:

- A specific condition is observable or backed by traceable evidence. No speculation.
- It has a real operational, security, reliability, compatibility or maintainability impact.
- It cannot be fixed now: it waits on a decision, access, spend or an external party, or the risk is accepted on purpose.
- A concrete next action exists, or a concrete condition that triggers reassessment.
- No other active record tracks it, such as an open issue or an ADR follow-up.

> [!WARNING]
> Do not add improvement ideas, speculation or a copy of the backlog. A problem that can be fixed now gets fixed, not logged.

## 🔄 Record maintenance

| Action | When | Rule |
| --- | --- | --- |
| ➕ Append | A new condition appears | Search both ledgers for the same condition first. |
| ✏️ Update | Evidence, impact, owner or next action changes | Revise in place. Keep confirmed facts apart from inference. |
| ✅ Resolve | The fix is verified | Move the entry to `closed-debt.md` with the same ID. Never just delete it. |

> [!IMPORTANT]
> An item moves to resolved debt only after the fix works and the original failure no longer reproduces.

## 🚦 Status legend

| Icon | Status | Meaning |
| --- | --- | --- |
| 🟡 | Pending | Confirmed, not yet worked on |
| 🔵 | In progress | A change is under way |
| 🟠 | Blocked | Waiting on a decision, access, spend or an external party |
| 🔴 | Risk accepted | Known and deliberately kept; its review condition still applies |

## 📋 Index

| ID | Title | Status |
| --- | --- | --- |
| DEBT-002 | Version-bump check fails on main after a revert of an unreleased bump and blocks every release | 🟠 Blocked |
| DEBT-006 | No gate runs the validators of `scripts/validators/`, so CI lost the checks `check-repo.mjs` dropped | 🟡 Pending |
| DEBT-010 | The mod gates of `scripts/gates.mjs` can miss a mod or report green on a lost test summary | 🟠 Blocked |
| DEBT-013 | The plugins' Markdown is not formatted or linted by Biome until each plugin next changes | 🔴 Risk accepted |

## 📂 Open items

### DEBT-002 — Version-bump check fails on main after a revert of an unreleased bump and blocks every release

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | reliability, quality |
| **Owner** | `scripts/check-version-bump.mjs` and the `version-bump` gate of `scripts/gates.mjs`, run by the `policy` job of `.github/workflows/validate.yml` |
| **Logged** | 2026-10-20 |

#### 🔎 Evidence

- **Confirmed facts:**
  - `.github/workflows/validate.yml` runs `check-version-bump.mjs` against `github.event.before` on a push and against the PR base on a pull request. `release.yml` runs only when `Validate` succeeds on a push to `main`, and it then tags every plugin whose current version has no tag.
  - On 2026-10-20 [PR #31](https://github.com/nerymurillohnd/the-claude-factory/pull/31) reverted [PR #27](https://github.com/nerymurillohnd/the-claude-factory/pull/27), so `plugins/bash-lsp-intelligence` went from 0.2.2 (never tagged) back to 0.2.1. The "Repository policy & script tests" job failed on the PR and on the push of `ad3951f` (run 39476280906) at the version-bump step: `files changed (...) but version is still 0.2.2`.
  - Reproduced locally on `ad3951f` with `node .github/scripts/check-version-bump.mjs a223707`: exit 1 with that message. With base `origin/main` it passes.
  - `git diff bash-lsp-intelligence--v0.2.1 origin/main -- plugins/bash-lsp-intelligence` is empty: the plugin is byte-identical to its last release, so no bump is warranted.
  - Because `Validate` is red on `main`, `Release` stays skipped. On 2026-10-20 no tag existed for python-lsp-intelligence 0.2.2, typescript6-lsp-intelligence 0.2.1 or typescript7-lsp-intelligence 0.3.1, all merged the same day.
- **Inferences:** any revert of a bump that was never released fails the same way, because the check compares with the previous commit, not with the last published tag (not tested beyond this case).
- **Open questions:** whether the check should compare each plugin with its latest release tag, accept a version equal to the latest tag, or stay as it is.

#### 📈 Impact and next step

- **Impact / risk:** one red `Validate` on `main` blocks the release of every plugin until a later push, outside `plugins/`, passes. The next push compares against the red commit, so it recovers by itself, but the failure repeats on the next revert.
- **Why it is not fixed now:** the rule for reverts, and how the check treats a version that returns to the last tag, is a design decision for Nery. This task was only to get the pending releases out.
- **Next action:** decide with Nery whether `check-version-bump.mjs` compares each plugin with its latest `<plugin>--v*` tag instead of the previous commit. If yes, change it with tests for both cases: a revert to the tagged state passes and an edit without a bump still fails.
- **Review condition:** closes when a revert of an unreleased bump passes `Validate` on `main` and a plugin change without a bump still fails it.
- **Related records:** [PR #27](https://github.com/nerymurillohnd/the-claude-factory/pull/27), [PR #31](https://github.com/nerymurillohnd/the-claude-factory/pull/31); the `release-and-versioning` skill.

### DEBT-006 — No gate runs the validators of `scripts/validators/`, so CI lost the checks `check-repo.mjs` dropped

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | quality, reliability |
| **Owner** | `scripts/gates.mjs`, `.github/workflows/validate.yml` |
| **Logged** | 2026-10-24 |

#### 🔎 Evidence

- **Confirmed facts:**
  - On 2026-10-24 `check-repo.mjs` stopped checking entry names, sources, directories, renames, the manifest name and homepage, the required files, SemVer, the entry version, `[Unreleased]`, the current version's section and the root CHANGELOG (commit `942df1e`), because the eight validators of `scripts/validators/` own them.
  - `scripts/gates.mjs` has no gate for any validator; `grep -n validators scripts/gates.mjs` finds only `MIGRATED_PYTHON`. There are nine validators now (`skill-names-consistency.py` was added on 2026-10-24).
  - `npm run validate` runs all nine and fails if one fails. The project `PreToolUse` hook `.claude/hooks/validators-gate.sh` runs it before every `git push` made from a Claude Code session in this repository and denies the push on a failure. A push from a plain terminal and every CI run skip them.
  - The four schema validators and `skill-names-consistency.py` need uv and Python 3.15 (inline metadata); the other four need a `python3` that is 3.15 (`TypeIs`, the `type` statement). CI's `python` job runs `uv python install 3.15`.
- **Inferences:** a pull request that breaks a plugin name, version or required file passes CI.
- **Open questions:** which CI group each validator joins, and whether the standard-library ones get a `python3` that is 3.15 there.

#### 📈 Impact and next step

- **Impact / risk:** the checks moved out of `check-repo.mjs` run automatically only on a push from a Claude Code session, never in CI.
- **Why it is not fixed now:** Nery limited the deduplication to the scripts and asked not to touch gates or CI in that task.
- **Next action:** add one gate per validator to the `python` group of `scripts/gates.mjs`, run by path, and confirm the CI `python` job runs them on Python 3.15.
- **Review condition:** closes when `npm run gates:ci -- --group python` runs all nine validators and a defect planted in a copy fails the run.
- **Related records:** ADR_2026-10-24_repository-checks-move-to-python-validators, ADR_2026-10-21_gates-run-from-one-script.

### DEBT-010 — The mod gates of `scripts/gates.mjs` can miss a mod or report green on a lost test summary

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | reliability, quality |
| **Owner** | Maintainer tooling (`scripts/gates.mjs`) |
| **Logged** | 2026-10-25 |

#### 🔎 Evidence

- **Confirmed facts (read on 2026-10-25):**
  - `scripts/gates.mjs:392-404` creates the `mod-test:<plugin>` gate only for plugins with tracked `*.test.ts` or `*.test.tsx` files, not for every plugin whose `hooks/hooks.json` lists `modules`.
  - `scripts/gates.mjs:406-417` creates the `mod-tsc:<plugin>` gate for any plugin with a `tsconfig.json`, and nothing refreshes the engine's declarations before it runs.
  - `scripts/gates.mjs:494` runs every gate with `stdio: ['ignore', 'pipe', 'pipe']`, so `claude plugin test` writes to a pipe.
  - anthropics/claude-code#103055 reports that `claude plugin test` on a pipe can lose the tail of its output, summary included, and exit 0. `testing-mods/scripts/check-mod.sh` writes to a file and fails without the summary.
- **Inferences:**
  - A mod without tests is never run by `claude plugin test` in the gates.
  - A failed test can pass the gate when the summary is lost.
  - `tsc` runs against declarations from an older build after an update.
- **Open questions:** whether #103055 still reproduces on 2.1.310 through `spawnSync` with pipes.

#### 📈 Impact and next step

- **Impact / risk:** the local release proof for a mod can report green on a mod that fails its tests, or that has none, and reach users.
- **Why it is not fixed now:** Nery deferred it on 2026-10-25 to keep the session on consolidating the mod documentation.
- **Next action:**
  - key `mod-test` on `modules` in `hooks/hooks.json`;
  - run `claude plugin test` with its output in a file, and fail when the `Ran N tests across N files` summary is missing, as `check-mod.sh` does;
  - name `mod-tsc` for what it checks, and check the declarations' `// Written by Claude Code <version>.` header against `claude --version` before `tsc`.
- **Review condition:** closes when a mod with no tests fails the gate, a test run with its summary removed fails it, and stale declarations are reported.
- **Related records:** ADR_2026-10-21_gates-run-from-one-script, ADR_2026-10-25_building-mods-skill-holds-mod-authoring.

### DEBT-013 — The plugins' Markdown is not formatted or linted by Biome until each plugin next changes

| Field | Value |
| --- | --- |
| **Status** | 🔴 Risk accepted |
| **Category** | quality, maintainability |
| **Owner** | `biome.json` (`!plugins/<name>/**/*.md` lines) and each plugin's next change, through `building-plugins` step 5 |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:**
  - On 2026-10-26, Biome 2.6.3 with Markdown enabled reformatted 202 Markdown files across all 17 plugins in a scratch worktree.
  - `biome.json` lists one `!plugins/<name>/**/*.md` line per plugin, 17 lines, so `biome ci plugins` reads none of their Markdown.
  - `building-plugins` step 5 removes a plugin's line and runs `biome check --write plugins/<name>` in that plugin's next change.
- **Inferences:** a plugin that never changes again keeps its Markdown unformatted and unlinted.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** a heading jump, a fenced block without a language or a malformed table in a plugin's README, skill reference or changelog passes every check until that plugin changes.
- **Why it is not fixed now:** formatting all 17 plugins at once would ship 17 versions whose only change is whitespace; Nery chose adoption on each plugin's next change (ADR_2026-10-26_biome-formats-and-lints-maintainer-markdown).
- **Next action:** in each plugin's next change, follow `building-plugins` step 5 and remove its line from `biome.json`.
- **Review condition:** closes when `biome.json` has no `!plugins/<name>/**/*.md` line left and `biome ci --error-on-warnings plugins` passes.
- **Related records:** ADR_2026-10-26_biome-formats-and-lints-maintainer-markdown.

<!--
Entry format. Copy this block above this comment for each new item and add its row to the Index.
Replace NNN with the next free number. Delete these instructions from the copy.

### DEBT-NNN — {{Short debt title}}

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | {{security, compatibility, cost, quality, ...}} |
| **Owner** | {{Person, team, system or repository area; "unassigned" if truly unowned}} |
| **Logged** | {{YYYY-MM-DD}} |

#### 🔎 Evidence

- **Confirmed facts:** {{Paths, revisions, commands, dates: what is actually verified.}}
- **Inferences:** {{Reasoned conclusions not directly verified, or "none".}}
- **Open questions:** {{Questions that affect the assessment, or "none".}}

#### 📈 Impact and next step

- **Impact / risk:** {{Current or plausible impact.}}
- **Why it is not fixed now:** {{The decision, access, spend or external party it waits on, or why the risk is accepted.}}
- **Next action:** {{The smallest concrete action that advances or resolves this.}}
- **Review condition:** {{Event, date or evidence that triggers reassessment or permits closure.}}
- **Related records:** {{Links to issues, ADRs or PRs, or "none".}}
-->
