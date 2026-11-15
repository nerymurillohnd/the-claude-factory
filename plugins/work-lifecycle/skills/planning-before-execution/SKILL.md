---
name: planning-before-execution
description: Plans multi-step work before anything changes. Researches current official sources and the code, then writes a self-contained, verifiable plan with a file map, tasks, checks and acceptance criteria, and sets how completion is proven. Use whenever a task spans several steps or files, changes architecture, migrates or upgrades something, touches data or deployments, or is costly to redo, and whenever the user asks to plan, scope, break down or design an approach, even if they never say plan. Also use for multi-step operations or content work that Claude will carry out. Not for one-line edits, questions, explanations, writing a plan document as the deliverable itself (such as a business plan), or work that already has an approved plan.
hooks:
  Stop:
    - hooks:
        - type: command
          command: python3
          args:
            - ${CLAUDE_PLUGIN_ROOT}/hooks/plan-gate.py
          timeout: 30
---

# Planning before execution

Turn a goal into an approved plan that an implementer who has seen neither the code nor this conversation can carry out and prove done. Nothing changes until the user approves the plan.

## Gotchas

1. Plan mode can be weaker than it looks: in interactive terminal sessions where bypass permissions is available, it doesn't block edits. Treat read-only as your own rule in every session, not only as the system's.
2. Planning is not strictly read-only: where auto mode is available, a classifier approves exploration commands without asking. Run only commands that change nothing.
3. Subagents inherit plan mode, whatever their own settings say. A probe that needs to write can't run during planning, even in a worktree: make it Task 0, run after approval.
4. `EnterPlanMode` is not always there: subagents don't have it, `denyInsteadOfPrompting` removes it, and chat has no plan mode. Check before calling it, and say when the guardrail is off.
5. Never choose where the plan is saved. In plan mode Claude Code stores it in its own plan file and tells you the path; elsewhere the plan goes in the reply.
6. `/goal` has limits: the condition holds at most 4,000 characters, so it references the plan by path; its evaluator reads only the conversation, runs no commands and reads no files, so "Done when" names evidence you print. Only the user can type it, one goal per session, and it's unavailable in chat and when hooks are disabled.
7. The first option of the plan approval menu starts auto mode. Recommend manual approval unless `permissions.ask` rules cover the reserved actions.
8. The task tools may be missing; they are off by default on newer models. Track progress in the progress checklist and the state file, never only in task tools.
9. A subagent's report is a set of claims until you check them. Re-verify every claim the plan depends on before writing it as a fact.
10. The examples show judgment, not a template. Copy their reasoning, never their languages, names or numbers.
11. Auto mode nudges you to keep going without asking. The phase 1 questions are required whenever scope, assumptions or a reserved action is unclear, in every permission mode.
12. Invoking this skill registers the plan gate, a Stop hook, for the rest of the session. It reads only the state file, so keep that file's status accurate and record each task's evidence right after its check passes.
13. A skill that declares hooks needs `Skill(work-lifecycle:planning-before-execution)` in `permissions.allow` to run in `claude -p`, scheduled tasks or `/loop`; without it the invocation is refused (observed in Claude Code, not in the docs page).

## Where you are running

Decide this before research, and write the result on the plan's Guardrail line.

- Already in plan mode: proceed; the plan lands in Claude Code's plan file.
- Claude Code, not in plan mode, `EnterPlanMode` available: call it before research.
- No plan mode (chat, a subagent, `EnterPlanMode` missing): work read-only by instruction and say at the top of the plan that the guardrail is off.
- Unattended run (scheduled task, `claude -p`, no user to answer): skip `EnterPlanMode`, deliver the plan, and execute nothing that needs authorization.
- In chat there are no agents, hooks or state file: do the research and the review inline, say so, and skip the state file and `/goal`.

## Workflow

Copy this checklist into your working notes and tick each item only when it is done:

```text
Planning progress:
- [ ] 1. Understand: goal restated, assumptions listed, questions asked or none needed
- [ ] 2. Research: sources and versions checked, code read, subagent claims re-verified
- [ ] 3. De-risk: read-only probes run; write probes moved to Task 0
- [ ] 4. Plan written from the template
- [ ] 5. Self-review passed with no findings
- [ ] 6. Independent review done, or not needed (state why)
- [ ] 7. Handoff: approval requested, completion mechanism named
```

### 1. Understand

1. Restate the goal in your own words and list your assumptions.
2. Ask 1 to 3 questions, each with your recommended option and why, whenever scope, an assumption or a reserved action (push, deploy, publishing, messages to third parties, spending) is unclear. Wait for the answers.
3. Skip the questions only when the request leaves nothing open, and say so.

### 2. Research

1. Read the current official sources for every library, tool or service the plan touches, and check the installed versions and their release notes. Current sources outrank memory.
2. Read the code the change touches: its callers, its tests, its configuration.
3. When the scope goes beyond a few files, delegate exploration to the `planning-researcher` agent, one brief per question. The brief says what to find, the scope, and what the answer decides; the agent already knows its report contract.
4. Treat a claim without evidence as unverified. Re-check yourself every claim the plan depends on before writing it under Verified facts.

### 3. De-risk

1. Find the assumptions that would sink the plan if wrong, and test each one now with a read-only probe: an existing test, a type check, a `--dry-run`, a query.
2. A probe that needs to write becomes Task 0 of the plan, run after approval by a subagent with `isolation: worktree`, with a go or no-go gate before the other tasks.
3. Skip this phase for a plan with no risky assumption, and say so in the checklist.

### 4. Write the plan

1. Start from `assets/plan-template.md`: a sensible default to adapt, not a form. Keep the minimum sections and expand as the plan's type and risk require.
2. Read `references/plan-structure.md` before writing: it holds the explicitness rules, the expansion rules and why each section exists.
3. Open the one example that matches the plan before writing it:
   - `references/examples/basic.md`: a change to a few files, two or three tasks.
   - `references/examples/intermediate.md`: a feature with interfaces between tasks and a Task 0 spike.
   - `references/examples/complex.md`: a phased migration with rollback, authorization checkpoints and subagent execution.
   - `references/examples/non-code.md`: operations or content work, with acceptance checks instead of tests.
4. For each code task, mark whether it is test-first. A test-first task names its test, the assertion and the failure message expected before the code exists, and is carried out with the `work-lifecycle:testing-before-implementation` skill.

### 5. Self-review

Run this loop before any handoff, every time:

1. Coverage: every requirement maps to a task.
2. Steps: each allows one reasonable action; no line that decides nothing ("TBD", "handle edge cases"), no code body the signature and tests already determine.
3. Consistency: names, types and signatures match across tasks.
4. Risks: each failure mode has its check in the task that owns it.
5. Proportion: the plan is not several times longer than the requirements.
6. Fix every issue found, then run the whole loop again. Hand off only after a pass that finds nothing.

### 6. Independent review

For high-stakes plans only (production, data, deployments, security, or anything costly to redo), give the plan and the requirements to the `plan-verifier` agent in plan mode, and resolve each finding before handoff. For other plans, write why the review was not needed.

### 7. Handoff

1. In plan mode, request approval through the native menu (`ExitPlanMode`). Recommend manual approval, or auto mode only when `permissions.ask` rules cover the reserved actions. Outside plan mode, ask for approval in the reply and wait.
2. Name how completion is proven:
   - In Claude Code, always the plan gate, through the state file described under Execution.
   - Also `/goal`, for a plan with more than one task and one measurable end state. Read `references/goal-handoff.md` and give the ready-to-paste condition with its length in characters.
   - In chat, the final report with each task's evidence.
3. When hooks are disabled, say that the gate won't run and that completion rests on the final report.

## Execution

These rules apply once the user approves the plan, in this session.

### Start: the state file

1. Create the folder `${CLAUDE_PROJECT_DIR}/.work-lifecycle/` if it is missing, with a `.gitignore` file there that holds the single line `*`, so nothing in it reaches the repository.
2. Copy `assets/plan-state.json` to `${CLAUDE_PROJECT_DIR}/.work-lifecycle/${CLAUDE_SESSION_ID}.json`. Use exactly its structure, because the gate parses it:
   - `plan`: the plan file's path, or `reply`.
   - `status`: `executing`.
   - one task per plan task, in plan order, with its `check`; `test_first` true for test-first tasks; `evidence`, `red` and `green` null.
3. Validate it with this skill's script, fix what the output names, and repeat until it reports the file valid:

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/validate-state.py" "${CLAUDE_PROJECT_DIR}/.work-lifecycle/${CLAUDE_SESSION_ID}.json"
   ```

   The gate itself is a hook script that Claude Code runs on its own; never run it.

4. Start the first task only after validation passes.

### Each task

1. Run the task's steps, then its check.
2. If the check fails, read the output, fix the cause and run the check again.
3. When it passes, record `evidence` as an object with `command` (the exact command) and `output` (its real output, trimmed to the lines that prove the result), then validate the file again. A test-first task also records `red` and `green` the same way, from the testing skill's cycle.
4. Never start the next task before the current one has its evidence.

### Reserved actions and the end

1. Before any reserved action, set `status` to `awaiting-authorization`, ask the user, and set it back to `executing` once they answer.
2. When every task has its evidence, set `status` to `done` and deliver the final report: each task with its check command and the result line of its real output, then what remains open.
3. If the user stops the plan, set `status` to `done` and report which tasks have no evidence.

### Delegation

1. Default to the main session.
2. Use one subagent per task when there are many independent tasks, the context would grow large, or a mistake is costly enough to justify a review per task. Run parallel subagents with `isolation: worktree`.
3. Tell each delegated code task to use the `work-lifecycle:testing-before-implementation` skill, and require back the commands and raw output of its checks.
4. Have `plan-verifier` check the work against the plan after the last task of a high-stakes plan.
