---
status: accepted
date: 2026-11-19
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-18_authoring-skills-stands-alone-from-auditing-skills
superseded-by: none
---

# authoring-skills loads auditing-skills only when the user chooses the audit

## Scope

How `plugins/skills-engineering/skills/authoring-skills/` relates to `auditing-skills`.

## Context and problem statement

ADR_2026-11-18_authoring-skills-stands-alone-from-auditing-skills allowed no reference to `auditing-skills` except the final offer. The redesign's Phase 7 now loads `auditing-skills` and follows it to its end when the user chooses the audit in Phase 6. ADR_2026-11-19_authoring-skills-runs-the-chosen-audit-and-evals records that choice.

## Decision drivers

- A skill installed or copied alone must still work.
- The audit spends usage and is the user's choice.

## Considered options

- **Load auditing-skills in Phase 7 only when chosen, and leave the option out when it isn't available**: chosen.
- **No reference except the offer**: rejected, because Phase 7 must run the audit the user chose.

## Decision outcome

Chosen option: **load it only when chosen**, because `authoring-skills` still works without it, and Phase 6 leaves out the audit option when the skill isn't among the available skills.

### Consequences

- Good, because the audit runs inside the workflow, and its findings are verified before they are applied.
- Bad, because Phase 7 now names `auditing-skills`, so a rename of that skill must update it.

## More information

Released as skills-engineering 0.2.0 on 2026-11-19.
