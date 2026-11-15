---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Evals in CI gate on score and delta, capped per effort group, on the owner's subscription

## Scope

`.github/workflows/evals.yml`, `.github/evals.json`, `scripts/checkers/eval_gate.py` (`npm run evals:gate`), the `evals` toolchain of `.github/actions/setup`, the eval cases' model pins and effort tags, and `.claude/rules/plugins/evals.md`.

## Context and problem statement

`.claude/rules/plugins/evals.md` required a plugin's suite to run in CI the first time and then on pull requests that change the plugin, but no workflow did. The rule set no pass bar, cost cap or credential. None of the 12 cases pinned the model or carried an effort tag.

## Decision drivers

- Every case and judge call bills the owner, so spend has a ceiling.
- Fail when the plugin stops helping, not only when a case scores low.
- Run cases on Sonnet 5.5 and judge with Opus 5.5.

## Considered options

- **Threshold 0.8, plus a mean delta of at least 0.2 from both arms**: chosen.
- **Threshold 0.8 only**: rejected, because it misses a plugin that no longer helps.
- **The CLI's default threshold of 1.0**: rejected, because model noise would fail it.

## Decision outcome

Chosen option: **score plus delta, USD 10 per effort group, OAuth only**:
- **What runs:** each changed plugin's suite on its pull requests, or one plugin through `workflow_dispatch`; each effort group runs on its own and an empty group is skipped.
- **Command:** `--model claude-sonnet-5-5 --judge-model claude-opus-5-5 --threshold 0.8 --max-cost-usd 10`, then `evals:gate` at a 0.2 mean delta.
- **Credential:** `CLAUDE_CODE_OAUTH_TOKEN` from the `claude` environment. The job fails if `ANTHROPIC_API_KEY` is set.
- **Gate:** `vars.CLAUDE_EVALS == 'enabled'`.
- **Gate script:** rebuilt in maintainer scope rather than calling plugin-engineering's `gate_eval_result.py`, so CI depends on no plugin file.
- **Effort tags:** Claude chose them, as the owner delegated: the 8 plugin-engineering trigger cases are `effort-low`, three project-maintainer record cases `effort-medium`, and the handoff case `effort-high`.

### Consequences

- Good, because spend stops at USD 10 per group, and a partial run fails the job instead of passing.
- Bad, because each case runs twice, with and without the plugin, to produce the delta.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Every case loads | `claude plugin eval plugins/<p> --tag effort-<level> --max-cost-usd 0` with no credential | 2026-11-15: 0 load failures | After a case changes |
| The gate's exit codes | `npm run test:scripts` (7 cases) | 2026-11-15: pass | Every change to the gate |
| A suite runs and gates in CI | The first dispatch with the token and variable set | pending | After the owner's setup |

## More information

- Decided by the owner on 2026-11-15: the pass bar, the cap, the OAuth token only, Sonnet cases with an Opus judge, and the effort tags left to Claude.
