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
| 2026-11-13 | DEBT-002 | resolved | The cloud setup script pins every tool it installs | none |
| 2026-11-13 | DEBT-004 | resolved | Changelog versions link to their release pages in the files, the procedure and the script | none |
| 2026-11-19 | DEBT-007 | resolved | The fourteen plugin subagents follow the house agent format | none |
| 2026-11-19 | DEBT-003 | resolved | The five mods pass strict, portable and hooks-catch validation, and the checks gate every merge | none |
| 2026-11-21 | DEBT-013 | resolved | cc-github-actions reaches a failed step's goal by any method within the session's permissions | none |

## 🏁 Closed items

### DEBT-002 — The cloud setup script pins every tool it installs

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-11-13 |
| **Logged on** | 2026-11-13 |
| **Owner** | unassigned |

#### ❗ The problem

The `the-claude-factory` environment's setup script installed `typescript-language-server`, `bash-language-server` and `svelte-language-server` at `@latest`, ShellCheck and shfmt from webi with no version, and actionlint at `@latest`, so two snapshots built on different days could hold different tool versions and give different lint results on the same commit.

#### 🔧 The closure

The owner chose exact pins on 2026-11-13. The setup script, replaced through the environment tools the same day, installs `typescript-language-server@6.1.0`, `bash-language-server@5.8.1`, `svelte-language-server@0.18.6`, `shellcheck@v0.11.0` and `shfmt@v3.14.1` through webi, and `actionlint@v1.7.12` through `go install`.

The image ships its own ShellCheck 0.11.0 in `/nix/var/nix/profiles/default/bin`, which comes first on the session's `PATH`, so a webi pin alone did not decide which ShellCheck runs: a request for webi's 0.10.0 switched the webi link and left `shellcheck --version` at 0.11.0. The script therefore appends one marked line to `~/.bashrc` that puts `~/.local/bin` first, matching the owner's machine, and logs `shellcheck on PATH is not 0.11.0` when the version on `PATH` differs.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | Running the script from the checkout's parent, without its `~/.bashrc` step, exited 0 in 15 seconds; `npm ls -g` listed `bash-language-server@5.8.1`, `svelte-language-server@0.18.6` and `typescript-language-server@6.1.0`; the summary showed shfmt v3.14.1 and actionlint v1.7.12; webi's ShellCheck link pointed to `shellcheck-v0.11.0`. The `~/.bashrc` step, run twice in a temporary `HOME`, wrote one line and moved `~/.local/bin` ahead of a leading `/nix/x`. ShellCheck reported nothing on the script. |
| 🚫 **Negative:** the original failure or condition is gone | The script sent to the environment contains no `@latest` (count 0) and no unversioned webi URL. |

#### 🔗 Follow-up

- **Residual risk:** the `~/.bashrc` step was not run against this session's own `~/.bashrc` (a write there was blocked by the permission classifier), so its effect on `PATH` is confirmed only at the first fresh session; the setup script's ShellCheck warning shows it if it fails. Version bumps for these tools are manual, since Dependabot does not read the setup script.
- **Closed by:** the setup script replacement of 2026-11-13.
- **Related records:** none.
- **Superseded by:** none

### DEBT-004 — Changelog versions link to their release pages in the files, the procedure and the script

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-11-13 |
| **Logged on** | 2026-11-13 |
| **Owner** | unassigned |

#### ❗ The problem

Step 5 of `.claude/skills/docs-maintenance/references/documents/changelog.md` and `npm run release:changelog` linked a new version as a compare with the previous tag. The 22 plugin CHANGELOGs link every version to `releases/tag/<plugin>--v<version>`. The next release would have mixed the two formats in one file.

#### 🔧 The closure

The owner kept the release-page format on 2026-11-13. Commit d3aef8e changed four places to link the new version to `{repositoryUrl}/releases/tag/<plugin>--v<version>`:
- the procedure's step 5
- `plugin-releases` step 4
- `scripts/release/release_tools/changelog.py`
- its test

`[Unreleased]` still compares from the newest tag.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | `npm run test:scripts`: 236 tests, OK, including `test_links_later_release`, which expects `[0.2.0]: …/releases/tag/demo--v0.2.0`. A trial on a throwaway copy of `block-no-verify` bumped to 0.1.6 wrote `[0.1.6]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/block-no-verify--v0.1.6`. |
| 🚫 **Negative:** the original failure or condition is gone | The same test failed before the fix (`FAIL: test_links_later_release`), when the script still wrote `compare/demo--v0.1.0...demo--v0.2.0`. `changelog.md` no longer says "each version compares its tag with the previous one". |

#### 🔗 Follow-up

- **Residual risk:** none.
- **Closed by:** commit d3aef8e.
- **Related records:** none.
- **Superseded by:** none

### DEBT-007 — The fourteen plugin subagents follow the house agent format

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-11-19 |
| **Logged on** | 2026-11-18 |
| **Owner** | unassigned |

#### ❗ The problem

Fourteen plugin subagents used Markdown headings instead of the house agent format of `.claude/rules/code-quality/agent-and-command-style.md`: `hook-engineering/agents/hook-engineer.md`, `instruction-engineering/agents/reviewer.md`, the six `skill-diagnostics/agents/*.md`, the two `svelte-development/agents/*.md` and the four `tailwind-development/agents/*.md`. A new agent modeled on one of them repeated the headings.

#### 🔧 The closure

On 2026-11-19 the owner asked for all fourteen in one branch instead of a pull request per plugin. Each agent now opens with its role paragraph, `Your expertise:` and `GOAL:`, marks every later section with an uppercase label instead of a heading, and drops bold outside code fences; fenced blocks, such as report templates, are byte-identical. Each `GOAL:` sums up the agent's existing rules, and a `/code-review` pass made three of them conditional where the rules are (the migrator's approval, the Svelte editor's unchecked exits, the verifier's fourth ruling). The five plugins took patch bumps: hook-engineering 0.3.2, instruction-engineering 0.2.2, skill-diagnostics 0.4.3, svelte-development 0.1.4 and tailwind-development 0.3.5.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | `claude plugin validate --strict` passed for each of the five plugins and the marketplace; `plugin details` listed every agent (1, 1, 6, 2 and 4); `npm run check:consistency -- --offline` exited 0; `npm run test:plugins` ran 58 tests, OK; `check:install --from local` installed each new version. A line-by-line comparison against a frozen baseline found every original body line in the new file, except the intended rewordings (bold removed, the hook-engineer field list moved into `Your expertise:` bullets, section references renamed), each confirmed word by word. |
| 🚫 **Negative:** the original failure or condition is gone | The same count the entry used, `#` lines outside code fences in each `plugins/*/agents/*.md` body, finds 0 files (was 14). |

#### 🔗 Follow-up

- **Residual risk:** `instruction-engineering/agents/reviewer.md` still fails FM-02 (a colon in `description`), which DEBT-005 holds; the frontmatter was not touched.
- **Closed by:** [#114](https://github.com/nerymurillohnd/the-claude-factory/pull/114).
- **Related records:** DEBT-005.
- **Superseded by:** none

### DEBT-003 — The five mods pass strict, portable and hooks-catch validation, and the checks gate every merge

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-11-19 |
| **Logged on** | 2026-11-13 |
| **Owner** | unassigned |

#### ❗ The problem

`npm run validate:portable` and `npm run validate:hooks-catch` could not join `npm run validate`, because five mods failed them: `file-tree-pane` and `project-maintainer` with TS5097 (`.ts` import specifiers), `model-trace` with TS2769 (`mode` on `WebSearch`), `tool-ledger` and `turn-meter` with TS2741 (`isCollapsed` missing), plus four gating hooks without `.catch` in `project-maintainer` and `turn-meter`. Plain `claude plugin validate --strict` failed on the same five, so `scripts/validators/pr-checks.sh` skipped them through `DEBT_003_PLUGINS` and Validate's non-blocking `Debt` job held their strict checks.

#### 🔧 The closure

On 2026-11-19 the owner scheduled the fixes. `file-tree-pane` and `project-maintainer` import their own files as `./file.js`, the form the mods docs show; `project-maintainer` and `turn-meter` answer for every gating hook with a `.catch`; the `tool-ledger`, `turn-meter` and `model-trace` tests build their fixtures to the current mod API (`isCollapsed`, a complete `AgentInfo`, and a `webSearch()` helper that type-checks whether or not the session's `WebSearch` schema has `mode`). `file-tree-pane` 0.1.7, `project-maintainer` 0.2.7 and `turn-meter` 0.1.7 took patch bumps; the `model-trace` and `tool-ledger` changes are test-only and took none, per `plugin-releases`. Then `pr-checks.sh` dropped `DEBT_003_PLUGINS` and its `debt-validate` step, its `validate` step runs `validate:portable` and `validate:hooks-catch`, `check:install` runs strict on every changed plugin, `npm run validate` chains both checks, and the `Debt` job lost its three DEBT-003 steps.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | With Claude Code 2.1.328 and with 2.1.325 (CI's `CLAUDE_CODE_VERSION`): `claude plugin validate --strict` printed `√ Validation passed` for each of the five; `npm run validate:hooks-catch` and `npm run validate:portable` exited 0; `claude plugin test` passed 62, 18, 56, 14 and 12 tests. `bash scripts/validators/pr-checks.sh validate` exited 0 with 50 `Validation passed` lines. `npm run check:install -- --from local` reported `file-tree-pane 0.1.7 ok`, `project-maintainer 0.2.7 ok` and `turn-meter 0.1.7 ok`. `actionlint` and `zizmor --offline .` reported nothing on `validate.yml`. |
| 🚫 **Negative:** the original failure or condition is gone | The commands that failed in the pending entry no longer fail: `--strict` on the five reports no TS5097, TS2769, TS2741 or TS2740, and `validate:hooks-catch` lists no hook; `grep DEBT_003 scripts/validators/pr-checks.sh` and `grep DEBT-003 .github/workflows/validate.yml` find nothing. |

#### 🔗 Follow-up

- **Residual risk:** no test makes the new `.catch` handlers of `turn-meter` run, so those paths have only been type-checked. The mods' tests are still not type-checked in the Git pre-commit gate, and the `typescript6-lsp-intelligence` post-edit hook checks a mod file against the root `tsconfig.json`, which reports errors the mod's own config does not.
- **Closed by:** commits 86c5b19, cbb8c19, a35d506, f670e39, c9e56db and 7baba17 on branch `claude/tech-debt-parallel-9lsn8d`.
- **Related records:** DEBT-006.
- **Superseded by:** none

### DEBT-013 — cc-github-actions reaches a failed step's goal by any method within the session's permissions

| Field | Value |
| --- | --- |
| **Outcome** | resolved |
| **Closed on** | 2026-11-21 |
| **Logged on** | 2026-11-21 |
| **Owner** | github-operations |

#### ❗ The problem

`cc-github-actions`' `SKILL.md` Rules limited every command to `git`, `gh`, the GitHub MCP tools, installed scanners and a few POSIX utilities, and ended "Never install any program, and never run any other". When the named tool failed, Claude could not reach the step's goal by another method it knew, such as `curl` to a raw file when `gh api` was refused, so the goal was recorded as not verified.

#### 🔧 The closure

On 2026-11-21 the owner asked for the change in the current 0.10.0 branch instead of a follow-up. The allowlist rule was removed. A rule now has Claude use first the tool a step names and, when it fails or is missing, keep the step's goal first, reach it with any method it knows and can access within its permissions, ask the user for anything outside them (installing a program included), and report what failed and which route worked. `references/detection-layers.md` and `references/version-drift.md` install a missing scanner or the `gh actions-lock` extension only after the user approves, and the plugin README and the 0.10.0 notes say the same.

#### 🧪 Verification

| Check | Evidence |
| --- | --- |
| ✅ **Positive:** the closure holds | `grep -n 'any method you know' plugins/github-operations/skills/cc-github-actions/SKILL.md` prints line 61; `claude plugin validate --strict plugins/github-operations` prints "Validation passed". |
| 🚫 **Negative:** the original failure or condition is gone | `grep -rn 'never run any other' plugins/github-operations/skills/cc-github-actions plugins/github-operations/README.md` prints nothing (exit 1). |

#### 🔗 Follow-up

- **Residual risk:** none.
- **Closed by:** commit e4611c6 on branch `ccr-2448a691-7xbgcg`.
- **Related records:** none.
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
