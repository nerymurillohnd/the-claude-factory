---
name: auto-pr-lifecycle
description: Use when asked to open a PR, ship or land a change, get a PR merged, babysit or check a PR through to completion, or drive CI failures and review feedback to resolution. Runs branch, validate, commit, push and PR, then observes and repairs until the PR is ready, merges only after explicit approval for the exact head SHA, then cleans up branches and syncs the base. Not for requests that only ask to commit or push.
argument-hint: "[PR number or URL]"
compatibility: Needs the GitHub MCP server (bundled with this plugin), local git, an authenticated gh CLI for operations the MCP lacks, and the Agent tool to run github-operations:pr-tracker.
---

# Automatic PR lifecycle

You own the PR from its starting point to the merge, not just to the push. Run the loop without routine check-ins. The one human gate is the merge approval.

## Roles

The main session acts and mutates: scope, local git, PR creation and updates, every fix, review replies and thread resolution, the readiness decision, the approval request, the merge, cleanup and the report. The `github-operations:pr-tracker` agent observes and diagnoses, read-only. Launch it with the Agent tool and `subagent_type` set to `github-operations:pr-tracker`. Never authorize it to edit, reply, resolve, rerun, commit, push, merge or change GitHub state. Its recommendations advise; they do not widen the task.

`$ARGUMENTS` is an optional PR number or URL. With one, resume that PR from the phase it is in. With none, work from the current checkout and branch.

## Lifecycle

```text
Scope → Prepare → Validate → Commit → Push → Create/Find PR
  → Launch tracker → Evaluate report → Repair → Commit/Push → Launch tracker again … until ready
  → Verify readiness → Request approval → Land → Observe landing
  → Clean up and sync → Report
```

Each repository and PR is an independent unit. Resume from the phase the PR is actually in; do not repeat completed work. If the repository or PR is ambiguous, ask before mutating anything.

Open a PR only when the request calls for one. "Commit", "commit and push" or "push" alone stop at that step and never open a PR.

## References

Read the one for the step you are on:

- [start.md](references/start.md): before the first push of a run. Scope, branch, validation, commit, push, create the PR, labels.
- [observe.md](references/observe.md): every time you need the PR's state. How to brief the tracker, check its report, map its status to a lifecycle state, wait for pending checks, and read GitHub yourself when the tracker cannot.
- [repair-loop.md](references/repair-loop.md): when an observation has actionable findings, the branch is behind its base or conflicts, or you reply to or resolve review threads.
- [merge-protocol.md](references/merge-protocol.md): when the PR looks ready. Readiness, merge method, approval, landing, cleanup.
- [tool-matrix.md](references/tool-matrix.md): before the first GitHub operation of a run and whenever a tool call fails. Preflight, and for each write task the preferred layer (MCP or `gh`) with its fallback.
- [final-report.md](references/final-report.md): when you close the run.

If a reference disagrees with the tools you have, inspect the actual tool interface and the repository policy. Do not invent tool names, parameters or operations.

## Lifecycle record

Keep in working context: repository, PR number and URL, base and feature branches, current head SHA, lifecycle state, commits pushed this run, the latest tracker report and its time, open findings and verification gaps, merge method and queue and deployment implications, and the approval (exact head SHA and action).

Refresh the remote head after every push, before each tracker launch, before requesting approval, and immediately before merging. A different head invalidates every head-specific conclusion and any earlier approval.

## States

- `pending`: checks or required approvals outstanding, nothing actionable.
- `actionable`: a fix, reply or other authorized action is needed.
- `ready`: gates pass and review housekeeping is done. A tracker status of `READY_FOR_MAIN_SESSION` is a recommendation, not this state.
- `blocked`: needs unavailable access, an external dependency or a human decision.
- `timeout`: the bounded wait in `observe.md` ended without a terminal state. Report what is still pending and ask whether to keep waiting.
- `awaiting_merge`: an authorized merge is queued or scheduled, not landed.
- `merged`: GitHub confirms the approved revision landed.

## Gates

- **Readiness:** a tracker report on the current head, and your own verification of it; required checks and approvals satisfied; actionable findings addressed; eligible threads resolved; not a draft; no merge conflict; allowed merge methods and queue rules read; deployment implications stated only if verified. A material verification gap means not ready.
- **Merge approval:** ask the user directly (AskUserQuestion when available), right before the merge, naming repository, PR, base and head branches, the freshly read head SHA, merge method, queue action, automatic deployment implications and the branches cleanup would delete. Approval covers that PR, that SHA and that action. Initial instructions to manage the lifecycle, silence or an earlier PR's approval never count. A new head voids it. If declined or postponed, stop at `ready_without_approval` with no merge or cleanup mutation.
- **Landing:** only GitHub's own PR state confirms a merge. A queue entry or enabled auto-merge is `awaiting_merge`.
- **Cleanup:** only after a confirmed merge, and never the base branch, a shared branch or another contributor's branch.

## Tool policy

Before the first GitHub operation of a run, do the preflight in the tool matrix. For each task use the layer the matrix lists first and fall back to the other in either direction. Do not declare a task impossible until its fallback was tried and both errors are in hand; then report them with the concrete unlock and wait for the user. A permission denial from Claude Code itself is the user's decision, not a gap to route around.

Keep branching, editing, validation, commits, signing and pushes in local git. Commits follow the user's and the repository's signing configuration: if signing is configured and fails, stop and say so; never use `--no-gpg-sign` or commit unsigned to get past it. Do not substitute API-created commits when that would bypass hooks, signing or repository behavior. Never use a fallback to bypass checks, reviews, permissions, hooks, branch protection or queues. Follow the session's permission and confirmation requirements for every operation.

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
- `ready_without_approval`: ready, but approval was declined, postponed or not given.
- `awaiting_merge`: an authorized queued or scheduled merge has not landed within the observation window.
- `externally_merged`: another actor merged the PR.
- `closed_without_merge`: the PR was closed unmerged.
- `blocked`: an unresolved gate, external dependency, verification gap or escalated timeout prevents completion.
