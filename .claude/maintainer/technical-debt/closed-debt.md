# ✅ Closed Debt

> [!NOTE]
> The history of technical and maintenance debt that is no longer open: fixed, no longer applicable, or kept for good on purpose. Each entry holds the evidence that closes it. Entries arrive here from `pending-debt.md` with the same ID.

**Important:** a closed entry is a dated historical record. If a later change invalidates the closure, keep the original entry and open a new pending item that links back to it. The only field that changes afterwards is "Superseded by".

## 🚦 Outcomes

| Outcome | Meaning | Evidence it needs |
| --- | --- | --- |
| resolved | A fix aimed at this item was made and it works | A positive check and a negative check |
| obsolete | The condition no longer exists for another reason: a change not aimed at this item removed the code or changed the architecture, or the item was logged in error or duplicates another | A negative check, and what changed |
| accepted | The user decided to keep the condition for good | The accepted ADR that records the decision |

## 📚 Index

| Closed on | ID | Outcome | Closure | Superseded by |
| --- | --- | --- | --- | --- |
| 2026-10-21 | DEBT-003 | resolved | basedpyright checks every tracked Python file locally and the maintainer Python in CI | none |
| 2026-10-22 | DEBT-005 | resolved | project-maintainer guardrails ask in the documented tool.check form and pass 50 of 50 on Claude Code 2.1.307+ | none |
| 2026-10-25 | DEBT-007 | resolved | The maintainer Node and schema tests pass, and CI runs the schema tests | none |
| 2026-10-25 | DEBT-004 | obsolete | Dropped by Nery: its next action rested on an eval requirement he never set | none |
| 2026-10-26 | DEBT-012 | obsolete | Logged in error: project-maintainer's mod already reminds Claude of write-records, and a live session met the review condition | none |
| 2026-10-26 | DEBT-001 | resolved | pr-tracker inherits the session's tools, so a GitHub MCP server of any name reaches it | none |
| 2026-10-26 | DEBT-008 | accepted | `main` and the release tags stay without GitHub protection by Nery's decision | none |
| 2026-10-26 | DEBT-009 | resolved | Biome 2.6.3 formats and lints the Markdown outside `plugins/`, locally and in CI | none |
| 2026-10-26 | DEBT-011 | resolved | The plugin README template takes the published shape, a scaffolded plugin passes `check-repo.mjs`, and the frozen templates are gone | none |

## 🏁 Closed items

### DEBT-003 — basedpyright checks every tracked Python file locally and the maintainer Python in CI

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-21 |
| **Logged on** | 2026-10-20 |
| **Owner** | `.claude/rules/QUALITY_GATE.md` (step 17), `.github/workflows/validate.yml`, `.pre-commit-config.yaml` |

#### ❗ The problem

basedpyright checked only the Python files outside hidden folders: at the repository root it found the `plugins/` files and never the tests under `.github/scripts/tests/`, and `validate.yml` never ran it. A basedpyright finding in those tests passed every gate, and a finding anywhere reached `main` whenever the local step was skipped.

#### 🔧 The closure

The cause was the folder, not the command. basedpyright's documented default excludes `**/.*`, an `exclude` setting only adds to it, and the patterns win over `include`, so the next action this entry recorded (pass the file list) could not work: the test files passed on the command line gave "No source files found". The maintainer scripts and their tests moved to `scripts/` (ADR_2026-10-21_maintainer-scripts-at-root), and the 4 errors and 28 warnings basedpyright then found in `scripts/tests/python-lsp-intelligence/test_check.py` were fixed (commit 75da92b). `scripts/gates.mjs` runs basedpyright on `scripts/` in the CI `python` job and on `plugins/` locally (ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure), the split Nery decided for plugin code analysis.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | `basedpyright --warnings --verbose` at the root: `Found 7 source files`, `0 errors, 0 warnings, 0 notes` (2026-10-21). `npm run gates:ci -- --group python`: `basedpyright-scripts` passed, exit 0 (2026-10-21, local simulation of the CI job). |
| 🚫 **Negative:** the original failure or condition is gone | Before the move the root reported `Found 4 source files` and the tests passed explicitly reported `No source files found`; after it, all 7 tracked `.py` files are found, the 3 tests included. |

#### 🔗 Follow-up

- **Residual risk:** the CI job has not run on GitHub yet; it runs on the branch's first push. basedpyright on `plugins/` runs only locally, by decision.
- **Closed by:** ADR_2026-10-21_maintainer-scripts-at-root, ADR_2026-10-21_ci-checks-maintainer-tooling-and-plugin-structure, commits e8f3b8c and 75da92b.
- **Related records:** ADR_2026-10-21_gates-run-from-one-script.
- **Superseded by:** none

### DEBT-005 — project-maintainer guardrails ask in the documented tool.check form and pass 50 of 50 on Claude Code 2.1.307+

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-22 |
| **Logged on** | 2026-10-22 |
| **Owner** | `plugins/project-maintainer` (its mod tests), the `mod-test:project-maintainer` gate of `scripts/gates.mjs` |

#### ❗ The problem

`claude plugin test plugins/project-maintainer` failed 5 of 50 on Claude Code 2.1.307 and 2.1.308, all authority-guard tests (`Expected: "person"`, `Received: undefined` on `verdict.decider`), after passing 50 of 50 on 2.1.304. Whether the shipped guards still asked the person live was unknown.

#### 🔧 The closure

Cause: Claude Code 2.1.307 removed `decider` from the `tool.check` result. The engine-written declarations went from `decider?: ToolCheckDecider` (written by 2.1.304) to an engine-pinned `plugin?: string` (written by 2.1.308), and the official changelog from 2.1.295 to 2.1.308 has no entry for it. The mod docs pages (`/en/plugins/mods/events`, `/en/plugins/mods/reference`) never documented `decider`: a `tool.check` answer is `{ decision, reason }`. The same docs say to trust the declarations the engine writes for the installed build over any page (Create a mod → Get type definitions for your version), and the 2.1.308 declarations pin `plugin` on a hook's `ask`, put it to a person and let no classifier's allow settle it. The guard now returns `{ decision: 'ask', reason }`, the tests assert `decision`, `reason` and `plugin`, and project-maintainer 0.2.0 requires Claude Code v2.1.307. On 2026-10-22 Nery replaced the review condition's "live run" with the tests plus a `--debug-file` log of a real session, because the official docs win over a project condition and offer `claude plugin test` and `--debug-file`, not a terminal-scraping test. That log shows the guard's ask reaching the permission dialog. Nery then ran the live check himself on 2026-10-22 (Claude Code 2.1.308, auto mode, `--plugin-dir` on the branch, an accepted ADR): asked to change the chosen option, Claude Code showed `Do you want to make this edit to ADR_2026-03-14_keep-sessions-in-postgres.md?`, Nery answered **No**, the transcript read `User rejected update`, and `grep` showed the file unchanged (`Chosen option: **Postgres**.`). The dialog was the `.claude/` protected-folder prompt and showed no reason from the guard. In a second session Nery chose **Yes, and allow Claude to edit files in this project's .claude folder for this session**; the next edit of the same accepted ADR asked him again, so a session-wide approval does not switch the guard off.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | `claude plugin test plugins/project-maintainer` on 2.1.307 and 2.1.308: `50 pass`, `0 fail`; `tsc -p plugins/project-maintainer/tsconfig.json --noEmit` exit 0; `claude plugin validate --strict`: `Validation passed`. Breaking the authority guard on purpose gave `46 pass`, `4 fail`, then restored. Live, 2.1.308, auto mode, settled ADR: `--debug-file` shows `project-maintainer@inline tool.check settled in 5.3ms`, `executePermissionRequestHooks called for tool: Edit`, `Slow permission decision: 112464ms` and the screen shows `Do you want to make this edit to ADR_2026-03-14_keep-sessions-in-postgres.md?`; the control with a `proposed` ADR showed no dialog and `Allowed by auto mode classifier`. The settled run's final `allow` came from the test script's own keystroke, not from a classifier. |
| 🚫 **Negative:** the original failure or condition is gone | The 0.1.0 code (`git archive` of `origin/main`) still fails on 2.1.307 and 2.1.308 with `45 pass`, `5 fail`, and passes `50 pass` on 2.1.306, so the failure is the 2.1.307 contract change and the fix removes it. |

#### 🔗 Follow-up

- **Residual risk:** the routing of a hook's `ask` to a person is stated in the engine's declarations, not on the docs pages, and the mod API can change again without a changelog entry. Users on 2.1.304 to 2.1.306 who update the plugin without updating Claude Code can have auto mode's classifier approve a guarded edit; on 2.1.306 the suite fails 44 of 50 for that reason. Reporting the undocumented 2.1.307 change to the docs team waits on Nery's approval.
- **Closed by:** commits 03ba140, d8f3e94 and ae98a47 on branch `fix/project-maintainer-mod-ask-api`.
- **Related records:** none.
- **Superseded by:** none

### DEBT-007 — The maintainer Node and schema tests pass, and CI runs the schema tests

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-25 |
| **Logged on** | 2026-10-24 |
| **Owner** | `scripts/tests/gates.test.mjs`, `scripts/tests/schemas/` |

#### ❗ The problem

`node --test "scripts/tests/*.test.mjs"` failed 3 tests in `gates.test.mjs`: two for `argsAtRun`, a runner feature removed from `scripts/gates.mjs`, and the `--ci` test, which expected the removed `pytest-env`, `basedpyright-maintainer` and `pytest-scripts` gates. The schema tests loaded the root monoliths `plugin`, `marketplace`, `hooks`, `lsp` and `mcp.schema.json`, which no longer exist, and asserted each schema's `$id`; case `mcp-63` expected an empty `mcpServers` map to fail although `claude plugin validate --strict` accepts it. The red `node-tests` gate hid any new failure.

#### 🔧 The closure

The two `argsAtRun` tests were removed, as the entry's next action said. `basedpyright-maintainer` and `pytest-scripts` exist again as gates of the `python` group: `scripts/basedpyright-maintainer.mjs` type-checks each maintainer file against its own interpreter, and `pytest-scripts` runs `scripts/tests/run_pytest.py scripts/tests/schemas` (commit 097c912). The schema tests now register every schema under its file URI, validate each kind of file through its folder's entry schema, and assert that no schema declares `$id`. `mcp-63` expects valid; `mcp-61` and `mcp-23` stay invalid with the more precise error paths the if/then transport selection reports (commit bf14629).

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | `node --test "scripts/tests/*.test.mjs"`: every test passes, `gates.test.mjs` 13 of 13. `scripts/tests/run_pytest.py scripts/tests/schemas`: `193 passed`, no skip. `node scripts/gates.mjs --ci`: `✔ All gates passed`, with `node-tests`, `basedpyright-maintainer` and `pytest-scripts` passing (2026-10-25). |
| 🚫 **Negative:** the original failure or condition is gone | The 3 `gates.test.mjs` failures no longer reproduce, and the schema tests no longer reference a root monolith (`grep` for the five root names in `test_schemas.py` finds none). A type error planted in a validator in a throwaway worktree makes `basedpyright-maintainer.mjs` exit 1. |

#### 🔗 Follow-up

- **Residual risk:** the schema tests use the python `jsonschema` library while the validators use jsonschema-rs; parity was measured at 107 instances with no difference on 2026-10-24, and nothing re-measures it.
- **Closed by:** commits 097c912 and bf14629.
- **Related records:** ADR_2026-10-24_maintainer-tests-run-pytest-from-a-pep723-runner, ADR_2026-10-24_schema-identity-is-its-file-location.
- **Superseded by:** none

### DEBT-004 — Dropped by Nery: its next action rested on an eval requirement he never set

| Field | Value |
| --- | --- |
| **Outcome** | obsolete |
| **Closed on** | 2026-10-25 |
| **Logged on** | 2026-10-22 |
| **Owner** | `plugins/typescript6-lsp-intelligence/hooks/tsc-check.sh` and its byte-identical copy in `typescript7-lsp-intelligence` |

#### ❗ The problem

It was unproven that the TypeScript post-edit hook's `PostToolUse` `decision: "block"` makes Claude fix the type errors before it moves on, while the README promises that Claude "has to fix it before continuing". The entry's next action was to write the plugin's evals because `.claude/CLAUDE.md` → Plugin Tooling required every plugin that ships hooks to carry evals.

#### 🔧 The closure

Logged in part in error. The eval requirement came from a CLAUDE.md draft applied on 2026-10-24 that contradicted Nery's own instruction of the same day, that plugins get evals only when he requests them. On 2026-10-25 Nery had the line removed from `.claude/CLAUDE.md` and dropped this item. No change was made to either plugin.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| 🚫 **Negative:** the original failure or condition is gone | `grep -n "carries evals" .claude/CLAUDE.md` finds nothing (2026-10-25). The hook behavior itself was not tested. |

#### 🔗 Follow-up

- **Residual risk:** the README claim that Claude "has to fix it before continuing" is still unproven by a controlled test; only everyday use while editing this repository's `.mjs` files suggests it holds.
- **Closed by:** Nery's decision on 2026-10-25.
- **Related records:** ADR_2026-10-22_tsc-hook-policy-defaults-user-wins.
- **Superseded by:** none

### DEBT-012 — Logged in error: project-maintainer's mod already reminds Claude of write-records, and a live session met the review condition

| Field | Value |
| --- | --- |
| **Outcome** | obsolete |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-25 |
| **Owner** | `plugins/project-maintainer` (skill `write-records`, its mod) |

#### ❗ The problem

The pending entry said the `write-records` skill was not loaded before records were written, because its description names events and "nothing reminds or requires it". On 2026-10-25 nine records of this repository were written without the skill. Its review condition: closes when a session that edits a record under `.claude/maintainer/`, without being asked to use the skill, loads it first or is told to; shown by a test or a recorded live session.

#### 🔧 The closure

Logged in error. The mod has reminded Claude of the skill since it was added on 2026-10-19 (commit `0f672e7`, "add a mod that enforces the rules of the records"): after a commit that looks like a decision, it tells Claude to record it with `write-records` (`plugins/project-maintainer/hooks/guard.ts`, `nudgeText`). The claim "nothing reminds" was false when the item was logged. Closed on Nery's order on 2026-10-26.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | not applicable |
| 🚫 **Negative:** the original failure or condition is gone | Live session of 2026-10-26 (project-maintainer 0.2.1, Claude Code 2.1.310): after commit `05c0462`, which touched `.github/workflows/`, the session received "Project Maintainer: the commit just made shows a CI workflow. If it settles a decision or leaves a problem that cannot be fixed now, record it with the write-records skill." Nery had not asked for the skill. Claude loaded `write-records` and then wrote ADR_2026-10-26_claude-workflows-follow-the-official-template and the supersede edit through it. `git log -S "record it with the write-records skill" -- plugins/project-maintainer/hooks/guard.ts` returns `0f672e7 2026-10-19`, six days before the item was logged. |

#### 🔗 Follow-up

- **Residual risk:** the reminder fires after a commit whose files or message look like a decision; a record edited in the middle of other work, before any such commit, still depends on Claude matching the skill's event-based description.
- **Closed by:** none
- **Related records:** ADR_2026-10-22_mod-guardrails-fail-closed-for-records, ADR_2026-10-26_claude-workflows-follow-the-official-template.
- **Superseded by:** none

### DEBT-001 — pr-tracker inherits the session's tools, so a GitHub MCP server of any name reaches it

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-19 |
| **Owner** | `plugins/github-operations` (agent `pr-tracker`, skill `auto-pr-lifecycle`) |

#### ❗ The problem

`plugins/github-operations/agents/pr-tracker.md` (0.3.1) set `tools:` to `ToolSearch` plus exact MCP tool names under two prefixes only, `mcp__plugin_github-operations_github__*` and `mcp__github__*`. In desktop Code tab sessions on PR #22 (2026-10-19) and PR #36 (2026-10-21) the session's GitHub tools were named `mcp__650eb531-…__*`, so the tracker launched with no GitHub tool and reported `BLOCKED`.

#### 🔧 The closure

On Nery's order the agent's `tools` allowlist was removed with no `disallowedTools`, so it inherits every tool of the session: [PR #37](https://github.com/nerymurillohnd/the-claude-factory/pull/37) (`4d0d65e`, 2026-10-22), shipped in github-operations 0.4.0 and kept in 0.4.1. The README FAQ says the agent can use every session tool and points to deny rules for a hard limit. The pending entry's next action also asked for a `PreToolUse` hook blocking the tracker's write calls and a desktop live run; both went beyond the logged problem, and the hook contradicts Nery's choice of inheritance with user deny rules, so neither is pursued.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | On 2026-10-22 the tracker (0.4.0, CLI session) read the checks, reviews, diff and Dependabot alerts of [PR #38](https://github.com/nerymurillohnd/the-claude-factory/pull/38) twice and reported `READY_FOR_MAIN_SESSION`. `/en/sub-agents` (read 2026-10-26): `tools` "Inherits every tool available to subagents if omitted", and "Subagents inherit the built-in tools and MCP tools available in the main conversation", whatever the server's name. |
| 🚫 **Negative:** the original failure or condition is gone | `grep -n -E "^(tools\|disallowedTools):" plugins/github-operations/agents/pr-tracker.md` finds nothing on 0.4.1 (2026-10-26): the fixed two-prefix allowlist that hid a connector named `mcp__<uuid>__*` no longer exists. |

#### 🔗 Follow-up

- **Residual risk:** the tracker can call every tool of the session, GitHub write methods included; its instructions keep it read-only and the README tells users how to deny tools. No live run from the desktop Code tab with only the Claude app connector has been recorded; the inheritance there rests on the docs.
- **Closed by:** [PR #37](https://github.com/nerymurillohnd/the-claude-factory/pull/37) (`4d0d65e`).
- **Related records:** ADR_2026-10-18_fold-pr-diagnostics-into-pr-tracker; PR #22, PR #36 (where it was observed).
- **Superseded by:** none

### DEBT-008 — `main` and the release tags stay without GitHub protection by Nery's decision

| Field | Value |
| --- | --- |
| **Outcome** | accepted |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-25 |
| **Owner** | GitHub repository settings of `nerymurillohnd/the-claude-factory` |

#### ❗ The problem

`main` had no branch protection and the repository had no rulesets, so the CI gate before users was voluntary, a push to `main` that fails Validate was not refused, and a `<plugin>--v<version>` release tag could be moved or deleted. The pending entry's next action was a ruleset on `main` requiring Validate and pull requests, and a tag ruleset on `*--v*`.

#### 🔧 The closure

Nery decided on 2026-10-26 to keep `main` and the release tags without GitHub protection, because the repository has a sole maintainer: only Nery and Claude Code push to it, and a ruleset requiring pull requests clashes with the rule that changes outside `plugins/` go straight to `main`. ADR_2026-10-26_main-and-release-tags-stay-unprotected records the decision.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | ADR_2026-10-26_main-and-release-tags-stay-unprotected, status `accepted`. On 2026-10-26 `gh api repos/nerymurillohnd/the-claude-factory/rulesets` returned no ruleset and `…/branches/main/protection` returned `Branch not protected` (HTTP 404), the state the decision keeps. |
| 🚫 **Negative:** the original failure or condition is gone | not applicable |

#### 🔗 Follow-up

- **Residual risk:** nothing on GitHub refuses a push to `main` that fails Validate, an unsigned commit (the three commits of PR #51 reached `main` unsigned on 2026-10-26), or a moved or deleted `*--v*` tag.
- **Closed by:** ADR_2026-10-26_main-and-release-tags-stay-unprotected.
- **Related records:** ADR_2026-10-25_release-tags-are-created-unsigned-by-ci.
- **Superseded by:** none

### DEBT-009 — Biome 2.6.3 formats and lints the Markdown outside `plugins/`, locally and in CI

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-25 |
| **Owner** | Maintainer tooling (`biome.json`, `scripts/gates.mjs`, `.github/workflows/validate.yml`, `.claude/CLAUDE.md` → Maintainer Tooling) |

#### ❗ The problem

`biome.json` read only JS, TS and JSON, so `biome check README.md` reported the file as ignored, while `.claude/CLAUDE.md` said Biome formats and lints Markdown. A malformed doc users read passed every check.

#### 🔧 The closure

Biome 2.6 supports Markdown. `biome.json` now includes `*.md`, excludes the never-format files and each plugin's Markdown until it adopts the format, parses frontmatter, indents with spaces, and turns on the three Markdown nursery rules (`useConsistentHeadingLevel`, `useFencedCodeLanguage`, `useSingleTopLevelHeading`) as errors, since the recommended preset leaves nursery rules off. The maintainer gate of `scripts/gates.mjs` passes `*.md` paths to `biome ci`, `validate.yml` installs `@biomejs/biome@2.6.3`, and `catalog.mjs` writes a `biome-ignore format` comment before each table so the catalog stays as generated. The 29 maintainer Markdown files were formatted. ADR_2026-10-26_biome-formats-and-lints-maintainer-markdown records the decision.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | On 2026-10-26 with Biome 2.6.3: `biome ci --error-on-warnings` on the maintainer gate's paths checked 105 files with no fixes; `node scripts/generators/catalog.mjs --check` and `marketplace.mjs --check` passed after formatting; `node --test scripts/tests/scripts.test.mjs scripts/tests/gates.test.mjs` passed 62 of 62. |
| 🚫 **Negative:** the original failure or condition is gone | In a scratch worktree, a planted `docs/planted.md` with a heading jump, a fenced block without a language and two top-level headings failed `biome lint` with `useConsistentHeadingLevel`, `useFencedCodeLanguage` and `useSingleTopLevelHeading`, and an unpadded table in it made `biome ci` exit 1. |

#### 🔗 Follow-up

- **Residual risk:** the plugins' Markdown joins only on each plugin's next change (DEBT-013); Biome does not check links, anchors or prose.
- **Closed by:** ADR_2026-10-26_biome-formats-and-lints-maintainer-markdown.
- **Related records:** ADR_2026-10-21_remove-markdownlint.
- **Superseded by:** none

### DEBT-011 — The plugin README template takes the published shape, a scaffolded plugin passes `check-repo.mjs`, and the frozen templates are gone

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-25 |
| **Owner** | `building-plugins` (`assets/README-template.md`, `scripts/scaffold-plugin.py`), `scripts/check-repo.mjs`, `scripts/tests/scripts.test.mjs` |

#### ❗ The problem

The skill's README template had its own eight sections and one "Works in" line, while the 17 published READMEs, the frozen `.claude/templates/plugin/README.md` and `REQUIRED_PLUGIN_SECTIONS` shared another shape. A plugin the scaffold created failed `check-repo.mjs` with `README.md missing the "Why use it" section`, the tests built their fixture from the frozen README, and every template existed twice.

#### 🔧 The closure

Nery chose the published shape (ADR_2026-10-26_plugin-readme-template-takes-the-published-shape). The template was rebuilt on it with the "What this plugin runs and sends" disclosure kept (commit `fdd05ff`), the scaffold fills the identity and surface parts (`fab4add`), `check-repo.mjs` reports author placeholders left outside code and the tests build their demo plugin with the scaffold (`64f2af5`), and `.claude/templates/` was deleted with its live references (`5836c06`). The 17 published READMEs were not touched.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | On 2026-10-26 in a scratch worktree, a plugin from `scaffold-plugin.py`, with its placeholders filled, its Compatibility table trimmed to Skills and one skill added, passed `node scripts/check-repo.mjs` (`✔ Repository checks passed`). `node --test scripts/tests/scripts.test.mjs scripts/tests/gates.test.mjs`: 64 of 64 pass; check-repo passes on the repository. |
| 🚫 **Negative:** the original failure or condition is gone | The same fresh scaffold fails with `README.md has unresolved <…> placeholders`, not with a missing section; `grep -rn ".claude/templates"` finds no live reader outside dated specs and ADRs. |

#### 🔗 Follow-up

- **Residual risk:** the placeholder check skips code spans and fenced blocks, so a placeholder left only inside code passes.
- **Closed by:** ADR_2026-10-26_plugin-readme-template-takes-the-published-shape, commits `fdd05ff`, `fab4add`, `64f2af5` and `5836c06`.
- **Related records:** ADR_2026-10-25_plugin-scaffold-belongs-to-building-plugins.
- **Superseded by:** none

<!--
Entry format. Copy this block above this comment for each closed item and add its row to the Index.
Use the ID the item had in pending-debt.md. Delete these instructions from the copy.

### DEBT-NNN — {{Short closure title}}

| Field | Value |
| --- | --- |
| **Outcome** | {{resolved, obsolete or accepted}} |
| **Closed on** | {{YYYY-MM-DD}} |
| **Logged on** | {{YYYY-MM-DD, copied from the pending entry}} |
| **Owner** | {{Copied from the pending entry}} |

#### ❗ The problem

{{The original limitation, risk or follow-up, as it stood in the pending entry.}}

#### 🔧 The closure

{{resolved: the corrective change and the resulting state. obsolete: what changed and why the condition no longer applies, or that it was logged in error or duplicates DEBT-NNN. accepted: the ADR ID and the decision to keep the condition.}}

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | {{resolved: the fix works, with commands, tests or review. obsolete: "not applicable". accepted: the ADR ID with status accepted.}} |
| 🚫 **Negative:** the original failure or condition is gone | {{resolved or obsolete: it no longer reproduces or exists; showing that a new path works is not enough. accepted: "not applicable".}} |

#### 🔗 Follow-up

- **Residual risk:** {{Anything left over, or "none".}}
- **Closed by:** {{The ADR ID, commit or pull request that caused the closure, or "none".}}
- **Related records:** {{Links to issues, ADRs or PRs, or "none".}}
- **Superseded by:** {{The ID of a newer item when this closure no longer describes the current state, or "none".}}
-->
