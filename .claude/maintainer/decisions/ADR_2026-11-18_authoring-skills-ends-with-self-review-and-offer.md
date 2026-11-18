---
status: accepted
date: 2026-11-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# authoring-skills ends with a self-review and an offer, with no tests or evals in its workflow

## Scope

The workflow of `plugins/skills-engineering/skills/authoring-skills/SKILL.md`, phase 6. How evals are built, when chosen, is out of scope.

## Context and problem statement

`skill-creator` builds and runs evals as part of creating a skill, and an earlier version of `authoring-skills` put fresh-session runs, baselines, trigger tests and a model matrix inside its workflow. The owner set the order on 2026-11-17: "cuando ya esté construida, Claude hace un self review de ella, y si considera que está lista, viene y se lo dice al usuario y le ofrece dos opciones o tres: se queda así, o tiene observaciones, construye evals, o si gusta que corran la auditoría de Auditing Skills contra esa nueva skill recién creada." On validation he added that the writing itself must assume the reading of a session with a clean context.

## Decision drivers

- The owner decides whether a skill gets evals or an audit, both of which spend usage.
- The review that every skill gets is reading it as the model will.

## Considered options

- **Self-review from the model's seat, then the four-way offer**: chosen.
- **Tests and evals inside the workflow, as skill-creator does**: rejected, because the owner placed them at the end, as an option.

## Decision outcome

Chosen option: **self-review, then the offer**, because it matches the owner's order and leaves every spend to the requester.

### Consequences

- Good, because phase 6 walks each use case from the description to its result, checks a list built to fail on bad work, and reports what was and wasn't checked.
- Good, because evals, when chosen, point to the official guide or `claude plugin eval`.
- Bad, because a skill can ship without a behavioral run when the requester declines one.

## More information

Rewrite in commit 823ca5a. The owner's words were quoted from this session's transcript.
