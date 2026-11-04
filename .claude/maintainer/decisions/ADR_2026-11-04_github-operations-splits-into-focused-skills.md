---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: ADR_2026-10-29_github-operations-one-contract-skill
superseded-by: none
---

# github-operations splits its GitHub work into four focused skills

## Scope

`plugins/github-operations/skills/`: the skills `auto-pr-lifecycle`, `cleanup-and-debug`, `github-files-setup` and `claude-github-actions`, and the removal of the `github` contract skill (commit b4109a2). Out of scope: the agents' tool limits, the hooks and the release, each in its own ADR.

## Context and problem statement

Version 0.5.x put every GitHub task behind one contract skill, `github`, with references per task. One trigger description had to cover pull requests, setup, audits and CI, and every task loaded the same contract. Should the plugin keep one contract skill, or give each kind of work its own skill?

## Decision drivers

- Each skill triggers on one coherent kind of request (agentskills.io, "Design coherent units").
- A skill loads only what its task needs.
- Each skill can carry its own agents, references, scripts and assets.

## Considered options

- **Four focused skills**: chosen.
- **Keep the `github` contract skill**: rejected because one description and one contract had to cover unrelated work, which made activation imprecise.

## Decision outcome

Chosen option: **four focused skills**, because each one owns one kind of work and its trigger stays precise:

- `auto-pr-lifecycle` takes a pull request to merge.
- `cleanup-and-debug` audits and cleans up a repository.
- `github-files-setup` writes a repository's templates, forms, labels and Dependabot setup from reference models.
- `claude-github-actions` diagnoses, audits, hardens and repairs GitHub Actions workflows.

### Consequences

- Good, because each skill loads only its own references, and its description routes precisely.
- Bad, because writing and triaging issues and discussions, which the `github` skill covered, has no skill in 0.6.0 (DEBT-048).
- Bad, because it is a breaking change: `/github-operations:github` no longer exists.

## More information

Decided by Nery during the 2026-11-04 redesign. The README's "Coming from 0.5.x?" table maps each old task to its new skill, and the 0.6.0 CHANGELOG records the removal as breaking. Related: ADR_2026-11-04_github-operations-skills-route-without-naming-each-other.
