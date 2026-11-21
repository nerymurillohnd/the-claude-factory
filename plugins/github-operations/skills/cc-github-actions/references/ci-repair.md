# Repair failing CI on the default branch

Find the workflows that fail, hang or stopped running on the default branch, fix their cause, and land the fix through a pull request. This finds what to repair, not every leftover of the repository's automation: a full sweep of runs, artifacts, caches and runners is a repository audit.

## 1. Find them

1. List the workflows, disabled ones included: `gh workflow list -R <o>/<r> --all --json id,name,state,path`. A workflow's `state` never shows that its file is invalid: find those from their runs, which have zero jobs and conclusion `failure`, or conclusion `startup_failure` (`gh run view` then prints "This run likely failed because of a workflow file issue."). GitHub creates such a failed run for every commit while the file stays invalid, and a file over the workflow file size limit on GitHub's [Actions limits](https://docs.github.com/en/actions/reference/limits) page starts no runs at all (W-12 in [workflow-audit.md](workflow-audit.md#checks-every-workflow-gets)).
2. For each active workflow, read its latest run on the default branch: `gh run list -R <o>/<r> --workflow <id> --branch <default branch> --limit 1 --json databaseId,status,conclusion,createdAt,startedAt,headSha,url`. Judge it by its state: a run is a failure to repair only when its `status` is `completed` and its `conclusion` is `failure`, `timed_out` or `startup_failure`. `success`, `skipped` and `neutral` are successful conclusions; `cancelled` is a separate question, usually a concurrency group or a person, so read why before treating it as a failure; `action_required` waits for approval (SE-10); `stale` is not a pass, since GitHub sets it on a check run left incomplete too long: report it as a run that never finished. An empty list, `[]`, means the workflow has no run on that branch: say so and check its triggers, never report it as passing.
3. A `queued` or `in_progress` run is still running only while it is within its limits; past them it hangs, and a hang is repaired like a failure. `gh` prints no log for a run or job still in progress, so read its jobs with `gh run view <run id> -R <o>/<r> --json jobs`, and each job's `timeout-minutes` from the workflow file at the run's `headSha`:
   - A job `in_progress` since its `startedAt` for longer than its `timeout-minutes` (360 when unset), or than its runner's job execution limit, read on GitHub's [Actions limits](https://docs.github.com/en/actions/reference/limits) page and, for single-CPU runners, its [runner table](https://docs.github.com/en/actions/reference/runners/github-hosted-runners#single-cpu-runners), hangs: GitHub documents that it cancels or fails a job at those limits.
   - A job that has sat `queued` on a self-hosted runner past the self-hosted queue limit on the Actions limits page hangs. GitHub's limits page says such a job is cancelled and its self-hosted reference says it fails: accept either conclusion. GitHub documents no queue limit for GitHub-hosted runners: report a long queue there with its age and the label it waits for, and check the label against GitHub's current runner table, because a label that doesn't exist or an image GitHub retired (W-10) waits with no runner to take it.
   - A run older than the workflow run time limit on that page hangs: GitHub cancels it at that age, waiting and approval included.
   - Diagnose a hung job from its `steps` in that output, where the step it hangs on is the one still `in_progress`, and a queued job from the runner label it waits for.
4. For each scheduled workflow, check that its latest run is as recent as its schedule says. In a public repository, GitHub disables scheduled workflows after the period of no repository activity that its [Disabling a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows#disabling-a-workflow) section gives.
5. For a failing workflow, check what its file references: branches in `on:` filters; files under `paths:`; `runs-on` labels; and secret names in `${{ secrets.NAME }}`, at every level the job can read them from: `gh secret list` for the repository, `--env <environment>` for each environment the job uses, `--org <org>` when readable, and `--app dependabot` for runs Dependabot starts. A name missing at every readable level is missing; one you couldn't read a level for is unverified.

## 2. Diagnose each failure

For each failing workflow, read the failed job's log (MCP `get_job_logs` with `failed_only`, or `gh run view <run id> --log-failed`). An empty log means the log couldn't be read, for example because it expired: record the job as not inspected, never as having no error. Otherwise record:

1. The failing step and the first real error, not the last line.
2. The root cause, kept apart from hypotheses.
3. Whether the same job fails on the base for the same reason, or started failing at a specific commit.
4. The cause class: code, tests, configuration, infrastructure, permissions, or a rate or budget limit.

A job that fails with `lockfile missing pin for <action>@<ref>`, at a `uses:` step or at a `./` action that uses other actions, is a workflow the lockfile lists whose entry is missing: a configuration cause. Fix it by regenerating the lockfile as the [Pinning policy](version-drift.md#pinning-policy) says, never by deleting `actions.lock` or removing the workflow from it, which would drop the locked commits already reviewed. When the failing step is a `./` action, regenerating alone fails with a `local-action` error: the fix is `$/` through `gh actions-lock --migrate-local-actions`, with the user's approval because it rewrites `./` references across the repository; on GitHub Enterprise Server, where `$/` doesn't exist, report it with that limit.

## 3. Repair

1. Make the smallest justified change. Never weaken tests or checks or suppress warnings. Broaden a permission only when the job needs it, and only with the user's approval; never to get a green run.
2. Never rerun hoping for green: rerun only as the rerun rule in SKILL.md's Gotchas says.
3. Report a cause outside the repository (an expired secret, a revoked app, a runner) to the user, with the unlock it needs.

## 4. Land the fix

1. Land each cause in its own pull request, through `github-operations:auto-pr-lifecycle`, only after its workflow patch passed [Validate the patches](workflow-audit.md#validate-the-patches) and the user approved it.
2. Re-enable a scheduled workflow GitHub disabled only with the user's approval, after the fix lands: `gh workflow enable <workflow>`.
3. After the merge, read the next run of that workflow on the default branch. When it passes, record it as passed in the report's Validation table. When it fails, go back to section 2 with its log; when it fails again for the same cause, stop and report both runs and what would unlock the fix. When it hasn't started by the end of the session, for a schedule or a path filter, record it as "not run" with the reason and when it is due, and list "confirm the next run" under "Left for you".
