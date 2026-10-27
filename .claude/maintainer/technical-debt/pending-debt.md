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
| DEBT-010 | The mod gates of `scripts/gates.mjs` can miss a mod or report green on a lost test summary | 🟠 Blocked |
| DEBT-014 | `release.yml` has not yet built release notes for a new tag with `release-notes.py` | 🟡 Pending |
| DEBT-015 | `plugin-hooks-guidance` states hook facts that contradict `building-plugins` and the hooks docs | 🟠 Blocked |
| DEBT-016 | `testing-mods` has no live MCP checks for a mod that ships an MCP server | 🟠 Blocked |
| DEBT-017 | `testing-plugins` says the full eval suite runs in CI, and no eval workflow exists | 🟠 Blocked |
| DEBT-020 | `docs/github-mcp-tools.md` serves one plugin but lives in the marketplace docs | 🟠 Blocked |
| DEBT-023 | Gaps from the TypeScript hook audit report are still unaddressed | 🟠 Blocked |
| DEBT-025 | Some repository scripts duplicate a check another script owns | 🟠 Blocked |
| DEBT-026 | Unconfirmed that `.claude/rules/readme-md.md` loads when a README is read | 🟡 Pending |
| DEBT-027 | `claude-review` was denied four tool calls on PR #42 | 🟡 Pending |
| DEBT-028 | TypeScript 7 and 5.x were never run against the TypeScript post-edit hook | 🟡 Pending |
| DEBT-030 | The svelte-development full-version local CLI waits on sveltejs/ai-tools #294 and PR #271 | 🟠 Blocked |
| DEBT-031 | No hook reminds Claude to load an LSP intelligence skill before the first edit | 🔴 Risk accepted |
| DEBT-032 | Biome's `useLiteralKeys` conflicts with tsc's `noPropertyAccessFromIndexSignature` | 🟠 Blocked |
| DEBT-033 | `biome.json` repeats the indentation and line-ending settings `.editorconfig` already sets | 🟡 Pending |
| DEBT-034 | Every `tsconfig*.json` is force-ignored by Biome with no recorded reason | 🟠 Blocked |
| DEBT-035 | `npm run test:plugins` fails when a plugin test family has no gate left | 🔴 Risk accepted |
| DEBT-036 | `biome check --staged` checks the working-tree copy of a partly staged file | 🔴 Risk accepted |

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

### DEBT-014 — `release.yml` has not yet built release notes for a new tag with `release-notes.py`

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | reliability |
| **Owner** | `.github/workflows/release.yml`, `.claude/skills/release-and-versioning/scripts/release-notes.py` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** `release.yml` runs `release-notes.py <plugin> --tag` and, for an untagged version, `release-notes.py <plugin> > notes.md`. Release run 40308391454 (2026-10-26) ran `--tag` on the runner's python3 and printed `✔ bash-lsp-intelligence--v0.2.4 already released`; no plugin had an untagged version, so the notes path did not run. The script was checked with ruff targeting Python 3.12, not run on 3.12.
- **Inferences:** none.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** the first release of a new plugin version could publish without notes, or fail, if the notes path breaks on the runner.
- **Why it is not fixed now:** it runs only when a plugin version is released.
- **Next action:** after the next plugin release, read its Release run and the published notes.
- **Review condition:** closes when a Release run publishes notes built by `release-notes.py` for a new tag.
- **Related records:** ADR_2026-10-25_release-workflow-runs-the-release-skill-script.

### DEBT-015 — `plugin-hooks-guidance` states hook facts that contradict `building-plugins` and the hooks docs

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality, compatibility |
| **Owner** | `.claude/skills/plugin-hooks-guidance/SKILL.md` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts (2026-10-26, compared with `hook-engineering:hook-development` 0.2.1 and the hooks docs it cites):**
  - Line 29 says the strictest decision wins on every event; the docs document that order only for PreToolUse, PreModelSwitch and Elicitation.
  - Line 32 states as fact that plugin hooks get no shell profile, so version-manager tools are missing; the docs say hooks run in non-interactive shells, and the missing tools are an inference.
  - Line 67 tells a hook script to resolve `node` and `tsc` across every Node manager, against `building-plugins`' rule not to add hand-written fallback paths.
  - Line 77 says "Exit 1 never blocks"; with `"onFailure": "block"` it does, as the skill's own step 5 says.
  - It omits plugin-relevant rules: a shell-form hook with `${user_config.*}` fails; `if` runs only on five events; a regex matcher is unanchored; agent-frontmatter hooks in a plugin are ignored.
  - Neither `.claude/CLAUDE.md` → Workflow nor `building-plugins`' Other skills table names the skill.
- **Inferences:** a hook written from the skill can ship wrong behavior to users.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** wrong guidance for the riskiest component a plugin ships.
- **Why it is not fixed now:** the plan agreed on 2026-10-26 waits on Nery's go: a PR to `hook-engineering` adds five generic points (an interpreter launcher, an `env -i` test, a subagent test, `default` and `bypassPermissions` tests, the README limitations), then `plugin-hooks-guidance` keeps only this marketplace's rules and points to `hook-engineering:hook-development` for hook facts.
- **Next action:** on Nery's go, open the `hook-engineering` PR, then reduce the skill and register it in the Workflow and in `building-plugins`.
- **Review condition:** closes when the skill states no hook fact the docs contradict and the Workflow routes hook work to it.
- **Related records:** none.

### DEBT-016 — `testing-mods` has no live MCP checks for a mod that ships an MCP server

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality |
| **Owner** | `.claude/skills/testing-mods/`, `.claude/skills/testing-plugins/references/mcp-live-checks.md` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** `building-plugins` sends a plugin that is or contains a mod to `testing-mods` for its live checks; `grep -rl "mcp-live-checks\|live MCP" .claude/skills/testing-mods` finds nothing (2026-10-26). The live MCP checks live in `testing-plugins/references/mcp-live-checks.md`.
- **Inferences:** a mod with an MCP server reaches release without its MCP checks.
- **Open questions:** whether `testing-mods` takes the reference or points to it.

#### 📈 Impact and next step

- **Impact / risk:** an MCP server bundled in a mod ships untested live.
- **Why it is not fixed now:** the choice between copying and pointing is Nery's.
- **Next action:** ask Nery, then add the reference or the pointer to `testing-mods`.
- **Review condition:** closes when `testing-mods` routes a mod with an MCP server through the live MCP checks.
- **Related records:** ADR_2026-10-25_testing-plugins-owns-live-mcp-checks.

### DEBT-017 — `testing-plugins` says the full eval suite runs in CI, and no eval workflow exists

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality |
| **Owner** | `.claude/skills/testing-plugins/SKILL.md` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** `testing-plugins/SKILL.md` line 25 says to "make sure CI will run the full suite" and line 38 is headed "Evals: pilot and smoke locally, full suite in CI"; `.github/workflows/` holds only `claude-code-review.yml`, `claude.yml`, `release.yml` and `validate.yml` (2026-10-26). The earlier "this repository's CI" phrase in `eval-policy.md` is gone.
- **Inferences:** a plugin with evals ships without its full suite ever running.
- **Open questions:** whether the full suite runs locally until an eval workflow exists, or a workflow is added (it spends money on every pull request that edits a plugin with evals).

#### 📈 Impact and next step

- **Impact / risk:** the skill promises a check nobody runs.
- **Why it is not fixed now:** the choice, and any CI spend, is Nery's.
- **Next action:** ask Nery; then change step 4 to run the full suite locally, or add the workflow with his approval.
- **Review condition:** closes when the skill and the workflows agree on where the full suite runs.
- **Related records:** none.

### DEBT-020 — `docs/github-mcp-tools.md` serves one plugin but lives in the marketplace docs

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | maintainability |
| **Owner** | `docs/github-mcp-tools.md`, `plugins/github-operations` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** the file exists (2026-10-26); `maintaining-user-docs` lists it as out of its scope because it belongs to one plugin.
- **Inferences:** none.
- **Open questions:** when to move it.

#### 📈 Impact and next step

- **Impact / risk:** a plugin's doc no skill maintains, outside the plugin users install.
- **Why it is not fixed now:** moving it into the plugin is a plugin change, timed by Nery.
- **Next action:** ask Nery when; then move it into `plugins/github-operations` in a PR and update its links.
- **Review condition:** closes when `docs/` no longer holds it.
- **Related records:** none.

### DEBT-023 — Gaps from the TypeScript hook audit report are still unaddressed

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality |
| **Owner** | `plugins/typescript6-lsp-intelligence`, `plugins/typescript7-lsp-intelligence` (post-edit hook) |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** the gap table of `~/Claude/projects/the-claude-factory-research/reports/Auditoría del hook TypeScript.md` lists items not yet taken (open since 2026-10-22).
- **Inferences:** none.
- **Open questions:** which gaps to take, and in which order.

#### 📈 Impact and next step

- **Impact / risk:** known weaknesses in a hook that runs on every TypeScript edit of every user.
- **Why it is not fixed now:** the choice is Nery's.
- **Next action:** read the report's gap table with Nery and take the chosen gaps in plugin PRs.
- **Review condition:** closes when every gap is fixed or dropped by Nery.
- **Related records:** none.

### DEBT-025 — Some repository scripts duplicate a check another script owns

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | maintainability |
| **Owner** | `scripts/bump-version.mjs`, `scripts/check-version-bump.mjs` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** `scripts/bump-version.mjs` and `scripts/check-version-bump.mjs` re-implement what `release-and-versioning`'s `bump-version.py` and `check-version-bump.py` do; the `version-bump` gate runs the `.mjs` one. The review of Biome's scripts on 2026-10-26 proposed one script per rule, retiring the `.mjs` copies; it was not approved. Skill scripts keep their own copies on purpose (memory `skill-checks-are-not-gates`).
- **Inferences:** a rule change made in one copy and not the other makes the gate and the skill disagree.
- **Open questions:** whether the gate keeps its own copy or runs the skill's script.

#### 📈 Impact and next step

- **Impact / risk:** two implementations of the bump rule to keep in step.
- **Why it is not fixed now:** it touches the agreed split between skills and gates; Nery decides.
- **Next action:** ask Nery whether the `version-bump` gate runs `check-version-bump.py`.
- **Review condition:** closes when each rule has one implementation per layer Nery approves.
- **Related records:** none.

### DEBT-026 — Unconfirmed that `.claude/rules/readme-md.md` loads when a README is read

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | quality |
| **Owner** | `.claude/rules/readme-md.md` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** the Confirmation of ADR_2026-10-25_every-readme-has-a-path-scoped-rule marks the load as pending; no fresh-session check has run.
- **Inferences:** it loads, as the earlier path-scoped rules did in a `claude -p` check.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** README rules silently absent when a README is edited.
- **Why it is not fixed now:** not run yet.
- **Next action:** run a `claude -p` that reads a README and check the rule loaded; record it in the ADR's Confirmation.
- **Review condition:** closes when the check passes.
- **Related records:** ADR_2026-10-25_every-readme-has-a-path-scoped-rule.

### DEBT-027 — `claude-review` was denied four tool calls on PR #42

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | reliability |
| **Owner** | `.github/workflows/claude-code-review.yml` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** run 39733419072 on PR #42 reported `permission_denials_count: 4`; the workflow's `--allowedTools` allows only inline comments.
- **Inferences:** the reviewer could not read what it needed.
- **Open questions:** which tools were denied.

#### 📈 Impact and next step

- **Impact / risk:** weaker automated reviews.
- **Why it is not fixed now:** the denied tool names are unread.
- **Next action:** read them in the run's log, then propose to Nery which read-only tools to allow.
- **Review condition:** closes when a review run reports no denial.
- **Related records:** none.

### DEBT-028 — TypeScript 7 and 5.x were never run against the TypeScript post-edit hook

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | compatibility |
| **Owner** | `plugins/typescript6-lsp-intelligence`, `plugins/typescript7-lsp-intelligence` (post-edit hook) |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** the hook's policy filter and no-config defaults were tested with TypeScript 6 only (open since 2026-10-22).
- **Inferences:** none.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** users on TypeScript 7 or 5.x may meet unchecked behavior.
- **Why it is not fixed now:** not run yet.
- **Next action:** install both in a scratch folder, point the hook at each, and run the hook test suite's compiler cases.
- **Review condition:** closes when both pass or their gaps are logged.
- **Related records:** none.

### DEBT-030 — The svelte-development full-version local CLI waits on sveltejs/ai-tools #294 and PR #271

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | compatibility |
| **Owner** | `plugins/svelte-development` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** upstream has shipped. On 2026-10-26: issue #294 is closed as completed, release PR #271 is merged, and `@sveltejs/mcp` 0.1.27 lists "class directive to clsx attribute fixer" (#269) and the linter cache fix (#295). 0.1.28 is the latest release. #291 is closed and #290 is open. The plugin has not adopted it: `svelte-docs-and-autofixer/SKILL.md:135` and the README FAQ still call 0.1.26 the latest and pass only the major to `--svelte-version`.
- **Inferences:** the CLI accepts a full version from 0.1.27 on. This is not checked against the installed binary.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** the plugin's local CLI fallback still misses the `class:` suggestion, and its text names a superseded release.
- **Why it is not fixed now:** it is a plugin change, which goes through a PR timed by Nery.
- **Next action:** on Nery's go, open a `svelte-development` PR: check `svelte-mcp --svelte-version 5.x.y` on 0.1.28, update `SKILL.md:135`, the README FAQ and the errata, and bump the version.
- **Review condition:** closes when upstream ships and the plugin adopts it, or the issue closes otherwise.
- **Related records:** none.

### DEBT-031 — No hook reminds Claude to load an LSP intelligence skill before the first edit

| Field | Value |
| --- | --- |
| **Status** | 🔴 Risk accepted |
| **Category** | quality |
| **Owner** | The LSP intelligence plugins |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** a `PreToolUse` reminder hook was deferred on 2026-10-20 until Nery reports skipped skills (memory `deferred-pretooluse-skill-reminder`).
- **Inferences:** none.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** Claude can edit before loading the language skill.
- **Why it is not fixed now:** Nery deferred it on purpose.
- **Next action:** none until Nery's report.
- **Review condition:** reassess when Nery reports a skipped skill.
- **Related records:** none.

### DEBT-032 — Biome's `useLiteralKeys` conflicts with tsc's `noPropertyAccessFromIndexSignature`

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality |
| **Owner** | `biome.json`, `tsconfig.base.json` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** on 2026-10-26 `biome ci` reported 4 `complexity/useLiteralKeys` infos in `scripts/tests/gates.test.mjs` for `process.env['GIT_INDEX_FILE']`, which `tsconfig.base.json`'s `noPropertyAccessFromIndexSignature` requires.
- **Inferences:** following Biome breaks tsc.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** noise in Biome's output; a fix that follows it would fail tsc.
- **Why it is not fixed now:** turning off a rule needs Nery's approval.
- **Next action:** with Nery's approval, turn `useLiteralKeys` off for JS and TS in `biome.json`, with the reason beside it.
- **Review condition:** closes when Biome reports none and tsc passes.
- **Related records:** none.

### DEBT-033 — `biome.json` repeats the indentation and line-ending settings `.editorconfig` already sets

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | maintainability |
| **Owner** | `biome.json` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** `formatter.indentStyle`, `indentWidth`, `lineEnding` and `markdown.formatter.indentStyle` repeat `.editorconfig`, which Biome reads (`useEditorconfig: true`); `biome.json` wins, so the two can drift. A scratch run without them changed none of 240 files (2026-10-26).
- **Inferences:** none.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** two sources of the same style.
- **Why it is not fixed now:** logged with the session's open items on Nery's order.
- **Next action:** remove the four keys and run `biome ci .`.
- **Review condition:** closes when `.editorconfig` is the only source and `biome ci .` changes nothing.
- **Related records:** none.

### DEBT-034 — Every `tsconfig*.json` is force-ignored by Biome with no recorded reason

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality |
| **Owner** | `biome.json` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** `biome.json` force-ignores `**/tsconfig.json` and `**/tsconfig.base.json` since commit `b3ada31`, which gives no reason. A scratch run without the exclusions linted clean and would reformat `scripts/tsconfig.json` and the four mods' `tsconfig.json` (2026-10-26).
- **Inferences:** none.
- **Open questions:** whether the maintainer ones join now and the plugin ones on each plugin's next change.

#### 📈 Impact and next step

- **Impact / risk:** a malformed tsconfig passes Biome.
- **Why it is not fixed now:** the scope is Nery's call.
- **Next action:** ask Nery; then include the maintainer tsconfigs and format them once.
- **Review condition:** closes when every tsconfig Nery includes passes `biome ci`.
- **Related records:** none.

### DEBT-035 — `npm run test:plugins` fails when a plugin test family has no gate left

| Field | Value |
| --- | --- |
| **Status** | 🔴 Risk accepted |
| **Category** | maintainability |
| **Owner** | `package.json` (`test:plugins`), `scripts/gates.mjs` (`selectGates`) |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** `test:plugins` selects `node-tests:,unittest:,by-path:,mod-test:`; `selectGates` exits 1 with `no gate matches "<selector>"` when a selector matches nothing. Every family has gates today.
- **Inferences:** none.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** the day a family's last plugin loses its tests, the script fails loudly for a reason unrelated to the change.
- **Why it is not fixed now:** it fails loudly and names the selector, which is the intended behavior.
- **Next action:** drop the selector from `test:plugins` when its family empties.
- **Review condition:** reassess when a plugin test family is removed.
- **Related records:** ADR_2026-10-26_npm-tools-and-git-hooks-are-pinned-dev-dependencies.

### DEBT-036 — `biome check --staged` checks the working-tree copy of a partly staged file

| Field | Value |
| --- | --- |
| **Status** | 🔴 Risk accepted |
| **Category** | quality |
| **Owner** | `.husky/pre-commit` |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:** the pre-commit hook runs `biome check --staged`, which reads the files on disk; Biome's git-hooks guide notes the limitation.
- **Inferences:** none.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** a partly staged file passes or fails on content that is not being committed; the pre-push gates check the committed state.
- **Why it is not fixed now:** it is a Biome limitation; the pre-push gates cover it.
- **Next action:** none.
- **Review condition:** reassess if Biome checks the staged blob.
- **Related records:** ADR_2026-10-26_npm-tools-and-git-hooks-are-pinned-dev-dependencies.

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
