---
status: deprecated
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_claude-reviews-every-pull-request-push-for-what-ci-cannot-check
superseded-by: none
---

# Claude reviews every push to a same-repository pull request and posts one summary per push

## Scope

`.github/workflows/claude-code-review.yml`.

## Context and problem statement

ADR_2026-11-15_claude-reviews-every-pull-request-push-for-what-ci-cannot-check set Claude's review to run on every push, limited to what Validate can't check. It kept one summary comment current with `gh pr comment --edit-last --create-if-none`. The whole-branch review of 2026-11-15 found two problems:
- `claude.yml` posts as the same Claude account, so `--edit-last` would overwrite Claude's latest reply to an `@claude` mention.
- A pull request from a fork gets no environment secret, so its review job fails red.

## Decision drivers

- Never overwrite another comment.
- No red check that comes from a missing secret.

## Considered options

- **One new summary comment per push, headed with the commit it reviewed; skip forks**: chosen.
- **Find the summary by a marker and edit it through the API**: rejected, because it needs a write tool beyond the four the official per-push example grants.

## Decision outcome

Chosen option: **one summary per push, and same-repository pull requests only**:
- The prompt tells Claude to post a summary per push, starting "Claude review of <short SHA>", and never to edit an earlier comment.
- The job runs only when `head.repo.full_name` equals the repository.
- Everything else in ADR_2026-11-15_claude-reviews-every-pull-request-push-for-what-ci-cannot-check still holds: the triggers, the scope, the permissions, the API key in the `claude` environment, the `CLAUDE_CODE_REVIEW` gate and the pins.

### Consequences

- Good, because `@claude` replies stay as written.
- Bad, because a pull request with many pushes collects one summary each.

## More information

- Found by the whole-branch review of 2026-11-15 and fixed as part of the release pipeline plan the owner approved.
