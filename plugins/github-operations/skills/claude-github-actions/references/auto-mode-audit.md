# Audit a workflow that runs Claude in auto mode

In auto mode Claude Code runs a tool call without asking when its safety review passes it. In a workflow nobody can answer a prompt, so auto mode decides most of what the agent does. It is a review, not a boundary: what limits an injected or mistaken agent is what the job lets it reach. This reference tells you how to find auto mode, how exposed the workflow is, which protective layers it needs, and how severe each missing layer is.

## Contents

- 1. Is auto mode on?
- 2. Who can start the run?
- 3. Check each layer
- 4. Rate and report
- What auto mode can't be relied on for
- Verify against

## 1. Is auto mode on?

Auto mode is on for a claude-code-action step when any of these holds:

- `claude_args` holds `--permission-mode auto`. In tag mode the action passes `--permission-mode acceptEdits` first and the user's `claude_args` after it, so the user's flag wins.
- The action's `settings` input sets `permissions.defaultMode: "auto"`. That input becomes Claude's user settings, so it applies with no flag.

A `defaultMode` of `auto` in the repository's `.claude/settings.json` does not turn it on. When neither of the two holds, this reference doesn't apply; go back to `workflow-audit.md`.

Auto mode needs a model that supports it: on the Anthropic API, Claude Opus 4.6 or later, Sonnet 4.6 or later, Haiku 5.5 or a Fable model; on Bedrock, Vertex and Foundry, Sonnet 5 or later, Opus 4.7 or later, Haiku 5.5 or a Fable model. Read `--model`, `--fallback-model` and the `settings` input's `model`. When the model doesn't support it, Claude Code starts in Manual mode instead, and a run nobody can answer then denies every call that no rule allows: the workflow fails closed, which is a functional finding, not a security one. An organization can also turn auto mode off in managed settings, with the same result.

## 2. Who can start the run?

The severity of every missing layer depends on who can reach the agent. Classify the workflow before checking the layers:

- **Open to outsiders** when any GitHub user can start it or put text in front of Claude: triggers `issues`, `issue_comment`, `discussion`, `discussion_comment`, `pull_request_review`, `pull_request_review_comment` or `pull_request_target`; any `allowed_non_write_users`; `allowed_bots: "*"`; or a public repository where the job reads issue, comment or pull request text.
- **Collaborators only** when only people with write access can start it, as with the action's default actor check in tag mode on a private repository, or `workflow_dispatch` and `schedule` with no outside text in the prompt.

When you can't tell, treat the workflow as open to outsiders and say why.

## 3. Check each layer

Check every layer, and record for each one the line that proves it, or "missing".

| Layer | What proves it in the workflow | When it is missing |
| :-- | :-- | :-- |
| A. Token and permissions | `github_token: ${{ secrets.GITHUB_TOKEN }}` on the step, so the agent's token expires with the job and has only the job's permissions; workflow-level `permissions: {}`; job write scopes only where a tool uses them; `id-token: write` only for workload identity federation | The action's GitHub App token is used (no `github_token`), whose scope the job's `permissions:` don't limit; or the job has write scopes nothing uses |
| B. Tools really limited | `--tools` listing only the built-in tools the job needs, such as `Bash,Read,Grep,Glob`; `--disallowedTools` naming `WebFetch`, `WebSearch` and `Monitor`, which reach the network, and `Edit`, `Write` and `NotebookEdit` when the job shouldn't change files, each as a bare name; the GitHub MCP approval and merge tools denied as `trust-boundaries.md` says | Only `--allowedTools` is set. In auto mode an allowed tool is approved in advance, not the only tool allowed: any other call goes to the safety review, and a broad grant such as `Bash(*)` is dropped. Raw `gh` with the job's token stays reachable unless the token's scope stops it |
| C. Script caps | `CLAUDE_CODE_SCRIPT_CAPS` as JSON giving each script that writes a call limit, such as `{"edit-issue-labels.sh": 2}`, **and** `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB: '1'` in `env:` or a non-empty `allowed_non_write_users` (which makes the action turn the scrub on) | Caps without the scrub do nothing; check that the JSON parses and that every writing script has a key. Caps are defense in depth: fan-out through `xargs` or `find -exec` is not counted |
| D. Network out of the runner | Evidence that the runner can reach only the hosts the job needs: a runner group whose network configuration restricts egress (GitHub's private networking for larger runners), a self-hosted runner behind a firewall, or a first step of the third-party `step-security/harden-runner` with `egress-policy: block` | A `runs-on` label alone proves nothing, whatever its name. Ask the user how the runner's network is restricted; until they confirm, report the layer as unverified. A self-hosted runner on a public repository is a finding by itself |
| E. Time and repetition | `timeout-minutes` on the job (the default is 360 minutes); a `concurrency` group with `cancel-in-progress: true` for runs that a new event supersedes | No timeout, or no concurrency group on a workflow that comments or labels |
| F. Configuration Claude reads | The agent's `CLAUDE.md`, settings and skills come from the base branch, as `trust-boundaries.md` says | The job checks out a pull request's head in the workspace: its `CLAUDE.md` reaches the safety review, which reads it, and steers what auto mode lets through |
| G. A model that supports auto mode | The model rule in section 1 | An unsupported model: the run falls back to Manual and fails closed |

## 4. Rate and report

Rate each missing layer with this table, then follow the severity scale in `workflow-audit.md` for the report:

| Missing layer | Open to outsiders | Collaborators only |
| :-- | :-- | :-- |
| A, B or F | high | medium |
| C or D | medium | low |
| E or G | low | low |

For each missing layer, write the patch from the "What proves it" column, adapted to the workflow, and name what it costs: a narrower tool list can break a prompt that relied on a tool, so read the prompt and keep the tools it uses.

Every workflow in auto mode also gets this residual risk in its report, whatever its layers: auto mode is a review, not a boundary; and on a runner without managed settings, a Claude Code mod can approve a call that a deny rule refuses, and in auto mode the mods Claude writes turn on without asking. Don't recommend a setting to close this until it has been tested in the action.

## What auto mode can't be relied on for

- It blocks nothing it can't see: tool results are stripped from what the safety review reads, and a run with no prompt tool keeps working after a call is refused.
- It doesn't replace any layer above. It lowers how often a mistake becomes an action; the layers decide what a mistake can reach.

## Verify against

- Claude Code, permission modes and auto mode: https://code.claude.com/docs/en/permission-modes
- Claude Code, permissions and rule precedence: https://code.claude.com/docs/en/permissions
- Claude Code, environment variables (`CLAUDE_CODE_SCRIPT_CAPS`, `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`): https://code.claude.com/docs/en/env-vars
- Claude Code, CLI reference (`--tools`, `--disallowedTools`): https://code.claude.com/docs/en/cli-reference
- `anthropics/claude-code-action`, `action.yml`, `src/modes/tag/index.ts`, `base-action/src/setup-claude-code-settings.ts` and `docs/security.md`: https://github.com/anthropics/claude-code-action
- GitHub, private networking for GitHub-hosted runners: https://docs.github.com/en/actions/concepts/runners/private-networking

Checked on 12 November 2026 against `anthropics/claude-code-action@4fa93a8` (v1.0.271), which runs Claude Code 2.1.322.
