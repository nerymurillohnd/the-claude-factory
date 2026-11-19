---
status: accepted
date: 2026-11-19
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-18_authoring-skills-ends-with-self-review-and-offer
superseded-by: none
---

# authoring-skills runs the audit and the evals the user chooses, then asks again

## Scope

Phases 5 to 7 of `plugins/skills-engineering/skills/authoring-skills/`.

## Context and problem statement

ADR_2026-11-18_authoring-skills-ends-with-self-review-and-offer ended the workflow with a self-review and an offer, with no evals or audit inside it. On 2026-11-19 the owner set the closing flow:

1. After the build, a stop and a self-review of the whole skill, with its fixes.
2. The report, and a question with no preselected option: keep the skill, run the audit, build evals or anything else.
3. The chosen audit or evals run inside the workflow, the audit first when both are chosen.
4. Audit findings are verified and agreed with the user before they are applied, with no new design or plan.
5. The question comes back until the user keeps the skill.

## Decision drivers

- Each audit and eval run spends the user's usage, so the user chooses it.
- A finding can be wrong, so each one is verified first.
- The skill is ready only when the user keeps it.

## Considered options

- **Phase 7 runs the chosen audit and evals, then Phase 6 asks again**: chosen.
- **End with the offer, outside the workflow**: rejected, because the owner wants the chosen review carried through until the skill is ready.
- **Recommend keeping the skill as it is**: rejected, so that no option is preselected.

## Decision outcome

Chosen option: **Phase 7 runs what the user chose, and Phase 6 asks again**, because the user controls every spend and the loop ends only when they keep the skill.

### Consequences

- Good, because every phase ends with an exit, and audit fixes never restart the design.
- Bad, because a long loop of audits and evals spends more usage, at the user's choice.

## More information

Released as skills-engineering 0.2.0 on 2026-11-19, on pull request [#113](https://github.com/nerymurillohnd/the-claude-factory/pull/113).
