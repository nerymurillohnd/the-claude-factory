# Repair failing CI on the default branch

Find the workflows that fail, hang or stopped running on the default branch, fix their cause, and land the fix through a pull request.

## 1. Find them

```sh
gh workflow list -R <o>/<r> --all --json id,name,state,path        # includes disabled workflows
gh api repos/<o>/<r>/actions/permissions
```

A filtered run list returns at most 1,000 results. To be complete, split by creation date until each window returns fewer than 1,000:

```sh
gh run list -R <o>/<r> --branch <default branch> --created '<from>..<to>' --limit 1000 --json databaseId,workflowName,event,status,conclusion,createdAt,headSha,url >> runs-default-branch.json
```

Then, per workflow, find the ones whose latest run on the default branch failed and was never followed by a success:

```sh
jq -s 'add | group_by(.workflowName) | map({workflow:.[0].workflowName, last:(sort_by(.createdAt)|last|{at:.createdAt,conclusion:.conclusion,url:.url}), lastSuccess:([.[]|select(.conclusion=="success")]|sort_by(.createdAt)|last|.createdAt)}) | map(select(.last.conclusion!="success"))' runs-default-branch.json
```

Also look for:

- **Scheduled workflows that stopped running**: `schedule` runs (`--event schedule`) whose newest run is older than the schedule says it should be. GitHub disables schedules after a period of repository inactivity: verify the current period in the GitHub docs before stating it.
- **Runs stuck** in `queued`, `waiting` or `in_progress` for more than a day: `gh run list -R <o>/<r> --status queued --limit 1000`, and the same for the others.
- **Workflows that reference things that no longer exist**: branches in `on:` filters, secret names in `${{ secrets.NAME }}` that `gh secret list` does not show, files under `paths:`.

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

1. Land each cause in its own pull request, through this plugin's pull request skill.
2. Re-enable a scheduled workflow GitHub disabled only with the user's approval, after the fix lands: `gh workflow enable <workflow>`.
3. After the merge, confirm the next run on the default branch passes.
