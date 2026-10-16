# Tool matrix: MCP first, gh as fallback, and back

For each write task, the layer that does it best is listed first. The read-only tasks (snapshot, checks, runs, logs, reviews, Dependabot, files) are in the shared read-tasks file that `SKILL.md` links. The other layer is the fallback and works in both directions: when the MCP tool is missing or fails, use `gh`; when `gh` fails or lacks the operation, use the MCP tool. "Best" here means the structured result or the shorter path; speed was not measured.

## Rules

- Never say something cannot be done until the task has been tried through its listed fallback, and the exact error of each attempt is in hand.
- If both layers fail, report what you tried, the exact errors and the concrete unlock (a token scope, a toolset URL, a repository permission), then wait for the user to decide.
- A permission denial from Claude Code itself (a permission rule or the auto-mode classifier) is the user's decision, not a tool gap. Do not route the same outcome through the other layer. Name the rule that would allow it.
- Commits and pushes always use local git. The MCP tools `push_files`, `create_or_update_file` and `delete_file` commit on GitHub without the user's signing key or hooks.
- Never pass `--admin`. Always pass the head guard on a merge (`expectedHeadSha` or `--match-head-commit`).
- Say in the final report which layer completed each action.

## Preflight

Before the first GitHub operation of a run, learn what you can do. Do not assume.

- MCP tools loaded: list them with `ToolSearch` (`+github`). A tool missing from a catalog entry usually means a narrower toolset URL or a token without the scope. The Actions, Dependabot, Discussions and Projects tools exist only on the all-toolsets URL.
- Identity: MCP `get_me`, or `gh auth status`, which masks the token and prints its scopes.
- Repository permission of the `gh` login: `gh api repos/<owner>/<repo> --jq '.permissions'` returns `admin`, `maintain`, `push`, `triage`, `pull`. The MCP server may use a different token, so a permission seen by one layer is not proof for the other.
- Rules on the base branch: MCP `repository_ruleset_read` with `method: get_rules_for_branch`, or `gh ruleset check <branch> -R <owner>/<repo>`.

## Pull request

**Find the PR for a branch**

- MCP: `list_pull_requests` with `head`, or `search_pull_requests`.
- gh: `gh pr list -R <owner>/<repo> --head <branch> --state open --json number,url,state`.

**Create**

- MCP: `create_pull_request`.
- gh: `gh pr create --base <base> --head <branch> --title <t> --body <b> --label <l>`; add `--draft` when asked.

**Labels**

- MCP: `issue_write` with `method: update`, `issue_number` set to the PR number and `labels`.
- gh: `gh pr edit <n> --add-label <name>`.

**Bring the branch up to date with its base**

- MCP: `update_pull_request_branch`.
- gh: `gh pr update-branch <n>`.

## CI

**Rerun failed jobs**

- MCP: `actions_run_trigger` with `rerun_failed_jobs`; the server flags it destructive.
- gh: `gh run rerun <run-id> --failed`.
- Only with evidence of a transient failure, or after the cause is fixed.

## Reviews

**Reply to a review comment**

- MCP: `add_reply_to_pull_request_comment`; `commentId` is the numeric id, not the thread node id.
- gh: `gh api repos/<owner>/<repo>/pulls/<n>/comments/<comment-id>/replies -f body=<text>`.

**Resolve a thread**

- MCP: `pull_request_review_write` with `resolve_thread` and the thread node id.
- gh: `gh api graphql` with the `resolveReviewThread` mutation. Not run in this session; check the first call.

## Merge

**Rules that apply: allowed methods, auto-delete, merge queue**

- gh: `gh repo view <owner>/<repo> --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed,deleteBranchOnMerge`, and `gh ruleset check <branch>`. A merge queue appears as a `merge_queue` rule.
- MCP: `repository_ruleset_read` covers rulesets only. No MCP tool returns the repository's merge-method settings.
- Classic branch protection: `gh api repos/<owner>/<repo>/branches/<branch>/protection`. HTTP 404 "Branch not protected" is a valid answer.

**Merge now**

- MCP: `merge_pull_request` with `expectedHeadSha` and `merge_method`.
- gh: `gh pr merge <n> --squash|--merge|--rebase --match-head-commit <approved-sha>`.

**Enable auto-merge or enter a merge queue**

- gh only: `gh pr merge <n> --auto --squash --match-head-commit <approved-sha>`. On a queue-protected branch no strategy flag is needed. `--disable-auto` withdraws it.
- No MCP tool covers this. Enrollment is `awaiting_merge`, not merged.

**Delete the remote feature branch**

- gh only: `gh api -X DELETE repos/<owner>/<repo>/git/refs/heads/<branch>`, or `git push origin --delete <branch>`. No MCP tool deletes a ref. Skip if `deleteBranchOnMerge` already did it.

## Beyond the lifecycle

The full MCP tool list, with read and write marks, is the shared catalog that `SKILL.md` links. Operations the MCP does not cover, such as creating releases and uploading assets (`gh release create|upload`), secrets and variables (`gh secret|variable set`) and repository settings, go through `gh` or `gh api`. `gh` also has command groups for `issue`, `discussion`, `project`, `search`, `ruleset`, `label`, `gist`, `cache`, `workflow` and `agent-task`.
