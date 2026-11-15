---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Claude's Auto-fix stays off; github-operations:auto-pr-lifecycle drives pull requests

## Scope

How CI failures and review findings on this repository's pull requests get fixed.

## Context and problem statement

Claude's Auto-fix for pull requests watches a pull request and "pushes a fix if one is clear" (code.claude.com/docs/en/claude-code-on-the-web, Auto-fix pull requests). This project pushes only with the owner's explicit authorization.

## Decision drivers

- Every push is authorized by the owner.
- CI failures and review comments still get fixed without manual triage.

## Considered options

- **Auto-fix off; `github-operations:auto-pr-lifecycle` fixes findings and asks before every push**: chosen.
- **Auto-fix on**: rejected, because it pushes without asking and would need an exception to the push rule.

## Decision outcome

Chosen option: **Auto-fix off, `auto-pr-lifecycle` on**, because it does the same work and keeps every push authorized.

### Consequences

- Good, because no change reaches a pull request without the owner's approval.
- Bad, because each fix waits for the owner's answer.

## More information

- Decided by the owner on 2026-11-15.
