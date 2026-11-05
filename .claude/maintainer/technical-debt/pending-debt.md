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
| DEBT-043 | No CI workflow runs the eval suites that `operating-standard.md` requires | 🟠 Blocked |
| DEBT-044 | tailwind-development phase 2 exists only in a local stash on a pre-0.2.0 base | 🟠 Blocked |
| DEBT-045 | `claude-github-actions` cannot write a Claude workflow from scratch | 🟠 Blocked |
| DEBT-046 | Nothing detects when claude-code-action changes the facts `claude-github-actions` relies on | 🟠 Blocked |
| DEBT-047 | `claude-github-actions` has no eval suite | 🟠 Blocked |
| DEBT-048 | github-operations 0.6.0 no longer writes, triages or answers issues and discussions, or turns an issue into a pull request | 🟠 Blocked |
| DEBT-049 | github-operations ships without an icon or a privacy policy URL, and turns on the GitHub MCP server's Insiders mode | 🟠 Blocked |
| DEBT-050 | A new cloud session starts on Node 22 without shfmt, and npm refuses to run on Node 22 since the devEngines pin | 🔵 In progress |

## 📂 Open items

### DEBT-002 — Version-bump check fails on main after a revert of an unreleased bump and blocks every release

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | reliability, quality |
| **Owner** | `scripts/release/check-version-bump.py` and the `version-bump` gate of `scripts/gates.mjs`, run by the `policy` job of `.github/workflows/validate.yml` |
| **Logged** | 2026-10-20 |

#### 🔎 Evidence

- **Confirmed facts:**
  - The `policy` job of `.github/workflows/validate.yml` runs `npm run gates:ci -- --group policy --base <BASE>`, with `BASE` the PR base on a pull request and `github.event.before` on a push (lines 68-70). Its `version-bump` gate (`scripts/gates.mjs:322-326`) runs `scripts/release/check-version-bump.py <BASE>`, which diffs `<BASE>...HEAD` and compares each changed plugin's version with its version at `<BASE>`, never with its latest tag (`check-version-bump.py:140-195`, read on 2026-11-01). `release.yml` runs only when `Validate` succeeds on a push to `main`, and it then tags every plugin whose current version has no tag.
  - On 2026-10-20 [PR #31](https://github.com/nerymurillohnd/the-claude-factory/pull/31) reverted [PR #27](https://github.com/nerymurillohnd/the-claude-factory/pull/27), so `plugins/bash-lsp-intelligence` went from 0.2.2 (never tagged) back to 0.2.1. The "Repository policy & script tests" job failed on the PR and on the push of `ad3951f` (run 39476280906) at the version-bump step: `files changed (...) but version is still 0.2.2`.
  - Reproduced locally on `ad3951f` with that day's script (`node .github/scripts/check-version-bump.mjs a223707`): exit 1 with that message. With base `origin/main` it passes. The Python script that replaced it keeps the same comparison.
  - `git diff bash-lsp-intelligence--v0.2.1 origin/main -- plugins/bash-lsp-intelligence` is empty: the plugin is byte-identical to its last release, so no bump is warranted.
  - Because `Validate` is red on `main`, `Release` stays skipped. On 2026-10-20 no tag existed for python-lsp-intelligence 0.2.2, typescript6-lsp-intelligence 0.2.1 or typescript7-lsp-intelligence 0.3.1, all merged the same day.
- **Inferences:** any revert of a bump that was never released fails the same way, because the check compares with the previous commit, not with the last published tag (not tested beyond this case).
- **Open questions:** whether the check should compare each plugin with its latest release tag, accept a version equal to the latest tag, or stay as it is.

#### 📈 Impact and next step

- **Impact / risk:** one red `Validate` on `main` blocks the release of every plugin until a later push, outside `plugins/`, passes. The next push compares against the red commit, so it recovers by itself, but the failure repeats on the next revert.
- **Why it is not fixed now:** the rule for reverts, and how the check treats a version that returns to the last tag, is a design decision for Nery. This task was only to get the pending releases out.
- **Next action:** decide with Nery whether `check-version-bump.py` compares each plugin with its latest `<plugin>--v*` tag instead of the previous commit. If yes, change it with tests for both cases: a revert to the tagged state passes and an edit without a bump still fails.
- **Review condition:** closes when a revert of an unreleased bump passes `Validate` on `main` and a plugin change without a bump still fails it.
- **Related records:** [PR #27](https://github.com/nerymurillohnd/the-claude-factory/pull/27), [PR #31](https://github.com/nerymurillohnd/the-claude-factory/pull/31); the `versioning` and `releases` skills.

### DEBT-010 — The mod gates of `scripts/gates.mjs` can miss a mod or report green on a lost test summary

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | reliability, quality |
| **Owner** | Maintainer tooling (`scripts/gates.mjs`) |
| **Logged** | 2026-10-25 |

#### 🔎 Evidence

- **Confirmed facts (read on 2026-10-25, line numbers rechecked on 2026-11-01):**
  - `scripts/gates.mjs:486-491` creates the `mod-test:<plugin>` gate only for plugins with tracked `*.test.ts` or `*.test.tsx` files, not for every plugin whose `hooks/hooks.json` lists `modules`.
  - `scripts/gates.mjs:654` runs every gate with `stdio: ['ignore', 'pipe', 'pipe']`, so `claude plugin test` writes to a pipe.
  - anthropics/claude-code#103055 reports that `claude plugin test` on a pipe can lose the tail of its output, summary included, and exit 0. It is still open on 2026-11-01. `testing-mods/scripts/check-mod.sh` writes to a file and fails without the summary.
- **Inferences:**
  - A mod without tests is never run by `claude plugin test` in the gates.
  - A failed test can pass the gate when the summary is lost.
- **Open questions:** whether #103055 reproduces on 2.1.316 through `spawnSync` with pipes.

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

- **Confirmed facts (2026-10-26, compared with `hook-engineering:hook-development` 0.2.1 and the hooks docs it cites; line numbers rechecked on 2026-11-01):**
  - Line 29 says the strictest decision wins on every event; the docs document that order only for PreToolUse, PreModelSwitch and Elicitation.
  - Line 32 states as fact that plugin hooks get no shell profile, so version-manager tools are missing; the docs say hooks run in non-interactive shells, and the missing tools are an inference.
  - Line 68 tells a hook script to resolve `node` and `tsc` across every Node manager, against `building-plugins`' rule not to add hand-written fallback paths.
  - Line 78 says "Exit 1 never blocks"; with `"onFailure": "block"` it does, as the skill's own step 5 says.
  - It omits plugin-relevant rules: a shell-form hook with `${user_config.*}` fails; `if` runs only on five events; a regex matcher is unanchored; agent-frontmatter hooks in a plugin are ignored.
  - Neither `.claude/CLAUDE.md` → Workflow nor `building-plugins`' Other skills table names the skill; only `.claude/rules/plugins/plugins-scripts.md:49` does.
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

- **Confirmed facts:**
  - The report `~/Claude/projects/the-claude-factory-research/reports/Auditoría del hook TypeScript.md` (2026-10-22) no longer exists: neither that path nor a file of that name anywhere under `~` (`find`, `mdfind`, 2026-11-01). Its five open gaps survive in earlier handoffs, which list them with "None blocks".
  - Open gaps in `hooks/tsc-check.sh`, identical in both plugins, on 2026-11-01:
    1. The 120-second `timeout` in `hooks/hooks.json` ends the hook before it reports what `tsc` found so far: the script has no deadline of its own (no match for one in `tsc-check.sh`).
    2. The `changedFiles` regex scans the whole event text instead of reading the field (`tsc-check.sh:927-929`). No failing case is known.
  - Nery dropped the report's other three gaps on 2026-11-01: Windows without Git Bash cannot start the hook (the README declares Git Bash on Windows, `README.md:60`, `:423-425`); both TypeScript plugins installed together check each edit twice (the README says to enable only one, `README.md:227`); the hooks use shell form, where the report said the docs prefer exec form.
- **Inferences:** none.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** on a program `tsc` cannot check within 120 seconds, Claude learns of the timeout but gets none of the errors found; the regex is a fragile parse in a hook that runs on every TypeScript edit of every user.
- **Why it is not fixed now:** the fix is a change to both plugins, with a pull request and a version bump each, timed by Nery.
- **Next action:** on Nery's go, give `tsc-check.sh` a deadline below the hook's `timeout` that reports what it found, and read `changedFiles` as a field; add a test for each in `scripts/testers/typescript6-lsp-intelligence/`, RED first; release both plugins through `versioning` and `releases`.
- **Review condition:** closes when both gaps are fixed, or Nery drops them.
- **Related records:** none.

### DEBT-028 — TypeScript 7 and 5.x were never run against the TypeScript post-edit hook

| Field | Value |
| --- | --- |
| **Status** | 🟡 Pending |
| **Category** | compatibility |
| **Owner** | `plugins/typescript6-lsp-intelligence`, `plugins/typescript7-lsp-intelligence` (post-edit hook) |
| **Logged** | 2026-10-26 |

#### 🔎 Evidence

- **Confirmed facts:**
  - The hook's policy filter and no-config defaults were tested with TypeScript 6 only (open since 2026-10-22).
  - `scripts/testers/typescript6-lsp-intelligence/tsc-check.test.mjs:562` stubs a `tsc` that prints `Version 7.0.2`: it tests the hook's message for an option TypeScript 7 removed, not a real TypeScript 7 compiler. No TypeScript 5.x case exists.
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

- **Confirmed facts:** upstream has shipped. On 2026-10-26: issue #294 is closed as completed, release PR #271 is merged, and `@sveltejs/mcp` 0.1.27 lists "class directive to clsx attribute fixer" (#269) and the linter cache fix (#295). 0.1.28 is the latest release, and still is on 2026-11-01 (`npm view @sveltejs/mcp version`). #291 is closed and #290 is open. The plugin has not adopted it: `svelte-docs-and-autofixer/SKILL.md:135` and the README FAQ still call 0.1.26 the latest and pass only the major to `--svelte-version`.
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

- **Confirmed facts:** the pre-commit hook runs `biome check --staged`, which reads the files on disk; Biome's git-hooks guide notes the limitation. The guide's alternative, `git-format-staged` piping the staged blob through `biome check --stdin-file-path`, does not work as a check on Biome 2.6.3 or 2.6.4. Without `--write`, the stdin check exits 1 even for a clean file ("The contents aren't fixed. Use the `--write` flag to fix them.", probed on 2026-10-27 and again on 2.6.4 on 2026-11-01). With `--write`, it rewrites the staged content during the commit, which is a different policy from a check.
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
    - `Edit`/`Write` of `plugins/*/.claude-plugin/plugin.json`, a plugin `CHANGELOG.md` or the root `CHANGELOG.md` → `versioning`;
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
  - `uv python list --only-installed` shows only CPython 3.15 on the maintainer machine (3.15.0 on 2026-10-28, 3.15.2 on 2026-11-01), and uv runs with `python-downloads = manual`.
  - Nery declined installing Python 3.12 on 2026-10-28 ("No instalar").
  - A run on Python 3.9 during the import found a runtime `str | list[str]` union that static tools had not flagged as a 3.9 problem; it was fixed with `empty_frontmatter()`.
- **Inferences:** a 3.12 runtime failure is unlikely after the static checks, but the 3.9 run shows a runtime check can find what they miss.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** users on 3.12 or 3.13 run a checker never executed on their version; the release went out on 2026-10-28 as 0.1.0.
- **Why it is not fixed now:** it needs a Python other than 3.15, which Nery declined.
- **Next action:** on Nery's yes, run the tests once with `uv run --python 3.12 --no-project` (a one-off download, no environment created).
- **Review condition:** closes when the checker's tests pass on 3.12, or when Nery drops the 3.12 floor.
- **Related records:** ADR_2026-10-28_instruction-engineering-joins-the-marketplace (superseded by ADR_2026-11-01_instruction-engineering-keeps-no-evals), ADR_2026-10-27_python-version-is-set-per-scope.

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
  - Reproduced on 2026-11-01: a plugin scaffolded into a scratch `TCF_ROOT` and piped through `biome format --stdin-file-path=plugins/<name>/.claude-plugin/plugin.json` comes back with `keywords` and `metadata.surfaces` spread over several lines.
- **Inferences:** none.
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
| **Owner** | `plugins/python-lsp-intelligence/hooks/check.py` (plugin scope; unchanged since 0.3.0, current 0.3.1) |
| **Logged** | 2026-10-29 |

#### 🔎 Evidence

- **Confirmed facts:**
  - `hooks/check.py` runs `basedpyright` on the edited file with the project's config (`-p <config> <file>`, line 339 on 2026-11-01) and the interpreter basedpyright finds by default. It has no branch for a file whose first line is `#!/usr/bin/env -S uv run --script`.
  - On 2026-10-29, every Edit and Write of `plugins/github-operations/skills/github/scripts/check-forms.py` (PEP 723: `ruamel.yaml`, `check-jsonschema`) made the hook block with `reportMissingImports` on `ruamel.yaml` and about 120 cascading `reportUnknown*` errors. The same file checked with `uv run --quiet --no-project --with-requirements <file> basedpyright --warnings <file>` reported 0 errors, 0 warnings, 0 notes.
  - That path no longer exists: commit b4109a2 (2026-11-04) removed the `github` skill. The script now lives at `plugins/github-operations/skills/github-files-setup/scripts/check-forms.py`, and on 2026-11-04 the hook blocked its edits with the same false errors; checked in its own uv environment it was clean.
  - On 2026-11-04, `hooks/check.py` still runs `basedpyright -p <config> <file>` at line 339 and has no `uv run` branch (0 matches); python-lsp-intelligence is still 0.3.1.
  - The repository's `basedpyright-plugins:<file>` gate (`scripts/gates.mjs`, commit 9ac3b11) already checks each PEP 723 plugin script that way.
  - The skill's own Gotchas already tell Claude that the server shows false import errors on PEP 723 scripts; the hook does not apply that knowledge.
- **Inferences:** every user of the plugin who edits a PEP 723 script with third-party dependencies gets the same blocking false errors after each edit.
- **Open questions:** what the hook does when `uv` is not installed on the user's machine: skip basedpyright for that file with a one-line note, or keep today's run.

#### 📈 Impact and next step

- **Impact / risk:** the post-edit hook blocks every edit of a PEP 723 script with errors that are not real, which trains Claude to ignore the hook's findings and buries real errors in the noise.
- **Why it is not fixed now:** the change belongs to another plugin, with its own pull request and version bump. Nery queued it after the github-operations 0.5.0 release, which was tagged on 2026-10-29, and no session has taken it since.
- **Next action:** in `hooks/check.py`, when the file's first line is the `uv run --script` shebang and `uv` is on `PATH`, run `uv run --quiet --no-project --with-requirements <file> basedpyright -p <config> <file>`; add a test in `scripts/testers/python-lsp-intelligence/` with a PEP 723 fixture that imports a third-party package, RED first; declare `uv` as optional in the README; version and release it through `versioning` and `releases`.
- **Review condition:** closes when an edit of a PEP 723 script with third-party dependencies produces no false `reportMissingImports` from the hook and the new test passes.
- **Related records:** DEBT-041; the `basedpyright-plugins:` gate in `scripts/gates.mjs`.

### DEBT-043 — No CI workflow runs the eval suites that `operating-standard.md` requires

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality, cost |
| **Owner** | Nery |
| **Logged** | 2026-11-01 |

#### 🔎 Evidence

- **Confirmed facts:**
  - `.claude/rules/operating-standard.md` → Evals in CI requires the whole suite of a plugin with evals the first time and every time the plugin has changes that take a pull request.
  - `plugins/project-maintainer/evals` and `plugins/skill-diagnostics/evals` exist; `grep -ln 'plugin eval' .github/workflows/*` prints nothing. The workflows are `claude-code-review.yml`, `claude.yml`, `release.yml` and `validate.yml`.
  - The previous `evals.yml` was removed in commit c748041 (2026-10-25), to be rebuilt from the `testing-plugins` skill; that skill ships the template `assets/evals-ci.yml` and the checklist in `references/eval-policy.md`.
  - On 2026-11-01 Nery chose to keep the rule and log the missing workflow as debt, to be built once he approves the spend.
  - Commit a57621d92a421f3e4c6e9b1965aac4c64810a8a7, "ci(evals): run the suite … with grants per plugin", is unreachable in the clone: c748041 replaced it 4 minutes later. It holds a per-plugin `.github/evals/*.json` layout and a rewritten `evals.yml`. Its grants and cost caps are also in `c748041^:scripts/evals-config.json`. It is kept as `refs/repo-cleanup-backup/lost-a57621d` in `~/Claude/backups/the-claude-factory/2026-11-01-audit/all.bundle`.
  - `instruction-engineering` has no eval suite, by ADR_2026-11-01_instruction-engineering-keeps-no-evals.
- **Inferences:** none.
- **Open questions:** the `--max-cost-usd` cap per run; whether a57621d's per-plugin layout is worth reusing.

#### 📈 Impact and next step

- **Impact / risk:** a pull request that changes `project-maintainer` or `skill-diagnostics` merges without its eval suite, so a regression in what those plugins teach reaches users unmeasured, against the rule.
- **Why it is not fixed now:** the workflow spends Claude usage on every pull request that edits a plugin with evals, and needs Nery's approval of that spend.
- **Next action:** on Nery's approval, adapt `testing-plugins/assets/evals-ci.yml` into `.github/workflows/evals.yml` with the checklist in `references/eval-policy.md`, then commit it only after he approves.
- **Review condition:** closes when a pull request that changes a plugin with evals runs its whole suite in CI and a pull request that changes no such plugin skips it.
- **Related records:** ADR_2026-10-21_ci-installs-claude-code-from-signed-apt; ADR_2026-10-28_withdrawn-debt-leaves-no-closed-entry.

### DEBT-044 — tailwind-development phase 2 exists only in a local stash on a pre-0.2.0 base

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality |
| **Owner** | Nery |
| **Logged** | 2026-11-01 |

#### 🔎 Evidence

- **Confirmed facts:**
  - `stash@{0}` (38661b87354105489693c11c565fc93e334a2436), "tailwind-development phase 2 WIP", was made on `feat/tailwind-development` on base 42ca474 (2026-10-27), before `tailwind-development` 0.2.0. Its content sits in its untracked parent e76475f, so `git stash show --stat` prints nothing.
  - It holds three files, 532 lines: `plugins/tailwind-development/scripts/lib/project.mjs` (321), `plugins/tailwind-development/shared/v4-traps.md` (52) and `scripts/tests/tailwind-development/project.test.mjs` (159).
  - None of them exists on `main`, in the six `tailwind-development--v*` tags (0.1.0 to 0.3.1) or anywhere else in the object store. The branch no longer exists, and a stash does not reach GitHub.
  - It is out of date: the test folder is now `scripts/testers/`, `v4-traps.md` names a `scan-v4-traps.mjs` that was never written, and its trap table was checked against Tailwind 4.3.3 on 2026-10-27. The plan is `.claude/plans/2026-10-27-tailwind-development-phase-2-inputs.md`.
  - Backed up on 2026-11-01 in `~/Claude/backups/the-claude-factory/2026-11-01-audit/`: `all.bundle` (ref `refs/repo-cleanup-backup/stash-0`) and `stash-0.patch`, with `manifest.txt` holding their checksums. On 2026-11-01 Nery chose to keep the stash.
- **Inferences:** landing it needs the files rebuilt on 0.3.1, the trap table checked again against the current Tailwind v4, and a minor bump.
- **Open questions:** whether phase 2 is still wanted.

#### 📈 Impact and next step

- **Impact / risk:** the only copies of the phase 2 work are a local stash and a local backup; a `git stash drop` or a lost machine loses it.
- **Why it is not fixed now:** landing it is feature work on `tailwind-development`, and dropping it is Nery's call; he chose to keep it for now.
- **Next action:** ask Nery whether phase 2 goes ahead. If yes, rebuild it on `main` from the stash on a feature branch, through `building-plugins`, `versioning` and `releases`. If no, drop the stash and close this item as accepted.
- **Review condition:** closes when the phase 2 files land on `main` in a release, or when Nery drops phase 2.
- **Related records:** none.

### DEBT-045 — `claude-github-actions` cannot write a Claude workflow from scratch

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality |
| **Owner** | Nery |
| **Logged** | 2026-11-04 |

#### 🔎 Evidence

- **Confirmed facts:**
  - On 2026-11-04 (commit d7d9912), `plugins/github-operations/skills/claude-github-actions/SKILL.md` gained routes that diagnose a Claude step, audit and harden workflow files, and repair CI on the default branch. Since commit c0d0edd its "When not to use" section says "Writing a new workflow from scratch: not covered yet; tell the user." (line 35), and `plugins/github-operations/README.md:452` says "Writing a new workflow from scratch is not covered yet." No sibling skill is handed that work.
  - The CI/CD Engineering blueprint (rev 13.1), which Nery shared in that session, defines the missing authoring playbooks: 1, a mention assistant; 2, automated PR review, with a default profile on Anthropic's `code-review` plugin and a strict profile with no shell; 4, migration of a legacy workflow.
  - Nery chose, through the approved plan, to defer authoring to the next change.
- **Inferences:** a request such as "add a workflow so Claude reviews every PR" is answered as out of scope.
- **Open questions:** which playbooks go first; whether the `code-review` plugin's skip conditions can be verified, since they were not found in `anthropics/claude-code@26382c0`.

#### 📈 Impact and next step

- **Impact / risk:** users who want Claude in their CI get no generated workflow, and may copy upstream examples that pin `@v6` or `@main`, interpolate `structured_output` into `run:` and name retired model IDs.
- **Why it is not fixed now:** deferred by Nery's decision; it needs the playbooks verified live, as the audit and diagnosis references were.
- **Next action:** ask Nery to choose the first authoring playbook, then build it in `claude-github-actions/references/`, following the verification rule of the 2026-11-04 plan.
- **Review condition:** closes when `claude-github-actions` can write at least the automated PR review workflow, with every reference verified at the then-current action commit.
- **Related records:** DEBT-046, DEBT-047.

### DEBT-046 — Nothing detects when claude-code-action changes the facts `claude-github-actions` relies on

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | maintainability |
| **Owner** | Nery |
| **Logged** | 2026-11-04 |

#### 🔎 Evidence

- **Confirmed facts:**
  - The references `sharp-edges.md`, `action-contract.md`, `trust-boundaries.md`, `auth-and-permissions.md` and `workflow-audit.md` under `plugins/github-operations/skills/claude-github-actions/references/` state the action's inputs, modes, actor gates, restored paths, log signals and GitHub MCP tool names. They were verified at `anthropics/claude-code-action@c0949c5` on 2026-11-04.
  - In that session, the blueprint's snapshot `6d5ae52`, from 2026-10-30, was already behind `c0949c5`.
  - No workflow under `.github/workflows/` watches the action (`claude-code-review.yml`, `claude.yml`, `release.yml`, `validate.yml`).
  - The plugin also relies on facts about `github/github-mcp-server`, and one was already wrong: on 2026-11-04 `github-files-setup/references/discussion-forms.md` listed category slugs with MCP `list_discussion_categories`, but its source (`pkg/github/discussions.go` on `main`) queries and returns only each category's `id` and `name`. Commit 285bf41 moved the step to `gh api graphql`.
- **Inferences:** the action and the MCP server both ship releases often, so a stated input, signal or tool name can go stale between plugin releases without anyone noticing.
- **Open questions:** whether the watch runs daily or on each release.

#### 📈 Impact and next step

- **Impact / risk:** the skill can tell users a fact the current action no longer holds, such as a removed input or a renamed log signal, and match a failure to the wrong sharp edge.
- **Why it is not fixed now:** it is maintainer automation outside this change and needs Nery's go-ahead for a new workflow in the marketplace repository.
- **Next action:** propose a scheduled workflow that resolves the action's latest release, diffs `action.yml` and the source files those references depend on against `c0949c5`, does the same for the `github/github-mcp-server` tool definitions the plugin names, and opens or updates one issue when they changed. It uses `gh api` and `git diff` only, with `permissions: {}` and `contents: read` plus `issues: write` on the job.
- **Review condition:** closes when that watch runs in the marketplace repository and its first issue, or its first clean run, is recorded.
- **Related records:** DEBT-045.

### DEBT-047 — `claude-github-actions` has no eval suite

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality |
| **Owner** | Nery |
| **Logged** | 2026-11-04 |

#### 🔎 Evidence

- **Confirmed facts:**
  - `plugins/github-operations/evals` does not exist (rechecked on 2026-11-04 after commits c0d0edd and 285bf41).
  - The diagnosis, audit and repair routes added on 2026-11-04 were checked only structurally: frontmatter, links and `claude plugin validate --strict`.
  - Nery asked that no tests or evals be run or created in that work.
- **Inferences:** whether the skill triggers on "the Claude review posted nothing" and stays silent on "fix the failing unit test" is untested.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** a wrong trigger, a missed sharp edge or an unsafe patch reaches users without a case that would catch it.
- **Why it is not fixed now:** Nery deferred evals.
- **Next action:** when Nery asks for evals, build a pilot suite through `testing-plugins`. Its first cases: one diagnosis case per log signal family, one audit case on a fixture workflow with seeded findings, and four trigger cases (two must load, two must not).
- **Review condition:** closes when the suite exists and has run once under `claude plugin eval`.
- **Related records:** DEBT-043, DEBT-045.

### DEBT-048 — github-operations 0.6.0 no longer writes, triages or answers issues and discussions, or turns an issue into a pull request

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality, compatibility |
| **Owner** | Nery |
| **Logged** | 2026-11-04 |

#### 🔎 Evidence

- **Confirmed facts:**
  - At tag `github-operations--v0.5.1`, the `github` skill routed `issue` (write, triage, mark a duplicate) to `references/authoring/issue.md`, "Fix issue #N" to `references/work/issue-to-pr.md`, and `discussion` to `references/authoring/discussion.md` (its SKILL.md lines 62 to 64).
  - Commit b4109a2 (2026-11-04) removed the `github` skill with those references. None of the four 0.6.0 skills or their agents covers them.
  - `plugins/github-operations/CHANGELOG.md:33` says "Writing issues and discussions (`issue`, `discussion`) is not part of this version", and the README's "Coming from 0.5.x?" table says "Not part of this version" for `issue` and `discussion`.
- **Inferences:** a 0.5.x user who updates and asks to file a bug, triage issues or fix issue #N gets no skill for it.
- **Open questions:** whether the capability comes back, and as its own skill or inside an existing one.

#### 📈 Impact and next step

- **Impact / risk:** 0.6.0 removes capabilities 0.5.x users had; until a decision, those requests fall outside the plugin.
- **Why it is not fixed now:** rebuilding them is a scope decision only Nery can make; ADR_2026-11-04_github-operations-0-6-0-ships-as-one-release keeps 0.6.0 to the four skills.
- **Next action:** ask Nery whether issue and discussion work returns, and where; then build it through `building-plugins`, `versioning` and `releases`.
- **Review condition:** closes when a release covers that work, or when Nery decides it stays out for good (closed as accepted, with an ADR).
- **Related records:** ADR_2026-11-04_github-operations-splits-into-focused-skills; ADR_2026-11-04_github-operations-0-6-0-ships-as-one-release.

### DEBT-049 — github-operations ships without an icon or a privacy policy URL, and turns on the GitHub MCP server's Insiders mode

| Field | Value |
| --- | --- |
| **Status** | 🟠 Blocked |
| **Category** | quality, compatibility |
| **Owner** | Nery |
| **Logged** | 2026-11-04 |

#### 🔎 Evidence

- **Confirmed facts:**
  - On 2026-11-04, `claude plugin validate --strict plugins/github-operations` (Claude Code 2.1.318) passed with two plugin directory warnings: ICON_MISSING and PRIVACY_URL_MISSING ("This plugin connects to a remote MCP server or HTTP hook but declares no privacy policy URL").
  - `plugins/github-operations/.mcp.json:9` sends `X-MCP-Insiders: true`. GitHub's `docs/server-configuration.md:348` (github/github-mcp-server, `main`, read 2026-11-04): "Features in Insiders Mode may change, evolve, or be removed based on user feedback."
  - The README discloses the early-access mode (lines 57 and 480).
- **Inferences:** the warnings do not change the validation result, but a submission to the plugin directory would need both fields; Insiders features can change under users between plugin releases.
- **Open questions:** which privacy policy the URL points to; whether Insiders mode stays.

#### 📈 Impact and next step

- **Impact / risk:** the listing has no icon or privacy link for a plugin that sends the user's token to a remote server, and users depend on experimental GitHub MCP features.
- **Why it is not fixed now:** the icon is an asset only Nery can supply, and the privacy URL and the Insiders choice are his decisions.
- **Next action:** ask Nery for a square PNG of 512 to 2048 px (saved inside the plugin, at `.claude-plugin/icon.png`), the privacy policy URL, and whether to keep `X-MCP-Insiders`; then apply them in a plugin change through `versioning` and `releases`.
- **Review condition:** closes when `claude plugin validate --strict` shows neither warning and the Insiders choice is applied and recorded.
- **Related records:** none.

### DEBT-050 — A new cloud session starts on Node 22 without shfmt, and npm refuses to run on Node 22 since the devEngines pin

| Field | Value |
| --- | --- |
| **Status** | 🔵 In progress |
| **Category** | maintainability, compatibility |
| **Owner** | Nery |
| **Logged** | 2026-11-04 |

#### 🔎 Evidence

- **Confirmed facts:**
  - Maintainer scope only: this concerns the cloud environment where Nery works on this repository, never a plugin or a user's machine.
  - On 2026-11-05 Nery created the personal cloud environment `the-claude-factory` (`env_01HumVFyT51CDf6AJdszJVkA`) with a setup script that installs Node from `.nvmrc`, npm 12.2.1, Python 3.15, ruff, basedpyright, ShellCheck, shfmt, actionlint, and Biome and TypeScript globally; it has no repository on its list yet. In the current container, shfmt v3.14.1 was installed with `go install mvdan.cc/sh/v3/cmd/shfmt@latest`.
  - The cloud container of 2026-11-04 started with Node 22.23.4 and npm 10.9.9 (`/opt/node22`), while `.nvmrc` says 26.13.0; `shfmt` was not on `PATH`, so the `shfmt-maintainer` and `shfmt-plugins` gates could not run.
  - Commit 2506755 set `devEngines.runtime` to `^26.13.0` with `onFail: error`. npm enforces `devEngines` since 10.9.0 (npm CHANGELOG, 2024-10-03).
  - With Node 24.22.1, both npm 11.19.1 and npm 12.2.1 stopped `npm run check:repo` with `EBADDEVENGINES`.
  - The session-start hook runs `npm install`, and the Husky hooks run `npm` scripts.
  - Stated by Nery on 2026-11-04: his MacBook is out of service, so he works only through Claude Code on the web.
- **Inferences:** in a new cloud session, `npm install`, `npm test` and the Husky hooks fail until Node 26 is installed. Not reproduced, because Node 22 was removed from this container.
- **Open questions:** none.

#### 📈 Impact and next step

- **Impact / risk:** every new cloud session starts unable to install the maintainer tools or commit through the hooks, which is Nery's only way to work while his machine is down.
- **Why it is not fixed now:** the cloud environment's Setup script is changed only by Nery, in the environment's settings on claude.ai (the cloud environment menu in the session's title bar, then Edit).
- **Next action:** add `nerymurillohnd/the-claude-factory` to the environment's repository list, start a new session on it, check that the setup summary shows no `MISSING` tool, then run `node --version` and `npm test`.
- **Review condition:** closes when a new cloud session starts on Node 26.13.0 with shfmt on `PATH`, and `npm test` passes there.
- **Related records:** ADR_2026-11-04_node-pinned-in-package-json-through-devengines; DEBT-051.

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
