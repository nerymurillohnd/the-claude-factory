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
| 2026-10-26 | DEBT-006 | resolved | Each validator of `scripts/validators/` is a gate of the CI python group, on Python 3.15 | none |
| 2026-10-26 | DEBT-013 | accepted | Biome never formats the plugins' Markdown, by Nery's decision | none |
| 2026-10-26 | DEBT-018 | resolved | building-plugins checks a new name against this marketplace before design | none |
| 2026-10-26 | DEBT-019 | obsolete | The mod READMEs already state the tested Claude Code version | none |
| 2026-10-26 | DEBT-021 | resolved | A validator fails on dead skill and path references in the project skills and CLAUDE.md | none |
| 2026-10-26 | DEBT-022 | obsolete | Nery dropped the five handoff items that named removed skills and files | none |
| 2026-10-26 | DEBT-024 | obsolete | Dropped by Nery: the never-run `block-no-verify` checks are no longer tracked | none |
| 2026-10-26 | DEBT-029 | obsolete | Dropped by Nery: the `claude-review` failures on PRs #20, #28 and #29 are no longer investigated | none |
| 2026-10-26 | DEBT-033 | resolved | `.editorconfig` is the only source of indentation and line endings for Biome | none |
| 2026-10-27 | DEBT-034 | resolved | Biome checks every tsconfig file, with an `expand: "auto"` override | none |
| 2026-10-27 | DEBT-032 | resolved | Biome's `useLiteralKeys` is off, so tsc's `noPropertyAccessFromIndexSignature` alone decides index-signature keys | none |
| 2026-10-27 | DEBT-014 | obsolete | `release.yml` published release notes built by `release-notes.py` for two new tags | none |
| 2026-10-27 | DEBT-026 | obsolete | `.claude/rules/readme-md.md` loads when a README is read | none |

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

### DEBT-006 — Each validator of `scripts/validators/` is a gate of the CI python group, on Python 3.15

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-24 |
| **Owner** | `scripts/gates.mjs`, `.github/workflows/validate.yml` |

#### ❗ The problem

On 2026-10-24 `check-repo.mjs` handed its plugin-structure checks to the validators of `scripts/validators/`, but no gate ran them: only the `PreToolUse` hook `.claude/hooks/validators-gate.sh` did, before a push from a Claude Code session. A push from a terminal and every CI run skipped them, so a pull request that broke a plugin name, version or required file passed CI.

#### 🔧 The closure

`scripts/gates.mjs` builds one gate per file of `scripts/validators/`, `validator:<name>`, in the `python` group CI runs. A PEP 723 validator runs by path in its own uv environment; a standard-library one runs through `uv run --no-project --python 3.15`, because CI's `python3` is 3.12 and those validators need 3.15. The Husky pre-push hook runs `npm run gates`, so a push from any terminal runs them too. Commit `fd2330a`.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | On 2026-10-26 `node scripts/gates.mjs --only validator:` ran the nine gates and all passed; the test `every validator runs in the CI python group on Python 3.15` passes in `scripts/tests/gates.test.mjs` (19 of 19). |
| 🚫 **Negative:** the original failure or condition is gone | With `plugins/turn-meter/LICENSE` moved away, `node scripts/gates.mjs --ci --group python` failed with `✖ [plugins/turn-meter] LICENSE is missing` and `✖ validator:plugin-required-files (exit 1)`; the file was restored. |

#### 🔗 Follow-up

- **Residual risk:** the CI python job has not run the new gates yet; the next push shows it.
- **Closed by:** ADR_2026-10-26_npm-tools-and-git-hooks-are-pinned-dev-dependencies.
- **Related records:** ADR_2026-10-24_repository-checks-move-to-python-validators, ADR_2026-10-21_gates-run-from-one-script.
- **Superseded by:** none

### DEBT-013 — Biome never formats the plugins' Markdown, by Nery's decision

| Field | Value |
| --- | --- |
| **Outcome** | accepted |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-26 |
| **Owner** | `biome.json` (`!plugins/<name>/**/*.md` lines) and each plugin's next change, through `building-plugins` step 5 |

#### ❗ The problem

`biome.json` listed one `!plugins/<name>/**/*.md` line per plugin, 17 lines, so Biome read none of the plugins' Markdown until each plugin's next change adopted it. A plugin that never changed again kept its Markdown unformatted and unlinted.

#### 🔧 The closure

Nery decided on 2026-10-26 that Biome never formats the Markdown under `plugins/` or `.claude/skills/` (ADR_2026-10-26_biome-never-formats-plugin-and-skill-markdown). The condition is kept for good: one `!plugins/**/*.md` line replaces the 17, and `building-plugins` step 5 no longer adopts Biome (commit fcd793c).

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | ADR_2026-10-26_biome-never-formats-plugin-and-skill-markdown, status accepted. `biome.json` has `"!plugins/**/*.md"` and `"!.claude/skills/**/*.md"`; `biome ci .` exits 0 and reports `plugins/turn-meter/README.md` as ignored (2026-10-26). |
| 🚫 **Negative:** the original failure or condition is gone | not applicable |

#### 🔗 Follow-up

- **Residual risk:** heading levels and fenced-code languages in plugin Markdown are checked only by reading.
- **Closed by:** ADR_2026-10-26_biome-never-formats-plugin-and-skill-markdown, commit fcd793c.
- **Related records:** ADR_2026-10-26_biome-formats-and-lints-maintainer-markdown (superseded).
- **Superseded by:** none

### DEBT-018 — building-plugins checks a new name against this marketplace before design

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-26 |
| **Owner** | `.claude/skills/building-plugins/`, `.claude/skills/plugin-renames-and-removals/scripts/check-new-name.py` |

#### ❗ The problem

`check-new-name.py` existed only in `plugin-renames-and-removals`, and `building-plugins` had no name check before design: the scaffold refused only an exact or retired name, at step 2. Whether a "similar name" meant this marketplace only or the official marketplaces too was undecided.

#### 🔧 The closure

Nery set the scope on 2026-10-26: this marketplace. `building-plugins` gained `scripts/check-plugin-name.py`, run in step 1 before any design. It refuses a name listed in `plugins` or `renames` of `marketplace.json` or present in `plugins/`, and lists names at most 2 edits apart, with the same words in another order, or whose words contain the other's; a similar name goes on only with Nery's OK (commit c2378f9).

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | Scratch runs on 2026-10-26: `invoice-tracker` exit 0; `turn-meter` exit 1 "taken"; `typescript8-lsp-intelligence` exit 1, similar to typescript6 and typescript7 "(at most 2 edits apart)"; `lsp-python-intelligence` exit 1 "(the same words in another order)"; `hook-engineering-pro` exit 1; a `renames` key exit 1 "a retired name is never reused"; `My_Plugin`, no argument and two arguments exit 2. `ruff check` passed and basedpyright reported `0 errors, 0 warnings, 0 notes`. |
| 🚫 **Negative:** the original failure or condition is gone | `building-plugins/SKILL.md` step 1 now runs `check-plugin-name.py` before any design (4 mentions in the skill; none before c2378f9). |

#### 🔗 Follow-up

- **Residual risk:** names in other marketplaces, official ones included, are not compared, by Nery's scope.
- **Closed by:** commit c2378f9.
- **Related records:** none
- **Superseded by:** none

### DEBT-019 — The mod READMEs already state the tested Claude Code version

| Field | Value |
| --- | --- |
| **Outcome** | obsolete |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-26 |
| **Owner** | `plugins/file-tree-pane`, `plugins/mods-engineering`, `plugins/tool-ledger`, `plugins/turn-meter` (README.md) |

#### ❗ The problem

The entry said the four mod READMEs lacked the "Tested with Claude Code X.Y.Z" line that `building-mods` section 5 requires, based on `grep -ci "tested with claude code"` returning 0 in all four.

#### 🔧 The closure

Logged in error. The search matched only the literal "tested with claude code": three READMEs state the version in the Claude Code row of their Compatibility table as "Tested with vX.Y.Z.", equal to their CHANGELOG. `mods-engineering` has no `hooks/hooks.json`, so it is not a mod and the rule does not apply to it. `building-mods` section 5 now names the row and the "Tested with vX.Y.Z." wording the READMEs use.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | not applicable |
| 🚫 **Negative:** the original failure or condition is gone | 2026-10-26: `file-tree-pane` README "Tested with v2.1.310." and CHANGELOG "Validated and tested on Claude Code v2.1.310."; `tool-ledger` and `turn-meter` READMEs "Tested with v2.1.308." and CHANGELOGs "Tested with Claude Code v2.1.308"; `plugins/mods-engineering/hooks/hooks.json` does not exist. |

#### 🔗 Follow-up

- **Residual risk:** none
- **Closed by:** none
- **Related records:** ADR_2026-10-25_mod-readmes-state-the-tested-claude-code-version.
- **Superseded by:** none

### DEBT-021 — A validator fails on dead skill and path references in the project skills and CLAUDE.md

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-26 |
| **Owner** | `.claude/skills/`, `.claude/CLAUDE.md` |

#### ❗ The problem

No script checked that the skills and repository paths cited by `.claude/skills/` and `.claude/CLAUDE.md` exist. A dead pointer to the removed `scripts/release-notes.mjs` and five references to the removed `.claude/rules/workflow.md` were found by hand.

#### 🔧 The closure

Nery chose a validator over a skill script. `scripts/validators/skill-references.py` checks every backticked repository path, skill name and `<plugin>:<name>` reference in those files. Paths resolve from the repository root or from the citing skill's directory. Placeholders, example plugin names and plugin-relative paths are skipped. It runs in the validators-gate commit hook, in `npm run validate` and in the gates, and `scripts/tests/validators/test_skill_references.py` covers it. Commit c1b9759.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | 2026-10-26: `npm run validate:skill-references` prints "✔ 101 skill and path reference(s) in .claude/skills and .claude/CLAUDE.md resolve", and `run_pytest.py scripts/tests/schemas scripts/tests/validators` gives 201 passed. |
| 🚫 **Negative:** the original failure or condition is gone | 2026-10-26: in a copy under `TCF_ROOT`, a line added to `release-and-versioning/SKILL.md` that cites `scripts/release-notes.mjs`, `.claude/rules/workflow.md` and the `plugin-development` skill exits 1 and names all three, with file and line. |

#### 🔗 Follow-up

- **Residual risk:** a skill name mentioned without the word "skill" or a `Skill:` line is not checked. A new built-in skill cited by name needs an `EXTERNAL_SKILLS` entry.
- **Closed by:** c1b9759
- **Related records:** none.
- **Superseded by:** none

### DEBT-022 — Nery dropped the five handoff items that named removed skills and files

| Field | Value |
| --- | --- |
| **Outcome** | obsolete |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-26 |
| **Owner** | Session handoffs |

#### ❗ The problem

Items 10, 11, 12, 16 and 22 of the 2026-10-22 07:24 handoff named `plugin-development`, `plugin-consistency`, `github-workflow` or `.claude/WORKFLOW.md`. All of these were removed, yet the items were carried from session to session.

#### 🔧 The closure

Nery dropped all five on 2026-10-26, and none was restated:

- 12 and 22 depend on the removed `github-workflow` skill and `WORKFLOW.md`.
- 16 is covered by the Workflow section of `.claude/CLAUDE.md`, which names the skill of each stage or says none exists yet.
- 11's questions are covered elsewhere: DEBT-015 tracks the plugin-hooks-guidance contradictions, `github-operations:auto-pr-lifecycle` covers review threads and branch cleanup, and the official docs govern the description limit.
- 10 was a generic check with no condition left to track.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | not applicable |
| 🚫 **Negative:** the original failure or condition is gone | 2026-10-26: `.claude/skills/plugin-development`, `.claude/skills/plugin-consistency`, `.claude/skills/github-workflow` and `.claude/WORKFLOW.md` do not exist, and the current handoff no longer carries the items. |

#### 🔗 Follow-up

- **Residual risk:** none
- **Closed by:** none
- **Related records:** DEBT-015.
- **Superseded by:** none

### DEBT-024 — Dropped by Nery: the never-run `block-no-verify` checks are no longer tracked

| Field | Value |
| --- | --- |
| **Outcome** | obsolete |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-26 |
| **Owner** | `plugins/block-no-verify` |

#### ❗ The problem

Three checks of `block-no-verify` were never run, open since 2026-10-20: the handler's own timing under macOS `/bin/bash` 3.2, the final review over the final Bash state, and ADRs for the choice of a Bash handler over a Python port and for the jq 1.6 minimum. The order was waiting on Nery.

#### 🔧 The closure

Nery withdrew the item on 2026-10-26, stated by the user on 2026-10-26. No change was made to the plugin.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | not applicable |
| 🚫 **Negative:** the original failure or condition is gone | 2026-10-26: the item no longer waits on a decision, since Nery dropped it. The timing, the review and the ADRs themselves were not done. |

#### 🔗 Follow-up

- **Residual risk:** the handler's timing under macOS bash 3.2 stays unmeasured, the final review stays unrun, and the two design choices stay without an ADR.
- **Closed by:** Nery's decision on 2026-10-26.
- **Related records:** none.
- **Superseded by:** none

### DEBT-029 — Dropped by Nery: the `claude-review` failures on PRs #20, #28 and #29 are no longer investigated

| Field | Value |
| --- | --- |
| **Outcome** | obsolete |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-26 |
| **Owner** | `.github/workflows/claude-code-review.yml` |

#### ❗ The problem

`claude-review` failed on PR #20 (run 39138684403, job 117708394324) and on Copilot's merge commits of PRs #28 (job 118802109187) and #29, and the logs were never read (open since 2026-10-18). The cause was unknown.

#### 🔧 The closure

Nery withdrew the item on 2026-10-26, stated by the user on 2026-10-26. The logs were not read and the workflow was not changed.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | not applicable |
| 🚫 **Negative:** the original failure or condition is gone | 2026-10-26: the item no longer waits on an investigation, since Nery dropped it. `gh run view 39138684403` still reports `failure`; the cause stays unknown. |

#### 🔗 Follow-up

- **Residual risk:** if the cause still exists, a later pull request can go without the automated review. DEBT-027 still tracks the denied tool calls of the same workflow on PR #42.
- **Closed by:** Nery's decision on 2026-10-26.
- **Related records:** DEBT-027.
- **Superseded by:** none

### DEBT-033 — `.editorconfig` is the only source of indentation and line endings for Biome

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-26 |
| **Logged on** | 2026-10-26 |
| **Owner** | `biome.json` |

#### ❗ The problem

`formatter.indentStyle`, `indentWidth`, `lineEnding` and `markdown.formatter.indentStyle` in `biome.json` repeated `.editorconfig`, which Biome reads with `formatter.useEditorconfig: true`. Settings in `biome.json` take precedence, so the two sources could drift.

#### 🔧 The closure

The four keys were removed from `biome.json`; `lineWidth` and `useEditorconfig` stay, since `.editorconfig` has no line width Biome reads. Biome 2.6.3 reads `indent_style`, `indent_size`, `end_of_line` and `insert_final_newline` from the root `.editorconfig` ([configuration reference](https://biomejs.dev/reference/configuration/#formatteruseeditorconfig), `biome ci --help`).

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | 2026-10-26, Biome 2.6.3: `npx biome ci .` checked 163 files, no fixes applied, 4 infos, the same result as before the change. |
| 🚫 **Negative:** the original failure or condition is gone | 2026-10-26: `biome.json` no longer names `indentStyle`, `indentWidth` or `lineEnding`. In a scratch copy without the keys, changing `.editorconfig` alone made `biome ci .` fail: `indent_size = 4` gave 151 errors, `indent_style = tab` 139, `end_of_line = crlf` 163, and a `[*.md]` section with `indent_size = 4` 2. |

#### 🔗 Follow-up

- **Residual risk:** none
- **Closed by:** the commit that removes the keys from `biome.json`.
- **Related records:** none.
- **Superseded by:** none

### DEBT-034 — Biome checks every tsconfig file, with an `expand: "auto"` override

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-27 |
| **Logged on** | 2026-10-26 |
| **Owner** | `biome.json` |

#### ❗ The problem

`biome.json` force-ignored `**/tsconfig.json` and `**/tsconfig.base.json` since commit `b3ada31`, with no recorded reason, so a malformed tsconfig passed Biome. Including them under the JSON-wide `expand: "always"` would have reformatted the four mods' tsconfig files, which needs plugin pull requests.

#### 🔧 The closure

Both `!!` patterns were removed. An override sets `json.formatter.expand: "auto"` for `**/tsconfig.json` and `**/tsconfig.*.json`, and `scripts/tsconfig.json` was formatted once, because its `include` line passed 100 columns. No plugin file changed. Nery chose this option on 2026-10-27: ADR_2026-10-27_biome-checks-every-tsconfig-with-auto-expand.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | 2026-10-27, Biome 2.6.3: `biome ci .` checked 170 files, no fixes, 4 infos. `npm run lint:js` passed `biome-maintainer` and `biome-plugins`. `tsc -p scripts/tsconfig.json --noEmit` and `tsc -p scripts/tsconfig.plugins.json --noEmit` exited 0. |
| 🚫 **Negative:** the original failure or condition is gone | 2026-10-27: `biome.json` has no `tsconfig` exclusion. `biome ci . --verbose` lists all seven tracked tsconfig files among the files processed, against none of the six excluded ones before. |

#### 🔗 Follow-up

- **Residual risk:** none
- **Closed by:** ADR_2026-10-27_biome-checks-every-tsconfig-with-auto-expand and the commit that applies it.
- **Related records:** ADR_2026-10-27_biome-checks-every-tsconfig-with-auto-expand.
- **Superseded by:** none

### DEBT-032 — Biome's `useLiteralKeys` is off, so tsc's `noPropertyAccessFromIndexSignature` alone decides index-signature keys

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-10-27 |
| **Logged on** | 2026-10-26 |
| **Owner** | `biome.jsonc`, `tsconfig.base.json` |

#### ❗ The problem

`biome ci` reported 4 `complexity/useLiteralKeys` infos in `scripts/tests/gates.test.mjs` for `process.env['GIT_INDEX_FILE']`, the bracket form that `tsconfig.base.json`'s `noPropertyAccessFromIndexSignature` requires. Following Biome would have broken tsc, and raising the rule to `"error"` with the other info-level rules would have made the gates contradict the type-check.

#### 🔧 The closure

`biome.jsonc` sets `complexity.useLiteralKeys` to `"off"`, with the reason beside it, in the same commit that raises the other 23 info-level rules of the preset to `"error"`. tsc keeps `noPropertyAccessFromIndexSignature`, the stricter of the two. Nery chose this on 2026-10-27: ADR_2026-10-27_tsc-decides-index-signature-keys-not-biome.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | 2026-10-27, Biome 2.6.3: `npm run typecheck:ts` and `npm run lint:js` passed. `biome rage --linter` lists 250 enabled rules, 251 before, the difference being `useLiteralKeys`. |
| 🚫 **Negative:** the original failure or condition is gone | 2026-10-27: `biome ci . --error-on-warnings` checked 171 files and found no diagnostic, against the 4 `useLiteralKeys` infos before. |

#### 🔗 Follow-up

- **Residual risk:** none
- **Closed by:** ADR_2026-10-27_tsc-decides-index-signature-keys-not-biome and the commit that applies it.
- **Related records:** ADR_2026-10-27_tsc-decides-index-signature-keys-not-biome.
- **Superseded by:** none

### DEBT-014 — `release.yml` published release notes built by `release-notes.py` for two new tags

| Field | Value |
| --- | --- |
| **Outcome** | obsolete |
| **Closed on** | 2026-10-27 |
| **Logged on** | 2026-10-26 |
| **Owner** | `.github/workflows/release.yml`, `.claude/skills/release-and-versioning/scripts/release-notes.py` |

#### ❗ The problem

`release.yml` had run `release-notes.py <plugin> --tag` on the runner's python3, but never the notes path (`release-notes.py <plugin> > notes.md`), because no plugin had an untagged version. The first release of a new version could have published without notes, or failed.

#### 🔧 The closure

Release run 40490117853 (2026-10-27), triggered by the merge of [PR #53](https://github.com/nerymurillohnd/the-claude-factory/pull/53), ran the notes path for two new tags and published both releases with notes built by `release-notes.py`. The release was not aimed at this item; it exercised the path the item waited for.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | not applicable |
| 🚫 **Negative:** the original failure or condition is gone | The run's log shows `release-notes.py "${target}" > notes.md` and `gh release create "${tag}" ... --notes-file notes.md`, and lists `Released python-lsp-intelligence--v0.3.0` and `Released skill-diagnostics--v0.2.0`. `diff` of each published release body against the local `release-notes.py <plugin>` output differs only by one trailing blank line. |

#### 🔗 Follow-up

- **Residual risk:** none
- **Closed by:** [PR #53](https://github.com/nerymurillohnd/the-claude-factory/pull/53), release run 40490117853.
- **Related records:** ADR_2026-10-25_release-workflow-runs-the-release-skill-script.
- **Superseded by:** none

### DEBT-026 — `.claude/rules/readme-md.md` loads when a README is read

| Field | Value |
| --- | --- |
| **Outcome** | obsolete |
| **Closed on** | 2026-10-27 |
| **Logged on** | 2026-10-26 |
| **Owner** | `.claude/rules/readme-md.md` |

#### ❗ The problem

The Confirmation of ADR_2026-10-25_every-readme-has-a-path-scoped-rule marked as pending whether the path-scoped rule loads when a README is read. No fresh-session check had run, so README rules could be silently absent when a README was edited.

#### 🔧 The closure

A session that was not aimed at this item showed the load. In session `f5bdd77c-541a-4187-8bf3-85461bccdf16`, on 2026-10-27 with Claude Code 2.1.311, the rule loaded on the read of a plugin README. The ADR's Confirmation now records it.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | not applicable |
| 🚫 **Negative:** the original failure or condition is gone | Session transcript, line 319: `{"ts":"2026-10-27T16:09:36.811Z","ver":"2.1.311","type":"nested_memory","path":".../.claude/rules/readme-md.md"}`. It directly follows the `Read` of `plugins/tailwind-development/README.md` at 16:09:36.704Z. A later `Edit` of that README also returned the rule's contents. |

#### 🔗 Follow-up

- **Residual risk:** none
- **Closed by:** none
- **Related records:** ADR_2026-10-25_every-readme-has-a-path-scoped-rule.
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
