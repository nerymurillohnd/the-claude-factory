---
status: accepted
date: 2026-11-19
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-18_authoring-skills-body-holds-every-run-decision
superseded-by: none
---

# authoring-skills keeps SKILL.md as the contract and gives each phase and topic its own reference

## Scope

The file layout of `plugins/skills-engineering/skills/authoring-skills/`.

## Context and problem statement

ADR_2026-11-18_authoring-skills-body-holds-every-run-decision kept every run's decisions in `SKILL.md` and six references for conditional depth. The redesign on pull request [#113](https://github.com/nerymurillohnd/the-claude-factory/pull/113) made `SKILL.md` the contract: role, goal, terms, twelve standards, gotchas and a seven-phase workflow. It gave each Phase 1 and Phase 2 topic one owner file, named by phase and topic, read at the step that points to it. The owner set the phased-reference standard: a rule kept in another phase's file is applied late or not at all.

## Decision drivers

- One owner per topic, with no duplicated rule.
- Each phase reads only its own files, in the order of its steps.
- The skill practices the progressive disclosure it teaches.

## Considered options

- **SKILL.md as the contract, one reference per phase and topic**: chosen.
- **Every run's decisions in SKILL.md, six conditional references**: rejected, because the redesign's content no longer fits the body, and topic files that span phases deliver rules late.

## Decision outcome

Chosen option: **SKILL.md as the contract, one reference per phase and topic**, because each rule then has one home, read when its phase needs it.

### Consequences

- Good, because each of the 23 references holds one phase and one topic, opens with its gotchas and closes with its sources and its exit.
- Bad, because `SKILL.md` grew to about 5.7k tokens on invoke, over the 5,000-token standard, tracked as DEBT-009.

## More information

Released as skills-engineering 0.2.0 on 2026-11-19. Related: ADR_2026-11-19_every-skill-reference-ends-with-an-exit.
