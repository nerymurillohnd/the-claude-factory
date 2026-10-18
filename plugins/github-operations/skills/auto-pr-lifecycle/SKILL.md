---
name: auto-pr-lifecycle
description: Use when asked to open a PR, review or check a PR through to completion, ship or land a change, get a PR merged, babysit a PR, or drive CI failures and review feedback to resolution. Runs branch, validate, commit, push and PR, then a monitor-and-repair loop through the pr-tracker agent, and merges only after explicit approval for the exact head SHA. Then cleans up branches and syncs the base.
compatibility: Needs the GitHub MCP server (bundled with this plugin), local git, an authenticated gh CLI for operations MCP lacks, and the Agent tool to run github-operations:pr-tracker. In the Claude app the tracker runs only in Cowork sessions.
---

# Automatic PR Lifecycle

Own the PR from its starting point to merge, not just to the push. The main session acts and mutates. The tracker `github-operations:pr-tracker` observes and diagnoses, read-only. Run the loop without routine check-ins; the one human gate is the merge approval.

## Lifecycle

```text
Scope → Prepare → Validate → Commit → Push → Create/Find PR
  → Delegate observation → Evaluate report → Repair → Commit/Push
  → Delegate observation again … until ready
  → Verify readiness → Request approval → Land → Observe landing
  → Clean up and sync → Report
```

Each repository and PR is an independent lifecycle unit. Resume from the phase the PR is actually in; do not repeat completed work. If the repository or PR is ambiguous, ask before mutating anything.

Read the reference for the step you are on:

- Read [phases.md](references/phases.md) in full before the first run in a repository, and use it afterward for the GitHub MCP tool behind each phase.
- Read [tracker-delegation.md](references/tracker-delegation.md) when you brief the tracker, read its report, or wait on pending checks.
- Read [repair-loop.md](references/repair-loop.md) when a report has actionable findings, or when you reply to or resolve review threads.
- Read [merge-protocol.md](references/merge-protocol.md) when the PR looks ready: readiness, merge method, approval, landing, cleanup.
- Read [tool-matrix.md](references/tool-matrix.md) before the first GitHub operation of a run and whenever a tool call fails: the preflight, and for each task the preferred layer (MCP or `gh`) with its fallback.
- Read `${CLAUDE_PLUGIN_ROOT}/references/github-read-tasks.md` when you inspect a PR, its checks, runs, logs, reviews or alerts: the exact read-only commands, MCP and `gh`, each with its fallback. The `pr-tracker` agent carries the MCP forms in its own instructions.
- Read `${CLAUDE_PLUGIN_ROOT}/references/mcp-catalog.md` when you need to know whether the GitHub MCP offers a tool, which toolsets it needs, or whether it writes.
- Read [final-report.md](references/final-report.md) when you close the run.

If a reference is missing or disagrees with the tools you have, inspect the actual tool interface and repository policy. Do not invent tool names, parameters or operations.

## Roles

Main session owns: scope, local git (branch, edit, validate, commit, push), PR creation and updates, evaluating tracker findings, every fix, review replies and thread resolution, the readiness decision, the approval request, the merge, cleanup, and the report.

Tracker owns read-only observation: CI and workflow runs, reviews and threads, warnings and deprecations, Dependabot alerts, comparison with prior reports, and evidence-backed causes and fixes. Launch it with the Agent tool and `subagent_type: github-operations:pr-tracker`. Never authorize it to edit, reply, resolve, rerun, commit, push, merge or change GitHub state. Its recommendations advise; they do not widen the task.

## Lifecycle record

Keep in working context: repository, PR number and URL, base and feature branches, current head SHA, lifecycle state, commits pushed this run, latest tracker report and timestamp, open findings and verification gaps, merge method and queue and deployment implications, and the approval (exact head SHA and action).

Refresh the remote head after every push, before each monitoring cycle, before requesting approval, and immediately before merging. A different head invalidates every head-specific conclusion and any earlier approval.

## States

- `pending`: checks or required approvals outstanding.
- `actionable`: a fix, reply or other authorized action is needed.
- `ready`: gates pass and review housekeeping is done.
- `blocked`: needs unavailable access, an external dependency or a human decision.
- `timeout`: bounded monitoring ended without a terminal state.
- `awaiting_merge`: an authorized merge is queued or scheduled, not landed.
- `merged`: GitHub confirms the approved revision landed.

A tracker status such as `READY_FOR_MAIN_SESSION` is a recommendation. The readiness decision is the main session's, and a material verification gap means not ready.

## Gates

- **Readiness:** a current tracker report on the current head; required checks and approvals satisfied; actionable findings addressed; eligible threads resolved; not a draft; no merge conflict; allowed merge methods and queue rules read; deployment implications stated only if verified.
- **Merge approval:** ask the user directly, right before the merge, naming repository, PR, base and head branches, the freshly read head SHA, merge method, queue action and automatic deployment implications. Approval covers that PR, that SHA and that action. Initial instructions to manage the lifecycle, silence or an earlier PR's approval never count. A new head voids it. If declined or postponed, stop at `ready-without-approval` with no merge or cleanup mutation.
- **Landing:** only GitHub's own PR state confirms a merge. A queue entry or enabled auto-merge is `awaiting_merge`.
- **Cleanup:** only after confirmed merge, and never the base branch, a shared branch or another contributor's branch.

## Tool policy

Before the first GitHub operation of a run, check what you can do: the MCP tools actually loaded, the identity, and the repository permission. Use the MCP tool or `gh`, whichever the tool matrix lists first for the task, and fall back to the other in either direction. Do not declare a task impossible until its fallback was tried and both errors are in hand; then report them with the concrete unlock and wait for the user. A permission denial from Claude Code itself is the user's decision, not a gap to route around. Keep branching, editing, validation, commits, signing and pushes in local git; do not substitute API-created commits when that would bypass hooks, signing or repository behavior. Never use a fallback to bypass checks, reviews, permissions, hooks, branch protection or queues. Follow the session's permission and confirmation requirements for every operation.

## Hard rules

- Never force-push, rewrite published history or use `--no-verify`.
- Never bypass hooks, required checks, reviews, branch protection or queues, and never use admin privileges to route around a gate.
- Never treat inaccessible evidence as a passing result.
- Never report a queued or scheduled merge as completed.
- Never merge a different head under an earlier approval.
- Never weaken tests or security controls, or suppress warnings, only to turn checks green.
- Never discard unrelated local work.
- Follow the repository's commit, PR and attribution conventions.

## Final outcome

Report exactly one:

- `merged`: the authorized revision was confirmed merged.
- `ready-without-approval`: ready, but approval was declined, postponed or not given.
- `awaiting-merge`: an authorized queued or scheduled merge has not landed within the observation window.
- `externally-merged`: another actor merged the PR.
- `closed-without-merge`: the PR was closed unmerged.
- `blocked`: an unresolved gate, external dependency, verification gap or escalated timeout prevents completion.
