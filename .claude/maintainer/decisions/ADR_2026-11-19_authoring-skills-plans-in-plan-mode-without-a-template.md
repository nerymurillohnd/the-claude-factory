---
status: accepted
date: 2026-11-19
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# authoring-skills writes its plan in plan mode, with no plan template

## Scope

Phase 3 of `plugins/skills-engineering/skills/authoring-skills/SKILL.md`.

## Context and problem statement

The plan must be approved by the user before anything is built. The owner asked on 2026-11-19 whether Claude can enter plan mode on its own. The Claude Code tools reference, read the same day, lists `EnterPlanMode` with no permission required, and `ExitPlanMode` with permission required. Changelog 2.1.0 removed the permission prompt for entering plan mode. The owner also ruled that the plan gets no template, because the user's own plan mode or settings may impose their own format.

## Decision drivers

- Only the user approves the plan.
- The plan expands the approved design into specifications, without repeating it.

## Considered options

- **Claude enters plan mode with EnterPlanMode and presents with ExitPlanMode, with no template**: chosen.
- **Recommend that the user switch to plan mode**: rejected, because Claude can do it itself.
- **A fixed plan template**: rejected, because it can clash with the user's own plan mode.

## Decision outcome

Chosen option: **plan mode with no template**, because only the user can approve `ExitPlanMode`, and the plan follows the session's own format.

### Consequences

- Good, because the plan holds each use case's checkable result, each file, the build order with its checks, and the open assumptions.
- Bad, because plan mode exists only in Claude Code: elsewhere the plan goes in the reply, and a subagent returns it as its result.
- Bad, because in a terminal session with bypass permissions available, plan mode doesn't block edits, so the skill tells Claude to keep to planning.

## More information

Sources: [tools-reference](https://code.claude.com/docs/en/tools-reference) and [permission-modes](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode), read 2026-11-19. Related: ADR_2026-11-19_authoring-skills-presents-a-versioned-design-document.
