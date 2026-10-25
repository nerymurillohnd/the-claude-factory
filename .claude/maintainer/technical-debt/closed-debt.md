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
