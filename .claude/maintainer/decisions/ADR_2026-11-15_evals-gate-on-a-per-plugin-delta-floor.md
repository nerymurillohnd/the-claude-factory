---
status: superseded
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_evals-ci-gates-on-score-and-delta-with-the-owners-subscription
superseded-by: ADR_2026-11-15_eval-gates-set-a-plugins-delta-floor-and-cost-cap
---

# Evals gate on a per-plugin delta floor, never below 0.2

## Scope

`.github/workflows/evals.yml`, the new `.github/eval-gates.json`, `.github/evals.json` and `.claude/rules/plugins/evals.md`. The threshold, the USD 10 cap per effort group, the models and the OAuth credential stay as ADR_2026-11-15_evals-ci-gates-on-score-and-delta-with-the-owners-subscription set them.

## Context and problem statement

The owner set a mean gain of at least 25 points over no plugin as the target for hook-engineering's `writing-hooks` suite, enforced with the gate of plugin-engineering's `plugin-testing-and-debugging` skill (`scripts/gate_eval_result.py --min-mean-delta 0.25`). `evals.yml` gated every plugin at a fixed 0.2, so a hook-engineering suite between 0.2 and 0.25 would pass CI below the owner's target.

## Decision drivers

- Enforce each plugin's target where its suite runs, in CI.
- Keep the repository-wide 0.2 as the floor no plugin goes under.
- Keep `.github/evals.json` a plain list of eval flags, which its jq step requires.
- Fail closed on a bad entry, as the flags step already does.

## Considered options

- **A per-plugin floor in `.github/eval-gates.json`, read by `evals.yml`, default 0.2, at least 0.2**: chosen.
- **Keep 0.2 for every plugin and check 0.25 by hand**: rejected, because CI would pass a suite below the target.
- **Put the floor in `.github/evals.json`**: rejected, because that file maps a plugin to the flag list passed to `claude plugin eval`, and its step fails on anything that is not a list.
- **Call plugin-engineering's `gate_eval_result.py` from CI**: rejected, for the reason the superseded ADR gives: CI depends on no plugin file. `scripts/checkers/eval_gate.py` applies the same delta rule.

## Decision outcome

Chosen option: **a per-plugin floor in `.github/eval-gates.json`**, because it enforces each plugin's own target in CI without changing the flag file, and it can only raise the bar:
- `evals.yml` reads `.[plugin] // 0.2` and fails the job unless the value is a number of at least 0.2.
- `hook-engineering` is set to 0.25.
- Each effort group still gates on its own, so every group of the suite must reach the floor, which is at least as strict as a mean across the whole suite.
- Decided by the owner (the 25-point target and the gate script); the mechanism was Claude's, which the owner delegated as a technical choice on 2026-11-15.

### Consequences

- Good, because a plugin's stricter target holds in CI and a typo can't lower any plugin below 0.2.
- Bad, because a group with one case, such as hook-engineering's `effort-medium` group, gates that one case at 0.25, which is noisier than a suite-wide mean.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The floor is read per plugin | `jq` on `.github/eval-gates.json` for hook-engineering and plugin-engineering | 2026-11-15: 0.25 and 0.2 | After the file changes |
| A `null`, `false` or below-0.2 entry fails the job instead of falling back to 0.2 | `jq` with `if has($p) then .[$p] else 0.2 end` on each value (the code review found `// 0.2` fell back on `null` and `false`) | 2026-11-15: 0.25 passes, a missing entry gives 0.2, `null`, `false` and 0.1 error | After the filter changes |
| The workflow is valid | `npm run lint:workflows` (actionlint, zizmor) | 2026-11-15: no findings | After `evals.yml` changes |
| A hook-engineering suite gates at 0.25 in CI | The first run with the token and the variable set | pending | After the owner's setup |
