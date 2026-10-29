# PR lifecycle

You own the PR from its starting point to the merge, not just to the push. Run the loop without routine check-ins. The one human gate is the merge approval.

## Roles

The main session acts and mutates: scope, local git, PR creation and updates, every fix, review replies and thread resolution, the readiness decision, the approval request, the merge, cleanup and the report. The `github-operations:pr-tracker` agent observes and diagnoses, read-only. Launch it with the Agent tool and `subagent_type` set to `github-operations:pr-tracker`. Never authorize it to edit, reply, resolve, rerun, commit, push, merge or change GitHub state. Its recommendations advise; they do not widen the task.

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

- `start.md`: before the first push of a run. Scope, branch, validation, commit, push, create the PR, labels.
- `observe.md`: every time you need the PR's state. How to brief the tracker, check its report, map its status to a lifecycle state, act after its wait, and read GitHub yourself when the tracker cannot.
- `repair.md`: when an observation has actionable findings, the branch is behind its base or conflicts, or you reply to or resolve review threads.
- `merge.md`: when the PR looks ready. Readiness, merge method, approval, landing, cleanup.
- `tooling.md`: before the first GitHub operation of a run and whenever a tool call fails. Routing, preflight, the read and write tools with their fallbacks, and the guardrails.
- `report.md`: when you close the run.

If a reference disagrees with the tools you have, inspect the actual tool interface and the repository policy. Do not invent tool names, parameters or operations.

## Lifecycle record

Keep the record in the state file, so it survives a compaction. The skill gives the scripts folder, the data folder and the session id; put them in place of `<skill-dir>`, `<data-dir>` and `<session-id>`.

1. Write the record after every push, every tracker report and every approval:
   `<skill-dir>/scripts/lifecycle-state.py write --data-dir "<data-dir>" --session "<session-id>" --set kind=pr --set repository=<owner/repo> --set pr=<number> --set base=<base> --set head=<sha> --set phase=<state>`
   Add `--set approval=<sha and action>` once the user approves, and `--set next_reference=<file>` for the step that comes next.
2. After a compaction, read it back with `lifecycle-state.py read` and the same `--data-dir` and `--session`, and resume from its phase.
3. Clear it with `lifecycle-state.py clear` when the run ends.

Keep in working context what the record does not hold: commits pushed this run, the latest tracker report and its time, open findings and verification gaps, the merge method, queue and deployment implications.

Refresh the remote head after every push, before each tracker launch, before the approval and immediately before merging. A different head invalidates every head-specific conclusion and any earlier approval.

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
- **Merge approval:** right before the merge, summarize in chat the repository, PR, base and head branches, the freshly read head SHA, merge method, queue action, automatic deployment implications and the branches cleanup would delete. Then call the merge with the head SHA. The plugin's merge hook turns that call into a permission prompt: the user's answer to it is the approval, for that PR, that SHA and that action. Initial instructions to manage the lifecycle, silence or an earlier PR's approval never count, and a new head voids it. If the user declines the prompt, stop at `ready_without_approval` with no merge or cleanup mutation.
- **Landing:** only GitHub's own PR state confirms a merge. A queue entry or enabled auto-merge is `awaiting_merge`.
- **Cleanup:** only after a confirmed merge, and never the base branch, a shared branch or another contributor's branch.

## Tools

Before the first GitHub operation of a run, do the preflight in `tooling.md`, then use the layer it lists first for each task and its fallback in either direction.

## Rules

- Never report a queued or scheduled merge as completed.
- Never merge a different head under an earlier approval.
- Never weaken tests or security controls, or suppress warnings, only to turn checks green.
- Never discard unrelated local work.

## Final outcome

Report exactly one:

- `merged`: the authorized revision was confirmed merged.
- `ready_without_approval`: ready, but approval was declined, postponed or not given.
- `awaiting_merge`: an authorized queued or scheduled merge has not landed within the observation window.
- `externally_merged`: another actor merged the PR.
- `closed_without_merge`: the PR was closed unmerged.
- `blocked`: an unresolved gate, external dependency, verification gap or escalated timeout prevents completion.
