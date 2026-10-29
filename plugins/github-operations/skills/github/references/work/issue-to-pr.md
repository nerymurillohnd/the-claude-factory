# From an issue to a pull request

Turn one issue into a fix or feature and a PR that resolves it.

## 1. Read the issue

1. Read the issue, its comments, labels and linked PRs with MCP `issue_read`, or `gh issue view <number> --comments`.
2. Check that no open PR already addresses it: MCP `search_pull_requests` with the issue number, or `gh pr list --search <number>`.
3. When the issue lacks the facts to act (a version, the steps, the expected result), ask for them in one comment after the user approves it, and stop until they arrive.

## 2. Map the form to the PR template

Use the table in `authoring/issue.md` to pick the PR template from the issue's form: a bug report becomes a bug fix, an incident a hotfix, a feature request or idea the standard template, maintenance or a docs issue the maintenance template.

## 3. Reproduce

1. Reproduce in a throwaway worktree outside the user's checkout, as `audit/investigate.md` "Working area" says, never in the checkout itself.
2. Record the commands and their raw output: they become the PR's evidence.
3. A bug you cannot reproduce is reported back on the issue with what you tried; never fix a guess.

## 4. Build and open the PR

1. Continue at `pr/start.md`: branch, change, validate, commit, push, PR.
2. Write the body with `authoring/pr-body.md`. Write `Closes #<number>` only when the PR fully resolves the issue; write `Related #<number>` otherwise.
3. Remove the worktree once the PR exists.
