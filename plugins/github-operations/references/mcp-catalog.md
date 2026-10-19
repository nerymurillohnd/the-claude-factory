# GitHub MCP Tool Catalog

The tools the remote GitHub MCP server returns from `tools/list` when the plugin sends `X-MCP-Toolsets: all` and `X-MCP-Insiders: true`. 104 tools at the last refresh. **Refresh before relying on it:** load the live list with `ToolSearch` (`+github`), and confirm a tool is loaded before planning around it. The live list wins over this file.

## Token decides availability

The returned list depends on the token. Observed, with the cause not documented: a token with `repo`, `workflow`, `read:org` and `gist` did not list `delete_repository`, and a broader token did. When a tool is missing, check the token scopes first.

## Tools that write

37 tools change state. A trailing `!` marks the 8 the server flags as destructive.

`create_repository`, `fork_repository`, `create_or_update_file`, `push_files`, `delete_file!`, `delete_repository!`, `star_repository`, `unstar_repository`, `create_branch`, `create_pull_request`, `update_pull_request`, `update_pull_request_branch`, `merge_pull_request`, `pull_request_review_write`, `add_comment_to_pending_review`, `add_reply_to_pull_request_comment`, `request_copilot_review`, `issue_write`, `add_issue_comment`, `update_issue_comment`, `sub_issue_write`, `label_write!`, `actions_run_trigger!`, `create_repository_ruleset`, `custom_properties_write`, `discussion_comment_write!`, `projects_write!`, `dismiss_notification`, `manage_notification_subscription!`, `manage_repository_notification_subscription!`, `mark_all_notifications_read`, `create_gist`, `update_gist`, `assign_copilot_to_issue`, `assign_copilot_to_issue_with_intent`, `create_pull_request_with_copilot`, `issue_dependency_write`

A tool not listed here was read-only at the last refresh. Check the schema of a tool that is new to the server.

## Tools outside GitHub's default toolsets

51 tools exist only with all toolsets on, which the plugin sets. With fewer toolsets, as on your own server with a shorter `X-MCP-Toolsets`, they are absent, and the `gh` fallback applies.

`search_orgs`, `get_repository_tree`, `star_repository`, `unstar_repository`, `list_starred_repositories`, `semantic_issue_similarity_search`, `list_label`, `label_write`, `actions_list`, `actions_get`, `get_job_logs`, `actions_run_trigger`, `list_dependabot_alerts`, `get_dependabot_alert`, `list_code_scanning_alerts`, `get_code_scanning_alert`, `get_code_quality_finding`, `list_secret_scanning_alerts`, `get_secret_scanning_alert`, `check_dependency_vulnerabilities`, `list_global_security_advisories`, `get_global_security_advisory`, `list_repository_security_advisories`, `list_org_repository_security_advisories`, `repository_ruleset_read`, `create_repository_ruleset`, `custom_properties_read`, `custom_properties_write`, `list_discussions`, `get_discussion`, `get_discussion_comments`, `list_discussion_categories`, `discussion_comment_write`, `projects_list`, `projects_get`, `projects_write`, `list_notifications`, `get_notification_details`, `dismiss_notification`, `manage_notification_subscription`, `manage_repository_notification_subscription`, `mark_all_notifications_read`, `list_gists`, `get_gist`, `create_gist`, `update_gist`, `assign_copilot_to_issue_with_intent`, `list_copilot_spaces`, `get_copilot_space`, `github_support_docs_search`, `web_search`

## Early access (insiders mode)

`get_file_blame`, `issue_dependency_read`, `issue_dependency_write` exist only with `X-MCP-Insiders: true`.

## Tools with several operations

These take a `method` parameter. Load the schema to see the supported methods before calling: `pull_request_read`, `issue_read`, `actions_list`, `actions_get`, `actions_run_trigger`, `projects_*`, `repository_ruleset_read`, `pull_request_review_write`, `issue_write`, `label_write`, `discussion_comment_write`.
