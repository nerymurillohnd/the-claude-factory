---
status: accepted
date: 2026-11-19
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Every skill reference ends with an Exit section after its official sources

## Scope

The reference layout in `.claude/rules/code-quality/skill-style.md`, every reference of `authoring-skills`, and what `authoring-skills` teaches for the phased skills it writes.

## Context and problem statement

The phases in `SKILL.md` gained exits, but the references they send Claude to ended on their sources. Claude was left to judge when a file was done and where to go next. On 2026-11-19 the owner asked that each reference end by validating: once Claude has read the file and decided what it uses from it, it moves on to the next document or phase.

## Decision drivers

- Claude moves on in order, instead of stopping or skipping ahead.
- A reference must not drift when `SKILL.md` reorders its steps.

## Considered options

- **A final `## Exit` after Official sources, with the file's condition and a return to the step list in `SKILL.md`**: chosen.
- **An Exit line at the end of the procedure, before the sources**: rejected by the owner, because the closing must be the last thing Claude reads.
- **Name the next file in each exit**: rejected, because a reorder in `SKILL.md` would leave the references stale.

## Decision outcome

Chosen option: **a final Exit section that returns to `SKILL.md`**.

### Consequences

- Good, because all 23 references close with a checkable condition. Phase 6 ends the work or goes on to Phase 7, and Phase 7 returns to Phase 6.
- Good, because `authoring-skills` teaches the same closing for the phased skills Claude writes.
- Bad, because the project's layout rule changed, so other skills' references follow it only when they are next edited.

## More information

Released as skills-engineering 0.2.0 on 2026-11-19.
