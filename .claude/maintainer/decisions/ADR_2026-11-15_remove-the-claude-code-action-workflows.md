---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_each-claude-workflow-reads-only-its-own-secret
superseded-by: none
---

# Remove the claude-code-action workflows

## Scope

`.github/workflows/claude-code-review.yml` and `.github/workflows/claude.yml`, PC-13 in `scripts/validators/plugin_consistency/checks.py`, `.github/zizmor.yml`, `.claude/rules/architecture/claude-workflows.md` and the `plugin-releases` skill. `evals.yml` is unchanged. The review and `@claude` records, ADR_2026-11-15_claude-review-posts-one-summary-per-push and ADR_2026-11-15_claude-answers-mentions-with-the-owners-subscription, are deprecated by this decision.

## Context and problem statement

`claude-code-review.yml` first ran Claude for real on pull request #108, on 2026-11-15: every earlier run ended green without running, because the workflow file differed from the default branch's copy. Each real run failed in under a second with `is_error: true`, no usage and USD 0, with `anthropics/claude-code-action` v1.0.276 (`f3b070c88125d33dbae5653df5f143101d4ea9dc`) and Claude Code 2.1.325. [anthropics/claude-code-action#2047](https://github.com/anthropics/claude-code-action/issues/2047), opened 2026-11-14, reports the same failure on the same commit since 2026-11-14 about 15:30 UTC, with the key, billing and model access ruled out. v1.0.276 is the newest release, and the action hides the error text even in a debug rerun.

## Decision drivers

- The owner wants no workflow that keeps failing on every pull request.
- A setup that needs keys, an environment and workflow changes merged to `main` before it can be tested cost the owner time without producing a review.

## Considered options

- **Remove both claude-code-action workflows**: chosen by the owner.
- **Keep them and wait for the upstream fix**: rejected by the owner.
- **Pin an older action release**: not tried; #2047 shows the same commit breaking without a change on the user's side, which points to a server-side cause.

## Decision outcome

Chosen option: **remove both workflows**, decided by the owner on 2026-11-15 (commit e460792):
- `claude-code-review.yml` and `claude.yml` are deleted.
- PC-13 lets no workflow read `ANTHROPIC_API_KEY`, and only `evals.yml` read `CLAUDE_CODE_OAUTH_TOKEN`.
- `zizmor.yml` drops the `dangerous-triggers` exception for `claude.yml`.
- A new workflow that runs `anthropics/claude-code-action` needs the owner's approval.

### Consequences

- Good, because no pull request shows a failing Review check, and no workflow reads the Console API key.
- Bad, because pull requests get no automatic Claude review and `@claude` mentions get no answer. A review runs on request from a Claude Code session with `/code-review`.
- Pending: `ANTHROPIC_API_KEY`, the `github-claude-review` service account and its key in the Claude Console, and the `CLAUDE_CODE_REVIEW` variable are no longer used; removing them is the owner's call.
- Pending: ADR_2026-11-15_zizmor-accepts-three-findings-with-their-reasons still lists the `claude.yml` exception that this change removed.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| No workflow reads `ANTHROPIC_API_KEY`, and only `evals.yml` reads the OAuth token | `npm run check:consistency -- --offline` (PC-13) and `npm run test:scripts` | 2026-11-15: exit 0; 332 tests OK | After a workflow changes |
| The workflows stay valid | `npm run lint:workflows` | 2026-11-15: no findings (5 ignored) | After a workflow or `zizmor.yml` changes |
