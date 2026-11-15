---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_eval-gates-set-a-plugins-delta-floor-and-cost-cap
superseded-by: none
---

# Eval gates add concurrency and a job timeout sized to the largest group

## Scope

`.github/eval-gates.json`, the eval job of `.github/workflows/evals.yml` and `.claude/rules/plugins/evals.md`. The delta floor (default 0.2, hook-engineering 0.25) and the cost cap (default USD 10, hook-engineering USD 20) stay as ADR_2026-11-15_eval-gates-set-a-plugins-delta-floor-and-cost-cap set them.

## Context and problem statement

The evals audit of 2026-11-15 (`.claude/maintainer/audits/2026-11-15-evals-docs-audit.md`, item 1) found the eval job capped at 60 minutes and running one run at a time, the documented default of `--concurrency`. hook-engineering's effort-high group is 5 cases × 3 runs × 2 arms, 30 runs of up to 2400 s each, so CI would stop it with exit 143 after spending. The docs (<https://code.claude.com/docs/en/plugin-evals>, Command options) give `-j, --concurrency <n>`, 1 to 8, sharing the account's rate limit.

## Decision drivers

- A group must finish inside the job before it bills the owner.
- Concurrency shares one rate limit, so a plugin may need fewer at a time.

## Considered options

- **`--concurrency` per plugin in `.github/eval-gates.json` (1 to 8, default 4) and `timeout-minutes: 240`**: chosen.
- **Shard each group with `--case`**: rejected for now; more jobs to read for the same suite.
- **Lower each case's `timeout_seconds`**: rejected; the docs say to set run limits generously and cap cost with `--max-cost-usd` instead.

## Decision outcome

Chosen option: **per-plugin concurrency and a sized timeout**, as part of the owner's instruction on 2026-11-15 to fix every finding of the audit:
- `evals.yml` reads `concurrency` beside `min_mean_delta` and `max_cost_usd`, defaults to 4, and fails the job on a value that is not an integer from 1 to 8.
- The eval job's `timeout-minutes` is 240; GitHub's ceiling is 360.

### Consequences

- Good, because hook-engineering's largest group fits: 30 runs ÷ 4 at a time is 8 waves.
- Bad, because 4 parallel runs on one subscription can hit its rate limit; a run that ends on an API error scores 0 and fails the job, and the plugin's `concurrency` then goes down.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The workflow is valid | `npm run lint:workflows` | 2026-11-15: no findings | After `evals.yml` changes |
| A group finishes inside the job | The first CI run of hook-engineering's suite | pending | Each run's `durationSeconds` |
