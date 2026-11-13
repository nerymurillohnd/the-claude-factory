---
status: deprecated
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Run the Claude workflows in auto mode on Opus, with write permissions and a pinned action

## Scope

`.github/workflows/claude.yml` and `.github/workflows/claude-code-review.yml`.

## Context and problem statement

Both workflows used `anthropics/claude-code-action@v1`, a moving tag, read-only permissions, and no permission mode. In its own repository Anthropic runs every Claude job with `--permission-mode auto`; its examples grant write permissions. Auto mode requires, on the Anthropic API, "Claude Opus 4.6 or later, Sonnet 4.6 or later, Haiku 5.5, or a Fable model", and the action sets no model.

## Decision drivers

- A safety classifier on every tool call that no rule allows outright.
- The permissions the action needs to comment and push.
- A fixed action version.

## Considered options

- **`--permission-mode auto` and `--model claude-opus-5-5`; `contents`, `pull-requests` and `issues` at `write`; the action pinned to commit 4fa93a88de49bbef68b10eb15aabedf28ca0e1ed (v1.0.271); `persist-credentials` left at its default**: chosen by the owner.
- **Sonnet for `claude.yml`**: rejected by the owner, who keeps Opus 5.5 for both.

## Decision outcome

Chosen option: **auto mode on Opus 5.5, write permissions, a pinned action and the default checkout credentials**. `write` includes `read` in GitHub permissions. The pin uses the commit, not the annotated tag object (9008224…), which GitHub Actions cannot resolve as a commit.

### Consequences

- Good, because a tool call outside the allowed tools runs only if Claude Code's classifier passes it.
- Bad, because Opus uses more of the subscription quota than Sonnet.
- Bad, because the review job holds `contents: write`, which it does not need to comment.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| `claude-opus-5-5` works with the OAuth token in CI | The first `@claude` run and the first review | Pending | First run after the push |
| The workflows are valid | `actionlint` | Passed on 2026-11-12 | Each workflow change |

## More information

- Sources: code.claude.com `/en/permission-modes` (auto mode requirements); `anthropics/claude-code-action` at d5f7970 (`.github/workflows/claude.yml`, `claude-review.yml`, `CLAUDE.md` "Security hardening for GitHub Actions", `src/github/operations/git-config.ts`); `actions/checkout` README ("Default: true").
- Pending, not decided: trigger the review only on `opened` and `ready_for_review`, skip fork pull requests, add `timeout-minutes` and `concurrency`, load the project's plugins in `claude.yml`, pin the `code-review` plugin.
- Commit: 48f7d5c.
