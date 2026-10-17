# Tracker delegation

How to brief `github-operations:pr-tracker`, what to hold its report to, and how to wait.

## Brief

Invoke the tracker with:

- Repository and PR number or URL.
- Freshly confirmed head SHA.
- Base branch.
- Previous tracker report or a concise findings ledger.
- Changes made since the last report.
- Known blockers and relevant access limitations.
- A bounded monitoring time budget, when appropriate.

The tracker's own report format covers CI failures, reviews and findings, warnings and deprecations, Dependabot, run comparisons and optimizations. Do not restate it in the brief.

## Hold the report to these points

- A review, a comment, a thread and an actionable finding are different units. Do not present one count as another.
- Root failures are separated from downstream skips and cancellations, and current-head failures from older runs.
- Every cause is labeled confirmed, likely or uncertain, with a minimal fix and a verification step.
- A component is not called outdated or unsupported without evidence, and not every warning is a merge blocker.
- When alert access is unavailable, the report states incomplete coverage, not zero alerts.
- Optional optimizations stay separate from required fixes, and the rationale is concise and evidence-backed, not a transcript of reasoning.

When the report lists a coverage gap because an MCP tool was missing (fewer toolsets than the plugin turns on, or a token without the scope), read that data yourself with the `gh` form before you classify.

## Classify the report

Map the tracker's status to a lifecycle state from `SKILL.md`: `ACTION_REQUIRED` to `actionable`, `PENDING` to `pending` (or `timeout` when the budget ended with nothing changing), `BLOCKED` to `blocked`, `READY_FOR_MAIN_SESSION` to `ready` only after you verify readiness yourself, `MERGED_OR_CLOSED` to a terminal outcome after you confirm it on GitHub. Classify warnings, security alerts and optimization suggestions separately from merge blockers. An existing unrelated alert does not make this PR responsible for remediation. Do not declare readiness when a verification gap prevents evaluating a required gate.

## Keep monitoring to a terminal decision

Continue the observe, diagnose, repair, validate, push loop until the PR is ready for approval, a genuine blocker needs the user, a monitoring timeout must be escalated, or the PR is externally merged or closed.

- While checks are pending and nothing is actionable, allow bounded monitoring instead of interrupting the user.
- Pass the previous report into every later tracker invocation so findings can be compared. The tracker has no memory of its own.
- Do not run overlapping cycles against the same head, and do not leave an obsolete tracker running once a new head supersedes its work.
- Do not send routine messages such as "still waiting" or "fixed one issue, continuing". Surface actionable blockers and terminal outcomes.
