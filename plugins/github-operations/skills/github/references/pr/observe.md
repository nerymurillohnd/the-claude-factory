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
6. When alert access or any tool was unavailable, the report's **Could not inspect** line names it, never as zero.
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

If the Agent tool is unavailable, or the report lists something it could not inspect (a missing MCP tool because the token lacks a scope or fewer toolsets are on), read that data yourself with the tools and the discipline in `tooling.md`, section `Reads`: current head only, data you could not read is "not inspected" and never zero, and every list read to its end.

What the tracker could not do is yours to finish in the same run. Inspect it, fix what it shows through the repair loop, and observe again. Never carry it forward as a pending item or leave it for later; only a gap you also cannot close after trying both tool layers makes the state `blocked`.
