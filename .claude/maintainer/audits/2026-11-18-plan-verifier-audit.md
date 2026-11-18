# Audit: `work-lifecycle:plan-verifier` compared with `work-lifecycle:migration-verifier`

- **Date:** 2026-11-18
- **Scope:** `plugins/work-lifecycle/agents/plan-verifier.md`, how `planning-before-execution/SKILL.md` launches it (phase 6, "Stops and the end" step 2), and its state file contract (`scripts/validate-state.py`). Compared with `plugins/work-lifecycle/agents/migration-verifier.md` and the per-task verifier this session ran for the `authoring-skills` reference restructure (plan `.claude/maintainer/plans/2026-11-18-authoring-skills-reference-restructure.md`).
- **Method:** Claude read both agents and the planning skill in full and checked each claim below against those files. No subagent wrote this report.
- **Status:** open. Recommendations await the owner's decision; nothing in `plan-verifier` or `planning-before-execution` was changed.

## Contents

- 1. What each verifier is
- 2. Where plan-verifier is stronger
- 3. Gaps and defects in plan-verifier
- 4. Recommendations, prioritized
- 5. Applied to migration-verifier from this comparison
- Unverified

## 1. What each verifier is

| Aspect | `plan-verifier` | `migration-verifier` (and this session's run) |
| :-- | :-- | :-- |
| Scope | Any plan run through `planning-before-execution` | Content-preserving documentation restructures only |
| When it runs | High-stakes plans only: once before handoff (plan mode), once after the last task (work mode) | Every restructure: READY at launch, after every task's commit, final full pass |
| Lifetime | Two fresh launches, no memory between them | One background agent resumed with `SendMessage` after each task |
| Reference point | The requirements and the plan; in work mode the state file and `git status`, `git diff --stat` | A frozen baseline copy, a ledger of every line, a block table, a commit per task |
| Deterministic checks | Re-runs the tasks' own checks | A purpose-built script (`restructure.py`) plus re-reading |
| Brief | Plan path, requirements written by the coordinator, research resources | Paths only, explicitly without the coordinator's justifications |
| Tool limits | `disallowedTools: Edit, Write`; "change nothing" by instruction | Same |
| Report | Findings with severity, Confirmed, Unverified | Per-task PASS or FLAGS with file, line and baseline text, script output, Checked by reading, Unverified |

## 2. Where plan-verifier is stronger

Keep these in any redesign:

- **Adversarial stance:** "try to prove the plan or the work wrong", and "try to refute each claim first".
- **Severity rating** (blocking, should fix, minor) tied to what the caller must resolve.
- **Unverified section** and "accept no claim you could not test". `migration-verifier` lacked it; added (section 5).
- **Research resources:** checks facts through docs servers and skills, with the WebFetch gotcha.
- **Test-quality checks** on test-first work: named break, hand-written expected values, no assertion on a mock, red run failed rather than errored.
- **Secrets rule** for `.env` and configuration files. `migration-verifier` lacked it; added.

## 3. Gaps and defects in plan-verifier

Each is checked against the file named.

1. **Defect: the "outside the file map" check sees nothing once work is committed.** Work mode step 5 checks "nothing outside the file map changed (`git status`, `git diff --stat`)" (`plan-verifier.md`). Neither command names a base: after the tasks are committed, both report a clean tree, and the check passes whatever changed. Neither the planning skill nor `validate-state.py` records a starting commit (no `commit`, `baseline` or `HEAD` anywhere in the skill, its references or the validator).
2. **Gap: verification only at the end.** In work mode the verifier runs once, after the last task. A defect introduced in task 2 of 10 is found after tasks 3–10 built on it. This session's run caught two lost rules and a stale pointer in the task that introduced them, when each fix was one line.
3. **Gap: no baseline of the project's checks.** The skill records evidence per task, but nothing records the lint, type and test output before task 1, so the verifier cannot tell a regression from a failure that was already there (the testing skill does this for code; plans that are not test-first don't).
4. **Risk: the brief is written by the coordinator.** In plan mode the brief carries "the requirements written out: the user's goal, their answers to your questions and their constraints" (`SKILL.md` phase 6). A gotcha warns against the framing, but the requirements themselves come through the party under review. This session showed the same risk: a verifier briefed with my allowed changes would have agreed with them.
5. **Gap: no check of pointers and mentions.** Neither mode asks the verifier to check that every file, section or step the changed files name still holds what they say. Line and test checks miss this class; it was the defect a fresh reader found in this session.
6. **Gap: no fresh-reader pass for content work.** The skill covers "multi-step operations or content work", but the verifier checks evidence and criteria, not whether the delivered text reads correctly to someone who never saw the old version.
7. **Gap: "high-stakes only" leaves medium plans unverified in work mode.** A plan that is not high-stakes gets the plan gate, which "only checks that evidence is recorded" (README Limitations), and no independent check at all.
8. **Weakness: deviations are not recorded.** When a task departs from the plan (an approved change mid-execution), the state file has no field for it, so the verifier can't tell an approved deviation from drift.

## 4. Recommendations, prioritized

| # | Recommendation | Fixes | Cost |
| :-- | :-- | :-- | :-- |
| R1 | Record `base_commit` in the state file when status becomes `executing` (validator: required when `executing` and the project is a git repository), and change work mode step 5 to `git diff --stat <base_commit>` plus `git status --short` | Defect 1 | Small: validator field, one skill step, one agent step, tests |
| R2 | Add an optional per-task mode: for high-stakes plans, launch `plan-verifier` in the background before task 1 with a name, and resume it with `SendMessage` after each task's check ("Verify task N at commit [sha]"); keep the final work-mode pass | Gap 2 | Medium: skill section, agent workflow branch; background agents keep a limited toolset, so confirm Bash is kept |
| R3 | Record the project's own checks before task 1 as `baseline` in the state file, and have work mode compare against it | Gap 3 | Small |
| R4 | Brief with paths and the user's own words only: quote the user's answers verbatim, never paraphrase, and send no justifications for choices | Risk 4 | Small: wording in phase 6 |
| R5 | Add a pointers check to work mode: every file, section or step the changed files name holds what it says | Gap 5 | Small |
| R6 | For content work, add an optional fresh-reader pass: copy the delivered documents outside the repository and have an Explore subagent read them in order | Gap 6 | Small |
| R7 | Add a `deviations` list to the state file (task, change, user approval) and have the verifier judge drift against it | Weakness 8 | Small |
| R8 | Offer the work-mode pass, at lower cost, for medium plans (the user chooses) | Gap 7 | Small; owner decision on cost |
| R9 | For a documentation restructure, have `planning-before-execution` hand off to `work-lifecycle:restructuring-documents` instead of planning it itself | Overlap | Small: one line in the planning skill's routing |

R1 is a correctness defect and should go first. R2, R4 and R5 carry the lessons of this session into every plan. Each change to `plan-verifier` or the planning skill is a skill or agent edit under `skills-engineering:authoring-skills`, a `minor` change for `plugin-releases`, and needs `validate-state.py` tests for R1, R3 and R7.

## 5. Applied to migration-verifier from this comparison

- Added the Unverified section to its REPORT, the "accept no claim you could not check" rule, and two checklist items.
- Added the secrets rule for `.env` and configuration files.

## Unverified

- Whether a background subagent resumed with `SendMessage` keeps Bash in every surface where `planning-before-execution` runs: this session's background verifier did, but the documented set of tools for background subagents was not re-read for this report. It affects R2.
- No eval measures how often either verifier misses a defect; the comparison rests on this session's single run.
