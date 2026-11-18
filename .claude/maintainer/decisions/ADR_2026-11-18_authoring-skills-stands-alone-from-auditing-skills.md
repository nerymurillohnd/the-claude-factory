---
status: accepted
date: 2026-11-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# authoring-skills stands alone from auditing-skills

## Scope

Every file of `plugins/skills-engineering/skills/authoring-skills/`.

## Context and problem statement

`authoring-skills` and `auditing-skills` ship in the same plugin, and an earlier draft of the first referred to the second in its references and its changelog line ("hands the finished skill to auditing-skills"). The owner ruled on 2026-11-17: "este skill no debe depender de auditing ni referenciarla", with the audit offered only at the end.

## Decision drivers

- A skill installed or copied alone must still work.
- The audit spends usage and is the requester's choice.

## Considered options

- **No reference to auditing-skills except the final offer**: chosen.
- **Hand every finished skill to auditing-skills**: rejected, because it couples the skills and runs an audit nobody chose.

## Decision outcome

Chosen option: **no reference except the final offer**, because the owner ruled so and the skill stays usable on its own.

### Consequences

- Good, because the only mention left is option 4 of phase 6, "if installed".
- Bad, because `authoring-skills` keeps its own short criteria for what `auditing-skills` checks in depth.

## More information

Changelog line fixed in 289b37b and e7d3c12; the example reference removed in 823ca5a.
