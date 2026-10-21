# Observe the PR through the tracker

The `github-operations:pr-tracker` agent observes. It reads one PR, diagnoses it and reports; it never changes anything. The main session (you) acts on the report. The agent carries the full inspection in its own instructions (workflows, jobs, runners, failures and their root cause, required checks, warnings, reviews, the diff, Dependabot, comparison with the previous report) and waits for the head's jobs to finish, so do not repeat any of that in the brief. This reference covers what is yours: when to launch it, what to give it, how to hold its report to account, how to turn its status into a lifecycle state, what to do after its wait, and how to read GitHub yourself when it cannot.

## 1. Launch the tracker

Launch it after the PR exists and after every push, with the Agent tool and `subagent_type` set to `github-operations:pr-tracker`. Launch it in the background when you have housekeeping to do meanwhile (updating the lifecycle record, answering review threads that need no new observation); wait for its report when you have nothing else to do. Never run two trackers against the same head, and do not leave one running after a new head supersedes its work.

Give it, in the prompt:

1. Repository as `owner/repo` and the PR number or URL.
2. The freshly confirmed head SHA and the base branch.
3. The previous tracker report, or a concise ledger of known findings. The agent keeps no memory between runs.
4. What changed since the last report.
5. Known blockers and access limits.
6. The wait limit, when the user set one other than 30 minutes.

## 2. Hold the report to these points

Before you trust a report, check it against this list. If a point fails, read that data yourself (section 5) or send the tracker back with the specific gap.

1. Its head SHA equals the head you gave it. A mismatch means someone else pushed: observe again against the new head.
2. A review, a comment, a thread and an actionable finding are different units, and the counts say how they were counted.
3. Root failures are separate from downstream skips and cancellations, and current-head failures from older runs.
4. Every cause has its class (code, tests, configuration, infrastructure or permissions), keeps facts apart from hypotheses, and says whether the same job fails on the base branch.
5. No component is called outdated or unsupported without evidence, and not every warning is treated as a merge blocker.
6. When alert access or any tool was unavailable, the report says incomplete coverage, never zero.
7. Optimizations are kept apart from required fixes.

## 3. Turn its status into a lifecycle state

| Tracker status | Lifecycle state | Your rule |
| :-- | :-- | :-- |
| `ACTION_REQUIRED` | `actionable` | Go to the repair loop. |
| `PENDING` | `pending`, or `timeout` | Section 4 says which. |
| `BLOCKED` | `blocked` | Name who must act. If every outside blocker is a check the report marks as not required, decide readiness yourself against the required gates and the user's rules, and list the failure in the approval request. |
| `READY_FOR_MAIN_SESSION` | `ready` | Only after you verify readiness yourself with the merge protocol. The status is a recommendation, and a material verification gap means not ready. |
| `MERGED_OR_CLOSED` | a final outcome | Only after you confirm it on GitHub. |

Classify warnings, security alerts and optimizations separately from merge blockers. An existing unrelated alert does not make this PR responsible for remediation.

## 4. After the tracker's wait

The tracker waits for the head's jobs to finish, for at most 30 minutes or the limit you gave it, and then reports. Do not wait yourself while it runs; act on its report when it arrives.

1. `PENDING` with jobs still running: the state is `timeout`. Report what is still running and ask whether to keep waiting; if the user says yes, launch the tracker again. Never wait without a bound.
2. `PENDING` because only a person's review or approval is missing: the state is `pending`. Report who must act instead of waiting for a human.

Do not send routine messages such as "still waiting" or "fixed one issue, continuing". Surface actionable blockers and terminal outcomes only.

## 5. When the tracker cannot run, or left a gap

If the Agent tool is unavailable, or the report lists something it could not inspect (a missing MCP tool because the token lacks a scope or fewer toolsets are on), read that data yourself, with the same discipline: current head only, data you could not read is "not inspected" and never zero, and every list read to its end. Use the MCP form first and `gh` as the fallback, in both directions. Check a `gh` command's help for exact options before first use.

| Fact | MCP | gh |
| :-- | :-- | :-- |
| PR snapshot | `pull_request_read`, method `get` | PR view with JSON fields for head SHA, state, draft, mergeable, merge state, base and head branch, review decision |
| Checks on the head | `pull_request_read`, methods `get_check_runs` and `get_status` | PR checks with JSON output (each check has a `bucket`: pass, fail, pending, skipping, cancel); it can be limited to required checks |
| Workflow runs for the head | `actions_list`, method `list_workflow_runs` with `workflow_runs_filter.branch`; keep the runs whose `head_sha` is the head | Run list filtered by commit |
| Jobs | `actions_list`, method `list_workflow_jobs`, `resource_id` = run id, `workflow_jobs_filter.filter` = `latest` | Run view with the jobs JSON field |
| Failure logs | `get_job_logs` with `run_id`, `failed_only`, `return_content`, `tail_lines` | Run view, failed logs |
| Reviews and threads | `pull_request_read`, methods `get_reviews`, `get_review_comments`, `get_comments` | PR view with reviews and comments; threads through a read-only GraphQL query on review threads |
| Dependabot | `list_dependabot_alerts`, `get_dependabot_alert` | The REST alerts endpoint through `gh api`; a PR list filtered to the Dependabot app |
| Required checks | `repository_ruleset_read`, level `repository`, method `get_rules_for_branch` | The ruleset check for the branch; classic protection through `gh api` on the branch's protection endpoint |

Never treat the combined commit status as proof that checks pass (a `pending` combined status with zero statuses means the head has no commit statuses), never run a GraphQL mutation while observing, and never report zero alerts when the call returned 403 or 404.
