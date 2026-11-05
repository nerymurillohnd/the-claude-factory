---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: ADR_2026-11-04_github-operations-skills-route-without-naming-each-other
superseded-by: none
---

# github-operations' skills name each other in their bodies, not in their descriptions

## Scope

The descriptions and the "When to use" and "When not to use" sections of the four skills in `plugins/github-operations/skills/`, and every place in their references that sends work to a sibling skill.

## Context and problem statement

ADR_2026-11-04_github-operations-skills-route-without-naming-each-other recorded that the skills route to each other in plain words, without names. That misread Nery's instruction: he asked to remove the sibling names from the descriptions only, and to keep explicit names in the body's "When to use" and "When not to use" sections. Plain-word hand-offs left the agent to guess which sibling a request belongs to. Where in a skill should a sibling be named?

## Decision drivers

- A description only has to make Claude pick the right skill; sibling names there add weight to every session's context.
- A hand-off inside a loaded skill must point to exactly one skill, with no guessing.
- A hand-off must name only work the receiving skill accepts.

## Considered options

- **Descriptions without sibling names; "When to use" and "When not to use" sections in each body that name each sibling as `github-operations:<skill>`**: chosen.
- **One plain-word "Hand off" rule in each skill's Rules, with no names**: rejected by Nery; it was the misreading.
- **Sibling names in the descriptions too**: rejected by Nery, because descriptions only select the skill.

## Decision outcome

Chosen option: **names in the body, none in the descriptions**. Each description ends with what "this plugin's other skills cover" and promises only work a sibling accepts. Each skill has "When to use" and "When not to use" sections; every hand-off there and in the references names its target as `github-operations:<skill>`. The generic "Hand off what this plugin's other skills cover" rules are removed. Work no skill covers, such as writing a new workflow from scratch, is stated as not covered.

### Consequences

- Good, because the descriptions stay short and every hand-off inside a skill points to one named skill.
- Bad, because renaming a skill means updating its siblings' bodies and references; a search for `github-operations:<old name>` finds every place.

## More information

Nery's correction in the session of 2026-11-04: "Yo te he pedido que las skills se referencien con un nombre explícito. Cuando yo pedí que lo cambiaras, me refería a la description … Y que mejor lo incluyeras en las secciones de cuándo usar y cuándo no dentro del cuerpo de cada skill."
