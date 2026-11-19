---
status: accepted
date: 2026-11-19
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# authoring-skills presents its design as a versioned document from a template

## Scope

Phase 2, step 6 of `plugins/skills-engineering/skills/authoring-skills/SKILL.md`, and `assets/design-proposal.md`.

## Context and problem statement

Phase 2 ended by presenting "the design" in one line, with no template, and Phase 3's plan template repeated its fields. The owner observed on 2026-11-19 that when the user corrects or asks something, Claude answers but doesn't update the design. Phase 3 then plans from memory of the conversation instead of from what was approved.

## Decision drivers

- The plan must start from what the user really approved.
- The design is the general sketch: what Claude understood, and everything it took to get there.

## Considered options

- **A versioned design document from a template, re-presented whole after every correction**: chosen.
- **A one-line design summary in the reply**: rejected, because corrections stay only in the conversation.
- **A template plus a reference file on how to fill it**: rejected, because the template carries its own fill guidance in brackets.

## Decision outcome

Chosen option: **a versioned design document**, because Phase 3 reads the approved version instead of recalling the conversation.

### Consequences

- Good, because the template covers the understanding, the goal, the use cases, the users, the environment, the domain sources, the type, the base architecture, the frontmatter, the name and description, the decisions and the open questions.
- Good, because in Claude Code the document is one file outside the skill's folder, in the session's scratchpad or the project's plans folder, and in plan mode or elsewhere it goes whole in the reply.
- Bad, because every correction costs a full re-presentation.

## More information

Released as skills-engineering 0.2.0 on 2026-11-19. Related: ADR_2026-11-19_authoring-skills-plans-in-plan-mode-without-a-template.
