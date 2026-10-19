# Start: from scope to an open PR

Goal: one pushed feature branch and one open PR for it. Tool names are the bare names of GitHub's official MCP server. In a session they carry a prefix: `mcp__plugin_github-operations_github__<tool>` for the server this plugin bundles, or `mcp__<server>__<tool>` for a server the user configured. Match by the bare name. The server groups operations behind one tool with a `method` parameter, so do not assume a tool named after the operation exists.

## 1. Scope

- Confirm the repository (several repositories are independent units), the changes that belong to the task, and the base branch. Take the base from the repository default unless the task or an open PR says otherwise.
- Derive owner and repo from `git remote -v` when inside a checkout. It avoids fork ambiguity. `search_repositories` locates a repository by name when the checkout does not say.

## 2. Inspect

- Read the repository instructions (`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, the PR template).
- Read the local git state: current branch, uncommitted changes, ahead or behind the remote, unrelated changes. Preserve unrelated changes; never fold them into this PR.
- `get_me` confirms which GitHub identity acts. `list_branches` checks for an existing remote branch with the name you intend to use.

## 3. Prepare the feature branch

- Create or check out a feature branch off the base. Never work on the base or a protected branch.
- Keep only task-related changes. Set unrelated changes aside before branching.
- Never force-push and never rewrite pushed history, including on your own branch once a PR is open.

## 4. Validate locally

- Run the repository's own gates (formatter, linter, type check, tests, build) before creating or updating the PR.
- Fix deterministic failures now. Do not push what you already know is red.
- Keep each command and its result for the final report. If the required checks are unclear, read the branch rules (Preflight in the tool matrix).

## 5. Commit

- Read the full local diff, classify the change, and write a message that matches the repository history and the session's attribution rules.
- Let hooks run; fix what they flag and retry. Never use `--no-verify`. Record the commit SHA.
- `get_commit` and `search_commits` only verify a commit's presence on GitHub. The commit itself is local git.

## 6. Push

- Check the current branch is the intended one, not a stale or already-merged branch. Push without `--force`.
- Verify afterwards that the remote branch points at the SHA you committed (`list_branches` or `get_commit`). Exit code 0 is not proof.

## 7. Create or find the PR

- Search for an open PR from this branch first: `search_pull_requests` with a query such as `repo:owner/name is:pr is:open head:branch-name`, or `list_pull_requests` filtered by `head`.
- Create one only when none exists: `create_pull_request` with `owner`, `repo`, `title`, `head`, `base`, and optional `body`, `draft`, `reviewers`. Build the title and body from the commit history and the repository's PR template: what changed, why, how it was validated, risks.
- Label every PR, following the repository's conventions: `issue_write` with `method: update`, `issue_number` set to the PR number, and `labels`.
- Record repository, PR URL and number, base, feature branch and head SHA in the lifecycle record.
