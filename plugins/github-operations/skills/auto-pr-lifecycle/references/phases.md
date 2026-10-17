# Phase-by-phase detail

Lookup table for what to call in each phase. The shape of the loop, the tracker delegation and the merge checkpoint live in `SKILL.md`. Tool names are bare names of GitHub's official MCP server tools. In a session they carry a prefix: `mcp__plugin_github-operations_github__<tool>` for the server this plugin bundles, or `mcp__<server>__<tool>` for a server the user configured. Match by the bare name. Where the server has no equivalent, the phase says so and the operation goes to `gh`.

## Contents

- [Tool mapping rules](#tool-mapping-rules)
- [1. Scope](#1-scope)
- [2. Inspect](#2-inspect)
- [3. Prepare the feature branch](#3-prepare-the-feature-branch)
- [4. Validate locally](#4-validate-locally)
- [5. Commit](#5-commit)
- [6. Push](#6-push)
- [7. Create or find the PR](#7-create-or-find-the-pr)
- [8. Observe and classify](#8-observe-and-classify)
- [9. Repair and revalidate](#9-repair-and-revalidate)
- [10. Confirm exact readiness](#10-confirm-exact-readiness)
- [11. Execute the merge](#11-execute-the-merge)
- [12. Observe the landing](#12-observe-the-landing)
- [13. Close and synchronize](#13-close-and-synchronize)
- [14. Report](#14-report)

## Tool mapping rules

- GitHub's MCP server groups operations behind one tool with a `method` parameter (`pull_request_read`, `pull_request_review_write`, `issue_write`). Do not assume a tool named after the operation exists.
- Inspect the tools actually exposed in the session. If a tool or method below is missing, use the other layer for that operation, and report the gap only after both failed. Do not invent names or parameters.
- For every task, use the preferred layer and its fallback, in both directions, as the tool matrix lists. Workflow runs, logs, reruns and Dependabot alerts exist in the MCP only with all toolsets on, which is how the plugin connects; repository merge-method settings, auto-merge, merge queue entry and remote ref deletion exist only in `gh`.

## 1. Scope

Confirm what is in scope before touching anything: the repository (several repositories are independent units), which changes belong to the task, and the base branch. Take the base from the repository default unless the task or an open PR says otherwise.

- Derive owner and repo from `git remote -v` when inside a checkout. It avoids fork ambiguity.
- `search_repositories` locates a repository by name when the checkout does not say.

## 2. Inspect

Read repository instructions (`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, PR template), then local git state: current branch, uncommitted changes, behind or ahead of the remote, and unrelated changes in the working tree. Preserve unrelated changes; never fold them into this PR.

- `get_me` confirms which GitHub identity acts.
- `list_branches` checks for an existing remote branch with the name you intend to use.
- Check write access with the preflight in the tool matrix when the task depends on it.

## 3. Prepare the feature branch

Create or check out a feature branch off the base branch, never work on the base or any protected branch. Keep only task-related changes; set unrelated changes aside before branching.

Never force-push and never rewrite pushed history, including on your own branch once a PR is open.

- Re-run `list_branches` after creating the branch to confirm there is no remote collision.
- Overlap with the base uses local git (`git log`, `git diff`, `git merge-base`). Once both sides exist remotely, `gh api repos/<owner>/<repo>/compare/<base>...<head>` also works.

## 4. Validate locally

Run the repository's own gates (formatter, linter, type check, tests, build) before creating or updating the PR. Fix deterministic failures now; do not push what you already know is red. Keep each command and its result for the final report.

No MCP call applies. If the required checks are unclear from repository config, read the branch rules (see the tool matrix).

## 5. Commit

Read the full local diff, classify the change, and write a message that matches the repository history and the session's attribution rules. Let hooks run; fix what they flag and retry. Never use `--no-verify`. Record the commit SHA.

- `get_commit` and `search_commits` only verify a commit's presence or metadata on GitHub. The commit itself is local git.

## 6. Push

Push the feature branch without `--force`. Before pushing, check the current branch is the intended one, not a stale or already-merged branch. Verify afterwards that the remote branch points at the SHA you committed. Exit code 0 is not proof.

- `list_branches` or `get_commit` (by SHA) confirms the pushed head is visible. GitHub's view is the source of truth for every later phase.

## 7. Create or find the PR

Search for an open PR from this branch before creating one.

- `search_pull_requests` (query such as `repo:owner/name is:pr is:open head:branch-name`) or `list_pull_requests` filtered by `head`.
- `pull_request_read` with `method: get` fetches full detail by number.
- `create_pull_request` (`owner`, `repo`, `title`, `head`, `base`, optional `body`, `draft`, `reviewers`) only when no open PR exists. Build the title and body from the commit history and the repository's PR template: what changed, why, how it was validated, risks.
- `issue_write` with `method: update`, `issue_number` set to the PR number, and `labels` applies labels. Pull requests are issues in GitHub's data model. Label every PR, following the repository's conventions.

Record repository, PR URL and number, base, feature branch and head SHA in the lifecycle record.

## 8. Observe and classify

The tracking agent performs the full observation (see `SKILL.md`, Roles). The main session reads the PR directly only for a quick head, state or mergeability check, or when no tracker is available. Read at the current head, never a cached one:

- `pull_request_read` with `method: get`: state, draft, mergeable state, head SHA.
- `method: get_status`: combined commit status.
- `method: get_check_runs`: individual jobs; this is what shows which check failed.
- `method: get_reviews`: review verdicts.
- `method: get_review_comments`: review threads with resolved state and each thread's node ID (needed to resolve it) and each comment's numeric ID (needed to reply). Paginate with `perPage` and `after`.
- `method: get_comments`: PR-level conversation.
- `method: get_diff`, `get_files`, `get_commits`: as needed to understand what is under review.

Normalize the result into one lifecycle state using the states in `SKILL.md` (States). While `pending`, wait for a real status change before re-reading; do not spin.

When the head changes for any reason, including a push by someone else, every observation and approval held is stale. Observe again against the new head first.

## 9. Repair and revalidate

For every actionable finding:

1. Pull the evidence: failing job logs (`get_job_logs` with all toolsets on, otherwise `gh run view --log-failed`), the review comment and diff context (`get_review_comments`, `get_diff`), the exact file and line.
2. Classify it: real branch-caused, valid pre-existing, stale, false positive, transient or infrastructure, external blocker, or non-blocking improvement.
3. For a real branch-caused problem, make the smallest change that fixes it. Do not refactor unrelated code.
4. Rerun a check only with evidence of a transient failure (`actions_run_trigger` with all toolsets on, otherwise `gh run rerun --failed`).
5. Re-run the local validation of phase 4 after every code change, before pushing.
6. Reply to each addressed review thread:
   - `add_reply_to_pull_request_comment` (`commentId` is the numeric review-comment ID, not the thread node ID) for a reply anchored to a line.
   - `add_issue_comment` for a PR-level reply.
7. Commit and push (phases 5 and 6). The new head SHA sends you back to phase 8.
8. Once the issue is fixed, pushed and revalidated: `pull_request_review_write` with `method: resolve_thread` and `threadId` set to the thread node ID. Resolving an already-resolved thread is a no-op. Never resolve before the fix lands.
9. To reverse a resolution: `method: unresolve_thread`.
10. Record stale and false-positive findings in the reply, with the evidence.

Repeat until phase 8 reports `ready` or a real `blocked`. Do not skip to phase 10 with an actionable finding open.

## 10. Confirm exact readiness

Process one `ready` PR at a time. Before asking for approval:

- Re-read the PR at the current head: `pull_request_read` with `get`, `get_status`, `get_check_runs`, `get_reviews`, `get_review_comments`. Time has passed since the last `ready`.
- Obtain a current tracker report for that head.
- Read allowed merge methods, branch protection and merge-queue requirements (see the tool matrix).
- If a merge queue is required, the approval requested is to enter the queue, not an immediate merge. Say so.

Ask the user directly, as the merge approval gate in `SKILL.md` (Gates) requires, scoped to this PR and head SHA. Without approval, stop at `ready-without-approval`.

## 11. Execute the merge

After approval:

1. Re-read the PR (`pull_request_read`, `method: get`) and compare the head SHA with the approved one. If it differs, the approval is void; return to phase 10.
2. Re-check that the readiness gates have not regressed (a new check or review).
3. `merge_pull_request` with `owner`, `repo`, `pullNumber`, `expectedHeadSha` set to the approved SHA (the merge fails safely if the head moved) and `merge_method` (`merge`, `squash` or `rebase`) chosen from the repository's allowed methods and the branch history.
4. For a required merge queue or auto-merge, use `gh pr merge --auto`, which carries `--match-head-commit`. The MCP tool only performs an immediate merge.

Never pass admin or bypass flags. If the merge is rejected because a gate is unmet, that is correct behavior.

## 12. Observe the landing

- `pull_request_read` with `method: get` confirms `merged: true` and gives `merge_commit_sha`.
- `method: get_status` sanity-checks the merge commit when relevant.

Record the approved head SHA and the resulting merge or squash commit SHA separately; they differ for squash and rebase. For a queue or auto-merge, this phase is where you wait: "enrolled" or "queued" is `awaiting_merge` until the PR itself reports merged. If someone else merges or closes the PR, report that outcome as theirs.

When the repository or task requires it, observe the post-merge workflows (run list and run view, MCP or `gh`). A merged PR is not a successful deployment.

## 13. Close and synchronize

Only after phase 12 confirms the merge:

- Inspect the working tree and preserve unrelated changes.
- Switch to the base branch and sync it with the remote using the repository's safe update (`git pull --ff-only`).
- Delete the local feature branch with `git branch -d`. If that refuses after a squash or rebase landing, verify what landed (compare the merge commit's tree with the branch) before considering `-D`. Do not force-delete on an inconclusive ancestry check alone.
- Delete the remote feature branch with `gh api -X DELETE` on the ref, unless the repository's `delete_branch_on_merge` already removed it (check the phase 12 read).
- Confirm the checkout is the base branch, not a deleted feature branch.
- Never delete the base branch, a shared branch or another contributor's active branch.

## 14. Report

Compile the final report from:

- `pull_request_read` (`get`, `get_status`, `get_reviews`, `get_review_comments`, `get_comments`).
- `get_commit` for the final and the authorized SHA.
- The last tracker report.

State exactly one final outcome from `SKILL.md` (Final outcome), and report `merged` only when GitHub confirms the authorized SHA landed.
