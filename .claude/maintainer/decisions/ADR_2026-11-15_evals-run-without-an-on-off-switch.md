---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Evals run without an on/off switch

## Scope

`.github/workflows/evals.yml`, the `plugin-releases` skill's one-time setup and `.claude/rules/architecture/github.md`.

## Context and problem statement

`evals.yml` ran only when the repository variable `CLAUDE_EVALS` was `enabled`, a switch introduced by the superseded ADR_2026-11-15_evals-ci-gates-on-score-and-delta-with-the-owners-subscription. No official doc defines it: the plugin-evals page (<https://code.claude.com/docs/en/plugin-evals>, Run evals in CI) runs `claude plugin eval` in CI with `--max-cost-usd` as the spend ceiling and no switch. The owner rejected it as an invention.

## Considered options

- **No switch; evals run on every pull request that changes a plugin with a suite**: chosen by the owner.
- **Keep `CLAUDE_EVALS`**: rejected; not in the docs.

## Decision outcome

Chosen option: **no switch**, decided by the owner on 2026-11-15 (commit 38b22f4). Spend stays bounded by `--max-cost-usd` per effort group and by `cancel-in-progress` on newer pushes.

### Consequences

- Good, because the workflow follows the documented recipe and needs no repository variable.
- Bad, because every push to such a pull request bills the owner's subscription.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| No workflow reads `CLAUDE_EVALS` | `grep -rn CLAUDE_EVALS .github` | 2026-11-15: no match | After `evals.yml` changes |
| The workflow is valid | `npm run lint:workflows` | 2026-11-15: no findings | After `evals.yml` changes |
