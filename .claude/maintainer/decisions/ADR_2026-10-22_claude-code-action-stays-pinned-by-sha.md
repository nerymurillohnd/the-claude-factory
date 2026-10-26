---
status: superseded
date: 2026-10-22
decision-makers:
  - "Nery"
supersedes: none
superseded-by: ADR_2026-10-26_claude-workflows-follow-the-official-template
---

# claude-code-action stays pinned to a commit SHA

## Scope

Applies to `anthropics/claude-code-action` in `.github/workflows/claude-code-review.yml` and `.github/workflows/claude.yml`. The Claude Code that Validate and Evals install is covered by ADR_2026-10-21_ci-installs-claude-code-from-signed-apt.

## Context and problem statement

The Claude reviewer on [PR #43](https://github.com/nerymurillohnd/the-claude-factory/pull/43) ran Claude Code 2.1.304, below the v2.1.307 that project-maintainer 0.2.0 requires. The action hardcodes the Claude Code version it installs, so the version follows the action's pin. Nery asked which version CI would use if the pin were removed.

## Decision drivers

- The CI reviewer should run the Claude Code version the plugins target.
- An action that holds the Claude OAuth token must not change under the repository without review.

## Considered options

- **Keep the SHA pin and bump it when the action releases (Dependabot weekly, or by hand)**: chosen.
- **Use a moving tag such as `@v1`**: rejected because a moved or compromised tag would run unreviewed code with the Claude token.
- **Point `path_to_claude_code_executable` at the apt-installed latest**: rejected because the action warns that pairing it with another Claude Code version can break it.

## Decision outcome

Chosen option: **keep the SHA pin and bump it**, because it keeps the reviewed-code guarantee and costs one small PR per release.

### Consequences

- Good, because every action change is a reviewed diff.
- Bad, because the reviewer lags the latest Claude Code until the next bump.
- Bad, because a PR that changes the action's workflow gets no Claude review: the action skips itself when the workflow differs from the default branch.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The reviewer installs Claude Code 2.1.308 | The next PR's `claude-review` log: `Installing Claude Code v2.1.308...` | Pending: PR #44 skipped the review by design | The next pull request |

## More information

Bumped to v1.0.258 (commit `6b6870e649b5ff408753befeaee5fc7989d4e6a9`) in [PR #44](https://github.com/nerymurillohnd/the-claude-factory/pull/44). The four upstream commits since v1.0.254 only bump Claude Code and the Agent SDK.
