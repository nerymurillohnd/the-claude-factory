# The claude-code-action contract

## Contents

- Resolve the contract live
- Modes
- Actor gates
- Comment and review surfaces
- Untrusted pull request configuration
- Structured output
- Plugins and skills on runners
- Removed inputs
- Versions and model IDs
- Verify against

## Resolve the contract live

Read `action.yml` at the commit the workflow pins, or will pin, and pass only the inputs it declares. Keep apart action inputs, CLI flags passed through `claude_args`, Claude Code settings (the `settings` input), environment variables and workflow keys. At the snapshot below, `action.yml` declares 39 inputs and 6 outputs: `conclusion`, `execution_file`, `branch_name`, `github_token`, `structured_output` and `session_id`.

## Modes

- `track_progress: true` on `pull_request`, `issues`, `issue_comment`, `pull_request_review_comment` or `pull_request_review` forces tag mode. On any other event, or on a `pull_request` action other than opened, synchronize, ready_for_review, reopened or labeled, the run fails (SE-05).
- On comment and review events, a `prompt` selects agent mode; otherwise the trigger phrase selects tag mode. A `prompt` without a job-level `if:` runs on every comment.
- On `issues` events, a `prompt` selects agent mode; otherwise a mention, `label_trigger` or `assignee_trigger` selects tag mode.
- On `pull_request` opened, synchronize, ready_for_review or reopened, a `prompt` selects agent mode.
- Everything else falls through to agent mode, which does nothing without a `prompt` (SE-04).

## Actor gates

- Issue and pull request events, and `workflow_run`, require the triggering actor, and for `workflow_run` the upstream run's actor, to have write access (SE-03).
- `allowed_non_write_users` bypasses that check only when `github_token` is provided.
- Actors that are not `User` accounts are rejected unless listed in `allowed_bots` (SE-02).
- `include_comments_by_actor` and `exclude_comments_by_actor` limit whose comments reach Claude.

## Comment and review surfaces

- Tag mode keeps one tracking comment. Agent mode writes to the run log unless the prompt asks Claude to post and a posting tool is granted (SE-13).
- Inline review comments go through `mcp__github_inline_comment__create_inline_comment`, whose server starts only when `--allowedTools` names it (SE-08). `classify_inline_comments` defaults to `true` and buffers comments until the session ends; `include_fix_links` defaults to `true`.
- The action does not block formal reviews, approvals or merges: its prompt tells Claude not to, which is an instruction, not a control. Once `--allowedTools` names `mcp__github` or any `mcp__github__*` tool, the action starts the GitHub MCP server it pins with the run's token. At the snapshot that server exposes `create_and_submit_pull_request_review`, `submit_pending_pull_request_review`, `merge_pull_request`, `update_pull_request`, `update_pull_request_branch`, `create_pull_request` and `request_copilot_review`. The policy for them is in `trust-boundaries.md`.
- Branches: triggered from an issue, Claude works on a new branch (`branch_prefix`, default `claude/`); on an open pull request it pushes to that branch.

## Untrusted pull request configuration

- On pull request events, and on `issue_comment` on a pull request, the action restores `.claude`, `.mcp.json`, `.claude.json`, `.gitmodules`, `.ripgreprc`, `CLAUDE.md`, `CLAUDE.local.md` and `.husky` from the base branch before Claude starts, and keeps the PR's versions in `.claude-pr/` (SE-12).
- Only those root paths are restored. A `CLAUDE.md` or `.claude/` in a subdirectory, package scripts and task runners stay under the PR's control.
- `workflow_run` and events that are not about a pull request get no restore.

## Structured output

- Requested with `--json-schema` in `claude_args`. Every field comes back in one `structured_output` JSON string.
- Read it with `fromJSON(...)` in `if:` conditions, or pass it through `env:` to the script. Never interpolate it into `run:` (`trust-boundaries.md`).
- Handle missing, malformed or oversized output (SE-01). A valid schema is not authorization: a write that depends on the output needs its own check.

## Plugins and skills on runners

- `plugin_marketplaces` takes newline-separated entries: an `https://` URL ending in `.git`, with no ref, or a local path starting with `./`, `../` or `/`. A URL installs the marketplace's moving default branch on every run, so check the marketplace out at a resolved commit and pass the local path instead.
- `plugins` takes `plugin-name@marketplace-name`, where the marketplace name comes from its manifest, not from the repository URL.
- Check the repository out before the action step when the prompt runs a repository skill.

## Removed inputs

None of these is declared in `action.yml`; a workflow that passes one gets nothing from it (SE-14):

- `mode`: removed, the mode is detected.
- `direct_prompt`, `override_prompt`: `prompt`.
- `custom_instructions`: `--append-system-prompt` in `claude_args`.
- `model`, `anthropic_model`, `fallback_model`, `max_turns`, `allowed_tools`, `disallowed_tools`, `mcp_config`: the matching flag in `claude_args` (`--model`, `--fallback-model`, `--max-turns`, `--allowedTools`, `--disallowedTools`, `--mcp-config`).
- `claude_env`: the `env` object of the `settings` input.
- `timeout_minutes`: the job's `timeout-minutes`.
- `experimental_allowed_domains`: no replacement input; egress control moves to the runner.

A dropped `disallowed_tools` or `experimental_allowed_domains` is a security regression: report it as one.

## Versions and model IDs

- Track separately the action's commit, the Claude Code version it bundles, the model, plugin versions and MCP dependencies.
- A moving major tag such as `v1` is never "the latest patch". Pin the commit, and never `@main`.
- Set no `--model` unless the user asks for one. Then resolve the ID live from Anthropic's model documentation and record where and when. The upstream documentation and examples carry stale model IDs; never copy them.
- `--max-turns` is read by the action itself; other flags in `claude_args`, such as `--max-budget-usd`, pass through to Claude Code.

## Verify against

- `anthropics/claude-code-action`: `action.yml` and `src/` (https://github.com/anthropics/claude-code-action)
- Anthropic models overview: https://platform.claude.com/docs/en/about-claude/models/overview

Verified at `anthropics/claude-code-action@c0949c5` on 4 November 2026. That commit pins `github/github-mcp-server` at `sha-23fa0dd`.
