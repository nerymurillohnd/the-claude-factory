---
status: superseded
date: 2026-11-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: ADR_2026-11-19_authoring-skills-splits-content-by-phase-and-topic
---

# authoring-skills keeps every run's decisions in SKILL.md and only conditional depth in references

## Scope

The file layout of `plugins/skills-engineering/skills/authoring-skills/`.

## Context and problem statement

An earlier plan split the content by topic into ten references that nearly every run would read. That breaks the rule the skill itself teaches: split by how content is used, and keep in the body what every run needs. The owner approved a rewrite plan on 2026-11-18 that puts every decision of every run in `SKILL.md`, as a criterion with its reason, and keeps references for depth only some runs need.

## Decision drivers

- The skill must practice what it teaches.
- The body must stay within 500 lines and about 5,000 tokens.
- Items are written as decisions with criteria, not topic lists.

## Considered options

- **Body with every run's decisions; six references for conditional depth**: chosen. The references are `frontmatter`, `special-placements`, `scripts-and-hooks`, `components`, `task-mechanisms` and `writing-patterns`.
- **Ten topic references read in most runs**: rejected, because it splits by topic instead of access and adds a read per step.

## Decision outcome

Chosen option: **every run's decisions in the body**, because it follows the skill's own rule and keeps the six phases readable on their own.

### Consequences

- Good, because `SKILL.md` is about 200 lines and an estimated 4,900 tokens on invoke, with each reference read only under its condition.
- Bad, because the body sits near its token budget, so new content must move to a reference or replace a line.

## More information

Commit 823ca5a; the token estimate comes from `claude plugin details`. Related: ADR_2026-11-18_authoring-skills-teaches-only-the-authors-trade.
