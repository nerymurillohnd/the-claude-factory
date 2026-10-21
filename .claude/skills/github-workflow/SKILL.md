---
name: github-workflow
description: Applies the repo's rules for issues, commits, pushes and PRs; use whenever you handle an issue or touch GitHub.
---

# GitHub workflow

Nery and Claude Code are the only developers and maintainers of this marketplace: it has no outside collaborators, and pull requests from users are not accepted. Users report through issues, and every reply, label, push and merge speaks for the marketplace in public. This skill covers an issue from its first read to its closing comment, and a PR from its first commit to "ready to merge".

## Role

Act as the maintainer who answers for what goes public. You confirm before you claim, you verify a review's finding before you act on it, and you never speak, push or merge on the marketplace's behalf without Nery's word.

## Rules

- Post a reply, label or close an issue only after Nery approves it: it speaks for the marketplace in public.
- Push and open a PR only on Nery's order, and push with `git push origin <branch>`, never a bare `git push`. Fix and commit freely. An order covers the action it names, on the branch it names, once: each later push, and any closing he approved in advance, is confirmed again when it happens.
- Every edit to a plugin's `plugin.json`, skills (`SKILL.md` and its files), agents, hooks, `.mcp.json`, `.lsp.json` or dependencies goes through a PR. Everything else goes by direct push or by PR, as Nery decides.
- Label every PR with labels that exist in `gh label list`.
- Reference a fixed issue as `Refs #n`, never `Closes #n`: the issue closes in the release step, once the fix is out.
- Verify each review finding against the files and the live docs before acting on it: reviewers over-report.
- Stop at ready to merge, tell Nery, and wait for his green light. Merge only when every job is green, every review is resolved and the `pr-tracker` agent, if available, reports no issues.
- When Nery asks for CI work, offer the open CI items one by one before anything new: recall memory `ci-simplify-skipped-findings`.

## Gotchas

- A push of `main` can publish and tag a plugin that is not ready: before any push of `main`, recall memory `main-holds-unreleased-hook-workbench`.
- The Bash tool runs zsh, which mangles text in commit messages and PR bodies. Write them through a quoted heredoc and read them back before pushing: recall memory `zsh-modifiers-in-shell-strings`.
- A push that fails with a broken pipe while fetch works: retry once with `git -c http.version=HTTP/1.1 push origin <branch>` and recall memory `github-push-http1-workaround`.
- PR review runs through the Claude workflows in `.github/workflows/` (the `claude-review` job), not a managed review service: recall memory `claude-plan-pro-max`.
- `gh pr review` cannot resolve a review thread. Reply and resolve through the GraphQL mutations `addPullRequestReviewThreadReply` and `resolveReviewThread` (both exist in GitHub's GraphQL schema).
- Labels come in families: `type:`, `status:`, `priority:`, `area:` and `plugin: <name>`, next to GitHub's default labels. A new plugin's label is created by `node .github/scripts/sync-labels.mjs` (run `--dry-run` first), not by hand.

## Workflow

Tick each step as you finish it. Steps 2 and 3 apply to an issue, step 5 to a PR; steps 1, 4, 6 and 7 apply to both.

Progress:
- [ ] 1. **Triage**: what arrived and which flow it needs.
- [ ] 2. **Confirm**: reproduce the issue or check it against code and docs.
- [ ] 3. **Reply**: labels and an English draft for Nery's approval.
- [ ] 4. **Fix**: root cause, in a PR that references the issue.
- [ ] 5. **Carry**: failed jobs and reviews until nothing is open.
- [ ] 6. **Push**: only on Nery's order, after the gates.
- [ ] 7. **Close out**: ready to merge, then release and report.

## Step details

### 1. Triage

Decide what you were given: a new issue, a PR to carry, a push or PR order, or a CI request. For issues, `gh issue list --state open --label "status: triage"` and `--label "status: needs-info"` list the ones awaiting you, and `gh issue view <n> --comments` shows one in full. Pick the steps that apply from the checklist above.

### 2. Confirm

Reproduce the report with the plugin loaded through `claude --plugin-dir plugins/<name>`, or confirm it against the plugin's README, the current code and the live official docs. State which of the two you did and quote the evidence. Read the entries about that plugin in `.claude/memory/MEMORY.md` first: an open app check or a known limit changes what "confirmed" means. A report you could not confirm is `status: needs-info`, with exactly what is missing.

### 3. Reply

1. Choose the plugin label (`plugin: <name>`), one `type:` label for the kind of report (`type: bug`, `type: enhancement`, `type: plugin-idea`, `type: documentation` or `type: question`), and one outcome:
   - `status: confirmed` with a `priority:` (high: core broken for many users; medium: a workaround exists; low: nice to have).
   - `status: needs-info`: list exactly what is missing.
   - `status: duplicate`: link the original.
   - `status: upstream`: Claude Code or a third party is the cause; link where to report it.
   - `status: wontfix`: out of scope or working as intended; explain why.
2. Draft the reply in English: specific to this report, courteous, no internal detail (no `.claude/`, no process).
3. Show Nery a table of issue · labels · outcome · reply and wait for his approval. Then post with `gh issue edit <n> --add-label "<labels>" --remove-label "<old status>"` (omit that flag if the issue had no status label) and `gh issue comment <n> --body-file <file>`.
4. If a report discloses a vulnerability in public, or you are unsure whether it does, such as a bypass of a safety hook, treat it as one until Nery decides: tell him at once, repeat none of the details in any reply, and propose moving it to a private security advisory.

### 4. Fix

Run `git status --short` first: changes that are not yours stay out of the commit. Branch off `origin/main` after `git fetch`, never off a local `main` that is ahead of it (`git log origin/main..HEAD` must be empty), or the PR carries unpublished commits. Fix the confirmed cause and not the symptom, and commit in separate, signed commits grouped by topic. A commit message says what changed and why; write it through a quoted heredoc. Reference the issue as `Refs #n`. Follow `plugin-development` and `plugin-consistency` for any plugin or docs file you touch. Open the PR only on Nery's order and label it.

### 5. Carry

Loop until nothing is left:

1. Read the failed jobs (`gh pr checks <n>`, then `gh run view <run-id> --log-failed`) and every review and comment, from Claude and from third parties (`gh pr view <n> --comments`, `gh api repos/nerymurillohnd/the-claude-factory/pulls/<n>/comments`).
2. Verify each finding against the files and the docs before acting on it. Note the ones that do not hold, with the evidence.
3. Fix the root cause and commit. Do not push yet.
4. Reply to each review and resolve its thread. This is part of carrying the PR and needs no separate approval; the push does.
5. Repeat until every job is green and no review, issue or failed job remains.

### 6. Push

Run the "Before Every Push" gates in `.claude/CLAUDE.md` → Commands, in order, and stop at the first failure. Push only after Nery says so, with `git push origin <branch>`, and read the Gotchas above if it fails.

### 7. Close out

Stop at ready to merge: tell Nery what the PR changed, the state of every job and review, and anything you did not verify, then wait for his green light. After the merge, follow the `release-and-versioning` skill to confirm the tag and the release; then draft, in English, the comment on each fixed issue saying what was fixed, show it to Nery, and with his approval post it, label the issue `status: released` and close it.
