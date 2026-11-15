---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Claude answers @claude mentions through claude.yml, with the owner's subscription token

## Scope

`.github/workflows/claude.yml`, and the `claude` environment that holds the Claude secrets.

## Context and problem statement

The owner asked for the `@claude` workflow alongside the review. Anthropic's example (`anthropics/claude-code-action`, `examples/claude.yml`) authenticates with an API key. The owner wanted everything except the review to run on his subscription.

## Decision drivers

- On-demand requests in issues and pull requests.
- Billing on the owner's subscription, not the API account.
- Secrets that only the jobs needing them can read.

## Considered options

- **Anthropic's example with `claude_code_oauth_token`, and its secret in an environment named `claude`**: chosen.
- **Repository-level secrets**: rejected, because every job in the repository could read them; zizmor's `secrets-outside-env` audit flags it.

## Decision outcome

Chosen option: **the official example on the subscription token**:
- **Triggers:** an `@claude` mention in an issue, a comment, a review or a review comment. The action itself refuses bots and users without write access.
- **Permissions:** `contents`, `pull-requests` and `issues` write; `id-token: write`; `actions: read`.
- **Credential:** `CLAUDE_CODE_OAUTH_TOKEN`, from the `claude` environment.
- **Pins:** `anthropics/claude-code-action` v1.0.276 and `actions/checkout` v7.0.1, both by SHA; checkout runs with `persist-credentials: false`.

### Consequences

- Good, because mentions bill the owner's subscription.
- Bad, because the token comes from `claude setup-token` in a terminal, so the workflow stays inert until the owner creates it.
- Bad, because zizmor flags comment triggers as dangerous, and `.github/zizmor.yml` accepts that for `claude.yml` (ADR_2026-11-15_zizmor-accepts-three-findings-with-their-reasons).

## More information

- Decided by the owner on 2026-11-15: "add claude.yml", and the subscription token for all but the review.
