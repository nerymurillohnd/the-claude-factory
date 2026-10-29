---
status: accepted
date: 2026-10-29
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# github-operations asks for the merge approval in the skill

## Scope

- The merge approval of the PR lifecycle: `skills/github/references/pr/lifecycle.md` (Gates) and `pr/merge.md` (section 3).
- Out of scope: the rest of ADR_2026-10-29_github-operations-one-contract-skill, which stands.

## Context and problem statement

ADR_2026-10-29_github-operations-one-contract-skill chose the merge hook's `ask` permission prompt as the approval. ADR_2026-10-29_github-operations-hooks-limit-only-reviewer-agents removes every hook decision on the main session, so no hook asks before a merge. Where is the merge approved now?

## Decision drivers

- The merge stays gated by the user's explicit approval for the exact head SHA.
- The plugin's hooks never block or ask in the main session (Nery).

## Considered options

- **The skill asks the user directly (AskUserQuestion when available), naming repository, PR, branches, head SHA, method, queue, deployment and cleanup**: chosen.
- **The merge hook's `ask` prompt**: rejected; the hooks no longer act on the main session.

## Decision outcome

Chosen option: **the skill asks the user directly**, because it keeps the per-SHA approval without a hook in the main session.

### Consequences

- Good, because the approval names deployment and cleanup in the same question.
- Bad, because in auto mode nothing but the instruction stops a merge; users who want a hard stop add an `ask` permission rule for `gh pr merge` and `merge_pull_request`, which the README must offer.

## More information

This record replaces only the merge-approval option chosen in ADR_2026-10-29_github-operations-one-contract-skill; that record's other choices stand.
