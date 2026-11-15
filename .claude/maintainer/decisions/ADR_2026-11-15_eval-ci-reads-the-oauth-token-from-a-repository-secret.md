---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Eval CI reads the OAuth token from a repository secret

## Scope

The eval job of `.github/workflows/evals.yml`, `.claude/rules/plugins/evals.md` and the `plugin-releases` skill's one-time setup.

## Context and problem statement

The eval job read `CLAUDE_CODE_OAUTH_TOKEN` from a GitHub environment named `claude`, a choice carried over from the superseded ADR_2026-11-15_evals-ci-gates-on-score-and-delta-with-the-owners-subscription. The official guide (<https://code.claude.com/docs/en/github-actions>) stores Claude credentials as repository secrets and never mentions environments, and the owner found the environment needless complexity.

## Decision drivers

- Follow the official setup.
- Keep billing on the owner's subscription, never the Console API account.

## Considered options

- **Repository secret `CLAUDE_CODE_OAUTH_TOKEN`, no environment**: chosen by the owner.
- **Keep the `claude` environment**: rejected. zizmor's auditor persona flags `secrets-outside-env` (medium) without it; the repository's default persona passes, and the owner chose the documented setup.
- **The Console API key**: rejected; evals bill the owner's subscription.

## Decision outcome

Chosen option: **a repository secret**, decided by the owner on 2026-11-15:
- `evals.yml` drops `environment: claude`, fails the job when the token is empty, and fails when `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` or a `CLAUDE_CODE_USE_*` provider variable is set, since each outranks the token (<https://code.claude.com/docs/en/authentication#authentication-precedence>).

### Consequences

- Good, because the setup is the one the docs describe, and a missing token fails loudly.
- Bad, because any workflow in the repository can read the secret by name; no workflow other than `evals.yml` does, which PC-13 checks.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Only `evals.yml` reads the token | `npm run check:consistency -- --offline` (PC-13) | 2026-11-15: exit 0 | After a workflow changes |
| The workflow is valid | `npm run lint:workflows` | 2026-11-15: no findings | After `evals.yml` changes |
