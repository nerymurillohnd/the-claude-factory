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
| DEBT-015 | `plugin-hooks-guidance` states hook facts that contradict `building-plugins` and the hooks docs | 🟠 Blocked |
| DEBT-016 | `testing-mods` has no live MCP checks for a mod that ships an MCP server | 🟠 Blocked |
| DEBT-023 | Gaps from the TypeScript hook audit report are still unaddressed | 🟠 Blocked |
| DEBT-028 | TypeScript 7 and 5.x were never run against the TypeScript post-edit hook | 🟡 Pending |
| DEBT-030 | The svelte-development full-version local CLI waits on sveltejs/ai-tools #294 and PR #271 | 🟠 Blocked |
| DEBT-031 | No hook reminds Claude to load an LSP intelligence skill before the first edit | 🔴 Risk accepted |
| DEBT-035 | `npm run test:plugins` fails when a plugin test family has no gate left | 🔴 Risk accepted |
| DEBT-036 | `biome check --staged` checks the working-tree copy of a partly staged file | 🔴 Risk accepted |
| DEBT-037 | Sessions skip the project skills the Workflow assigns to the area they work in | 🟠 Blocked |
| DEBT-039 | The `instruction-engineering` checker never ran on Python 3.12, its declared minimum | 🟠 Blocked |
| DEBT-040 | `scaffold-plugin.py` writes a `plugin.json` that Biome's formatter rejects | 🟠 Blocked |
| DEBT-042 | python-lsp-intelligence's post-edit hook type-checks a PEP 723 script without its dependencies | 🟡 Pending |

## 📂 Open items

### DEBT-002 — Version-bump check fails on main after a revert of an unreleased bump and blocks every release

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | reliability, quality |
| **Owner** | `.claude/skills/release-and-versioning/scripts/check-version-bump.py` and the `version-bump` gate of `scripts/gates.mjs`, run by the `policy` job of `.github/workflows/validate.yml` |
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
- **Next action:** decide with Nery whether `check-version-bump.py` compares each plugin with its latest `<plugin>--v*` tag instead of the previous commit. If yes, change it with tests for both cases: a revert to the tagged state passes and an edit without a bump still fails.
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

- **Confirmed facts (read on 2026-10-25, line numbers rechecked on 2026-10-29):**
  - `scripts/gates.mjs:487-500` creates the `mod-test:<plugin>` gate only for plugins with tracked `*.test.ts` or `*.test.tsx` files, not for every plugin whose `hooks/hooks.json` lists `modules`.
  - `scripts/gates.mjs:657` runs every gate with `stdio: ['ignore', 'pipe', 'pipe']`, so `claude plugin test` writes to a pipe.
  - anthropics/claude-code#103055 reports that `claude plugin test` on a pipe can lose the tail of its output, summary included, and exit 0. `testing-mods/scripts/check-mod.sh` writes to a file and fails without the summary.
- **Inferences:**
  - A mod without tests is never run by `claude plugin test` in the gates.
  - A failed test can pass the gate when the summary is lost.
- **Open questions:** whether #103055 still reproduces on 2.1.310 through `spawnSync` with pipes.

#### 📈 Impact and next step

- **Impact / risk:** the local release proof for a mod can report green on a mod that fails its tests, or that has none, and reach users.
- **Why it is not fixed now:** Nery deferred it on 2026-10-25 to keep the session on consolidating the mod documentation.
- **Next action:**
  - key `mod-test` on `modules` in `hooks/hooks.json`;
  - run `claude plugin test` with its output in a file, and fail when the `Ran N tests across N files` summary is missing, as `check-mod.sh` does.
- **Review condition:** closes when a mod with no tests fails the gate and a test run with its summary removed fails it.
- **Related records:** ADR_2026-10-21_gates-run-from-one-script, ADR_2026-10-25_building-mods-skill-holds-mod-authoring, ADR_2026-10-29_remove-the-mod-tsc-gate.

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

- **Confirmed facts:** the pre-commit hook runs `biome check --staged`, which reads the files on disk; Biome's git-hooks guide notes the limitation. The guide's alternative, `git-format-staged` piping the staged blob through `biome check --stdin-file-path`, does not work as a check on Biome 2.6.3. Without `--write`, the stdin check exits 1 even for a clean file ("The contents aren't fixed. Use the `--write` flag to fix them.", probed on 2026-10-27). With `--write`, it rewrites the staged content during the commit, which is a different policy from a check.
- **Inferences:** none.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** a partly staged file passes or fails on content that is not being committed; the pre-push gates check the committed state.
- **Why it is not fixed now:** it is a Biome limitation; the pre-push gates cover it.
- **Next action:** check the review condition.
- **Review condition:** reassess if Biome checks the staged blob, or if a stdin check of a clean file exits 0.
- **Related records:** ADR_2026-10-26_npm-tools-and-git-hooks-are-pinned-dev-dependencies.

### DEBT-037 — Sessions skip the project skills the Workflow assigns to the area they work in

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality |
| **Owner** | `.claude/settings.json` and `.claude/hooks/` |
| **Logged** | 2026-10-27 |

#### 🔎 Evidence

- **Confirmed facts:**
  - In the 2026-10-27 session that built `tailwind-development`, Claude never invoked two project skills that applied, although the Workflow of `.claude/CLAUDE.md` and the hook rule of that day name them (`.claude/rules/hooks-and-scripts.md`, retired on 2026-10-28; `.claude/rules/plugins/plugins-scripts.md` now names `plugin-hooks-guidance`):
    - `testing-plugins`, while building and running the plugin's eval suite;
    - `plugin-hooks-guidance`, while designing a plugin `PostToolUse` hook (DESIGN.md section 10.5).
  - Of the other project skills, only `building-plugins`, `plugin-categories` and `release-and-versioning` were invoked; `testing-plugins` was read in part with `cat`. Claude reported this to Nery on 2026-10-27 when he asked which project skills had been used.
  - The proposed fix, stated in that session and deferred by Nery on 2026-10-27, is a maintainer `PreToolUse` hook, `.claude/hooks/require-workflow-skill.py`, registered in `.claude/settings.json`. Once per session per skill, it denies the first tool call in an area the Workflow assigns to a skill, with a reason that names the skill; Claude then invokes the skill and repeats the call.
  - Proposed mapping:
    - `Edit`/`Write` under `plugins/*/hooks/**`, or Bash with `claude plugin test` → `plugin-hooks-guidance`, or `testing-mods` for a mod;
    - Bash with `claude plugin eval`, or `Edit`/`Write` under `plugins/*/evals/**` → `testing-plugins`;
    - `Edit`/`Write` of `plugins/*/.claude-plugin/plugin.json`, a plugin `CHANGELOG.md` or the root `CHANGELOG.md` → `release-and-versioning`;
    - any other file under `plugins/<plugin>/` → `building-plugins`;
    - `scripts/categories.json` → `plugin-categories`.
  - A marker in the session's `scratchpad_dir` records "reminded", not "invoked": `transcript_path` is written asynchronously, and a `PreToolUse` `additionalContext` reaches Claude only after the tool ran (memory `deferred-pretooluse-skill-reminder`).
- **Inferences:** instruction text alone does not hold over long sessions with many topics; more emphasis in `CLAUDE.md` would not fix it.
- **Open questions:**
  - whether the mapping table becomes the single source, with the Workflow of `.claude/CLAUDE.md` pointing at it;
  - whether a `claude plugin test` call should route to `testing-mods` or `plugin-hooks-guidance` when a plugin is both a mod and has command hooks.

#### 📈 Impact and next step

- **Impact / risk:** work in an area runs without the procedure written for it, so its checks and rules can be missed. In the 2026-10-27 session this left the eval suite unchecked against `testing-plugins` and the hook design unchecked against `plugin-hooks-guidance`.
- **Why it is not fixed now:** Nery deferred it on 2026-10-27, to keep the session on the `tailwind-development` release and its phase 2.
- **Next action:** on Nery's go, build the hook with `hook-engineering:hook-development` and `plugin-hooks-guidance`, then:
  - probe it with three inputs (a first `claude plugin eval` is denied naming `testing-plugins`, the same call later in the session passes, unreadable input passes);
  - lint `.claude/settings.json`;
  - confirm it live in a `claude --debug` session.
- **Review condition:** Nery's go, or another session that skips a Workflow skill.
- **Related records:** DEBT-031 (the separate, user-facing reminder for the LSP intelligence plugins); DEBT-015 (`plugin-hooks-guidance` contradicts the hooks docs, which the build must account for).

### DEBT-039 — The `instruction-engineering` checker never ran on Python 3.12, its declared minimum

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | compatibility |
| **Owner** | `plugins/instruction-engineering/skills/claude-md-and-rules/scripts/check_instructions.py` |
| **Logged** | 2026-10-28 |

#### 🔎 Evidence

- **Confirmed facts:**
  - The plugin README declares `python3` 3.12 or later. Ruff and Basedpyright check the script against 3.12 and pass; the tests in `scripts/testers/instruction-engineering/` run on 3.15.
  - `uv python list` on 2026-10-28 shows only CPython 3.15.0 on the maintainer machine, and uv runs with `python-downloads = manual`.
  - Nery declined installing Python 3.12 on 2026-10-28 ("No instalar").
  - A run on Python 3.9 during the import found a runtime `str | list[str]` union that static tools had not flagged as a 3.9 problem; it was fixed with `empty_frontmatter()`.
- **Inferences:** a 3.12 runtime failure is unlikely after the static checks, but the 3.9 run shows a runtime check can find what they miss.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** users on 3.12 or 3.13 run a checker never executed on their version; the release went out on 2026-10-28 as 0.1.0.
- **Why it is not fixed now:** it needs a Python other than 3.15, which Nery declined.
- **Next action:** on Nery's yes, run the tests once with `uv run --python 3.12 --no-project` (a one-off download, no environment created).
- **Review condition:** closes when the checker's tests pass on 3.12, or when Nery drops the 3.12 floor.
- **Related records:** ADR_2026-10-28_instruction-engineering-joins-the-marketplace, ADR_2026-10-27_python-version-is-set-per-scope.

### DEBT-040 — `scaffold-plugin.py` writes a `plugin.json` that Biome's formatter rejects

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality |
| **Owner** | `.claude/skills/building-plugins/scripts/scaffold-plugin.py`, `.claude/skills/building-plugins/assets/plugin-template.json` |
| **Logged** | 2026-10-28 |

#### 🔎 Evidence

- **Confirmed facts:**
  - The scaffold fills the template with `json.dumps(...)` values (line 191, and `surfacesJson` at line 208), which writes arrays on one line.
  - On 2026-10-28 the scaffolded `plugins/instruction-engineering/.claude-plugin/plugin.json` failed Biome's format check and was fixed with `npx biome format --write` before commit `c4fdb40`.
  - Nery stopped the scaffold work on 2026-10-28 to keep the session on the plugin.
- **Inferences:** every new plugin scaffolded today needs the same manual format step.
- **Open questions:** whether the scaffold formats its output with Biome or writes the template's layout itself.

#### 📈 Impact and next step

- **Impact / risk:** a manual step on every new plugin; skipping it fails the pre-commit hook.
- **Why it is not fixed now:** Nery deferred it on 2026-10-28.
- **Next action:** on Nery's go, make the scaffold write Biome's layout, and add a test that scaffolds into a temporary root and runs `biome format` on the result.
- **Review condition:** closes when a freshly scaffolded `plugin.json` passes `biome format` unchanged.
- **Related records:** none.

### DEBT-042 — python-lsp-intelligence's post-edit hook type-checks a PEP 723 script without its dependencies

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | quality, compatibility |
| **Owner** | `plugins/python-lsp-intelligence/hooks/check.py` (plugin scope, released 0.3.0) |
| **Logged** | 2026-10-29 |

#### 🔎 Evidence

- **Confirmed facts:**
  - `hooks/check.py` runs `basedpyright` on the edited file with the project's config (`-p <config> <file>`, around line 339) and the interpreter basedpyright finds by default. It has no branch for a file whose first line is `#!/usr/bin/env -S uv run --script`.
  - On 2026-10-29, every Edit and Write of `plugins/github-operations/skills/github/scripts/check-forms.py` (PEP 723: `ruamel.yaml`, `check-jsonschema`) made the hook block with `reportMissingImports` on `ruamel.yaml` and about 120 cascading `reportUnknown*` errors. The same file checked with `uv run --quiet --no-project --with-requirements <file> basedpyright --warnings <file>` reported 0 errors, 0 warnings, 0 notes.
  - The repository's `basedpyright-plugins:<file>` gate (`scripts/gates.mjs`, commit 9ac3b11) already checks each PEP 723 plugin script that way.
  - The skill's own Gotchas already tell Claude that the server shows false import errors on PEP 723 scripts; the hook does not apply that knowledge.
- **Inferences:** every user of the plugin who edits a PEP 723 script with third-party dependencies gets the same blocking false errors after each edit.
- **Open questions:** what the hook does when `uv` is not installed on the user's machine: skip basedpyright for that file with a one-line note, or keep today's run.

#### 📈 Impact and next step

- **Impact / risk:** the post-edit hook blocks every edit of a PEP 723 script with errors that are not real, which trains Claude to ignore the hook's findings and buries real errors in the noise.
- **Why it is not fixed now:** the change belongs to another plugin, with its own pull request and version bump; Nery queued it after the github-operations 0.5.0 release.
- **Next action:** in `hooks/check.py`, when the file's first line is the `uv run --script` shebang and `uv` is on `PATH`, run `uv run --quiet --no-project --with-requirements <file> basedpyright -p <config> <file>`; add a test in `scripts/testers/python-lsp-intelligence/` with a PEP 723 fixture that imports a third-party package, RED first; declare `uv` as optional in the README; release through `release-and-versioning`.
- **Review condition:** closes when an edit of a PEP 723 script with third-party dependencies produces no false `reportMissingImports` from the hook and the new test passes.
- **Related records:** DEBT-041; the `basedpyright-plugins:` gate in `scripts/gates.mjs`.

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
