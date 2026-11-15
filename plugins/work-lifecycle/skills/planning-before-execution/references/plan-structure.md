# Plan structure

Read this before writing a plan. It explains why each section exists, how explicit to be, and when to expand.

## Contents

- Why the plan stands on its own
- Why each minimum section exists
- How explicit a plan is
- Expansion rules
- Writing the plan for Claude

## Why the plan stands on its own

Approving with "clear context" makes Claude implement from the plan alone, a new session sees nothing of this conversation, and a subagent sees only its own task. Write every plan for an implementer who has seen neither the code nor the conversation: each task carries its files, names, interfaces and check.

## Why each minimum section exists

- Guardrail: says whether plan mode enforced read-only, so the reader knows what the planning could and couldn't touch.
- Goal: the outcome and why it matters. The why lets the implementer make the calls the plan leaves open.
- Acceptance criteria: the behavior or business outcome that proves the goal, beyond passing tests. Tests can pass while the goal fails.
- Verified facts: what the plan relies on, each with its evidence. A fact without evidence goes under Assumptions instead.
- Assumptions and open questions: what is not verified yet, and how each will be confirmed or which task de-risks it.
- File map: every file created, modified or deleted, with its responsibility after the change. It fixes the decomposition before the tasks, so tasks don't overlap.
- Tasks: each with files, what it consumes and produces, whether it is test-first, its steps, its check with the expected output, and a done criterion. Consumes and Produces make the interfaces between tasks explicit, so tasks can run in order or in parallel without guessing.
- Authorization checkpoints: every step that needs the user's go-ahead, so execution stops there instead of discovering it.
- Risks: the most likely failure modes, each tied to the check in the task that owns it.
- Execution strategy: main session or subagents, with the reason.
- Handoff: how completion is proven: the state file and plan gate, plus the `/goal` condition when it applies.

## How explicit a plan is

- Write only the decisions the implementer can't make alone: files, names, signatures, values, tests and the exact check commands.
- Leave out code bodies, except a non-obvious algorithm or fixed copy (an error message, a legal sentence, a configuration value).
- Leave out every line that decides nothing, such as "TBD", "handle edge cases" or "add tests as needed": replace it with the case, the test or a question.
- Size each task so its check proves one thing. A task whose check needs several unrelated commands is two tasks.
- Give each step one reasonable reading. If two implementers could do different things, decide which.

## Expansion rules

- Several subsystems: split into phases, each ending in a check that proves the phase, or into separate plans when the phases can ship apart.
- Deploys or data: add a rollback plan with its own check, and an authorization checkpoint before the irreversible step.
- A write-only probe: Task 0, run by a subagent with `isolation: worktree`, with a go or no-go gate that names what changes in the plan on no-go.
- Non-code work: acceptance checks replace tests. Each check is still something that comes back pass or fail: a count, a query, a rendered page inspected against a list, a recipient list compared with its source.
- Test-first code tasks: the test name, its assertion and the failure message expected before the code exists.

## Writing the plan for Claude

The plan's reader is Claude, so write it like a good prompt:

- Be explicit: a colleague with minimal context should not be confused by any step.
- Give the why behind each decision that is not obvious.
- Say what to do, not only what to avoid.
- Track state for long work: the state file is the structured record of each task's evidence; progress notes and git checkpoints help across long sessions.
