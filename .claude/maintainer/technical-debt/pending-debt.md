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
| DEBT-001 | pr-tracker gets no GitHub tools when the GitHub MCP server has another name | 🔵 In progress |
| DEBT-002 | Version-bump check fails on main after a revert of an unreleased bump and blocks every release | 🟠 Blocked |
| DEBT-006 | No gate runs the validators of `scripts/validators/`, so CI lost the checks `check-repo.mjs` dropped | 🟡 Pending |
| DEBT-008 | `main` and the release tags have no GitHub protection | 🟠 Blocked |
| DEBT-009 | Biome ignores Markdown, so no tool formats or lints the repository's Markdown | 🟡 Pending |
| DEBT-010 | The mod gates of `scripts/gates.mjs` can miss a mod or report green on a lost test summary | 🟡 Pending |

## 📂 Open items

### DEBT-001 — pr-tracker gets no GitHub tools when the GitHub MCP server has another name

| Field | Value |
| --- | --- |
| **Status** | 🔵 In progress |
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
  - On 2026-10-21 it happened again on [PR #36](https://github.com/nerymurillohnd/the-claude-factory/pull/36) in the desktop Code tab: the tracker found no `mcp__plugin_github-operations_github__*` or `mcp__github__*` tool while the session's GitHub tools were `mcp__650eb531-…__*`, and reported `BLOCKED`.
  - On 2026-10-21, on branch `fix/pr-tracker-inherit-tools`, Nery had the agent's `tools` allowlist removed with no `disallowedTools`, so it inherits every tool of the session (Bash, Edit, Write and GitHub write methods included); the bullets of its "Tools" section (prefixes, `ToolSearch`, missing-tool handling) were removed, leaving the call table, and its role still calls it a read-only observer. The README FAQ now says the agent can use every session tool and points to deny rules for a hard limit. [sub-agents docs](https://code.claude.com/docs/en/sub-agents): `disallowedTools` wildcards cover one server or all MCP tools (`mcp__*`), not one method across servers, so write methods can't be denied by name for an unknown server.
  - That change merged with [PR #37](https://github.com/nerymurillohnd/the-claude-factory/pull/37) on 2026-10-22 (`4d0d65e`) and ships in github-operations 0.4.0: `agents/pr-tracker.md` has no `tools:` or `disallowedTools:` line, and the plugin has no `hooks/` folder.
  - On 2026-10-22 the tracker (0.4.0, CLI session with `plugin:github-operations:github` connected) read the checks, reviews, diff and Dependabot alerts of [PR #38](https://github.com/nerymurillohnd/the-claude-factory/pull/38) twice and reported `READY_FOR_MAIN_SESSION`. This is not the desktop Code tab case the review condition names.
- **Inferences:** the `650eb531-…` server is the GitHub connector Nery added in the Claude app (not verified). Any user who turns the plugin on in the Claude app, connects the connector and works in the desktop Code tab gets a blind tracker, because the connector's UUID name is unpredictable.
- **Open questions:** why the desktop session did not load the plugin's own `github` server alongside the connector; whether `agent_type` for a plugin agent arrives as `github-operations:pr-tracker` (to test live).

#### 📈 Impact and next step

- **Impact / risk:** in that setup the PR lifecycle loses its monitoring agent; every tracker round is wasted and the main session must observe with `gh`. The tracker reports the gap honestly, so there is no false "clean" result.
- **Why it is not fixed now:** on 2026-10-21 Nery asked only for the `tools` change; the hook adds a component (and its tests) to the plugin, and closing needs a live run in the desktop Code tab.
- **Next action:** finish the fix in github-operations (the tool inheritance shipped in 0.4.0 through PR #37, without the `disallowedTools` of option A, by Nery's choice): add a `PreToolUse` hook in the plugin's `hooks/hooks.json` that blocks write MCP methods (merge, create, update, delete, resolve, rerun) when `agent_type` is the tracker; have `auto-pr-lifecycle` check which GitHub MCP prefix the session has before delegating and go to `gh` when none matches. Test the hook live, including the `agent_type` value.
- **Review condition:** closes when the tracker, run from the desktop Code tab with only the Claude app connector, reads a PR's checks and reviews, and its write calls are blocked by the hook.
- **Related records:** PR #22 (where it was observed); ADR_2026-10-18_fold-pr-diagnostics-into-pr-tracker.

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

### DEBT-008 — `main` and the release tags have no GitHub protection

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | security, reliability |
| **Owner** | GitHub repository settings of `nerymurillohnd/the-claude-factory` |
| **Logged** | 2026-10-25 |

#### 🔎 Evidence

- **Confirmed facts:**
  - On 2026-10-25 `gh api repos/nerymurillohnd/the-claude-factory/branches/main/protection` returned `Branch not protected` (HTTP 404), and the repository has no rulesets (`gh api repos/nerymurillohnd/the-claude-factory/rulesets` returned `[]`).
  - Users clone `main`, and the `version` in `plugin.json` names their cached copy (`/en/plugins/loading`, "How Claude Code computes the version"). A merge to `main` is therefore the release, and the pull request's CI is the last gate before users.
  - `release.yml` creates the `<plugin>--v<version>` tags unsigned (ADR_2026-10-25_release-tags-are-created-unsigned-by-ci).
- **Inferences:** a direct push to `main` that changes a plugin without a bump reaches new installs under an existing version, and nothing stops a merge with failing checks or a moved or deleted release tag.
- **Open questions:** whether GitHub immutable releases are available for this repository and add anything over a tag ruleset.

#### 📈 Impact and next step

- **Impact / risk:** the CI gate before users is voluntary, and a release tag can be moved or deleted, which would change what a plugin dependency range resolves to.
- **Why it is not fixed now:** Nery decided on 2026-10-25 to protect `main` last, after the current consolidation of the rules, skills and pipeline, so that its changes are not routed through the new rules.
- **Next action:** create a ruleset on `main` that requires the Validate checks and changes through pull requests, with Nery as bypass actor for documentation and maintainer commits, and a tag ruleset on `*--v*` that blocks update and deletion. Then add "A tag ruleset protects `*--v*` against update and deletion." to the release-tag line of `.claude/CLAUDE.md` → Change Control.
- **Review condition:** closes when both rulesets exist, a push to `main` that fails Validate is refused, and deleting a test tag that matches `*--v*` is refused.
- **Related records:** ADR_2026-10-25_release-tags-are-created-unsigned-by-ci.

### DEBT-009 — Biome ignores Markdown, so no tool formats or lints the repository's Markdown

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | quality, maintainability |
| **Owner** | Maintainer tooling (`biome.json`, `.claude/CLAUDE.md` → Maintainer Tooling) |
| **Logged** | 2026-10-25 |

#### 🔎 Evidence

- **Confirmed facts:**
  - `biome.json` `files.includes` lists only `**/*.{js,cjs,mjs,jsx,ts,cts,mts,tsx,json,jsonc}`.
  - On 2026-10-25, `biome check README.md` with Biome 2.6.2 printed `These paths were provided but ignored: README.md` and exited 0.
  - `.claude/CLAUDE.md` → Maintainer Tooling says "Markdown, JSON, JavaScript and TypeScript: format and lint with Biome", and its protected-files line says `biome.json` excludes them "whenever Markdown is in its `files.includes`".
  - The `maintaining-user-docs` skill records that no linter reads the user docs, so broken links, anchors and tables are found only by opening them.
- **Inferences:** user-facing Markdown (root README, `docs/`, plugin READMEs and changelogs) can ship malformed with every gate green.
- **Open questions:** whether Biome 2.6.2 formats and lints Markdown at all, and if not, which tool should, given ADR_2026-10-21_remove-markdownlint.

#### 📈 Impact and next step

- **Impact / risk:** CLAUDE.md promises a Markdown gate that does not exist, and a formatting or link error in a doc users read is caught by no check.
- **Why it is not fixed now:** Nery deferred it on 2026-10-25 to keep the session on the user-docs and skills consolidation.
- **Next action:** check Biome's current docs and release notes for Markdown support. Then either add Markdown to `files.includes`, with the protected files excluded, or make the CLAUDE.md Maintainer Tooling line say what really reads Markdown.
- **Review condition:** closes when `.claude/CLAUDE.md` and `biome.json` agree, and a Markdown check, if one is adopted, fails on a deliberately broken user doc.
- **Related records:** ADR_2026-10-21_remove-markdownlint, ADR_2026-10-25_marketplace-user-docs-have-their-own-skill.

### DEBT-010 — The mod gates of `scripts/gates.mjs` can miss a mod or report green on a lost test summary

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | reliability, quality |
| **Owner** | Maintainer tooling (`scripts/gates.mjs`) |
| **Logged** | 2026-10-25 |

#### 🔎 Evidence

- **Confirmed facts (read on 2026-10-25):**
  - `scripts/gates.mjs:392-404` creates the `mod-test:<plugin>` gate only for plugins with tracked `*.test.ts` or `*.test.tsx` files, not for every plugin whose `hooks/hooks.json` lists `modules`.
  - `scripts/gates.mjs:406-417` creates the `mod-tsc:<plugin>` gate for any plugin with a `tsconfig.json`, and nothing refreshes the engine's declarations before it runs.
  - `scripts/gates.mjs:494` runs every gate with `stdio: ['ignore', 'pipe', 'pipe']`, so `claude plugin test` writes to a pipe.
  - anthropics/claude-code#103055 reports that `claude plugin test` on a pipe can lose the tail of its output, summary included, and exit 0. `testing-mods/scripts/check-mod.sh` writes to a file and fails without the summary.
  - Before 2026-10-25, `.claude/CLAUDE.md` said `npm run gates` ran these checks "after the declarations are refreshed".
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
