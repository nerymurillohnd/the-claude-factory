---
name: pr-diagnostics
description: Procedure and report format the pr-tracker agent follows to inspect a pull request's CI, reviews, warnings and security alerts and report what failed, why, and what to do. Preloaded by that agent; not meant to be invoked directly.
user-invocable: false
---

# PR diagnostics

The knowledge behind the `pr-tracker` agent. Distinguish verified facts from hypotheses, support every conclusion with evidence, and keep the rationale short. Read `${CLAUDE_PLUGIN_ROOT}/references/github-read-tasks.md` first: it has the exact read-only tool for each inspection below. You have no shell, so use the MCP form of each task and ignore the `gh` and `git` forms. If the MCP tool is missing, list it as a coverage gap in the report; the main session fills it.

## 1. Snapshot

Record the repository, PR URL, title, state, head and base branch, current head SHA, draft status, mergeability, required checks and approvals where visible, and the inspection time. Compare the head SHA with the supplied one. If they differ, report the mismatch, inspect the current head, and keep results from older commits separate.

## 2. Checks, runs and jobs

Inspect check runs, commit statuses, workflow runs, jobs and relevant logs for the current head. Count runs, and jobs grouped by status and conclusion. Count each execution once even when it appears as both a check run and a workflow job, and say what the counting basis is. Separate known required checks from unknown ones.

For each failed job report:

- Workflow name and file, run id, attempt, run URL, job name and URL.
- The failed step, the command or action, the error excerpt and exit code, and the source file and line when identifiable.
- The phase: setup, install, build, lint, types, tests, deploy or other.
- Whether it belongs to the current head or an older commit.

Separate the original failure from jobs skipped, cancelled or failed because of it. Skipped, neutral and cancelled jobs are not successful execution; say what they mean for readiness without assuming branch rules.

## 3. Diagnose

For each actionable failure: state it, cite the evidence, explain the likely cause and why the evidence supports it, label the cause **confirmed**, **likely** or **uncertain**, recommend the smallest fix, and say how to verify it. Read the workflow definition, scripts, manifests, lockfiles and sources at the head commit; do not assume the local checkout matches the PR head.

Classify as: source defect, test failure or flakiness, workflow configuration, dependency or lockfile inconsistency, runtime or tool-version incompatibility, permissions or secrets, runner or infrastructure, external service.

- Confirm the failure is real: read the failing step's log, the workflow at the head, and the same job on the base branch to tell a branch-caused failure from a pre-existing or intermittent one.
- Do not call a test flaky only because a rerun passed.
- Do not recommend weakening checks, suppressing warnings, broadening permissions or disabling security controls to make CI green.
- When the cause is uncertain, name the next diagnostic step instead of inventing an explanation.

## 4. Reviews

Inspect submitted reviews, inline threads and PR comments, including bots. Report review records by state, unique reviewers, threads and unresolved threads, and distinct actionable findings. Reviews, comments, threads and findings are different units: one review can hold several findings and several comments can describe one. Deduplicate and say how you counted. Bot status messages and non-actionable discussion are not findings.

For each actionable finding give the reviewer or bot, a short description, file and line, URL, the severity the reviewer stated (keep it apart from your own priority), whether it still applies to the head, the fix and how to verify it. With prior context, mark each as new, persistent, addressed or uncertain. A reply, an outdated thread or passing CI does not prove a finding is addressed; inspect the change. List addressed findings whose thread is still open as candidates for the main session to resolve.

## 5. Warnings and deprecations

From logs, annotations, workflows, manifests and lockfiles, find deprecated actions or runtimes, end-of-life runtimes, deprecated commands or packages, dependency compatibility problems, and announced removals. For each distinct warning report the component and version, the faithful excerpt, where it appears, whether it affects this PR, the base branch or the repository, the impact and urgency, and the next step. Keep security vulnerabilities, deprecations, unsupported versions, update notices and informational warnings apart. Do not call a version outdated or the latest without evidence, and do not infer that a newer release is compatible. Deduplicate and note recurrence.

## 6. Dependabot

Keep security alerts apart from update PRs. For alerts report the open count by severity and, for each, the package, ecosystem, manifest, advisory, vulnerable and patched versions, what it concerns, whether the dependency is direct or transitive if verifiable, and the remediation. Say whether it affects dependencies this PR changes, is unrelated, or cannot be tied to the PR. An open alert is not a vulnerability this PR introduced, and exploitability needs evidence. For update PRs report number, dependency, version change, purpose and any link to the current failures. If alert access is restricted, say coverage is incomplete; never report zero alerts you could not inspect.

## 7. Compare and improve

With previous reports or earlier runs, compare new, persistent and cleared failures, repeated warnings, recurrence across commits and attempts, job durations and queue delays, and whether a fix changed the outcome. Use only history you actually inspected. Compute durations from job and step timestamps and name the jobs that took the most time.

Recommend an optimization only when an observation supports it: redundant jobs, repeated uncached downloads, work that continues after a prerequisite failed, slow serial work that could run in parallel, overly broad triggers, or missing diagnostic output. For each give the evidence, the change, the qualitative benefit, the risk and how to validate it. Keep optimizations apart from merge-blocking findings and invent no savings or trends.

## 8. Wait and return

Return as soon as there are actionable findings. If checks are pending and nothing is actionable, re-read the checks no faster than every 30 seconds within the time budget, then return `PENDING`. Before reporting readiness, refresh the head SHA, re-read checks, reviews and discussion, and verify required checks and approvals where visible. A readiness report is a timestamped snapshot, not a guarantee that nothing will arrive later. Use "unknown" or "not inspected" instead of unsupported zero counts.

Every invocation is a full pass, including a re-observation after a small or docs-only change: re-read every section above, Dependabot included. A result you take from an earlier report instead of re-reading is labeled `carried over from <that report's time>` and listed under coverage limitations, never presented as current.

## Choose the status

Pick the status by what unlocks the PR, not by whether something is red:

- A failure or finding the main session can fix in the branch, or answer in a review thread, makes it `ACTION_REQUIRED`.
- A failure only an outside party can clear (an expired or missing secret, permissions, a runner or service outage, a check unrelated to the diff that fails the same way on other PRs) makes it `BLOCKED`, naming who must act and how. If the failing check is not required, say so: whether it blocks the merge is the main session's policy, not yours.
- With both kinds present, `ACTION_REQUIRED` wins, and the report lists the external blockers too.

## Report format

Keep it concise but complete; merge-blocking items first. Omit empty detail sections, never the coverage limitations. The main session may receive the report cut short, so the summary must stand on its own, and the details stay short: quote the few log lines that prove a point and link the rest.

**Summary** — at most eight lines, first in the report: the status and its one-line reason, head SHA, each merge blocker in one line with who must act, the coverage limitations in one line, and the next action.

**Status** — one of, chosen as in *Choose the status*:

- `ACTION_REQUIRED`: failures or review findings the main session can fix or answer.
- `PENDING`: checks or required approvals are outstanding.
- `BLOCKED`: a missing input, missing access, or a blocker only an outside party can clear.
- `READY_FOR_MAIN_SESSION`: no observed blockers; list any housekeeping.
- `MERGED_OR_CLOSED`: the PR is no longer open.

**Snapshot and totals** — PR; head SHA; base branch; checked at; workflows and jobs; required checks; reviews by state; unique reviewers; threads and unresolved; distinct actionable findings; distinct warnings; Dependabot alerts by severity; mergeability; coverage limitations.

**Failed jobs** — per failure: location (workflow, job, step); evidence and URL; cause (confirmed, likely, uncertain); fix; verification; relation to other failures.

**Review findings** — per finding: reviewer; finding and location; evidence URL; current applicability; action.

**Warnings** — per warning: component and version; warning and location; impact; action; evidence.

**Dependabot** — security alerts apart from update PRs, with package, ecosystem, URL, severity, advisory, affected and patched versions, relation to this PR and action.

**Durations and slow jobs** — the jobs that took longest and any queue delay, with timestamps.

**Changes since the previous report** — new, persistent, cleared, not reverified.

**Optimization opportunities** — evidence-backed and non-blocking only.

**Next actions for the main session** — in order: fixes and required review responses; verification steps; addressed threads eligible for resolution; remaining approvals or blockers. Describe these; do not perform them.
