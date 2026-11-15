---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_evals-gate-on-a-per-plugin-delta-floor
superseded-by: none
---

# Eval gates set a plugin's own delta floor and cost cap

## Scope

`.github/eval-gates.json`, the gate block of `.github/workflows/evals.yml` and `.claude/rules/plugins/evals.md`. The threshold, the models, the OAuth credential and the overlay of ADR_2026-11-15_eval-overlays-add-files-to-the-with-plugin-arm-only are unchanged.

## Context and problem statement

ADR_2026-11-15_evals-gate-on-a-per-plugin-delta-floor let `.github/eval-gates.json` raise one plugin's delta floor, and kept USD 10 per effort group for every plugin. hook-engineering's five quality cases run in one effort group, three runs in two arms. The first both-arm smoke run cost USD 0.86 for one case and one run (2026-11-15), so the group is about USD 13: over USD 10, which ends the run as partial and fails the job.

## Decision drivers

- The suite runs at the documented three runs per case, so its mean is stable enough to gate at 0.25.
- Spend stays capped per plugin, and only the owner raises a cap.
- A malformed entry fails the job instead of falling back.

## Considered options

- **A per-plugin object in `.github/eval-gates.json` with `min_mean_delta` and `max_cost_usd`, defaults 0.2 and USD 10**: chosen.
- **Two runs per case to fit USD 10**: rejected by the owner, because two runs give a less stable mean than the three the docs use by default.
- **Keep USD 10 for every plugin**: rejected by the owner, because the job would end partial and fail.

## Decision outcome

Chosen option: **a per-plugin object with both gates**, decided by the owner on 2026-11-15:
- `hook-engineering`: `min_mean_delta` 0.25, `max_cost_usd` 20.
- `evals.yml` reads both before the run, with 0.2 and 10 for a missing plugin or key, and fails the job on a value that is not a number, a floor under 0.2, a cap of 0 or less, or an entry that is not an object.

### Consequences

- Good, because hook-engineering's suite can finish at three runs, and every other plugin keeps the old cap.
- Bad, because a full hook-engineering run can bill up to USD 20 of the owner's usage per push to its pull request.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Both gates read per plugin, with defaults | The workflow's jq program on hook-engineering, a missing plugin, a number, `null`, a floor of 0.1, a `null` cap and a cap of 15 | 2026-11-15: `0.25 20`, `0.2 10`, four errors, `0.2 15` | After the gate block changes |
| The workflow stays valid | `npm run lint:workflows` | 2026-11-15: no findings | After `evals.yml` changes |
| A hook-engineering run finishes inside its cap | The first CI run on its pull request | pending | Each run's cost in the result |
