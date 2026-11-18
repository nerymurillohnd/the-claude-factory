---
name: planning-before-execution
description: Plans multi-step work before anything changes. Researches current official sources and the code, then writes a self-contained, verifiable plan with a file map, tasks, checks and acceptance criteria, and sets how completion is proven. Use whenever a task spans several steps or files, changes architecture, migrates or upgrades something, touches data or deployments, or is costly to redo, and whenever the user asks to plan, scope, break down or design an approach, even if they never say plan. Also use for multi-step operations or content work that Claude will carry out. Not for one-line edits, questions, explanations, writing a plan document as the deliverable itself (such as a business plan), or work that already has an approved plan.
compatibility: Claude Code on macOS or Linux with python3 3.12 or later on PATH for the plan gate and the state file validator, standard library only. In the Claude app it plans without agents, hooks or state file.
allowed-tools: Bash(python3 "${CLAUDE_SKILL_DIR}/scripts/validate-state.py" *)
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
4. `EnterPlanMode` is not always there: subagents don't have it, `denyInsteadOfPrompting` removes it, and the Claude app has no plan mode. Check before calling it, and say when the guardrail is off.
5. Never choose where the plan is saved. In plan mode Claude Code stores it in its own plan file and tells you the path; elsewhere the plan goes in the reply.
6. `/goal` has limits: the condition holds at most 4,000 characters, so it references the plan by path; its evaluator reads only the conversation, runs no commands and reads no files, so "Done when" names evidence you print. Only the user can type it, one goal per session, and it's unavailable in the Claude app and when hooks are disabled.
7. One option of the plan approval menu starts auto mode, or bypass permissions when that is enabled, and stops asking before reserved actions. Recommend manual approval ("Yes, manually approve edits") unless `permissions.ask` rules cover the reserved actions.
8. The task tools may be missing; some models don't have them by default. Track progress in the progress checklist and the state file, never only in task tools.
9. A subagent's report is a set of claims until you check them. Re-verify every claim the plan depends on before writing it as a fact.
10. The examples show judgment, not a template. Copy their reasoning, never their languages, names or numbers.
11. Auto mode nudges you to keep going without asking. The phase 1 questions are required whenever scope, assumptions or a reserved action is unclear, in every permission mode.
12. Invoking this skill registers the plan gate, a Stop hook, for the rest of the session. It reads only the state file, so keep that file's status accurate and record each task's evidence right after its check passes.
13. A resumed session (`--resume`, `--continue`) or a cleared context loses both the gate and this skill's text: the gate is not registered again on resume (observed in Claude Code, not in the docs). That is why the plan's handoff tells the implementer to invoke this skill before Task 1 and after any resume or clear.

## What this session has

Decide this from what you can see, not from the app's name, before research. Write the result on the plan's Guardrail line.

- Already in plan mode: proceed; the plan lands in Claude Code's plan file.
- Not in plan mode, `EnterPlanMode` available: call it before research.
- No `EnterPlanMode` (a subagent, a setting that removes it, the Claude app): work read-only by instruction and say at the top of the plan that the guardrail is off.
- The plugin's agents are available only when `work-lifecycle:planning-researcher` is among the agents you can call. Without them, do the research and the review inline and say so.
- The state file and the gate are available only when the paths under Execution reached you as absolute paths. If they still show `${`, the placeholders weren't substituted: skip the state file and `/goal`, and say that completion rests on the final report.
- Unattended run (scheduled task, no user to answer): skip `EnterPlanMode`, list each unanswered question under Assumptions and open questions with your recommended answer, deliver the plan, and execute nothing that needs authorization.

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
2. When the goal, the context, a constraint or a reserved action is unclear, ask before researching further. Reserved actions are push, deploy, publishing, messages to third parties and spending; the plan lists each one as an authorization checkpoint. Never fill the gap with a guess:
   - Ask with the `AskUserQuestion` tool when it is available; otherwise ask in the reply and stop until the user answers.
   - Ask 1 to 4 questions about what only the user knows: the outcome they want, who it is for, the current situation, the constraints, the priorities, what must not change. Offer concrete options and mark the one you recommend.
   - Never ask the user to choose a method, a tool or a technical design. Those are your decisions: make them from the answers and the research, and present them in the plan with the reason for each.
   - If the answers still leave the goal unclear, ask again.
3. Skip the questions only when the request leaves nothing open, and say so in the checklist.

### 2. Research

1. Read the current official sources for every library, tool or service the plan touches, and check the installed versions and their release notes. Current sources outrank memory.
2. Read the code the change touches: its callers, its tests, its configuration.
3. When the scope goes beyond a few files, delegate exploration to the `work-lifecycle:planning-researcher` agent, one brief per question, and send the briefs for independent questions in one message so they run in parallel. The brief says what to find, the scope, and what the answer decides; the agent already knows its report contract.
4. Treat a claim without evidence as unverified. Re-check yourself every claim the plan depends on before writing it under Verified facts.

### 3. De-risk

1. Find the assumptions that would sink the plan if wrong, and test each one now with a read-only probe: an existing test, a type check, a `--dry-run`, a query.
2. A probe that needs to write becomes Task 0 of the plan, run after approval by a subagent with `isolation: worktree`, with a go or no-go gate before the other tasks.
3. Skip this phase for a plan with no risky assumption, and say so in the checklist.

### 4. Write the plan

1. Start from `assets/plan-template.md`. Keep every section it has, and add or expand sections as the plan's type and risk require.
2. Read `references/plan-structure.md` before writing: it holds the explicitness rules, the expansion rules and why each section exists.
3. Open the one example that matches the plan before writing it:
   - `references/examples/basic.md`: a change to a few files, two or three tasks.
   - `references/examples/intermediate.md`: a feature with interfaces between tasks and a Task 0 spike.
   - `references/examples/complex.md`: a phased migration with rollback, authorization checkpoints and subagent execution.
   - `references/examples/non-code.md`: operations or content work, with acceptance checks instead of tests.
4. For each code task, mark whether it is test-first. A test-first task names its test, the assertion and the failure message expected before the code exists. It is carried out with the `work-lifecycle:testing-before-implementation` skill, which records two runs: `red`, the test failing for the named reason before the code exists, and `green`, the same test passing after the code.

### 5. Self-review

Run this loop before any handoff, every time:

1. Coverage: every requirement maps to a task.
2. Steps: each allows one reasonable action; no line that decides nothing ("TBD", "handle edge cases"), no code body the signature and tests already determine.
3. Consistency: names, types and signatures match across tasks.
4. Risks: each failure mode has its check in the task that owns it.
5. Proportion: the plan is not several times longer than the requirements.
6. Fix every issue found, then run the whole loop again. Hand off only after a pass that finds nothing.

### 6. Independent review

For high-stakes plans only (production, data, deployments, security, anything published to third parties, such as a public plugin or marketplace, or anything costly to redo), brief the `work-lifecycle:plan-verifier` agent in plan mode. It can't see this conversation, so the brief carries the plan's file path, or the plan's full text when it is only in the reply, and the requirements written out: the user's goal, their answers to your questions and their constraints. Resolve each blocking finding before handoff. For other plans, write why the review was not needed.

### 7. Handoff

1. In plan mode, request approval through the native menu (`ExitPlanMode`). Recommend manual approval, or auto mode only when `permissions.ask` rules cover the reserved actions. Outside plan mode, ask for approval in the reply and wait.
2. When the user asks for changes instead of approving, rewrite the plan in full with the changes merged into it, run the phase 5 self-review again, and phase 6 again on a high-stakes plan, then ask for approval of the full plan again. Never execute an approved list of changes: the implementer, often a new session, sees only the plan text.
3. End the plan's Handoff section with this line, word for word, because a resumed or cleared session loses the gate and these rules: "Before Task 1, and after any resume or context clear, invoke the work-lifecycle:planning-before-execution skill and follow its Execution section."
4. Name how completion is proven:
   - With the state file, always the plan gate, as described under Execution.
   - Also `/goal`, for a plan in Claude Code with more than one task and one measurable end state. Read `references/goal-handoff.md` and give the ready-to-paste condition.
   - Without the state file, the final report with each task's evidence.
5. When hooks are disabled, say that the gate won't run and that completion rests on the final report.

## Execution

These rules apply once the user approves the plan. If the session was resumed or its context cleared since this skill was invoked, invoke it again before going on, so the gate is registered. After invoking it again on a resumed session, ask the user to run `/hooks` and confirm that a Stop hook running `plan-gate.py` is listed; if it isn't, say that the gate is off for this session and that completion rests on the final report.

Without the state file (see What this session has), skip "Start: the state file" and every instruction about `status` and validation, and keep each task's command and real output for the final report.

### Start: the state file

1. Run `python3 --version`. If it fails or reports a version older than 3.12, say that the plan gate and the validator can't run on this machine and that completion rests on the final report, then continue without the state file.
2. Create the folder `${CLAUDE_PROJECT_DIR}/.work-lifecycle/` if it is missing, with a `.gitignore` file there that holds the single line `*`, so nothing in it reaches the repository.
3. Find this plan's state file before creating one, so a resume or a clear never loses recorded evidence:
   - If `${CLAUDE_PROJECT_DIR}/.work-lifecycle/${CLAUDE_SESSION_ID}.json` exists and its `plan` names this plan and its `status` isn't `done`, keep it: never copy the template over it. If it belongs to a finished plan or another plan, rename it to `${CLAUDE_SESSION_ID}-previous-<n>.json`, with the first free number, and go on below.
   - Otherwise, if the folder holds exactly one state file whose `plan` names this plan's file path and whose `status` isn't `done`, it is this plan's record from before a context clear: rename it to `${CLAUDE_SESSION_ID}.json` and keep its evidence. If several match, or the plan is only in the reply (`plan` is `reply`, which can't tell plans apart), ask the user before adopting a file.
   - Otherwise copy `assets/plan-state.json` to `${CLAUDE_PROJECT_DIR}/.work-lifecycle/${CLAUDE_SESSION_ID}.json`. Use exactly its structure, because the gate parses it: set `plan` to the plan file's path, or `reply`; set `status` to `executing`; and replace both sample tasks with one task per plan task, in plan order, each with its `id`, `title` and `check`, `test_first` true for test-first tasks, and `evidence`, `red` and `green` null. Keep a Task 0 only when the plan has one: a leftover sample can never gain evidence and holds the gate.
4. Validate it with this skill's script, fix what the output names, and repeat until it reports the file valid:

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/validate-state.py" "${CLAUDE_PROJECT_DIR}/.work-lifecycle/${CLAUDE_SESSION_ID}.json"
   ```

   The gate itself is a hook script that Claude Code runs on its own; never run it.

5. Start at the first task without evidence, only after validation passes.

### Each task

1. Run the task's steps, then its check.
2. If the check fails, read the output, fix the cause and run the check again.
3. When it passes, record `evidence` as an object with `command` (the exact command) and `output` (its real output, trimmed to the lines that prove the result), then validate the file again. A test-first task also records `red` and `green` the same way.
4. Never start the next task before the current one has its evidence.

### Stops and the end

1. Whenever you must stop for the user (a reserved action at its authorization checkpoint, a question, a decision the plan leaves to them), set `status` to `awaiting-authorization` first, ask, and set it back to `executing` once they answer.
2. On a high-stakes plan, after the last task, give the `work-lifecycle:plan-verifier` agent the plan's path and the state file's path, naming work mode in the brief, and resolve every blocking finding before going on.
3. When every task has its evidence, set `status` to `done` and deliver the final report in this structure:

   ```text
   ## Final report: <plan title>
   - Task <id>: <title>
     - Check: `<exact command>`
     - Result: `<result line of its real output>`
   Verifier: <verdict, and how each blocking finding was resolved | not run, because <reason>>
   Open: <what remains open | none>
   ```

4. If the user stops the plan, set `status` to `done` and report which tasks have no evidence.

### Delegation

1. Default to the main session.
2. Use one subagent per task when there are many independent tasks, the context would grow large, or a mistake is costly enough to justify a review per task. Run parallel subagents with `isolation: worktree`.
3. Tell each delegated code task to use the `work-lifecycle:testing-before-implementation` skill, and require back the commands and raw output of its checks, the red and green runs included.
4. Only the main session writes the state file: record each subagent's evidence from the output it returns, so parallel tasks never write the file at once.
