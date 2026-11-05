---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# The PR lifecycle runs three agents, and the user approves every push

## Scope

`plugins/github-operations/skills/auto-pr-lifecycle/` and `agents/pr-lifecycle/` (`pr-tracker`, `pr-fixer`, `pr-finalizer`), and `commands/init-pr-lifecycle.md`. Out of scope: the agents' tool limits (ADR_2026-11-04_pr-agents-deny-tools-in-frontmatter) and how they read GitHub (ADR_2026-11-04_pr-agents-read-github-through-mcp-first).

## Context and problem statement

In 0.5.x one read-only `pr-tracker` observed a pull request, and the main session fixed, replied, resolved threads and merged on its own. How should the work be split, and where does the user step in?

## Decision drivers

- Each agent does one job, with limits that fit that job.
- Nothing reaches GitHub, and nothing is merged, without the user's approval.
- Review threads that people opened stay theirs to resolve.

## Considered options

- **Three agents, a push gate after each fix round, and a merge gate**: chosen.
- **One observer agent, with the main session doing everything else**: rejected because one context held observation, fixes and GitHub writes together, with no separation of limits.

## Decision outcome

Chosen option: **three agents and two user gates**.

- `pr-tracker` observes the pull request and reports.
- `pr-fixer` fixes reported findings in the local clone and commits; it never pushes.
- `pr-finalizer` verifies each fix, replies in the review threads, and resolves only the threads bots opened.
- The main session verifies every report against its evidence and holds the user's gates: each push ("Push", "Push without asking again on this pull request", "Don't push") and the merge at the approved head SHA. It stops and asks after five fix rounds.

### Consequences

- Good, because every write to GitHub and every merge is behind an approval the user gave, and each agent's report is checked before it is acted on.
- Good, because threads people opened stay open for their reviewer.
- Bad, because the finalizer posts replies without asking on the user's own repository; on other repositories it needs approval. The blueprint reviewed on 2026-11-04 required explicit approval for every comment; this was reported to Nery and left as is.
- Bad, because the fixer and finalizer could be launched outside the skill. Their descriptions and an intake check (a findings ledger, `Replies approved`) keep them from writing when they are.

## More information

Decided by Nery in the approved PR lifecycle plan of 2026-11-04; built from commit 327e800 to e1daaa3, with later fixes (cba3367, bcb8810, 3833693, 463b5a3). ADR_2026-10-18_fold-pr-diagnostics-into-pr-tracker still holds: each agent carries its whole procedure in its own file. ADR_2026-10-29_github-operations-merge-approval-asked-by-the-skill still holds.
