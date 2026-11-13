# Trust boundaries in workflows that run Claude

What actually limits an agent in a GitHub workflow, and which designs keep untrusted text, code and configuration away from its credentials. The claude-code-action facts these rules rest on are in [action-contract.md](action-contract.md).

**Contents**
- [What limits an agent in each mode](#what-limits-an-agent-in-each-mode)
- [Shell injection is not prompt injection](#shell-injection-is-not-prompt-injection)
- [Configuration Claude reads](#configuration-claude-reads)
- [Fork, Dependabot and pull_request_target designs](#fork-dependabot-and-pull_request_target-designs)
- [Credentials in a Claude job](#credentials-in-a-claude-job)
- [Approval, merge and branch-write tools](#approval-merge-and-branch-write-tools)

## What limits an agent in each mode

Assume an injection in an issue, comment, diff, log or artifact succeeds, and judge a workflow by what the agent can then do. Prompt wording, delimiters and warnings are never the control.

| Control | Under auto | Under acceptEdits or Manual |
| :-- | :-- | :-- |
| A tool or command left out of `--allowedTools` | **Doesn't limit it.** The call goes to Claude Code's safety review and runs if it passes | Limits it: the call is denied |
| A deny rule (`--disallowedTools`, the untrusted-PR list) | Limits it | Limits it |
| `--tools` | Removes built-in tools from the session | Same |
| The token's permissions | Limit what any call can do on GitHub | Same |
| The runner's network | Limits where data can go | Same |

Which mode a step runs in: [Permission mode](action-contract.md#permission-mode). So:

- Under auto, every capability you want removed needs a deny rule, or a strict mode set in `claude_args` with a strict allow list. A missing grant is not a limit.
- Only the actor's own text is the request, but Claude still reads everyone else's text as context ([Actor and text trust](action-contract.md#actor-and-text-trust)). A maintainer who labels or assigns an outsider's issue hands its body to Claude.
- CI logs and job names on an outside pull request are text the pull request controls ([Untrusted pull requests](action-contract.md#untrusted-pull-requests)).

## Shell injection is not prompt injection

- `${{ }}` inside `run:` expands before the shell parses the line. An event field, a title, a branch name or `structured_output` interpolated there is shell injection; quoting doesn't help. Pass the value through `env:` and read `"$VAR"`.
- A value passed through `env:` is still untrusted text when it reaches Claude.
- Text a step prints can also be read by the runner as a workflow command (W-13).

## Configuration Claude reads

- **Who controls it.** In tag mode on an open pull request the workspace is the pull request's head; in agent mode it is whatever the workflow checked out ([Configuration restored from the base branch](action-contract.md#configuration-restored-from-the-base-branch)). Only the restored root paths come from the base. Nested `CLAUDE.md`, `.claude/rules/` and `.claude/skills/`, package scripts, task runners and formatter configuration stay under the pull request's control.
- **To keep a pull request's code from running in the agent's job**, take review criteria and agent configuration from the base branch, with nothing of the head in the workspace. When the job must have the head's files in the workspace (tag mode on a pull request event), deny Bash, or the commands that run code, in `--disallowedTools`, or set a strict mode in `claude_args` with an allow list that runs no code; layer F then stays a finding, because the head's nested configuration still loads.
- **The untrusted-PR deny list helps, but only so far.** It covers authors without write access, not trusted authors, issues or `workflow_run`, and it is not a sandbox ([Untrusted pull requests](action-contract.md#untrusted-pull-requests)). Never build or test the pull request in the agent's job.
- `--add-dir` on a copy of the head loads its skills, commands, agents and plugins.

## Fork, Dependabot and pull_request_target designs

- **What GitHub gives these runs.** A fork's `pull_request` run gets no secrets and a read-only `GITHUB_TOKEN`; write scopes, `id-token` among them, are downgraded to read unless an admin of a private repository enables sending write tokens. A Dependabot run gets Dependabot secrets, not Actions secrets, and a read-only token that `permissions:` can raise [unverified: whether that allows `id-token: write`; GitHub's Dependabot-on-Actions docs or one run settle it]. Skip both with a job-level `if:` unless the design below is used.
- **`workflow_run`** gets secrets and write tokens even when the run that triggered it didn't, and the untrusted-PR deny list never applies to it.
- **`pull_request_target`** runs with the base's privileges. GitHub's new default policy blocks it in public repositories that set no Actions event policy; the enforcement date is in [the Snapshot](version-drift.md#snapshot).
- **Tag mode on `pull_request_target`** (`track_progress`) checks out the open pull request's head into the workspace itself. Treat that job like a `pull_request` job with the base's secrets (W-02).
- **When Claude must read the head** under `pull_request_target` or `workflow_run`:
  1. Fetch the head outside the workspace, for example under `$RUNNER_TEMP`, and pass it with `--add-dir`. `actions/checkout` v7 and its backports refuse this unless `allow-unsafe-pr-checkout: true` is set: set it only here, with a comment saying why.
  2. Before the run, remove or rename that copy's `.claude/`.
  3. Leave `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` unset, so the copy's `CLAUDE.md` doesn't load.
  4. Build, test or run nothing from the head.
- Never check out the pull request's head inside the workspace under `pull_request_target`.

## Credentials in a Claude job

- **Checkout's credential.** Set `persist-credentials: false` on the checkout in every job that doesn't push with it, the Claude job included: the action doesn't remove the credential that `actions/checkout` v6 and later leave ([Git, branches and credentials](action-contract.md#git-branches-and-credentials)). Its cost is in [Costs of each change](auth-and-permissions.md#costs-of-each-change).
- **Everything in the step's environment reaches the session** ([Environment variables the action passes](action-contract.md#environment-variables-the-action-passes)). Never put deployment credentials, or secrets the task doesn't need, in a job whose agent untrusted events can start.
- **Steps after Claude in the same job** run with what the session left: edited workspace files, and the action's token in `origin`'s URL unless it was revoked ([Session guard](action-contract.md#session-guard)). Don't run workspace code with secrets after Claude in the same job.
- Keep untrusted build and test runs apart from the job that runs the agent, and both apart from publishing.
- In a workflow file or repository variable, never `secrets: inherit`, `ACTIONS_STEP_DEBUG`, `set -x` beside secrets, a broad Bash grant, or `*` in `allowed_bots` or `allowed_non_write_users`. `show_full_output` and `--debug` follow C-14; a one-off debug rerun is step 6 of [the diagnosis](claude-step-diagnosis.md#6-hand-off-or-propose-the-fix), with the user's approval.
- Run Claude jobs on an egress-controlled runner when the organization has one; otherwise deny the network tools the job doesn't need in `--disallowedTools` (`WebFetch`, `WebSearch`, `Monitor`), as layer B in [auto-mode-audit.md](auto-mode-audit.md#3-check-each-layer) says; Bash can reach the network too.
- Pin actions, reusable workflows and plugin marketplaces to resolved commits ([Pick the newest release](version-drift.md#pick-the-newest-release)).

## Approval, merge and branch-write tools

- **Never grant `mcp__github` or `mcp__github__*`.** Once any GitHub MCP tool is granted, the server exposes all of its tools ([Tools the action grants](action-contract.md#tools-the-action-grants-and-the-mcp-servers-it-starts)). Grant individual `mcp__github__<name>` tools the task needs.
- **Deny the whole class** in `--disallowedTools`, as `mcp__github__<name>`, read from `pkg/github/tools.go` at the pinned image's commit: every tool that creates, edits, submits or deletes a review or a pending review, merges, changes a pull request's state or reviewers, updates its branch, creates a pull request or requests a review, and the branch writers (`push_files`, `create_or_update_file`, `delete_file`, `create_branch`) unless the task needs them. Under auto these deny rules are the only hard block.
- **Formal reviews only when the user asks.** A grant to submit a review can't be limited to `COMMENT`, so say that Claude could then approve. Whether a bot's approval counts toward required reviews is [unverified: GitHub's branch-protection docs don't state it]; recommend a ruleset that requires a human or code-owner review.
- **Branch protection still matters.** A fork's pull request pushes to `pr-N` in the base repository, but a pull request opened from the default branch can update the default branch.

## Verify against

- GitHub, secure use of Actions: https://docs.github.com/en/actions/reference/security/secure-use
- GitHub, events that trigger workflows (fork and Dependabot runs): https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- Claude Code, permissions: https://code.claude.com/docs/en/permissions
- Claude Code, skills and memory loading: https://code.claude.com/docs/en/skills and https://code.claude.com/docs/en/memory
- `anthropics/claude-code-action`, `docs/security.md` at the pin: https://github.com/anthropics/claude-code-action
