# Merge protocol

## 1. Verify readiness

Before requesting approval, work these in order:

1. Refresh the PR head.
2. Observe the PR at that head, as the observation reference says.
3. Confirm required checks pass for the applicable revision.
4. Confirm required reviews and approvals are satisfied.
5. Confirm actionable findings are addressed.
6. Complete the eligible review-thread resolution.
7. Confirm the PR has no unresolved merge conflict and is not a draft. A draft created in this run is marked ready for review once everything else passes, because that notifies reviewers (`update_pull_request` with `draft: false`, or the `gh` PR ready command). Any other draft is the author's choice: ask.
8. Read the allowed merge methods and the applicable queue and protection rules (the tool matrix says where).
9. Identify automatic deployment implications from available evidence.
10. Record remaining non-blocking warnings, alerts and advisory work.

"No new findings" means none appeared in the latest completed inspection, not that no review or check can still arrive. Do not claim mergeability or deployment behavior you could not verify.

## 2. Select the merge method

Respect repository-enforced methods and merge-queue requirements. When several methods are allowed:

- Prefer squash for incremental, corrective or work-in-progress commits that need not stay separate.
- Prefer a merge commit when distinct, meaningful commits and their history matter.
- Use another allowed method only when repository conventions or explicit user instructions call for it.

Decide from the actual branch history (the PR's commits) and from how the base branch's recent merges landed, not from branch size or author count. When the history is ambiguous, prefer squash. State the method before asking for approval, and do not change it afterwards without renewed approval.

## 3. Request approval

Stop before the merge and ask the user directly. Include:

- Repository.
- PR number, title and URL.
- Base and head branches.
- Freshly confirmed head SHA.
- Intended merge method.
- Merge-queue requirement and intended queue action, if any.
- Known automatic deployment implications.
- The cleanup that follows: which local and remote feature branches would be deleted.
- Material non-blocking warnings or inspection limits.

When a queue is required, the approval requested is to enter it, and the request says so.

## 4. Land and observe

Immediately before the approved action:

1. Refresh the PR head and the relevant gates.
2. Confirm they still match the approved action. If the head, method or conditions changed, stop and reassess.
3. Always pass the expected-head guard on the merge (`expectedHeadSha` on the MCP, the match-head option on `gh`). Both layers support it.
4. Perform only the authorized action.

If the head changes while the state is `awaiting_merge`, reassess the authorization and queue state rather than treating the new revision as approved. If a pending merge must be stopped but you cannot or are not authorized to stop it, report urgently.

Confirm landing from GitHub's PR state: read the PR (`pull_request_read`, method `get`, or the `gh` PR view with its state, merged time, merge commit and head SHA fields). Record the approved head SHA and the resulting merge or squash commit SHA separately; they are not assumed equal. If someone else merges or closes the PR, verify and report it as their outcome.

Observe post-merge workflows when the task or repository requires it. A merged PR is not a successful deployment.

## 5. Clean up and sync

Only after a confirmed merge, and only the cleanup the approval named. Work in order:

1. Inspect the working tree and preserve unrelated changes. If switching to the base would overwrite them, stop and report; do not stash or discard them.
2. Switch to the base branch, fetch from the remote with pruning, and fast-forward the local base to the remote base. If it cannot fast-forward, the local base holds commits the remote lacks: stop and report.
3. Delete the local feature branch. Try the safe delete first. A squash or rebase landing makes the safe delete refuse even when everything landed. In that case verify first: GitHub shows the PR merged at the approved head SHA, and the local branch tip equals that SHA or has no commits beyond it. Only then is the forced delete justified. Otherwise keep the branch and report why.
4. Delete the remote feature branch only when all of these hold: the repository did not already delete it on merge, the branch belongs to this repository and not a fork, no other open PR uses it as its base (deleting it would close those PRs; check with `list_pull_requests` filtered by base), and the approval named the deletion.
5. Confirm the checkout is the base branch, synced, and that the feature branch is gone where it should be, by listing branches and the short status.
6. Report cleanup steps skipped because of local changes, shared branches, permissions or policy.
