# Agentic patterns

Read for prompts that use tools, run long, act autonomously, or delegate. Where model-specific guidance differs, it takes priority.

## Contents

- Action defaults
- Parallel tool calls
- Long-horizon work and state
- Autonomy and reversibility
- Unattended runs
- Scope and overengineering
- Tests and general solutions
- Grounded answers and claims
- Subagents
- Research
- Communicating with the user
- Memory
- Temporary files

## Action defaults

- **Proactive:** implement rather than suggest; when intent is unclear, infer the most useful action and use tools to fill missing details instead of guessing.
- **Conservative:** research and recommend by default; edit only when explicitly asked.

## Parallel tool calls

- The covered models run independent calls in parallel. An instruction can push this close to always: when calls have no dependencies, issue them together (for example, read three files in three parallel calls); keep dependent calls sequential and never guess missing parameters.
- To reduce parallelism (system strain), ask for sequential execution.
- Fable 5.1 in coding and computer-use loops may issue one call per turn. After each round of tool results, append a turn-scoped system message asking it to list privately what it needs next and request every independent item in one response.

## Long-horizon work and state

- Tell the model when the harness compacts context or saves state externally, so it does not wrap up early: keep working, save progress before the context refreshes, do not stop because of the budget.
- Multi-window tasks:
  1. Use a different prompt for the first window to set up the framework (tests, setup scripts); later windows iterate on a to-do list.
  2. Track tests in a structured file (for example `tests.json`) and state that removing or editing tests to pass is unacceptable.
  3. Encourage setup scripts (for example `init.sh`) to start servers, tests, and linters.
  4. Starting fresh can beat compaction: tell it how to re-orient (working directory, progress notes, tests file, git log, run a basic integration test before new work).
  5. Provide verification tools (browser automation, computer use) for UI work.
  6. For very long tasks, encourage planning and full use of the context while avoiding large uncommitted work.
- State: structured formats (JSON) for structured status; free-text progress notes for context; git for history and checkpoints; emphasize incremental progress.

## Autonomy and reversibility

Ask the model to weigh reversibility: proceed with local, reversible actions (editing files, running tests); confirm before destructive, hard-to-reverse, or externally visible actions (deleting files or branches, dropping tables, force-pushes, hard resets, pushing code, posting comments, sending messages, changing shared infrastructure). Do not bypass safety checks or discard unfamiliar files as a shortcut.

## Unattended runs

- State that the user is not watching and cannot answer mid-task, so permission questions block the work; proceed with reversible steps that follow from the request.
- Before ending a turn, check whether the last paragraph is a plan, a promise, or a question about work it could do, and do that work.
- Pause only for destructive actions, real scope changes, or input only the user has. Externally visible actions (pushing, posting, sending) still follow "Autonomy and reversibility": say in the prompt which of them the run may take on its own.
- Harness support (documented for Opus 5.5): treat a text-only end of turn as a report, not completion; keep the task's parts in a checklist the model updates; if items remain open with no stated blocker, send a short message naming them; stop after two or three automatic continuations.
- Leave these instructions out of human-in-the-loop products.

## Scope and overengineering

- Deliver what was asked at the intended scope; voice concerns briefly and continue under stated assumptions; extras are suggestions at the end.
- Guard against overengineering: no unrequested features, refactors, docstrings on untouched code, defensive handling for impossible cases, one-off helpers, or design for hypothetical futures; validate only at system boundaries.
- When the user describes a problem or asks a question, the deliverable is the assessment; do not apply a fix until asked.

## Tests and general solutions

Models can over-focus on passing tests. Ask for a general solution with standard tools, no hard-coded or test-specific logic, and a report of incorrect tests or infeasible tasks instead of workarounds.

## Grounded answers and claims

- On long runs, audit each progress claim against a tool result from the session; report failures and skipped steps plainly.
- Before state-changing commands, confirm the evidence supports that specific action.

## Subagents

- Delegate when work is parallel, needs isolated context, or forms independent workstreams. Work directly for simple, sequential, single-file tasks or when context must carry across steps.
- Models differ. Opus 5 delegates readily and needs damping. Fable-class models are dependable at parallel delegation: use subagents often, with explicit guidance on when, and asynchronous coordination.
- Harness option (Fable 5.1): the start-subagent tool returns immediately, results arrive later, and a separate tool lets the lead wait, so the lead keeps working.
- Fresh-context verifier subagents tend to beat self-critique on long runs (measured on Fable 5). Do not apply this to Opus 5 (no verification subagents) or to Sonnet 5.5 at `xhigh`/`max` (no self-started reviewer subagents).

## Research

For complex research, ask it to develop competing hypotheses, track confidence levels, self-critique periodically, and keep a notes file, in addition to stating what counts as a successful answer.

## Communicating with the user

- Describe the update cadence wanted (intent before starting, updates on important findings, outcome-first recap). Positive examples beat prohibitions.
- Final summaries are for a reader who saw none of the work: outcome first, then what is needed from the user, complete sentences, no private shorthand.
- For verbatim mid-task delivery, a send-to-user tool plus an instruction to use it only for user-facing content.
- If tool output is hidden from the user, say so, so the model puts needed output in its reply (documented for Fable 5.1).

## Memory

Give the agent a place to record lessons (one per file, one-line summary, corrections and confirmed approaches with reasons, nothing the repo or chat history already records, update instead of duplicating, delete wrong notes). Documented for Fable 5.

## Temporary files

The covered models create scratch files while coding; if net-new files should be avoided, ask for cleanup at the end.
