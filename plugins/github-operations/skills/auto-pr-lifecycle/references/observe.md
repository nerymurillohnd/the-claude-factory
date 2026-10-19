# Observe the PR through the tracker

The `github-operations:pr-tracker` agent observes. It reads one PR, diagnoses it and reports; it never changes anything. The main session (you) acts on the report. The agent carries the full inspection procedure in its own instructions (snapshot, checks and jobs, diagnosis, reviews, warnings, Dependabot, comparison with the previous report), so do not repeat that procedure in the brief. This reference covers what is yours: when to launch it, what to give it, how to hold its report to account, how to turn its status into a lifecycle state, how to wait, and how to read GitHub yourself when it cannot.

## 1. Launch the tracker

Launch it after the PR exists and after every push, with the Agent tool and `subagent_type` set to `github-operations:pr-tracker`. Launch it in the background when you have housekeeping to do meanwhile (updating the lifecycle record, answering review threads that need no new observation); wait for its report when you have nothing else to do. Never run two trackers against the same head, and do not leave one running after a new head supersedes its work.

Give it, in the prompt:

1. Repository as `owner/repo` and the PR number or URL.
2. The freshly confirmed head SHA and the base branch.
3. The previous tracker report, or a concise ledger of known findings. The agent keeps no memory between runs.
4. What changed since the last report.
5. Known blockers and access limits.

## 2. Hold the report to these points

Before you trust a report, check it against this list. If a point fails, read that data yourself (section 5) or send the tracker back with the specific gap.

1. Its head SHA equals the head you gave it. A mismatch means someone else pushed: observe again against the new head.
2. A review, a comment, a thread and an actionable finding are different units, and the counts say how they were counted.
3. Root failures are separate from downstream skips and cancellations, and current-head failures from older runs.
4. Every cause is labeled confirmed, likely or uncertain, with a minimal fix and a way to verify it.
5. No component is called outdated or unsupported without evidence, and not every warning is treated as a merge blocker.
6. When alert access or any tool was unavailable, the report says incomplete coverage, never zero.
7. Optimizations are kept apart from required fixes.

## 3. Turn its status into a lifecycle state

| Tracker status | Lifecycle state | Your rule |
| :-- | :-- | :-- |
| `ACTION_REQUIRED` | `actionable` | Go to the repair loop. |
| `PENDING` | `pending` | Wait as section 4 says; `timeout` when the bound ends with nothing changed. |
| `BLOCKED` | `blocked` | Name who must act. If every outside blocker is a check the report marks as not required, decide readiness yourself against the required gates and the user's rules, and list the failure in the approval request. |
| `READY_FOR_MAIN_SESSION` | `ready` | Only after you verify readiness yourself with the merge protocol. The status is a recommendation, and a material verification gap means not ready. |
| `MERGED_OR_CLOSED` | a final outcome | Only after you confirm it on GitHub. |

Classify warnings, security alerts and optimizations separately from merge blockers. An existing unrelated alert does not make this PR responsible for remediation.

## 4. Wait for pending checks

The tracker cannot wait; it returns `PENDING`. You wait, then launch it again. Wait until something changes, for at most 30 minutes in one stretch unless the user set another limit.

1. With `gh`: start its PR checks watcher in the background with fail-fast, a 30-second interval and a 30-minute timeout, and carry on only when it exits and you are notified. Then launch the tracker again. The only documented exit status is 8, "checks pending"; decide from the report, not from the exit status.
2. Without `gh`: relaunch the tracker no more often than once a minute, and only when the report gave you a reason to expect a change.
3. Reviews and required approvals arrive without a check changing. When the checks are done and only a human approval is missing, report `pending` and name who must act instead of waiting for a human.
4. When the bound ends without a terminal state, the state is `timeout`: report what is still pending and ask whether to keep waiting. Never wait without a bound.

Do not send routine messages such as "still waiting" or "fixed one issue, continuing". Surface actionable blockers and terminal outcomes only.

## 5. When the tracker cannot run, or left a gap

If the Agent tool is unavailable, or the report lists a coverage gap (a missing MCP tool because the token lacks a scope or fewer toolsets are on), read that data yourself, with the same discipline: current head only, data you could not read is "not inspected" and never zero, and every list read to its end. Use the MCP form first and `gh` as the fallback, in both directions. Check a `gh` command's help for exact options before first use.

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
