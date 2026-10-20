# 🧾 Pending Debt

> [!NOTE]
> Unresolved technical or maintenance conditions that cannot be fixed now. Each one has evidence, an owner and a way out. Fixed items move to `resolved-debt.md`.

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
| ✅ Resolve | The fix is verified | Move the entry to `resolved-debt.md` with the same ID. Never just delete it. |

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
| DEBT-001 | pr-tracker gets no GitHub tools when the GitHub MCP server has another name | 🟡 Pending |
| DEBT-002 | Version-bump check fails on main after a revert of an unreleased bump and blocks every release | 🟠 Blocked |
| DEBT-003 | basedpyright checks only half of the repository's Python files and never runs in CI | 🟠 Blocked |

## 📂 Open items

### DEBT-001 — pr-tracker gets no GitHub tools when the GitHub MCP server has another name

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | compatibility, reliability |
| **Owner** | `plugins/github-operations` (agent `pr-tracker`, skill `auto-pr-lifecycle`) |
| **Logged** | 2026-10-19 |

#### 🔎 Evidence

- **Confirmed facts:**
  - `plugins/github-operations/agents/pr-tracker.md` (plugin 0.3.1) sets `tools:` to `ToolSearch` plus exact MCP tool names under two prefixes only: `mcp__plugin_github-operations_github__*` and `mcp__github__*`.
  - On 2026-10-19, in a Claude Code desktop (Code tab) session on PR #22, the session's GitHub tools were named `mcp__650eb531-f579-4af8-a637-6ce6bd506b6b__*`, and no `mcp__plugin_github-operations_github__*` tool was loaded. The `pr-tracker` launched with only `ToolSearch` (plus its hand-back tool), found no GitHub tool and reported `BLOCKED` with nothing inspected; the main session observed the PR with `gh` instead.
  - The loaded copy in that session was `github-operations@synced` 0.3.0; the repository's 0.3.1 has the same fixed-name list, so the published version is affected too.
  - `claude mcp list` in the CLI shows `plugin:github-operations:github` connected with the token set, so the CLI tracker gets its tools.
  - [sub-agents docs](https://code.claude.com/docs/en/sub-agents) ("Restrict which tools a subagent can use"): `tools` is an allowlist resolved against the session's pool; `disallowedTools` is a denylist that keeps MCP tools inherited; when nothing in `tools` resolves, Claude Code usually refuses to launch the subagent. Here `ToolSearch` resolved, so it launched.
  - [hooks docs](https://code.claude.com/docs/en/hooks): plugin `PreToolUse` hooks fire inside subagents, and the input carries `agent_type`.
- **Inferences:** the `650eb531-…` server is the GitHub connector Nery added in the Claude app (not verified). Any user who turns the plugin on in the Claude app, connects the connector and works in the desktop Code tab gets a blind tracker, because the connector's UUID name is unpredictable.
- **Open questions:** why the desktop session did not load the plugin's own `github` server alongside the connector; whether `agent_type` for a plugin agent arrives as `github-operations:pr-tracker` (to test live).

#### 📈 Impact and next step

- **Impact / risk:** in that setup the PR lifecycle loses its monitoring agent; every tracker round is wasted and the main session must observe with `gh`. The tracker reports the gap honestly, so there is no false "clean" result.
- **Why it is not fixed now:** one open task at a time: svelte-development (PR #22) is in progress, and Nery chose to fix github-operations after it merges (2026-10-19).
- **Next action:** fix option A in github-operations, chosen by Nery: replace `tools:` with `disallowedTools: Edit, Write, NotebookEdit, Bash, PowerShell, Agent` so the agent inherits GitHub tools under any server name; add a `PreToolUse` hook in the plugin's `hooks/hooks.json` that blocks write MCP methods (merge, create, update, delete, resolve, rerun) when `agent_type` is the tracker; have `auto-pr-lifecycle` check which GitHub MCP prefix the session has before delegating and go to `gh` when none matches. Test the hook live, including the `agent_type` value.
- **Review condition:** closes when the tracker, run from the desktop Code tab with only the Claude app connector, reads a PR's checks and reviews, and its write calls are blocked by the hook.
- **Related records:** PR #22 (where it was observed); ADR_2026-10-18_fold-pr-diagnostics-into-pr-tracker.

### DEBT-002 — Version-bump check fails on main after a revert of an unreleased bump and blocks every release

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | reliability, quality |
| **Owner** | `.github/scripts/check-version-bump.mjs` and the "Version bumps" step of `.github/workflows/validate.yml` |
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
- **Related records:** [PR #27](https://github.com/nerymurillohnd/the-claude-factory/pull/27), [PR #31](https://github.com/nerymurillohnd/the-claude-factory/pull/31); `.claude/rules/RELEASES.md`.

### DEBT-003 — basedpyright checks only half of the repository's Python files and never runs in CI

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality |
| **Owner** | `.claude/rules/QUALITY_GATE.md` (step 17), `.github/workflows/validate.yml`, `.pre-commit-config.yaml` |
| **Logged** | 2026-10-20 |

#### 🔎 Evidence

- **Confirmed facts:**
  - `basedpyright --warnings --verbose` (basedpyright 1.40.2, based on pyright 1.1.414) at the repository root prints `Auto-excluding **/.*` and `Found 2 source files`, then `0 errors, 0 warnings, 0 notes`. The repository tracks 4 `.py` files; the two under `.github/scripts/tests/` are never checked by QUALITY_GATE step 17.
  - No basedpyright config exists: `pyrightconfig.json` (`{"pythonVersion": "3.9"}`) was deleted in 56d0115, and there is no `pyproject.toml`.
  - `basedpyright --warnings` on the 4 files passed explicitly reports `0 errors, 0 warnings, 0 notes` (2026-10-20), so nothing is hidden today.
  - No `# pyright:`, `# type: ignore` or `# noqa` comment exists in the 4 files.
  - `validate.yml` never runs basedpyright. Its only other caller, `.pre-commit-config.yaml` (hook `basedpyright`, `--warnings`, rev 1.40.2), is run by no git hook, per QUALITY_GATE.
  - mypy (`--strict`, step 16) and ruff (steps 14 and 15) do cover all 4 files.
- **Inferences:** none.
- **Open questions:** whether basedpyright gets an explicit scope (a config with `include`, or the file list as in step 16) and a CI job, or mypy stays the only type check for `.github/`.

#### 📈 Impact and next step

- **Impact / risk:** a basedpyright finding in a Python test under `.github/scripts/tests/` would pass every gate, and a finding anywhere would reach `main` whenever the local step 17 is skipped. The gate report "0 errors" reads as full coverage when it is not.
- **Why it is not fixed now:** the scope and whether CI runs it are Nery's call (handoff 2026-10-20-2228, item 3).
- **Next action:** decide with Nery; if yes, change step 17 to `git ls-files -z '*.py' | xargs -0 basedpyright --warnings`, add the same command to `validate.yml`, and confirm with `--verbose` that it reports 4 source files.
- **Review condition:** closes when step 17 and CI check every tracked `.py` file, or when Nery accepts mypy as the only type check for `.github/`.
- **Related records:** none.

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
