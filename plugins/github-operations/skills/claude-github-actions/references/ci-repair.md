# Repair failing CI on the default branch

Find the workflows that fail, hang or stopped running on the default branch, fix their cause, and land the fix through a pull request. This finds what to repair, not every leftover of the repository's automation: a full sweep of runs, artifacts, caches and runners is a repository audit.

## 1. Find them

1. List the workflows, disabled ones included: `gh workflow list -R <o>/<r> --all --json id,name,state,path`.
2. For each active workflow, read its latest run on the default branch: `gh run list -R <o>/<r> --workflow <id> --branch <default branch> --limit 1 --json databaseId,status,conclusion,createdAt,headSha,url`. Judge it by its state: a run is a failure to repair only when its `status` is `completed` and its `conclusion` is `failure`, `timed_out` or `startup_failure`. `success`, `skipped` and `neutral` are successful conclusions; a `queued` or `in_progress` run is still running; `cancelled` is a separate question, usually a concurrency group or a person, so read why before treating it as a failure; `action_required` waits for approval (SE-10).
3. For each scheduled workflow, check that its latest run is as recent as its schedule says. In a public repository, GitHub disables scheduled workflows after 60 days with no repository activity.
4. For a failing workflow, check what its file references: branches in `on:` filters, secret names in `${{ secrets.NAME }}` that `gh secret list` does not show, files under `paths:`.

## 2. Diagnose each failure

For each failing workflow, read the failed job's log (MCP `get_job_logs` with `failed_only`, or `gh run view <run id> --log-failed`) and record:

1. The failing step and the first real error, not the last line.
2. The root cause, kept apart from hypotheses.
3. Whether the same job fails on the base for the same reason, or started failing at a specific commit.
4. The cause class: code, tests, configuration, infrastructure, permissions, or a rate or budget limit.

## 3. Repair

1. Make the smallest justified change. Never weaken tests or checks, suppress warnings, or broaden permissions without need and the user's approval.
2. Never rerun hoping for green: rerun only with evidence of a transient failure, or after fixing what stopped it.
3. Report a cause outside the repository (an expired secret, a revoked app, a runner) to the user, with the unlock it needs.

## 4. Land the fix

1. Land each cause in its own pull request, through `github-operations:auto-pr-lifecycle`.
2. Re-enable a scheduled workflow GitHub disabled only with the user's approval, after the fix lands: `gh workflow enable <workflow>`.
3. After the merge, confirm the next run on the default branch passes.
