---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# github-operations 0.6.0 ships the whole redesign as one release

## Scope

The release of `plugins/github-operations` from the branch `claude/audit-new-plugin-kvbrcv`: version 0.6.0, set in commit fca975e and not yet tagged.

## Context and problem statement

The redesign replaced the `github` skill, the hooks and two agents, and added four skills, three PR agents and two commands, in phases. Should each phase ship as its own release?

## Decision drivers

- One breaking change and one migration for users, not several.
- Phases are reviewed on the branch before anything reaches `main`.

## Considered options

- **One release after every phase is done**: chosen.
- **A release per phase**: rejected because users would migrate several times.

## Decision outcome

Chosen option: **one release, 0.6.0**. Phases are committed on the branch; nothing merges between them. The CHANGELOG 0.6.0 entry and the README's "Coming from 0.5.x?" table carry the single migration.

### Consequences

- Good, because users migrate once.
- Bad, because the release waits on every open item before it: the minimum Claude Code version, the open debt the release depends on, and the gates.

## More information

Decided by Nery in the plan approved on 2026-11-04.
