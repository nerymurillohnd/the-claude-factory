# Start: from scope to an open PR

Goal: one pushed feature branch and one open PR for it. Work the steps in order and do not skip one. A step is done only when its check passes.

Tool names below are the bare names of GitHub's official MCP server. In a session they carry a prefix: `mcp__plugin_github-operations_github__<tool>` for the server this plugin bundles, or `mcp__<server>__<tool>` for a server the user configured. Match by the bare name. The server groups operations behind one tool with a `method` parameter, so do not assume a tool named after the operation exists. For local git and `gh`, check the command's own help for exact options before the first use in a run; never rely on remembered flags.

## 1. Scope

1. Confirm the repository, the changes that belong to the task, and the base branch. Take the base from the repository's default branch unless the task or an open PR says otherwise.
2. Take owner and repo from the checkout's remote when you are inside one; it avoids fork ambiguity. Use `search_repositories` only when the checkout does not say.
3. If the user gave a PR number or URL, or a PR already exists for the current branch (step 7 explains how to look), resume from the phase that PR is in: commit and push only what is missing, then go to `observe.md`. Never create a second PR.

Check: you can state repository, base branch and whether a PR already exists.

## 2. Inspect

1. Read the repository's instructions: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and the PR template. Read its recent commit history to learn the commit convention.
2. Read the local git state: current branch, uncommitted changes, whether the branch is ahead of or behind its remote, and any changes unrelated to the task. Preserve unrelated changes and never fold them into this PR.
3. Confirm which GitHub identity acts (`get_me`). Check with `list_branches` that no remote branch already has the name you intend to use.

## 3. Prepare the feature branch

1. Create or check out a feature branch off the base. Never work on the base or on a protected branch.
2. Keep only task-related changes. Set unrelated changes aside before branching.
3. Never force-push and never rewrite pushed history, including on your own branch once a PR is open.

## 4. Validate locally

1. Run the repository's own gates (formatter, linter, type check, tests, build) before creating or updating the PR.
2. Fix deterministic failures now. Do not push what you already know is red.
3. Keep each gate and its result for the final report. If the required checks are unclear, read the branch rules as the preflight in `tooling.md` describes.

## 5. Commit

1. Read the full local diff and classify the change. When it spans several topics, make one commit per topic.
2. Write each message to say what changed and why, in the repository's convention (Conventional Commits when it has none) and the session's attribution rules.
3. Let hooks run. Fix what they flag and commit again. Never skip hooks.
4. Let the configured signing setup sign the commit. If signing fails, stop and tell the user; never commit unsigned.
5. Record the commit SHA. `get_commit` and `search_commits` only verify that a commit exists on GitHub; the commit itself is made with local git.

## 6. Push

1. Check that the current branch is the intended one, not a stale or already-merged branch.
2. Push without force, setting the upstream on the branch's first push.
3. Verify that the remote branch points at the SHA you committed, using `list_branches` or `get_commit`. A successful exit status is not proof.

## 7. Create or find the PR

1. Look for an open PR from this branch first. With the MCP, use `list_pull_requests` with `head` in the form `<owner>:<branch>`, or `search_pull_requests` with a repository, PR, open and head-branch query. With `gh`, list open PRs filtered by head branch; that filter takes the bare branch name, not `owner:branch`.
2. Write the title and body as `authoring/pr-body.md` says, and check them with its script.
3. Create a PR only when none exists: `gh pr create --title <title> --body-file <body file> --base <base> --head <branch>`, with MCP `create_pull_request` (owner, repo, title, head, base, body) as the fallback. Create it ready for review unless the task asks for a draft. Request reviewers only when the task, CODEOWNERS or the repository's conventions call for it.
4. Record repository, PR URL and number, base, feature branch and head SHA in the lifecycle record.

## 8. Label the PR

Every PR carries the labels the repository uses to classify the type of change. Choose and apply them by the label rule in `authoring/pr-body.md`, with the tools in `tooling.md`, `Writes: pull requests`. The MCP label update replaces the whole list, so send the labels already on the PR with the new ones.

Check: the PR shows the intended labels and none that were there before were lost.
