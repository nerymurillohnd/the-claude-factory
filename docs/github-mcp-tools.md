# 🧰 GitHub MCP tools

> Every GitHub tool Claude gets when you install **GitHub Operations**, grouped by what it does, with whether each one only reads or can change things on GitHub.

The plugin connects Claude Code to GitHub's official remote MCP server with every toolset turned on, plus GitHub's early-access mode. Claude can use any tool below, within what your token allows. The plugin's [README](../plugins/github-operations/README.md) covers installing and using it.

---

## 🔌 What the plugin connects

| Setting | Value |
| :-- | :-- |
| Server | `https://api.githubcopilot.com/mcp/` |
| Your token | The plugin's `github_token` option, sent as `Authorization: Bearer` |
| `X-MCP-Toolsets` | `all`: every toolset GitHub offers |
| `X-MCP-Insiders` | `true`: GitHub's early-access mode, which adds the tools marked *Early access* below |

> [!IMPORTANT]
> Claude Code asks for the token when you install the plugin from a session and keeps it in your system's secure credential store. The README's [Configuration](../plugins/github-operations/README.md#-configuration) shows how to set or change it. Until it is set, the plugin's GitHub server is missing from `/mcp` and Claude reads GitHub through `gh`.

## 🔐 Your token decides what works

The list below is what the server offers. What GitHub allows is set by your token: a tool your token has no permission for does not give a result, and GitHub may hide some tools from the list altogether. Two tokens can see different lists. That makes your token the real control over what Claude can do.

Create a [fine-grained token](https://github.com/settings/personal-access-tokens/new) for the repositories you work in and grant only the permissions you want Claude to have.

## 🧰 The tools

*Read* tools only look. *Write* tools create or change something on GitHub. *Write · deletes* tools are the ones GitHub flags as destructive. Several tools take a `method` parameter that groups related operations (`pull_request_read`, `issue_read`, `actions_list`, `actions_get`, `actions_run_trigger`, `projects_*`, `repository_ruleset_read`, `pull_request_review_write`, `issue_write` and others), so one row can cover several actions.

### Identity, orgs and users

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `get_me` | Get my user profile | Read | |
| `get_teams` | Get teams | Read | |
| `get_team_members` | Get team members | Read | |
| `search_users` | Search users | Read | |
| `search_orgs` | Search organizations | Read | Outside GitHub's default toolsets |

### Repositories and files

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `search_repositories` | Search repositories | Read | |
| `create_repository` | Create repository | Write | |
| `fork_repository` | Fork repository | Write | |
| `list_repository_collaborators` | List repository collaborators | Read | |
| `get_file_contents` | Get file or directory contents | Read | |
| `get_repository_tree` | Get repository tree | Read | Outside GitHub's default toolsets |
| `search_code` | Search code | Read | |
| `create_or_update_file` | Create or update file | Write | |
| `push_files` | Push files to repository | Write | |
| `delete_file` | Delete file | Write · deletes | |
| `delete_repository` | Delete repository | Write · deletes | A classic token hides it without the `delete_repo` scope; a fine-grained token lists it, and GitHub refuses the call without permission |
| `star_repository` | Star repository | Write | Outside GitHub's default toolsets |
| `unstar_repository` | Unstar repository | Write | Outside GitHub's default toolsets |
| `list_starred_repositories` | List starred repositories | Read | Outside GitHub's default toolsets |

### Commits, branches, tags, releases

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `list_commits` | List commits | Read | |
| `get_commit` | Get commit details | Read | |
| `search_commits` | Search commits | Read | |
| `list_branches` | List branches | Read | |
| `create_branch` | Create branch | Write | |
| `list_tags` | List tags | Read | |
| `get_tag` | Get tag details | Read | |
| `list_releases` | List releases | Read | |
| `get_latest_release` | Get latest release | Read | |
| `get_release_by_tag` | Get a release by tag name | Read | |

### Pull requests

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `list_pull_requests` | List pull requests | Read | |
| `search_pull_requests` | Search pull requests | Read | |
| `pull_request_read` | Get details for a single pull request | Read | |
| `create_pull_request` | Open new pull request | Write | |
| `update_pull_request` | Edit pull request | Write | |
| `update_pull_request_branch` | Update pull request branch | Write | |
| `merge_pull_request` | Merge pull request | Write | |

### Reviews

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `pull_request_review_write` | Write operations (create, submit, delete) on pull request reviews | Write | |
| `add_comment_to_pending_review` | Add review comment to the requester's latest pending pull request review | Write | |
| `add_reply_to_pull_request_comment` | Add reply to pull request comment | Write | |
| `request_copilot_review` | Request Copilot review | Write | |

### Issues and labels

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `list_issues` | List issues | Read | |
| `search_issues` | Search issues | Read | |
| `semantic_issue_similarity_search` | Semantic Issue Similarity Search | Read | Outside GitHub's default toolsets |
| `issue_read` | Get issue details | Read | |
| `issue_write` | Create or update issue/pull request | Write | |
| `add_issue_comment` | Add comment to issue or pull request | Write | |
| `update_issue_comment` | Update issue comment | Write | |
| `sub_issue_write` | Change sub-issue | Write | |
| `list_issue_types` | List available issue types | Read | |
| `list_issue_fields` | List issue fields | Read | |
| `get_label` | Get a specific label from a repository | Read | |
| `list_label` | List labels from a repository | Read | Outside GitHub's default toolsets |
| `label_write` | Write operations on repository labels | Write · deletes | Outside GitHub's default toolsets |
| `ui_get` | Get UI data | Read | |

### GitHub Actions

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `actions_list` | List GitHub Actions workflows in a repository | Read | Outside GitHub's default toolsets |
| `actions_get` | Get details of GitHub Actions resources (workflows, workflow runs, jobs, and artifacts) | Read | Outside GitHub's default toolsets |
| `get_job_logs` | Get GitHub Actions workflow job logs | Read | Outside GitHub's default toolsets |
| `actions_run_trigger` | Trigger GitHub Actions workflow actions | Write · deletes | Outside GitHub's default toolsets |

### Security and dependencies

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `list_dependabot_alerts` | List dependabot alerts | Read | Outside GitHub's default toolsets |
| `get_dependabot_alert` | Get dependabot alert | Read | Outside GitHub's default toolsets |
| `list_code_scanning_alerts` | List code scanning alerts | Read | Outside GitHub's default toolsets |
| `get_code_scanning_alert` | Get code scanning alert | Read | Outside GitHub's default toolsets |
| `get_code_quality_finding` | Get code quality finding | Read | Outside GitHub's default toolsets |
| `list_secret_scanning_alerts` | List secret scanning alerts | Read | Outside GitHub's default toolsets |
| `get_secret_scanning_alert` | Get secret scanning alert | Read | Outside GitHub's default toolsets |
| `run_secret_scanning` | Run Secret Scanning | Read | |
| `check_dependency_vulnerabilities` | Check Dependency Vulnerabilities | Read | Outside GitHub's default toolsets |
| `list_global_security_advisories` | List global security advisories | Read | Outside GitHub's default toolsets |
| `get_global_security_advisory` | Get a global security advisory | Read | Outside GitHub's default toolsets |
| `list_repository_security_advisories` | List repository security advisories | Read | Outside GitHub's default toolsets |
| `list_org_repository_security_advisories` | List org repository security advisories | Read | Outside GitHub's default toolsets |

### Rulesets and custom properties

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `repository_ruleset_read` | Read repository rulesets | Read | Outside GitHub's default toolsets |
| `create_repository_ruleset` | Create repository ruleset | Write | Outside GitHub's default toolsets |
| `custom_properties_read` | Read custom properties | Read | Outside GitHub's default toolsets |
| `custom_properties_write` | Set custom properties | Write | Outside GitHub's default toolsets |

### Discussions

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `list_discussions` | List discussions | Read | Outside GitHub's default toolsets |
| `get_discussion` | Get discussion | Read | Outside GitHub's default toolsets |
| `get_discussion_comments` | Get discussion comments | Read | Outside GitHub's default toolsets |
| `list_discussion_categories` | List discussion categories | Read | Outside GitHub's default toolsets |
| `discussion_comment_write` | Manage discussion comments | Write · deletes | Outside GitHub's default toolsets |

### Projects

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `projects_list` | List GitHub Projects resources | Read | Outside GitHub's default toolsets |
| `projects_get` | Get details of GitHub Projects resources | Read | Outside GitHub's default toolsets |
| `projects_write` | Manage GitHub Projects | Write · deletes | Outside GitHub's default toolsets |

### Notifications and gists

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `list_notifications` | List notifications | Read | Outside GitHub's default toolsets |
| `get_notification_details` | Get notification details | Read | Outside GitHub's default toolsets |
| `dismiss_notification` | Dismiss notification | Write | Outside GitHub's default toolsets |
| `manage_notification_subscription` | Manage notification subscription | Write · deletes | Outside GitHub's default toolsets |
| `manage_repository_notification_subscription` | Manage repository notification subscription | Write · deletes | Outside GitHub's default toolsets |
| `mark_all_notifications_read` | Mark all notifications as read | Write | Outside GitHub's default toolsets |
| `list_gists` | List Gists | Read | Outside GitHub's default toolsets |
| `get_gist` | Get Gist Content | Read | Outside GitHub's default toolsets |
| `create_gist` | Create Gist | Write | Outside GitHub's default toolsets |
| `update_gist` | Update Gist | Write | Outside GitHub's default toolsets |

### Copilot and search helpers

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `assign_copilot_to_issue` | Assign Copilot to issue | Write | |
| `assign_copilot_to_issue_with_intent` | Assign Copilot to issue with intent | Write | Outside GitHub's default toolsets |
| `create_pull_request_with_copilot` | Perform task with GitHub Copilot coding agent | Write | |
| `get_copilot_job_status` | Get Copilot coding agent job status | Read | |
| `list_copilot_spaces` | List Copilot Spaces | Read | Outside GitHub's default toolsets |
| `get_copilot_space` | Get Copilot Space | Read | Outside GitHub's default toolsets |
| `github_support_docs_search` | GitHub Support Docs Search | Read | Outside GitHub's default toolsets |
| `web_search` | Web Search | Read | Outside GitHub's default toolsets |

### Early access (insiders mode)

| Tool | What it does | Access | Notes |
| :-- | :-- | :-- | :-- |
| `get_file_blame` | Get file blame information | Read | Early access |
| `issue_dependency_read` | Read issue dependencies | Read | Early access |
| `issue_dependency_write` | Change issue dependency | Write | Early access |

## ✂️ Reduce what Claude can use

Pick the lightest option that does what you need.

### 1. Limit the token

Grant the token fewer permissions or fewer repositories. This is the strongest limit, because GitHub enforces it whatever Claude asks for.

### 2. Block tools in your settings

A deny rule removes a tool from Claude's context. Add the rules to your Claude Code settings:

```json
{
  "permissions": {
    "deny": [
      "mcp__plugin_github-operations_github__delete_file",
      "mcp__plugin_github-operations_github__delete_repository",
      "mcp__plugin_github-operations_github__create_*"
    ]
  }
}
```

Use `mcp__plugin_github-operations_github` to block the whole server. When a tool is missing, the pull request loop reads that data through `gh` instead.

### 3. Use your own server instead

Turn the plugin's server off in `/mcp`, then add your own to the project's `.mcp.json`. Name it `github`, so the tracker agent can use its tools. This example offers every toolset but only the tools that read. It reads the token from a `GITHUB_PAT` environment variable, so start Claude Code from a shell that sets it:

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}",
        "X-MCP-Toolsets": "all",
        "X-MCP-Readonly": "true"
      }
    }
  }
}
```

Change `X-MCP-Toolsets` to a comma-separated list to narrow it, for example `issues`. Prefer the headers to a URL ending in `/readonly`: any `X-MCP-Readonly` value other than `false`, `f`, `no`, `n`, `0`, `off` or empty (spaces and letter case are ignored) counts as read-only, so a typo keeps you read-only, while a misspelled `/readonly` in the URL is ignored and leaves the write tools on. A misspelled toolset name is ignored too, and connects with no tools.

## 📚 Sources

The server, its toolsets and these tool names are GitHub's: see the [GitHub MCP Server](https://github.com/github/github-mcp-server) (MIT license, © GitHub), its [remote server guide](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md) and its [tools reference](https://github.com/github/github-mcp-server#tools). GitHub adds and changes tools, so its documentation is the reference if the two differ, and `/mcp` shows what your session actually received. Not affiliated with or endorsed by GitHub.
