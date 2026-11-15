# Plan: <what gets built or changed, in one line>

<!-- A sensible default, not a form to fill. Keep every section below; add sections or expand them as the plan's type and risk require. Merge two only when one would hold a single line such as "None". Write for an implementer who has seen neither the code nor this conversation. -->

Guardrail: <plan mode on | off, and why: chat, subagent, tool unavailable, unattended run>

## Goal

<The outcome in one or two sentences, and why it matters, so the implementer can make the calls this plan leaves open.>

## Acceptance criteria

- <Observable behavior or business outcome that proves the goal is met, beyond passing tests.>

## Verified facts

- <Fact the plan relies on> — <evidence: file and line, command and its real output, or URL with its date>

## Assumptions and open questions

- <Assumption> — <how it will be confirmed, or which task de-risks it>
- <Question for the user, with the recommended answer>

## File map

- `<path>` (create | modify | delete): <its responsibility after the change>

## Tasks

### Task 1: <name>

- Files: `<path>`, `<path>`
- Consumes: <interfaces, data or results from earlier tasks>
- Produces: <names, signatures, files or results later tasks rely on>
- Test first: <yes, with the test name, its assertion and the failure message expected before the code exists | no, and why>
- Steps:
  1. <one action that allows one reasonable reading>
- Check: `<exact command>` → <expected output>
- Done when: <the check passes and its evidence is recorded>

## Authorization checkpoints

- Before <push | deploy | publishing | message to a third party | spending>: <task and step>, stop and ask.

## Risks

- <Most likely failure mode> — checked by <the check, in the task that owns it>

## Execution strategy

<Main session, or one subagent per task, with the reason. Worktree isolation for parallel subagents.>

## Handoff

<Completion: the plan gate records each task's evidence. For more than one task in Claude Code, the /goal condition from references/goal-handoff.md, with its approximate length.>

Before Task 1, and after any resume or context clear, invoke the work-lifecycle:planning-before-execution skill and follow its Execution section.
