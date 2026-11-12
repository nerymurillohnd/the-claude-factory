# GitHub access

How each step reads and writes GitHub, in an order that works on the user's computer, in Claude Code on the web and where `gh` is missing.

## Contents

- Order of routes
- When GraphQL is blocked
- Operations
- What has no API

## Order of routes

For every operation below, use the first route that works, and move to the next one when a route is missing, errors, returns 403 or 404, or returns nothing where data must exist:

1. **The GitHub MCP server.** Its tools load on demand: before the first call, load them with `ToolSearch` (query `+github`). Its result also names a GitHub server that failed to connect; then skip to `gh`. Their full names depend on the server (`mcp__github__…` for a server the user added as `github`, another prefix for a claude.ai connector), so match them by the tool name. The `labels` and `discussions` toolsets are not in the server's default set: when `list_label` or `list_discussion_categories` is missing, the server runs without them.
2. **`gh api` with a REST path.** It needs `gh` installed and signed in (`gh auth status`).
3. **`gh api graphql`**, only for what has no REST endpoint (discussion categories, contact links).
4. **The user.** Name the page in GitHub's settings and what to read or change there.

Report something as out of reach only after every route failed, with each error.

## When GraphQL is blocked

Some environments block GitHub's GraphQL API while REST works. Claude Code on the web answers every GraphQL call with `HTTP 403: GitHub GraphQL is not available from Claude Code sessions; use the REST API`. That 403 is a blocked route, not a missing permission: move to the REST route of the same row, or to the user.

Claude Code on the web also binds a session to its repositories: an `orgs/…` or `users/…` path, or another repository's path, returns 403 "sessions are bound to their configured repositories". Read those facts through the MCP server, or ask the user.

Several `gh` commands use GraphQL even though they look like REST: `gh repo view --json`, `gh label list`, `gh label clone`, `gh pr view --json` and `gh issue list --json`. `gh label create`, `gh label edit`, `gh label delete` and `gh api repos/…` use REST.

## Operations

| Operation | MCP, first | `gh api` REST, next | Otherwise |
| :-- | :-- | :-- | :-- |
| Visibility, default branch, Discussions on, your permission | — | `gh api repos/<owner>/<repo> --jq '{visibility, private, default_branch, has_discussions, has_issues, permissions}'` | Ask the user |
| Private vulnerability reporting on | — | `gh api repos/<owner>/<repo>/private-vulnerability-reporting --jq .enabled` | Ask the user whether private vulnerability reporting is on in the repository's security settings |
| Files on the default branch, including the owner's `.github` repository | `get_file_contents` | `gh api repos/<owner>/<repo>/contents/<path>` | Read the local clone |
| The repository's labels | `list_label` (paginate with `after`) | `python3 <skill-dir>/scripts/labels-sync.py` reads them through REST | — |
| Create or update a label | `label_write` (`method: create` or `update`; color without `#`) | `labels-sync.py --apply`, or `gh label create "<name>" --color <hex> --description "<text>" --force` | Ask the user to create it in **Issues → Labels** |
| Merge settings, read and change | No MCP tool edits them | `gh api repos/<owner>/<repo>` to read; `gh api --method PATCH repos/<owner>/<repo> -f …` to change ([merge-message-setting.md](merge-message-setting.md)) | **Settings → General → Pull Requests** |
| Discussion categories and their slugs | `list_discussion_categories` lists names and IDs only, with no slug | No REST endpoint | `gh api graphql` ([discussion-forms.md](discussion-forms.md)), or the slug from each category's URL |
| Issue types the repository can use (organization and personal accounts) | — | `gh api repos/<owner>/<repo>/issue-types --jq '.[].name'` | Ask the user |
| CODEOWNERS errors after the merge | — | `gh api "repos/<owner>/<repo>/codeowners/errors?ref=<branch>"` | The file's page on GitHub highlights errors |
| Community profile of a public repository | — | `gh api repos/<owner>/<repo>/community/profile` | **Insights → Community standards** |

## What has no API

- No API creates a discussion category: the user creates it in **Settings → Discussions** (up to 25 per repository).
- No MCP tool changes a repository's merge settings.
