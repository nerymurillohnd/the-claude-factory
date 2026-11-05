# Trust boundaries in workflows that run Claude

## Contents

- Prompt injection is limited by capability
- Shell injection is not prompt injection
- Who controls the configuration Claude loads
- Fork, Dependabot and pull_request_target designs
- Credentials, jobs and egress
- Approval and merge tools
- Verify against

## Prompt injection is limited by capability

Assume an injection in an issue, comment, diff, log or artifact succeeds, and limit what the agent can then do: its tools, its token's permissions, its network and the paths it can write. Prompt wording such as delimiters or warnings is a second layer, never the control.

## Shell injection is not prompt injection

- `${{ }}` inside `run:` expands before the shell parses the line. An event field, a PR title, a branch name or `structured_output` interpolated there is shell injection. Pass the value through `env:` and read `"$VAR"`.
- Quoting does not help: `RESULT='${{ steps.<id>.outputs.result }}'` is still injection, because a `'` in the value ends the string.
- A value passed through `env:` is still untrusted text when it reaches Claude.

## Who controls the configuration Claude loads

- In a `pull_request` job the checkout is the PR's code, so the PR's author controls `CLAUDE.md`, `.claude/settings.json`, `.claude/skills/`, `.mcp.json`, hooks, package scripts and formatter configuration in it. The action restores only the root paths listed in `action-contract.md`; anything below the root and every script stays under the PR's control.
- Take review criteria and agent configuration from the base branch, or grant only tools that make the PR-controlled files harmless: no general Bash, and no build or test of the PR in the agent's job.

## Fork, Dependabot and pull_request_target designs

- Fork and Dependabot pull requests get no secrets and no OIDC token (SE-11). Skip them with a job-level `if:` unless the design below is used.
- With `pull_request_target` or `workflow_run`, the workspace is the base branch, so the configuration Claude loads is trusted. When Claude must read the PR's head:
  1. Fetch the head outside the workspace, for example under `$RUNNER_TEMP`, and pass it with `--add-dir`.
  2. Before the run, remove or rename that copy's `.claude/`: Claude Code loads the skills, commands and agents of every `--add-dir` directory.
  3. Leave `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` unset, so the copy's `CLAUDE.md` does not load.
  4. Build, test or run nothing from the head.
- Never check out the PR's head inside the workspace under `pull_request_target`.

## Credentials, jobs and egress

- `actions/checkout` with `persist-credentials: false` in every job that does not push.
- Keep untrusted build and test runs apart from the job that holds credentials and runs the agent, and both apart from publishing. Never put deployment credentials in a workflow whose agent job untrusted events can start.
- Never `secrets: inherit`, `show_full_output: true`, `--debug` in `claude_args`, `ACTIONS_STEP_DEBUG`, `set -x` beside secrets, a broad Bash grant, or `*` in `allowed_bots` or `allowed_non_write_users` by default.
- Run Claude jobs on an egress-controlled runner when the organization has one; otherwise keep network-capable tools to the minimum.
- Pin actions, reusable workflows and plugin marketplaces to resolved commits (see `SKILL.md`). A marketplace URL runs upstream's newest code on every run.

## Approval and merge tools

- Never grant `mcp__github` as a wildcard; grant individual `mcp__github__*` tools only when the task needs them.
- Always pass `--disallowedTools` naming the GitHub MCP tools that submit reviews or change a pull request's state, resolved against the server version the pinned action uses: at the snapshot, `create_and_submit_pull_request_review`, `submit_pending_pull_request_review`, `merge_pull_request`, `update_pull_request`, `update_pull_request_branch` and `create_pull_request`, each as `mcp__github__<name>`.
- Offer formal reviews only when the user asks. A submit grant cannot be limited to `COMMENT`, so say that Claude could then approve. Whether a bot's approval counts toward required reviews is `[unverified]`; recommend a ruleset that requires a human or code-owner review.

## Verify against

- GitHub, secure use of Actions: https://docs.github.com/en/actions/reference/security/secure-use
- Claude Code, additional directories: https://code.claude.com/docs/en/skills and https://code.claude.com/docs/en/memory
- `anthropics/claude-code-action`, `docs/security.md` and `src/`: https://github.com/anthropics/claude-code-action

Verified at `anthropics/claude-code-action@c0949c5` and the documentation above on 4 November 2026.
