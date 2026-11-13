# The claude-code-action contract

**Contents**
- [How to use this page](#how-to-use-this-page)
- [Inputs and outputs](#inputs-and-outputs) · [Modes and triggers](#modes-and-triggers) · [Permission mode](#permission-mode)
- [Actor and text trust](#actor-and-text-trust) · [Untrusted pull requests](#untrusted-pull-requests) · [Configuration restored from the base branch](#configuration-restored-from-the-base-branch)
- [Tools the action grants and the MCP servers it starts](#tools-the-action-grants-and-the-mcp-servers-it-starts) · [Git, branches and credentials](#git-branches-and-credentials) · [Session guard](#session-guard)
- [GitHub token and the Claude App token](#github-token-and-the-claude-app-token) · [Inference credentials](#inference-credentials) · [Comments, reviews and structured output](#comments-reviews-and-structured-output)
- [Plugins and marketplaces](#plugins-and-marketplaces) · [Removed inputs](#removed-inputs) · [Claude Code version, models and auto availability](#claude-code-version-models-and-auto-availability) · [Environment variables the action passes](#environment-variables-the-action-passes)

## How to use this page

- This page is the only place the skill states how `anthropics/claude-code-action` behaves. Every other reference links here instead of repeating a fact.
- Each fact holds at the commit in [the Snapshot](version-drift.md#snapshot). Before you rely on a topic for a step, run [the drift check](version-drift.md#compare-with-the-snapshot) on the commit that step runs. A topic whose `Sources:` file changed is described by the code at the pin, not by this page.
- `[unverified: …]` marks a fact the code and docs don't settle, with what would settle it. Treat it as unknown, never as true.
- "Tag run" means a mention, label or assignee run; "agent run" means a run driven by `prompt`.

## Inputs and outputs

- Read the `inputs:` block of `action.yml` at the pinned commit, and pass only the inputs it declares. Don't rely on a count of inputs: releases add them.
- Keep apart action inputs, CLI flags passed through `claude_args`, Claude Code settings (the `settings` input), environment variables and workflow keys.
- Outputs: `conclusion`, `execution_file`, `branch_name`, `github_token`, `structured_output` and `session_id`. `skipped_due_to_workflow_validation_mismatch` is a step output the action uses internally, not an action output.
- Input defaults that change behavior: `restrict_untrusted_prs: "true"`, `classify_inline_comments: "true"`, `include_fix_links: "true"`, `track_progress: "false"`, `use_sticky_comment: "false"`, `use_commit_signing: "false"`, `label_trigger: "claude"`, `trigger_phrase: "@claude"`, `branch_prefix: "claude/"`.
- Several behavior changes since v1.0.273 don't show in `action.yml` descriptions: the auto-mode default, the effect of `allowed_bots` on git and on bot-acted pull requests, and the label and assignee gates on prompt runs. Read the topics below, not the descriptions.
- `--max-turns` in `claude_args` is read by the action; other flags, such as `--max-budget-usd`, pass through to Claude Code. Lines in `claude_args` whose first non-blank character is `#` are removed before parsing.

Sources: `action.yml`, `base-action/action.yml`, `src/entrypoints/collect-inputs.ts`

## Modes and triggers

- `track_progress: true` forces tag mode on `pull_request` (which includes `pull_request_target`), `issues`, `issue_comment`, `pull_request_review_comment` and `pull_request_review`. On any other event, or on a `pull_request` action other than `opened`, `synchronize`, `ready_for_review`, `reopened` or `labeled`, the step fails with `track_progress is only supported for events: …` or `track_progress for pull_request events is only supported for actions: …`, and no tracking comment is made. The `action.yml` description of this input doesn't match the code.
- On comment and review events, a `prompt` selects agent mode; otherwise the trigger phrase selects tag mode. A `prompt` without a job-level `if:` runs on every comment.
- On `issues` events, a `prompt` selects agent mode; otherwise a mention, `label_trigger` or `assignee_trigger` selects tag mode.
- On `pull_request` `opened`, `synchronize`, `ready_for_review` or `reopened`, a `prompt` selects agent mode.
- Everything else falls through to agent mode, which does nothing without a `prompt`.
- Tag mode doesn't start on a `deleted` comment event, or on an edit or review whose author isn't the actor. Agent mode doesn't check this: see [Actor and text trust](#actor-and-text-trust).
- With `prompt` and `track_progress`, issue `labeled` and `assigned` events must match `label_trigger` or `assignee_trigger`. An empty `label_trigger` accepts any label.

Sources: `src/modes/detector.ts`, `src/github/validation/trigger.ts`, `src/github/context.ts`

## Permission mode

The action decides one flag, then the user's `claude_args` follow it. `defaultsToAutoMode()` returns false, keeping the pre-v1.0.273 behavior, when any of these holds:

- `allowed_non_write_users`, `allowed_bots` or `path_to_claude_code_executable` is non-blank;
- `ANTHROPIC_BASE_URL` is set in the environment the action step sees [unverified: whether a job-level `env:` reaches the composite step; one run with a gateway settles it];
- the `settings` input isn't JSON (a file path always counts), sets `env.ANTHROPIC_BASE_URL`, or sets a `permissions.defaultMode` other than `auto`.

It doesn't check the Bedrock, Vertex or Foundry base URLs, or the repository's `.claude/settings.json`: those runs default to auto too.

| Pin | Run | `defaultsToAutoMode()` | Flag the action passes | Effective mode with no user flag |
| :-- | :-- | :-- | :-- | :-- |
| v1.0.272 or older | tag | (no gate) | `--permission-mode acceptEdits` | acceptEdits |
| v1.0.272 or older | agent | (no gate) | none | the `settings` input's `permissions.defaultMode`, else Manual |
| v1.0.273 or later | tag | true | `--permission-mode auto` | auto; when auto is unavailable, acceptEdits with a warning |
| v1.0.273 or later | tag | false | `--permission-mode acceptEdits` | acceptEdits |
| v1.0.273 or later | agent | true | `--permission-mode auto` | auto; when auto is unavailable, Manual with no warning |
| v1.0.273 or later | agent | false | none | the `settings` input's `permissions.defaultMode`, else Manual |

- **The user's flag wins.** The user's `claude_args` come last, so `--permission-mode X` in the space form sets the mode to X in every row. The equals form, `--permission-mode=X`, is kept as a separate entry [unverified: whether the CLI ends up with it; one run with Claude Code 2.1.323 settles it]. `--dangerously-skip-permissions` overrides any mode.
- **`settings` doesn't change tag runs.** A `permissions.defaultMode` in the `settings` input is overridden by the flag tag mode always passes; it applies only to agent runs that get no flag.
- **When auto is unavailable** (see [Claude Code version, models and auto availability](#claude-code-version-models-and-auto-availability)), the session opens in Manual. Tag runs log `Auto mode is not available for this run, for example because of its model. Using acceptEdits instead.` and switch; if the switch fails they log `Could not switch to acceptEdits, so tool calls that need permission will be denied.` Agent runs stay in Manual silently, including those that pass `--permission-mode auto` themselves. With Claude Code 2.1.322 (bundled by v1.0.273) such a session could start "in a mode that could allow more" [unverified: which mode; the 2.1.322 source or a run on an unsupported model settles it].
- **What each mode does with a call no allow rule covers.** In acceptEdits and Manual, the call is denied: the run has no one to ask and the action sets no permission handler. In auto, Claude Code's safety review decides, and the call runs when the review passes it. So under auto, `--allowedTools` is no longer a strict list, and broad allow rules (`Bash(*)`, wildcarded interpreters, package-manager run commands, Agent, Monitor) are dropped. A denied call doesn't stop the run: Claude keeps working.
- **Deny rules win in every mode**, `bypassPermissions` included.
- **Older Claude Code.** On a pin that bundles Claude Code older than 2.1.302, an agent run with no mode could start in auto when it didn't fetch feature flags (a third-party provider, or `DISABLE_TELEMETRY`).

Sources: `src/modes/permission-mode.ts`, `src/modes/tag/index.ts`, `src/modes/agent/index.ts`, `base-action/src/parse-sdk-options.ts`, `base-action/src/run-claude-sdk.ts`, `src/entrypoints/run.ts`

## Actor and text trust

- **Write gate.** Issue and pull request events and `workflow_run` require write access from the actor. For `workflow_run` the upstream run's actor is checked too and, when the run came from a fork, the fork's owner. A `workflow_run` without `head_repository` fails with `Actor does not have write permissions to the repository`.
- `allowed_non_write_users` bypasses the write gate only when `github_token` is provided.
- Actors that aren't `User` accounts are rejected unless listed in `allowed_bots`, on every event, scheduled runs included. An actor whose login ends in `[bot]` passes the write check, so a listed bot runs without write access.
- **A bot acting on a pull request.** On `pull_request` and `pull_request_target` events with a `[bot]` actor, the pull request's author must have write access, be in `allowed_bots`, or be in `allowed_non_write_users` with `github_token`. Otherwise the step logs `<bot> acted on a pull request by <author>, who is not allowed to start a run` and fails with `A bot acted on this pull request, but its author does not have write access`. Bot comments and reviews aren't covered.
- **Only the actor's own text is the request.** A comment, review or issue or pull request body becomes the request, which can run slash commands, only when the actor wrote it. Other people's text is still read as context.
- **Edited and deleted comments.** Tag mode doesn't start on a `deleted` event, or on an edited comment or review written by someone other than the actor. **Agent mode does**: with `prompt` and no `track_progress`, a maintainer editing or deleting someone else's comment or review still starts a run. The action's `docs/security.md` says it doesn't; the code says it does.
- **Label and assignment cutoff.** On issue `labeled` and `assigned` events, only comments made before the actor's own matching label or assignment reach Claude.
- `include_comments_by_actor` and `exclude_comments_by_actor` limit whose comments reach Claude.

Sources: `src/github/validation/permissions.ts`, `src/github/validation/actor.ts`, `src/github/validation/trigger.ts`, `src/create-prompt/index.ts`, `src/github/data/fetcher.ts`, `src/modes/detector.ts`, `docs/security.md`

## Untrusted pull requests

- `restrict_untrusted_prs` defaults to `"true"`. Only the string `false`, trimmed and in any case, turns it off; `0`, `no` and empty keep it on.
- **When it applies:** on `pull_request` (and `pull_request_target`), `pull_request_review`, `pull_request_review_comment` and `issue_comment` on a pull request, when the pull request's **author**, not the actor, isn't confirmed to have write or admin access. A `[bot]` author, a missing author and a failed lookup count as untrusted. `allowed_bots` and `allowed_non_write_users` don't exempt anyone.
- **Not covered:** `issues`, comments on issues, `workflow_run`, `workflow_dispatch`, `repository_dispatch` and `schedule`.
- **What it does:** it adds the fixed list `UNTRUSTED_PR_DISALLOWED_TOOLS` (in `untrusted-pr.ts`) to the deny rules: package managers, test runners, interpreters, build tools, shells, `git config` and `git -c`. Deny wins, so `--allowedTools` can't re-enable them; the user's `--disallowedTools` are added to it. Git hooks are also turned off before the pull request is checked out.
- **What it doesn't do:** it is not a sandbox. `/usr/bin/npm`, `./scripts/x.sh`, `git rebase --exec` and a `Write` allow rule on files later steps run all escape it. A `--tools` list without Bash makes the list moot [unverified: how a `--tools` passed through `claude_args` combines with the deny list; one run settles it].
- It applies in agent mode even when the workspace holds base code. In tag mode on a closed or merged pull request nothing is denied, but hooks stay off and the denial warning is still logged.
- **Signals:** the step still succeeds. The log has `The author of pull request #N is not confirmed to have write access, so commands that run code from the checkout are denied.`, `Could not check repository access for pull request author X, treating them as untrusted: HTTP <status>` on a failed lookup, and `N Bash rule(s) in claude_args are not on the deny list and stay allowed.`
- **Reading CI results on outside pull requests** (the action's documented path): run the tests in a separate `pull_request` workflow with `contents: read`, require approval for outside contributors, give Claude's job `actions: read`, and deny `mcp__github_ci__download_job_log` and `mcp__github_ci__get_workflow_run_details`, because logs and job names are text the pull request controls.

Sources: `src/github/validation/untrusted-pr.ts`, `src/entrypoints/run.ts`, `action.yml`, `docs/security.md`, `src/modes/agent/parse-tools.ts`

## Configuration restored from the base branch

- On every pull request event, and `issue_comment` on a pull request, the action restores the paths in `SENSITIVE_PATHS` (`restore-config.ts`) from the base branch before Claude starts: `.claude`, `.mcp.json`, `.claude.json`, `.gitmodules`, `.ripgreprc`, `CLAUDE.md`, `CLAUDE.local.md` and `.husky`. It keeps the pull request's versions in `.claude-pr/`.
- Only those root paths are restored. A `CLAUDE.md`, `.claude/rules/` or `.claude/skills/` in a subdirectory loads from the pull request when Claude works on files there. `package.json`, lockfiles, task runners and scripts stay at the pull request's head.
- `.claude-pr/` sits inside the workspace [unverified: whether Claude Code loads its `CLAUDE.md` or skills when Claude reads files there; a local headless run settles it].
- **Who checks out the head.** Tag mode checks out an open pull request's head commit itself (`pr-N` locally for a fork) and refuses a head pushed after the trigger. Agent mode never checks out: Claude works on whatever the workflow's own checkout left, which is the base for `pull_request_target` and `workflow_run`.
- `workflow_run` and events that aren't about a pull request get no restore.
- `--add-dir` on a directory holding the pull request's head loads its skills, commands, agents and `enabledPlugins` (Claude Code's additional-directories rules).

Sources: `src/github/operations/restore-config.ts`, `src/github/operations/branch.ts`, `src/entrypoints/run.ts`

## Tools the action grants and the MCP servers it starts

- **Tag mode grants:** `Glob`, `Grep`, `LS`, `Read`, `mcp__github_comment__update_claude_comment`, the three `mcp__github_ci__` tools, and every user `--allowedTools` entry that starts with `mcp__github_`. For commits it adds the four git wrappers (see [Git, branches and credentials](#git-branches-and-credentials)), or `mcp__github_file_ops__commit_files` and `delete_files` when `use_commit_signing` is on without an SSH key.
- **Edit, MultiEdit and Write are not granted.** The permission mode is what lets tag mode edit files in the workspace. So a `--tools` list without `Edit` and `Write` removes code editing from mention runs.
- **Agent mode grants nothing** of its own beyond the mode flag and `--mcp-config`.
- **How the lists merge.** `--allowedTools`, `--disallowedTools`, `--mcp-config` and `--add-dir` accumulate across every occurrence; the action's entries come first, then the user's. The user can add allow and deny rules but can't remove the action's. `--tools` isn't merged: it passes through to Claude Code, the last one wins, and the action never sets it.
- **The GitHub MCP server.** The action runs `ghcr.io/github/github-mcp-server` at the image in [the Snapshot](version-drift.md#snapshot), through Docker, with the run's token. It starts in agent mode when `--allowedTools` names `mcp__github` or any `mcp__github__*` tool; in tag mode only for a named `mcp__github__*` tool, so a bare `mcp__github` doesn't start it there.
- **Once started, it exposes every toolset**, not only the tools you granted. Under auto, an ungranted tool goes to the safety review. Its write tools include, for example, `merge_pull_request`, `create_and_submit_pull_request_review`, `submit_pending_pull_request_review`, `update_pull_request` (which can also request reviewers), `update_pull_request_branch`, `create_pull_request`, `request_copilot_review`, and the branch writers `push_files`, `create_or_update_file`, `delete_file` and `create_branch`. Read the full list from `pkg/github/tools.go` in `github/github-mcp-server` at the image's commit. At v0.17.1 no tool enables auto-merge.
- **The CI server** (`mcp__github_ci__*`) starts only on pull requests: always in tag mode, and in agent mode only when `--allowedTools` names a `mcp__github_ci` tool. It always uses the job's `github.token`, so it needs `actions: read` in the job's `permissions:`; without it the server is skipped with a warning. `additional_permissions` doesn't enable it.
- **The inline-comment server** starts on a pull request when `--allowedTools` names an inline-comment tool or a GitHub MCP tool.

Sources: `src/modes/tag/index.ts`, `src/modes/agent/index.ts`, `src/mcp/install-mcp-server.ts`, `base-action/src/parse-sdk-options.ts`, `src/modes/agent/parse-tools.ts`

## Git, branches and credentials

- **Checkout's credential.** The action removes `http.<server>.extraheader` from the local `.git/config` and from files it pulls in through `include.path`. `actions/checkout` v6.0.0 and later include their credentials file through `includeIf.gitdir:…` instead (see [the Snapshot](version-drift.md#snapshot)), which the action doesn't read. So with checkout v6 or later that credential stays readable during the session; its reach is the job's `GITHUB_TOKEN` permissions. `persist-credentials: false` on the checkout step removes it.
- **The action's own git token.** By default it goes in `origin`'s URL in `.git/config`. With `allowed_bots` or `allowed_non_write_users` set, `origin` holds no token: a credential helper registered only for this host reads `GH_TOKEN`. In every case the token is also in Claude's environment as `GITHUB_TOKEN` and `GH_TOKEN`.
- **Later steps in the job.** With the credential helper, a later step that uses `origin` needs its own credentials. With the token in the URL, the URL survives the session; when the token was the Claude App token, the action revokes it at the end, so a later push through `origin` fails [unverified: inferred from code; one run settles it]. A `github_token` input is never revoked and stays usable there.
- **`persist-credentials: false` and tag mode.** Tag mode fetches the pull request before it sets up its own credentials [unverified: whether that fetch fails on a private repository without checkout's credential; one run settles it].
- **The git wrappers** (tag mode, git path). Claude commits through four scripts in the action's `scripts/` folder, not raw git:
  - `git-add.sh` accepts `-A`, `-u`, `-v`, `--chmod=±x`, `--` and paths; `git add -f` is refused.
  - `git-commit.sh` needs a literal `-m` message and refuses `--amend`, `-F`, `--no-verify` and `--author`.
  - `git-push.sh` accepts only `origin HEAD` or `origin <session branch>` and pushes to the session branch, never forced. Anything else fails with `this session can only push to <branch>`.
  - `git-rm.sh` accepts `-r`, `-f`, `--cached`, `-q`, `--` and paths.
  - Every wrapper ignores the session's `GIT_*` variables (except author and committer), `XDG_CONFIG_HOME`, `EDITOR`, `PAGER` and `SSH_ASKPASS`, and runs git with hooks off on untrusted pull requests. A workflow that pushes over SSH with `GIT_SSH_COMMAND` must allow its own command, such as `Bash(git push:*)`, and loses the wrappers' protection.
  - Deny rules for `git add`, `rm`, `commit` or `push` in `claude_args` carry over to the wrappers; deny rules in settings files don't.
- **Other git commands.** Read-only git runs without asking. Anything else (`checkout`, `fetch`, `rebase`, `reset`, a push outside the wrapper) has no allow rule: under auto it goes to the safety review; in acceptEdits or Manual it is denied.
- **Branches in tag mode.** From an issue, or a closed or merged pull request: a new branch `<branch_prefix><issue|pr>-N-<YYYYMMDD-HHMM>` (or `branch_name_template`) from `base_branch` or the default branch. On an open pull request from the same repository: its head branch. On an open fork pull request: `pr-N` in this repository; the fork's branch is never updated.
- **Branches in agent mode.** Without `use_commit_signing`, the action creates and checks out no branch. With it, API commits go to `issue-N` for an issue, the head branch for a same-repository pull request, and `pr-N` for a fork or for `issue_comment` on a pull request; `issue-N` and `pr-N` start from the base branch. `CLAUDE_BRANCH` in the step's environment overrides that name.

Sources: `src/github/operations/git-config.ts`, `src/github/operations/branch.ts`, `src/utils/branch-template.ts`, `src/modes/agent/index.ts`, `scripts/git-env.sh`, `scripts/git-add.sh`, `scripts/git-commit.sh`, `scripts/git-push.sh`, `scripts/git-rm.sh`, `action.yml`

## Session guard

- **Restored after the session:** `GITHUB_ENV`, `GITHUB_PATH`, `.git/config`, `.git/config.worktree`, `~/.gitconfig`, the XDG git config, `GIT_CONFIG_GLOBAL`, and every file git reaches through `include.path`. A file the session changed is put back with `The session changed files that later steps trust, so they were restored: …`; one it couldn't put back gets `Could not restore …`. A session therefore can't pass variables through `GITHUB_ENV`; pass results through `--json-schema` instead.
- **Always off:** `core.fsmonitor`. During the session the global `safe.bareRepository=explicit` is set (needs git 2.38); the other settings need git 2.31.
- **Hooks off:** during the session on untrusted pull requests, and always for the action's own git commands after it.
- **Not restored:** tracked workspace files, home dotfiles outside the list (`~/.bashrc`, `~/.npmrc`, `~/.ssh/config`), submodule config, and anything when the run is cancelled or times out mid-session. A later step that runs workspace code (`npm test`, `make`, a local `uses: ./…`) runs whatever the session edited, and a later step's own `git commit` runs hooks normally.

Sources: `src/github/operations/session-guard.ts`, `src/entrypoints/run.ts`

## GitHub token and the Claude App token

- With `github_token` set, the action uses it as given (`Using provided GITHUB_TOKEN for authentication`): the job's `GITHUB_TOKEN`, a custom App token or a PAT. It is never revoked by the action.
- Without it, the action exchanges the job's OIDC token for the Claude App token, with `contents`, `pull_requests` and `issues` write plus `additional_permissions`. The job needs `id-token: write`. That token is revoked at the end of the action.
- **Workflow-validation skip** (App path only). When the exchange answers `workflow_not_found_on_default_branch`, or 401 with `workflow validation failed`, the action logs `Skipping action due to workflow validation: <message>` and `Action skipped due to workflow validation error. …`, sets `skipped_due_to_workflow_validation_mismatch=true`, and ends green without running Claude. Which differences from the default branch's copy trigger it is decided by Anthropic's service.
- The author lookup for [Untrusted pull requests](#untrusted-pull-requests) uses the selected token; when it fails, the author counts as untrusted.

Sources: `src/github/token.ts`, `src/entrypoints/run.ts`, `action.yml`

## Inference credentials

- Profiles: `anthropic_api_key`; `claude_code_oauth_token`; Anthropic workload identity federation (`anthropic_federation_rule_id` and `anthropic_organization_id`, optional `anthropic_service_account_id`, `anthropic_workspace_id` and `anthropic_oidc_audience`, default audience `https://api.anthropic.com`, needs `id-token: write`); `use_bedrock`, `use_vertex` or `use_foundry` with OIDC and `id-token: write`.
- The checks fail the step before Claude starts only when the direct Anthropic API has no API key, no OAuth token and not both federation IDs; when more than one of Bedrock, Vertex and Foundry is enabled; or when the enabled provider lacks a variable it requires.
- Other mixes pass the checks. An API key beside an OAuth token isn't rejected. A static key or token beside the federation IDs, from the inputs or the job's `env:`, only logs a warning and wins, so federation isn't used.
- The federation IDs aren't credentials and may sit in the workflow or in repository variables.

Sources: `base-action/src/validate-env.ts`, `base-action/src/workload-identity.ts`, `action.yml`

## Comments, reviews and structured output

- Tag mode keeps one tracking comment. Agent mode writes to the run log unless the prompt asks Claude to post. Under auto a posting call no allow rule covers, such as `gh pr comment`, can pass the safety review; in acceptEdits or Manual a posting tool must be granted.
- `use_sticky_comment` keeps one comment across runs.
- **Inline review comments** go through `mcp__github_inline_comment__create_inline_comment`. With `classify_inline_comments` (default `true`) they are buffered until the session ends, then classified and posted. Classification needs the `anthropic_api_key` **input**: without it the step logs `ANTHROPIC_API_KEY not set — skipping classification, posting all unconfirmed comments`. Comments Claude marked `confirmed: false` are never posted.
- The action's prompt tells Claude not to approve or merge. That is an instruction, not a control.
- **Structured output:** request it with `--json-schema` in `claude_args`. Every field comes back in one `structured_output` JSON string. Read it with `fromJSON(...)` in `if:` conditions, or pass it through `env:` to a script; never interpolate it into `run:`.

Sources: `src/entrypoints/post-buffered-inline-comments.ts`, `src/mcp/install-mcp-server.ts`, `src/entrypoints/run.ts`, `action.yml`, `src/github/operations/comments/create-initial.ts`

## Plugins and marketplaces

- `plugin_marketplaces` takes newline-separated entries: an `https://` URL ending in `.git`, with no ref, or a local path starting with `./`, `../` or `/`. A URL installs the marketplace's moving default branch on every run; to pin, check the marketplace out at a resolved commit in an earlier step and pass the local path.
- `plugins` takes `plugin-name@marketplace-name`, where the marketplace name comes from its manifest, not from the repository URL.
- Anthropic's plugins, `code-review` among them, live in `anthropics/claude-plugins-official` (marketplace `claude-plugins-official`), which has no version tags (see [the Snapshot](version-drift.md#snapshot)). The `claude-code-plugins` marketplace in `anthropics/claude-code` only redirects each entry there.
- Check the repository out before the action step when the prompt runs a repository skill.

Sources: `base-action/src/install-plugins.ts`

## Removed inputs

None of these is declared in `action.yml`; a workflow that passes one gets nothing from it, and the run doesn't fail:

- `mode`: removed, the mode is detected.
- `direct_prompt`, `override_prompt`: use `prompt`.
- `custom_instructions`: `--append-system-prompt` in `claude_args`.
- `model`, `anthropic_model`, `fallback_model`, `max_turns`, `allowed_tools`, `disallowed_tools`, `mcp_config`: the matching flag in `claude_args` (`--model`, `--fallback-model`, `--max-turns`, `--allowedTools`, `--disallowedTools`, `--mcp-config`).
- `claude_env`: the `env` object of the `settings` input.
- `timeout_minutes`: the job's `timeout-minutes`.
- `experimental_allowed_domains`: no replacement input; egress control moves to the runner.

Check this list against the `inputs:` block of `action.yml` at the pin.

Sources: `action.yml`

## Claude Code version, models and auto availability

- Each release bundles one Claude Code version (`CLAUDE_CODE_VERSION` in `base-action/action.yml`); the snapshot's is in [the Snapshot](version-drift.md#snapshot). v1.0.274 moved it from 2.1.322 to 2.1.323 without saying so in its notes.
- **No default model.** The action sets none, so Claude Code's applies: Opus 5.5 with an API key, an OAuth token, Bedrock or Vertex, and Sonnet 4.5 on Foundry (Claude Code's model configuration docs). `ANTHROPIC_MODEL` in the step's environment beats `--model` in `claude_args` [unverified: whether a job-level `env:` reaches the composite step].
- **Models that support auto** (Claude Code's permission-modes docs): on the Anthropic API, Opus 4.6 or later, Sonnet 4.6 or later, Haiku 5.5 and Fable models; on Bedrock, Vertex and Foundry, Sonnet 5 or later, Opus 4.7 or later, Haiku 5.5 (Claude Code 2.1.293 or later) and Fable. Sonnet 4.5, Opus 4.5 and Haiku 4.5 are unsupported everywhere, so a Foundry run with no `--model` can't use auto.
- **Auto is also unavailable** when `disableAutoMode` is set in any settings file or managed settings, when auto is turned off or refused server-side, and, since 2.1.323, behind an `ANTHROPIC_BASE_URL` gateway for a model whose name contains "haiku".
- **Auto's own costs:** where the server-side review doesn't reach a session, Claude Code makes its own classifier requests, which count toward token usage. On Bedrock the account may need access to the classifier's model, or calls that need review are blocked.

Sources: `base-action/action.yml`, `base-action/package.json`, `src/entrypoints/run.ts`, `base-action/src/run-claude-sdk.ts`, `base-action/src/parse-sdk-options.ts`

## Environment variables the action passes

- **`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`:** the workflow's own value when set; otherwise `1` when `allowed_non_write_users` is non-empty; otherwise unset. `allowed_bots` alone doesn't set it. The documented opt-out is `'0'` [unverified: that a string `'0'` survives the action's expression; one run settles it].
- What the scrub removes (Claude Code's environment-variables docs): it leaves `GITHUB_TOKEN` and `GH_TOKEN` in place, and removes variables such as `NPM_TOKEN`, `DB_PASSWORD` and `DATABASE_URL` from Claude's subprocesses. On Linux, `ps`, `pgrep` and `kill` can't see host processes. Claude Code older than 2.1.323 (claude-code-action v1.0.273 and earlier) could need approval for, or refuse, read-only git commands under the scrub on Linux.
- With `allowed_non_write_users` on Linux the action also installs an isolation step, which the opt-out skips.
- **`CLAUDE_CODE_SCRIPT_CAPS`:** passed through from the workflow's environment. Its value is a JSON object mapping a script's file name, as the workflow runs it from the repository, to its maximum number of calls, for example `{"edit-issue-labels.sh": 2}` (the action's `docs/security.md`). The action never reads it, and only the action's `docs/security.md` documents it; Claude Code's own environment-variables docs don't list it [unverified: that Claude Code enforces it].
- The step's whole environment, minus OIDC values and the action's raw inputs, reaches Claude Code: every secret the job puts in `env:` is visible to the session.

Sources: `action.yml`, `base-action/src/parse-sdk-options.ts`, `docs/security.md`
