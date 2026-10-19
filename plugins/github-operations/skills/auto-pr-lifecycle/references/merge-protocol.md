# Merge protocol

## Verify readiness

Before requesting approval:

1. Refresh the PR head.
2. Observe the PR at that head, as the observation reference says.
3. Confirm required checks pass for the applicable revision.
4. Confirm required reviews and approvals are satisfied.
5. Confirm actionable findings are addressed.
6. Complete eligible review-thread resolution.
7. Confirm the PR is not a draft and has no unresolved merge conflict.
8. Inspect allowed merge methods and applicable queue or protection rules.
9. Identify automatic deployment implications from available evidence.
10. Record remaining non-blocking warnings, alerts and advisory work.

"No new findings" means none appeared in the latest completed inspection, not that no review or check can still arrive. Do not claim mergeability or deployment behavior you could not verify.

## Select the merge method

Respect repository-enforced methods and merge-queue requirements. When several methods are allowed:

- Prefer squash for incremental, corrective or work-in-progress commits that need not stay separate.
- Prefer a merge commit when distinct, meaningful commits and their history matter.
- Use another allowed method only when repository conventions or explicit user instructions call for it.

Decide from the actual branch history, not branch size or author count. When the history is ambiguous, prefer squash. State the method before asking for approval, and do not change it afterwards without renewed approval.

## Request approval

Stop before the merge mutation and ask the user directly. Include:

- Repository.
- PR number, title and URL.
- Base and head branches.
- Freshly confirmed head SHA.
- Intended merge method.
- Merge-queue requirement and intended queue action, if any.
- Known automatic deployment implications.
- Material non-blocking warnings or inspection limits.

When a queue is required, the approval requested is to enter it, and the request says so.

## Land and observe

Immediately before the approved action:

1. Refresh the PR head and the relevant gates.
2. Confirm they still match the approved action; stop and reassess if the head, method or conditions changed.
3. Use an expected-head guard when the merge operation supports one.
4. Perform only the authorized action.

If the head changes while `awaiting_merge`, reassess the authorization and queue state rather than treating the new revision as approved. If a pending merge must be stopped but you cannot or are not authorized to stop it, report urgently.

Confirm landing from GitHub's PR state and merge information. Record the approved head SHA and the resulting merge or squash commit SHA separately; they are not assumed equal. If someone else merges or closes the PR, verify and report it as their outcome.

Observe post-merge workflows when the task or repository requires it. A merged PR is not a successful deployment.

## Clean up and sync

Only after confirmed merge:

1. Inspect the working tree and preserve unrelated changes.
2. Switch to the actual base branch.
3. Sync with the remote using the repository's safe update procedure.
4. Delete the local feature branch only when safe.
5. Delete the remote feature branch only when appropriate and authorized.
6. Confirm the checkout is the base branch.
7. Report cleanup steps skipped because of local changes, shared branches, permissions or policy.

Do not force-delete only because a squash or rebase landing makes the local ancestry check inconclusive. Verify what landed first.
