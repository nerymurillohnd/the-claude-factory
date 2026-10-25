---
name: github-workflow
description: Use for any issue, commit, push, PR, CI failure or review comment on this repo's GitHub.
---

# GitHub workflow

Nery and Claude Code are the only developers and maintainers of this marketplace: it has no outside collaborators, and pull requests from users are not accepted. Users report through issues, and every reply, label, push and merge speaks for the marketplace in public. This skill covers an issue from its first read to its closing comment, and a PR from its first commit to "ready to merge".

## Role

Act as the maintainer who answers for what goes public. You confirm before you claim, you verify a review's finding before you act on it, and you never speak, push or merge on the marketplace's behalf without Nery's word.

## Rules

- Post a reply, label or close an issue only after Nery approves it: it speaks for the marketplace in public. His order to carry a PR already covers replying to and resolving its review threads (step 6).
- Push and open a PR only on Nery's order, and push with `git push origin <branch>`, never a bare `git push`. Fix and commit freely. An order covers the action it names, on the branch it names, once: each later push, and any closing he approved in advance, is confirmed again when it happens.
- Every change inside a plugin's directory, a `README.md`-only change included, and every change to `scripts/` goes through a PR. Everything else goes by direct push or by PR, as Nery decides.
- Label every PR with labels that exist in `gh label list`.
- Reference a fixed issue as `Refs #n`, never `Closes #n`: the issue closes in step 8, once the fix is out.
- Verify each review finding against the files and the live docs before acting on it: reviewers over-report.
- The merge is Nery's. Tell him the PR is ready only when every job is green, every review is resolved and the `pr-tracker` agent (Agent tool, `subagent_type` `github-operations:pr-tracker`, given the PR number), if available, reports no issues; then wait for his green light.

## Gotchas

- A push of `main` can publish and tag a plugin that is not ready, because `release.yml` tags every plugin whose version has no tag: before any push of `main`, list those plugins (each `plugin.json` version against `git tag -l '<plugin>--v<version>'`) and confirm each is meant to ship.
- The Bash tool runs zsh, which mangles text in commit messages and PR bodies. Write them through a quoted heredoc and read them back before pushing.
- A push that fails with a broken pipe while fetch works: retry once with `git -c http.version=HTTP/1.1 push origin <branch>`.
- PR review runs through the Claude workflows in `.github/workflows/` (the `claude-review` job), not a managed review service: the account has no managed Code Review.
- `gh pr review` cannot resolve a review thread. Reply and resolve through the GraphQL mutations `addPullRequestReviewThreadReply` and `resolveReviewThread` (both exist in GitHub's GraphQL schema).
- A PR that changes `claude-code-review.yml` or `claude.yml` gets no Claude review: the action skips itself (`Skipping action due to workflow validation`) and the job still passes. Say so in the PR and check the next PR's review log.
- Labels come in families: `type:`, `status:`, `priority:`, `area:` and `plugin: <name>`, next to GitHub's default labels. A new plugin's label is created by `node scripts/sync-labels.mjs` (run `--dry-run` first), not by hand.

## Hand-offs

| When | Invoke with the Skill tool |
| :-- | :-- |
| The fix touches a plugin file (step 4) | `plugin-development`, which ends in `plugin-consistency` |
| The fix changes only docs, a README or a changelog (step 4) | `plugin-consistency` |
| The change ships a version and the PR does not carry the bump yet (before step 5), or the PR is merged (step 7, to verify the tag) | `release-and-versioning` |

A skill you invoke hands back to you when it ends: continue at your next step. When a row names the skill that invoked you, hand back to it instead of invoking it, and never re-invoke it.

## Workflow

Tick each step as you finish it; the tag says which flow a step belongs to, and an issue fixed through a PR follows both.

Progress:
- [ ] 1. **Triage** (issue, PR): what arrived and which flow it needs.
- [ ] 2. **Confirm** (issue): reproduce it or check it against code and docs.
- [ ] 3. **Reply** (issue): labels and an English draft for Nery's approval.
- [ ] 4. **Fix** (issue, PR): root cause, in a PR that references the issue.
- [ ] 5. **Push** (issue, PR): gates, then push and open the PR, only on Nery's order.
- [ ] 6. **Carry** (PR): failed jobs and reviews until nothing is open.
- [ ] 7. **Ready to merge** (PR): stop, report and wait; then verify the release.
- [ ] 8. **Close out** (issue): the fixed issues, once the release is verified.

## Step details

### 1. Triage

Decide what you were given: a new issue, a PR to carry, a push or PR order, or a CI request. For issues, `gh issue list --state open --label "status: triage"` and `--label "status: needs-info"` list the ones awaiting you, and `gh issue view <n> --comments` shows one in full. Pick the steps that apply from the checklist above.

### 2. Confirm

Reproduce the report with the plugin loaded through `claude --plugin-dir plugins/<name>`, or confirm it against the plugin's README, the current code and the live official docs. State which of the two you did and quote the evidence. Read the entries about that plugin in `.claude/memory/MEMORY.md` first: a known limit changes what "confirmed" means. A report you could not confirm is `status: needs-info`, with exactly what is missing.

### 3. Reply

1. Choose the plugin label (`plugin: <name>`), one `type:` label for the kind of report (`type: bug`, `type: enhancement`, `type: plugin-idea`, `type: documentation` or `type: question`), and one outcome:
   - `status: confirmed` with a `priority:` (high: core broken for many users; medium: a workaround exists; low: nice to have).
   - `status: needs-info`: list exactly what is missing.
   - `status: duplicate`: link the original.
   - `status: upstream`: Claude Code or a third party is the cause; link where to report it.
   - `status: wontfix`: out of scope or working as intended; explain why.
2. Draft the reply in English: specific to this report, courteous, no internal detail (no `.claude/`, no process).
3. Show Nery a table, one row per issue (e.g. `#14 · plugin: <name>, type: bug, status: confirmed, priority: medium · confirmed · "Thanks, reproduced on …"`), and wait for his approval. Then post with `gh issue edit <n> --add-label "<labels>" --remove-label "<old status>"` (omit that flag if the issue had no status label) and `gh issue comment <n> --body-file <file>`.
4. If a report discloses a vulnerability in public, or you are unsure whether it does, such as a bypass of a safety hook, treat it as one until Nery decides: tell him at once, repeat none of the details in any reply, commit message, PR text or changelog, and propose moving it to a private security advisory. His order to fix the report does not answer this; ask.

### 4. Fix

Run `git status --short` first: changes that are not yours stay out of the commit. Branch off `origin/main` after `git fetch`, never off a local `main` that is ahead of it (`git log origin/main..HEAD` must be empty), or the PR carries unpublished commits. Fix the confirmed cause and not the symptom, and commit in separate, signed commits grouped by topic. A commit message says what changed and why; write it through a quoted heredoc. Reference the issue as `Refs #n`. Before you write each plugin file invoke `plugin-development`, and for docs `plugin-consistency`, as the table above says; commit after they hand back, so the bump and the changelog are in the commits the PR carries. The PR opens in step 5.

### 5. Push

Run the checks in `.claude/CLAUDE.md` → Maintainer and Plugin Scopes (Maintainer Tooling, Plugin Tooling) on what the branch changes, and stop at the first failure. On Nery's order, push with `git push origin <branch>`, read the Gotchas above if it fails, and open the PR with its labels (Rules). Each later push is a new order.

### 6. Carry

Loop until nothing is left:

1. Read the failed jobs (`gh pr checks <n>`, then `gh run view <run-id> --log-failed`) and every review and comment, from Claude and from third parties (`gh pr view <n> --comments`, `gh api repos/nerymurillohnd/the-claude-factory/pulls/<n>/comments`).
2. Verify each finding (Rules) and note the ones that do not hold, with the evidence.
3. Fix the root cause and commit; a fix to a plugin file goes through the step 4 hand-offs again. Do not push yet.
4. Reply to each review and resolve its thread. This is part of carrying the PR and needs no separate approval; the push does.
5. Push the fixes as in step 5, then repeat until every job is green and no review, issue or failed job remains.

### 7. Ready to merge

Tell Nery what the PR changed, the state of every job and review, and anything you did not verify, then wait for his green light. If the PR is still open on a later day than its root `CHANGELOG.md` line, move the line first (`release-and-versioning` step 8). The merge is his; you learn of it from him or from `gh pr view <n> --json mergedAt`. After it, invoke `release-and-versioning` for its steps 9 and 10 to confirm the tag and the release; it hands back here.

### 8. Close out

For each fixed issue, draft in English the comment that says what was fixed and that it is released, show it to Nery, and with his approval post it, run `gh issue edit <n> --add-label "status: released" --remove-label "<its current status label>"` (read it with `gh issue view <n>`) and close the issue.
