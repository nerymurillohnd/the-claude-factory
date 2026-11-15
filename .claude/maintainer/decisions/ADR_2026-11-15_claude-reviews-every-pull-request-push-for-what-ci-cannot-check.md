---
status: superseded
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: ADR_2026-11-15_claude-review-posts-one-summary-per-push
---

# Claude reviews every push to a pull request, only for what CI's scripts can't check

## Scope

`.github/workflows/claude-code-review.yml`. Out of scope: the `@claude` workflow (ADR_2026-11-15_claude-answers-mentions-with-the-owners-subscription).

## Context and problem statement

The owner wanted a remote review of every pull request, on every push, posted on the pull request. He also wanted no review of what Validate already checks. The earlier Claude workflows were deleted on 2026-11-13 because they never ran correctly; the owner asked to rebuild from Anthropic's official examples, not from them.

## Decision drivers

- Review every push, and post the findings where the owner reads pull requests.
- Cover only what scripts can't: bugs, breaches of `CLAUDE.md` and the rules, version bumps and docs made untrue.
- Start from the official examples, with the smallest permissions.

## Considered options

- **The per-push example from `anthropics/claude-code-action` `docs/solutions.md`, with a prompt scoped to what Validate can't check**: chosen.
- **Anthropic's `code-review` plugin (the docs' "Run a skill" example)**: rejected, because its command stops on a pull request Claude has already commented on, so later pushes go unreviewed.
- **The managed Code Review service**: rejected, because it needs a Team or Enterprise organization, bills separately and never blocks.

## Decision outcome

Chosen option: **the per-push example with a scoped prompt**:
- **Triggers:** opened, synchronize, reopened and ready_for_review; drafts and Dependabot are skipped, and a newer push cancels the older run.
- **Permissions:** `contents: read`, `pull-requests: write`, `issues: read` and `id-token: write`, as in the per-push example.
- **Posting:** inline comments, plus one summary kept current with `gh pr comment --edit-last --create-if-none`.
- **Credential:** `ANTHROPIC_API_KEY`, from the `claude` environment.
- **Off switch:** the job runs only when `vars.CLAUDE_CODE_REVIEW` is `enabled`.
- **Pins:** `anthropics/claude-code-action` v1.0.276 (commit `f3b070c`) and `actions/checkout` v7.0.1, both by SHA.

### Consequences

- Good, because each push gets a review that doesn't repeat Validate.
- Bad, because every push costs API tokens.
- Bad, because the action skips itself while the workflow differs from the default branch's copy, so the pull request that adds this file gets no review.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The workflow passes its linters | `npm run lint:workflows`, `zizmor --persona auditor` | 2026-11-15: no findings | Every workflow change |
| A review posts on a pull request | The first pull request after the merge, with the variable and secret set | pending | After the owner's setup |

## More information

- Decided by the owner on 2026-11-15: an API key for the review, a review on every push, and write permission for its comments.
