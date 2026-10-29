# Repair failing CI on the default branch

Find the workflows that fail, hang or stopped running on the default branch, fix their cause, and land the fix through a PR.

## 1. Find them

Run the commands in `audit/github.md`, section "Actions": the workflow list with disabled workflows, the run list for the default branch split until each window is complete, the latest-run-not-success query, stuck runs, scheduled workflows that stopped, and workflows that reference missing branches, secrets or paths.

## 2. Diagnose each failure

For each failing workflow, read the failed job's log (MCP `get_job_logs` with `failed_only`, or `gh run view <run id> --log-failed`) and record:

1. The failing step and the first real error, not the last line.
2. The root cause, kept apart from hypotheses.
3. Whether the same job fails on the base for the same reason, or started failing at a specific commit.
4. The cause class: code, tests, configuration, infrastructure or permissions.

## 3. Repair

1. Apply `pr/repair.md` "Repair each finding": the smallest justified change, no weakened tests or checks, no suppressed warnings, no broadened permissions without need and approval.
2. Never rerun hoping for green; rerun only with evidence of a transient failure, or after fixing what stopped it.
3. A cause outside the repository (an expired secret, a revoked app, a runner) is reported to the user with the unlock it needs.

## 4. Land the fix

1. Continue at `pr/start.md` with one PR per cause.
2. A scheduled workflow GitHub disabled is re-enabled only with the user's approval, after the fix lands: `gh workflow enable <workflow>`.
3. After the merge, confirm the next run on the default branch passes.
