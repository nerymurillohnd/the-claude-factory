---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# github-operations' skills route to each other in their rules, without naming each other

## Scope

The descriptions and governance rules of the four skills in `plugins/github-operations/skills/` (commits b51e8a1 and 7a22c1d).

## Context and problem statement

Each skill had a "When not to use" section and a description that named its siblings, such as "(github-files-setup)". That weighed on every skill and tied it to its siblings' names. How should a skill send a request it does not cover?

## Decision drivers

- Lighter skills.
- Routing that works where a sibling is renamed or absent.
- One place in each skill for the rule.

## Considered options

- **One rule in each skill's governance, in plain words, with no sibling names**: chosen.
- **"When not to use" sections and descriptions that name each sibling**: rejected by Nery.

## Decision outcome

Chosen option: **a governance rule in plain words**. Each description ends with what "this plugin's other skills cover". Each skill's Rules section holds one "Hand off what this plugin's other skills cover" rule that lists the requests to send away. Each hand-off names only work the receiving skill accepts.

### Consequences

- Good, because the descriptions are shorter and no skill depends on another's name.
- Bad, because the agent must match the plain-word description to the right sibling skill; no name points it there.

## More information

Directed by Nery on 2026-11-04: the instruction to use the other skills belongs in each skill's governance section.
