---
status: accepted
date: 2026-10-26
decision-makers:
  - "Nery"
supersedes: ADR_2026-10-22_claude-code-action-stays-pinned-by-sha
superseded-by: none
---

# The Claude workflows follow the official `/install-github-app` template

## Scope

Applies to `.github/workflows/claude.yml` and `.github/workflows/claude-code-review.yml`: the `anthropics/claude-code-action` reference, the `actions/checkout` reference and `runs-on`. The inputs of the action (`claude_args`, `--allowedTools`, `plugin_marketplaces`, triggers, permissions) are out of scope. The Claude Code that Validate and Evals install is covered by ADR_2026-10-21_ci-installs-claude-code-from-signed-apt.

## Context and problem statement

ADR_2026-10-22_claude-code-action-stays-pinned-by-sha pinned the action to a commit SHA and accepted that the reviewer lags the latest Claude Code until each bump. That lag is what it was meant to fix: on [PR #43](https://github.com/nerymurillohnd/the-claude-factory/pull/43) the reviewer ran Claude Code 2.1.304, below the v2.1.307 a plugin required. On 2026-10-26 Nery ran `/install-github-app`, which opened [PR #51](https://github.com/nerymurillohnd/the-claude-factory/pull/51) with the official template: `anthropics/claude-code-action@v1`, `actions/checkout@v4` and `ubuntu-latest`. Nery merged it and stated that it corrects what the repository was doing wrong. Should the workflows keep the SHA pins or follow the official template?

## Decision drivers

- The CI reviewer should run the current Claude Code, which the plugins target.
- Official documentation and the official setup command outrank project rules.
- No recurring manual bump for the maintainer, who works alone.

## Considered options

- **Follow the official template, with `claude-code-action@v1`**: chosen.
- **Keep the SHA pin and bump it through Dependabot**: rejected because the reviewer runs an older Claude Code between bumps, as on PR #43, and every release costs a PR.

## Decision outcome

Chosen option: **follow the official template**, because `v1` is a moving tag that follows each release of the action, so the reviewer always installs the action's current Claude Code, and it is the form every example of `/en/github-actions` uses.

### Consequences

- Good, because the reviewer stays on the current Claude Code with no bump PRs.
- Good, because the workflows match what `/install-github-app` writes, so running it again changes nothing.
- Bad, because a moved or compromised `v1` tag runs unreviewed code with the `CLAUDE_CODE_OAUTH_TOKEN` secret; the trust moves to Anthropic's release process.
- Bad, because the template's `actions/checkout@v4` is older than the v7.0.1 the repository pinned before, and older than the `@v6` in the `/en/github-actions` cloud-provider examples.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| `v1` follows the latest release | `gh api repos/anthropics/claude-code-action/git/tags/<v1 tag object>` against the newest `v1.0.*` tag | Passed on 2026-10-26: `v1` → `925afb5`, the commit of v1.0.262 (2026-10-24) | When a reviewer run shows an older Claude Code than expected |
| The reviewer installs the current Claude Code | The next PR's `claude-review` log, line `Installing Claude Code v…` | Pending: no PR has run since PR #51 | The next pull request |

## More information

Decided by Nery on 2026-10-26, after merging PR #51. The three commits of PR #51 (`b0c6474`, `9c6ae56`, merge `5ea20b8`) were made by the GitHub app and are not signed. Dependabot [PR #49](https://github.com/nerymurillohnd/the-claude-factory/pull/49), which bumps the old SHA pin, no longer applies to these workflows.
