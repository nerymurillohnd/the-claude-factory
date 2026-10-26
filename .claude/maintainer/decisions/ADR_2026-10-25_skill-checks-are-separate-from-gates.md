---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Skill checks are separate from gates

## Scope

The checks a project skill runs while it works, and the gates of `scripts/gates.mjs` and CI. Out of scope: defining the gates, which comes later.

## Context and problem statement

The nine validators of `scripts/validators/` were run by no skill, no gate and no CI job, only by `npm run validate` (DEBT-006). Asked which skill each validator belongs to, the open question was whether skills should run them through `gates.mjs`. Do skills and gates share their checks?

## Decision drivers

- A skill executes according to what it governs and the scope it owns, at the moment its procedure scaffolds, runs or implements something.
- Gates are requirements set before given moments, processes, pipelines or stages, and are still to be defined.

## Considered options

- **Separate layers**: chosen. Each skill runs, with its own scripts, the checks of its scope while it works; gates hold their own grouped checks, and neither calls the other.
- **Skills run their checks through `gates.mjs`**: rejected because gates have nothing to do with the skills' work.

## Decision outcome

Chosen option: **Separate layers**, because a skill must check what it builds at the moment it builds it, while a gate is a later, grouped requirement.

### Consequences

- Good, because each skill is complete for its own scope without waiting for the gates to be designed.
- Bad, because the same check can exist twice, once in a skill and once in a gate, and the copies can drift.

## More information

Stated by Nery on 2026-10-25: "gates no tiene nada que ver con las skills… las skills deben de ejecutar conforme a lo que gobiernan y al scope que les corresponde… mientras que en las skills es al momento de hacer el scaffold o de ejecutar o de implementar lo que estas contienen." First applied in `building-plugins` (commit `4565c0d`). Related: DEBT-006.
