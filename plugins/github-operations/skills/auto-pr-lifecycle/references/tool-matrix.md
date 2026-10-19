# Tool matrix: MCP first, gh as fallback, and back

For each write task, the layer that does it best is listed first. The read-only tasks (snapshot, checks, runs, logs, reviews, Dependabot, files) are in the observation reference. The other layer is the fallback and works in both directions: when the MCP tool is missing or fails, use `gh`; when `gh` fails or lacks the operation, use the MCP tool. "Best" here means the structured result or the shorter path; speed was not measured. Check a `gh` command's own help for its exact options before the first use in a run.

## Rules

1. Never say something cannot be done until the task has been tried through its listed fallback, and the exact error of each attempt is in hand.
2. If both layers fail, report what you tried, the exact errors and the concrete unlock (a token scope, a toolset, a repository permission), then wait for the user to decide.
3. A permission denial from Claude Code itself (a permission rule or the auto-mode classifier) is the user's decision, not a tool gap. Do not route the same outcome through the other layer. Name the rule that would allow it.
4. Commits and pushes always use local git. The MCP tools `push_files`, `create_or_update_file` and `delete_file` commit on GitHub without the user's signing key or hooks.
5. Never use administrator privileges to merge. Always pass the expected-head guard on a merge or a branch update.
6. Say in the final report which layer completed each action.

## Preflight

Before the first GitHub operation of a run, learn what you can do. Do not assume.

1. MCP tools loaded: list them with `ToolSearch` (query `+github`). A tool missing from the live list usually means fewer toolsets than the plugin turns on, or a token without the scope. The Actions, Dependabot, Discussions and Projects tools exist only with all toolsets on, which is how the plugin connects.
2. Identity: MCP `get_me`, or `gh` auth status, which masks the token and prints its scopes.
3. Repository permission of the `gh` login: read the repository through `gh api` and look at its `permissions` object (`admin`, `maintain`, `push`, `triage`, `pull`). The MCP server may use a different token, so a permission seen by one layer is not proof for the other.
4. Rules on the base branch: MCP `repository_ruleset_read` with `method: get_rules_for_branch`, or the `gh` ruleset check for the branch.

## Pull request

| Task | MCP | gh | Notes |
| :-- | :-- | :-- | :-- |
| Find the PR for a branch | `list_pull_requests` with `head` = `<owner>:<branch>`, or `search_pull_requests` | PR list filtered by head branch (bare branch name), open state | |
| Create | `create_pull_request` (owner, repo, title, head, base; optional body, draft, reviewers) | PR create with base, head, title, body and label options; add the draft option only when asked | |
| List labels | `list_label` | label list | Ordered by use on the MCP |
| Create a label | `label_write` with `method: create`, `name`, `color`, `description` | label create | Only when the repository has none for this kind of change |
| Apply labels | `issue_write` with `method: update`, `issue_number` = PR number, `labels` | PR edit with the add-label option | The MCP update replaces the label list: send the existing labels too. The `gh` form only adds |
| Mark a draft ready | `update_pull_request` with `draft: false` | PR ready | Notifies reviewers |
| Bring the branch up to date with its base | `update_pull_request_branch` with `expectedHeadSha` | PR update-branch | Merges the base into the branch. Never use the rebase option: it rewrites published commits |

## CI

| Task | MCP | gh | Notes |
| :-- | :-- | :-- | :-- |
| Rerun failed jobs | `actions_run_trigger` with `method: rerun_failed_jobs` and `run_id` (the server flags it destructive) | Run rerun with the failed-only option | Only with evidence of a transient failure, or after the cause is fixed |

## Reviews

| Task | MCP | gh | Notes |
| :-- | :-- | :-- | :-- |
| Reply to a review comment | `add_reply_to_pull_request_comment` with `pullNumber`, `commentId`, `body` | `gh api` POST to the comment's replies endpoint with the body | `commentId` is the numeric comment id, not the thread node id |
| Resolve a thread | `pull_request_review_write` with `method: resolve_thread` and `threadId` (the thread node id, from `get_review_comments`) | `gh api graphql` with the `resolveReviewThread` mutation, passing the thread node id and asking for `thread.isResolved` | The result must show it resolved. The GraphQL form comes from GitHub's reference and was not run live when this was written: check the first response |

## Merge

| Task | MCP | gh | Notes |
| :-- | :-- | :-- | :-- |
| Allowed merge methods, auto-delete | no tool | repository view with the squash, merge, rebase and delete-branch-on-merge fields | `repository_ruleset_read` covers rulesets only |
| Merge queue and rules | `repository_ruleset_read` | ruleset check for the branch | A merge queue appears as a `merge_queue` rule |
| Classic branch protection | no tool | `gh api` on the branch's protection endpoint | A 404 "Branch not protected" is a valid answer |
| Merge now | `merge_pull_request` with `pullNumber`, `expectedHeadSha`, `merge_method` | PR merge with the method option and the match-head-commit option | |
| Enable auto-merge or enter a merge queue | no tool | PR merge with the auto option and the match-head-commit option; on a queue-protected branch no method is needed; the disable-auto option withdraws it | Enrollment is `awaiting_merge`, not merged |
| Delete the remote feature branch | no tool | `gh api` DELETE on the branch's ref, or push with the delete option | Skip if delete-on-merge already did it |

## Beyond the lifecycle

Operations the MCP does not cover, such as creating releases and uploading assets, secrets and variables, and repository settings, go through `gh` or `gh api`. `gh` also has command groups for `issue`, `project`, `search`, `ruleset`, `label`, `gist`, `cache`, `workflow` and `agent-task`. It has no `discussion` command: discussions go through `gh api graphql` or the MCP discussion tools.
