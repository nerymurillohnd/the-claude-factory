# GitHub MCP tool catalog

The tools the remote GitHub MCP server returns from `tools/list` with the plugin's headers (`X-MCP-Toolsets: all` and `X-MCP-Insiders: true`), grouped by area. Refresh before relying on it: load the live list with `ToolSearch` (`+github`) or read the server's `tools/list`.

Marks after each name: `R` read-only, `W` writes, `!` the server flags it destructive, `+` only with all toolsets on, absent from GitHub's default toolsets, `I` only in early-access (insiders) mode.

The list depends on the token. Observed, not documented here: with a token holding `repo`, `workflow`, `read:org` and `gist`, `delete_repository` was absent from `tools/list`, while another session with a broader token showed it. Treat a missing tool as a scope question first. Check the tools actually loaded before planning around one.

Tools with a `method` parameter group several operations (`pull_request_read`, `issue_read`, `actions_list`, `actions_get`, `actions_run_trigger`, `projects_*`, `repository_ruleset_read`, `pull_request_review_write`, `issue_write`, `label_write`, `discussion_comment_write`). Load the tool's schema for the method list.

## Identity, orgs and users

`get_me` R, `get_teams` R, `get_team_members` R, `search_users` R, `search_orgs` R+

## Repositories and files

`search_repositories` R, `create_repository` W, `fork_repository` W, `list_repository_collaborators` R, `get_file_contents` R, `get_repository_tree` R+, `search_code` R, `create_or_update_file` W, `push_files` W, `delete_file` W!, `delete_repository` W, `star_repository` W+, `unstar_repository` W+, `list_starred_repositories` R+

## Commits, branches, tags, releases

`list_commits` R, `get_commit` R, `search_commits` R, `list_branches` R, `create_branch` W, `list_tags` R, `get_tag` R, `list_releases` R, `get_latest_release` R, `get_release_by_tag` R

## Pull requests

`list_pull_requests` R, `search_pull_requests` R, `pull_request_read` R, `create_pull_request` W, `update_pull_request` W, `update_pull_request_branch` W, `merge_pull_request` W

## Reviews

`pull_request_review_write` W, `add_comment_to_pending_review` W, `add_reply_to_pull_request_comment` W, `request_copilot_review` W

## Issues and labels

`list_issues` R, `search_issues` R, `semantic_issue_similarity_search` R+, `issue_read` R, `issue_write` W, `add_issue_comment` W, `update_issue_comment` W, `sub_issue_write` W, `list_issue_types` R, `list_issue_fields` R, `get_label` R, `list_label` R+, `label_write` W!+, `ui_get` R

## GitHub Actions

`actions_list` R+, `actions_get` R+, `get_job_logs` R+, `actions_run_trigger` W!+

## Security and dependencies

`list_dependabot_alerts` R+, `get_dependabot_alert` R+, `list_code_scanning_alerts` R+, `get_code_scanning_alert` R+, `get_code_quality_finding` R+, `list_secret_scanning_alerts` R+, `get_secret_scanning_alert` R+, `run_secret_scanning` R, `check_dependency_vulnerabilities` R+, `list_global_security_advisories` R+, `get_global_security_advisory` R+, `list_repository_security_advisories` R+, `list_org_repository_security_advisories` R+

## Rulesets and custom properties

`repository_ruleset_read` R+, `create_repository_ruleset` W+, `custom_properties_read` R+, `custom_properties_write` W+

## Discussions

`list_discussions` R+, `get_discussion` R+, `get_discussion_comments` R+, `list_discussion_categories` R+, `discussion_comment_write` W!+

## Projects

`projects_list` R+, `projects_get` R+, `projects_write` W!+

## Notifications and gists

`list_notifications` R+, `get_notification_details` R+, `dismiss_notification` W+, `manage_notification_subscription` W!+, `manage_repository_notification_subscription` W!+, `mark_all_notifications_read` W+, `list_gists` R+, `get_gist` R+, `create_gist` W+, `update_gist` W+

## Copilot and search helpers

`assign_copilot_to_issue` W, `assign_copilot_to_issue_with_intent` W+, `create_pull_request_with_copilot` W, `get_copilot_job_status` R, `list_copilot_spaces` R+, `get_copilot_space` R+, `github_support_docs_search` R+, `web_search` R+

## Early access (insiders mode)

`get_file_blame` RI, `issue_dependency_read` RI, `issue_dependency_write` WI
