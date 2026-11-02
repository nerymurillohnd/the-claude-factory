---
status: accepted
date: 2026-11-01
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-26_claude-workflows-follow-the-official-template
superseded-by: none
---

# The Claude workflows pin their actions by SHA, Dependabot bumps them, and the review skips Dependabot's pull requests

## Scope

Applies to `.github/workflows/claude.yml` and `.github/workflows/claude-code-review.yml`: how `anthropics/claude-code-action`, `actions/checkout` and the runner are referenced, and which pull requests the `claude-review` job runs on. The action's inputs and the Claude Code that Validate installs are out of scope.

## Context and problem statement

ADR_2026-10-26_claude-workflows-follow-the-official-template chose the `/install-github-app` template: `claude-code-action@v1`, `actions/checkout@v4` and `ubuntu-latest`. On 2026-10-27, commit 7854162 pinned both workflows again, without a record: checkout v7.0.1 and claude-code-action v1.0.263 by SHA, and `ubuntu-24.04`. Its reasons were that `checkout@v4` targets Node.js 20 and draws GitHub's deprecation warning, and that `ubuntu-latest` moves to Ubuntu 26 (actions/runner-images#14748). So the workflows contradicted the accepted ADR.

The pin made Dependabot open bump pull requests, and their `claude-review` check failed: run 41366451860 ([#76](https://github.com/nerymurillohnd/the-claude-factory/pull/76)) logged that a non-human actor is not allowed. Dependabot's runs get only Dependabot secrets, and the repository has none, so `CLAUDE_CODE_OAUTH_TOKEN` is empty in them. [#75](https://github.com/nerymurillohnd/the-claude-factory/pull/75) passed only because the action skipped itself on a pull request that changes its own workflow file. Run 41366435437 says so: "Action skipped due to workflow validation error". Releases v1.0.264 and v1.0.265 of the action change nothing about bots.

## Decision drivers

- A reference that cannot move under the workflow keeps unreviewed code away from the OAuth token: the superseded ADR listed a moved `v1` tag as its main risk.
- No pinned action targets a deprecated Node.js runtime, and the runner does not change Ubuntu release on its own.
- A check that fails on every Dependabot pull request hides real failures.
- The OAuth token never reaches a job a bot starts.

## Considered options

- **Pin by SHA, let Dependabot bump the pins, and skip `claude-review` on Dependabot's pull requests**: chosen.
- **Return to `@v1` and the template, and skip Dependabot's pull requests**: rejected because the template's `checkout@v4` targets Node.js 20 and `ubuntu-latest` changes release under the workflow.
- **Allow `dependabot[bot]` with `allowed_bots` and copy the token to the Dependabot secrets**: rejected because it hands Nery's OAuth token to jobs a bot starts.

## Decision outcome

Chosen option: **pin by SHA, Dependabot bumps, skip Dependabot's pull requests**, because the reviewed commit is the one that runs, the deprecation and runner drift are gone, and a Dependabot pull request no longer shows a failure that is not one.

- `claude-review` carries `if: github.event.pull_request.user.login != 'dependabot[bot]'` (db33556).
- Dependabot's `github-actions` entry proposes each new action release as a pull request; Nery merges it.

### Consequences

- Good, because the action that runs with the token is the commit Nery merged.
- Good, because Dependabot pull requests show a skipped review instead of a failed one.
- Bad, because the reviewer runs the Claude Code that the pinned action bundles until the next bump is merged, the lag the superseded ADR wanted to remove.
- Bad, because Dependabot's own pull requests get no Claude review.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| `claude-review` is skipped on a Dependabot pull request | The job's conclusion on #75 and #76 after their rebase | Pending | After the rebase |
| `claude-review` still runs on Nery's pull requests | The job runs on the next pull request Nery opens | Pending | The next pull request |

## More information

Nery decided on 2026-11-01, from the consolidated audit of 2026-11-01. The same day he chose to merge #75 and #76 and to close [#77](https://github.com/nerymurillohnd/the-claude-factory/pull/77) (TypeScript 7), and `dependabot.yml` now ignores TypeScript majors.
