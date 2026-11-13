# Sharp edges of anthropics/claude-code-action

## Contents

- How to use this catalog
- One entry per sharp edge, numbered SE-01 onward
- Verify against

## How to use this catalog

Each entry gives the symptom, the log signal, the cause, the fix, and the action-contract.md topics whose facts it rests on. Run [the drift check](version-drift.md#compare-with-the-snapshot) first: a log string can change with the action's version. Match a run against the whole catalog, by its log lines and its workflow file, before forming a general hypothesis. Name the matched ID in the report, or say that no entry matched.

## SE-01. Missing or empty `structured_output`

- Symptom: a step that reads `fromJSON(steps.<id>.outputs.structured_output)` fails, or the Claude step fails after a run that looked complete.
- Signal: "--json-schema was provided but Claude did not return structured_output".
- Cause: with `--json-schema` in `claude_args`, the action fails the step when the result is unsuccessful or carries no structured output; without the flag the output is never set. The flag is found only after `claude_args` is shell-parsed, so quoting can drop or split the schema.
- Fix: quote the schema as one argument, guard every consumer with `if: steps.<id>.outputs.structured_output != ''`, and read it through `env:`.
- Facts: [Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output)

## SE-02. Bot actors rejected

- Symptom: runs triggered by Dependabot, Renovate, `github-actions[bot]`, Copilot or another app fail at once.
- Signal: "Workflow initiated by non-human actor: <name> (type: Bot)" or "(actor not found on GitHub)".
- Cause: `allowed_bots` is empty by default, and any actor whose account type is not `User`, or that the Users API cannot resolve, is rejected. The check runs after the trigger check, on every run that passes it, scheduled runs included. A scheduled run is attributed to a repository user, usually the one who last changed the workflow's `cron` [unverified: GitHub's docs don't state which account], and a bot there is rejected too.
- Fix: decide per bot whether Claude should run. Skip unwanted bot events with a job-level `if:` before a runner starts, and list only the needed bots in `allowed_bots`. Never `*` by default. For a scheduled workflow last edited by a bot, list that bot or have a person edit the schedule.
- Facts: [Actor and text trust](action-contract.md#actor-and-text-trust)

## SE-03. The write-access gate, and a bypass that does nothing

- Symptom: runs for contributors without write access fail, even with `allowed_non_write_users` set.
- Signal: "Actor does not have write permissions to the repository".
- Signal, also: the `workflow_run` and bot-author lines belong to SE-20; match them there.
- Cause: issue, pull request and `workflow_run` events check the actor's write access; for `workflow_run` also the upstream run's actor and, for a run from a fork, the fork's owner, failing closed when the run doesn't name its repository. On `pull_request` and `pull_request_target`, a `[bot]` actor also needs a pull request author with write access, in `allowed_bots`, or in `allowed_non_write_users` with `github_token`. `allowed_non_write_users` is honored only when the `github_token` input is provided; otherwise the bypass is skipped. An actor whose login ends in `[bot]` passes the write check without one, and the action's security notes say allowed bots are not checked for repository permissions: an `allowed_bots` entry lets that bot run Claude without write access.
- Fix: use the bypass only with `github_token: ${{ secrets.GITHUB_TOKEN }}`, minimal permissions and minimal tools, never with a personal access token. On a public repository, treat every `allowed_bots` entry as a grant to an actor without write access. Removing either list changes more than the gate: read its row in [Costs of each change](auth-and-permissions.md#costs-of-each-change) first.
- Facts: [Actor and text trust](action-contract.md#actor-and-text-trust), [Git, branches and credentials](action-contract.md#git-branches-and-credentials)

## SE-04. Mode surprises and green no-ops

- Symptom: Claude answers every comment, ignores `@claude`, or the run is green while nothing happened.
- Signal: "Mode: tag" or "Mode: agent", "Trigger result: false", "No trigger found, skipping remaining steps"; the step still succeeds.
- Cause: on comment and review events a `prompt` selects agent mode, so the trigger phrase stops mattering; a `pull_request` event without `prompt` or `track_progress` does nothing.
- Fix: pair every `prompt` on comment events with a job-level `if:`. Report a green run with "No trigger found" as a no-op, never as a success.
- Facts: [Modes and triggers](action-contract.md#modes-and-triggers)

## SE-05. `track_progress` on unsupported events

- Symptom: the step fails before Claude starts, or tools and comments change once `track_progress` is added.
- Signal: "track_progress is only supported for events: ..." or "track_progress for pull_request events is only supported for actions: ...".
- Cause: it accepts `pull_request` (opened, synchronize, ready_for_review, reopened, labeled), `issues`, `issue_comment`, `pull_request_review_comment` and `pull_request_review`; on them it forces tag mode.
- Fix: use it only there, and review the tools and the tracking comment it brings.
- Facts: [Modes and triggers](action-contract.md#modes-and-triggers)

## SE-06. Sticky comments that do not stick

- Symptom: `use_sticky_comment: true` still posts a new comment each run.
- Cause: the sticky path runs only for `pull_request` events, and finds the previous comment by a bot login containing `claude` or by the exact initial body. With `github_token` (`github-actions[bot]`) or a custom app without `claude` in its login, nothing matches.
- Fix: rely on sticky comments only with the Claude GitHub App.
- Facts: [Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output)

## SE-07. CI tools missing

- Symptom: Claude says it cannot see CI results.
- Signal: "The github_ci MCP server requires 'actions: read' permission. Skipping CI server installation." The run continues.
- Cause: the CI server is installed only on a pull request, in tag mode or in agent mode with `mcp__github_ci__*` named in `--allowedTools`, and only when the job's own token has `actions: read`. `additional_permissions` widens the Claude App token, not the job token.
- Fix: grant `actions: read` in the job's `permissions`, and name the CI tools in agent mode. Outside pull requests the server never starts.
- Facts: [Tools the action grants and the MCP servers it starts](action-contract.md#tools-the-action-grants-and-the-mcp-servers-it-starts)

## SE-08. Review findings in the log, nothing on the PR

- Symptom: a review run is green and its log holds findings, but the PR shows no inline comments.
- Cause: the inline-comment server starts only on a pull request, and only when `--allowedTools` names an inline-comment tool (`mcp__github_inline_comment` or `mcp__github_inline_comment__…`) or a GitHub MCP tool. In agent mode that can be `mcp__github` or `mcp__github__…`; in tag mode only names that start with `mcp__github_` count, so a bare `mcp__github` starts nothing there. Without either, no tool can post inline. With `classify_inline_comments` at its default `true`, comments are buffered and classified after the session (SE-16); `confirmed: true` posts at once.
- Fix: name `mcp__github_inline_comment__create_inline_comment` in `claude_args`.
- Facts: [Tools the action grants and the MCP servers it starts](action-contract.md#tools-the-action-grants-and-the-mcp-servers-it-starts), [Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output)

## SE-09. Run outcome edge cases

- Signal: an error result subtype from the Claude Code SDK, such as `error_max_turns` `[unverified: not in the action's source]`; "Claude reported a successful result after <n> turns, exceeding the configured maximum of <m>"; "Claude result reported subtype success with is_error:true"; "No result message received from Claude".
- Cause: the step fails when `--max-turns` is exceeded even on a success result, and treats `success` with `is_error` as a failure. Budget exhaustion and a turn overrun need opposite answers: more budget, or less scope.
- Fix: decide from the result subtype and `is_error` together, never from the red check alone. Read `conclusion` and `execution_file` before any retry, and rerun an errored-but-completed run at most once.
- Facts: [Inputs and outputs](action-contract.md#inputs-and-outputs)

## SE-10. Claude's commits run no CI, or wait for approval

- Symptom: Claude's commits on a PR show no checks, or checks waiting for "Approve workflows to run".
- Cause: events caused by `GITHUB_TOKEN` start no runs, except `workflow_dispatch` and `repository_dispatch`, and a workflow-created or workflow-updated pull request's `opened`, `synchronize` and `reopened` events, which start runs that a user with write access must approve.
- Fix: choose the token knowingly (see `auth-and-permissions.md`). Report "awaiting approval" as such, never as passing or failing.
- Facts: [GitHub token and the Claude App token](action-contract.md#github-token-and-the-claude-app-token)

## SE-11. Fork and Dependabot pull requests without secrets or OIDC

- Symptom: authentication fails only on fork PRs, or only on Dependabot PRs.
- Cause: GitHub gives fork pull request runs a read-only token, downgrading every write scope, `id-token` among them, unless an admin of a private repository enabled "Send write tokens to workflows from pull requests", and withholds every secret but `GITHUB_TOKEN`. Dependabot pull request runs get Dependabot secrets instead of Actions secrets, and a read-only token their `permissions:` can raise [unverified: whether that yields an OIDC token]. API-key, OAuth, workload-identity, Bedrock, Vertex and Foundry profiles all fail there, and so does the default App token, which needs `id-token: write`.
- Fix: skip those events with a job-level `if:`, or use the fork-safe pattern in `trust-boundaries.md`. Never check out the head under `pull_request_target`; `actions/checkout` v7 and its backports refuse it unless `allow-unsafe-pr-checkout: true` is set, and GitHub's new default policy blocks `pull_request_target` in public repositories (date in [the Snapshot](version-drift.md#snapshot)). Report "Send write tokens" as a risk.
- Facts: [Inference credentials](action-contract.md#inference-credentials)

## SE-12. Restored configuration confuses the agent

- Symptom: on a PR that edits `.claude/`, `CLAUDE.md` or another restored path, Claude reports files missing or unchanged.
- Signal: "Restoring ... from origin/<base> (PR head is untrusted)".
- Cause: on pull request events the action restores the root paths in `SENSITIVE_PATHS` from the base branch and keeps the PR's versions in `.claude-pr/`. Only root paths: a `CLAUDE.md`, `.claude/rules/` or `.claude/skills/` in a subdirectory stays at the PR's version and loads when Claude works there. Agent mode never checks out the PR's head, so the workspace holds what the workflow's own checkout fetched.
- Fix: one prompt line naming the restore and pointing to `.claude-pr/`.
- Facts: [Configuration restored from the base branch](action-contract.md#configuration-restored-from-the-base-branch)

## SE-13. Findings that cannot be published

- Symptom: the check is red or green, the PR shows no review, and the findings are only in the log.
- Cause: the prompt asks Claude to comment, but no posting tool is granted. In acceptEdits or Manual each attempt is denied; under auto a posting call no rule covers, such as `gh pr comment`, goes to the safety review and may run or be refused. The result's `permission_denials_count` counts the refusals.
- Fix: grant the posting tool the prompt relies on (SE-08), or have the prompt write only to the run log and the step summary.
- Facts: [Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output), [Permission mode](action-contract.md#permission-mode)

## SE-14. Removed inputs ignored

- Symptom: a workflow that still passes a removed input runs green without what that input configured.
- Signal: GitHub's "Unexpected input(s)" warning annotation on the step `[unverified wording]`.
- Cause: the input is no longer declared in `action.yml`. A dropped `disallowed_tools` widens what the agent may do, and a dropped `experimental_allowed_domains` removes the network restriction: both are security regressions. The replacements are in `action-contract.md`.
- Fix: replace every input the resolved `action.yml` does not declare.
- Facts: [Removed inputs](action-contract.md#removed-inputs)

## SE-15. Workflow validation skip: green, and nothing ran

- Symptom: the Claude step is green, posts nothing and leaves no Claude output, typically on the pull request that adds or edits the Claude workflow.
- Signal: three log lines, the only signals of the skip: "Skipping action due to workflow validation: <message>" (a warning annotation, `::warning::` in the raw log), "Action skipped due to workflow validation error. This is expected when adding Claude Code workflows to new repositories or on PRs with workflow changes. If you're seeing this, your workflow will begin working once you merge your PR.", then "Exiting due to workflow validation skip". The action declares no step output for the skip, so a later step cannot detect it through `steps.<id>.outputs`.
- Cause: on the default GitHub App path (no `github_token` input), the action exchanges the job's OIDC token for an App token at Anthropic's token-exchange endpoint. When the endpoint rejects the workflow, with the error code `workflow_not_found_on_default_branch` or a 401 whose message contains "workflow validation failed", the action ends the step early and successfully. With `github_token` set, this path never runs.
- Fix: merge the workflow change to the default branch first and judge the workflow on the next run there; report the skip as a no-op, never as a pass. Accept the skip on the pull request that changes the workflow.
- Facts: [GitHub token and the Claude App token](action-contract.md#github-token-and-the-claude-app-token)

## SE-16. Inline comments dropped, or posted unfiltered

- Symptom: a review run's log shows inline comments that never reach the pull request, or test-like comments appear on it.
- Signal: "::warning::<n> buffered comment(s) classified as test/probe — NOT posted", "<n> with confirmed=false — not posting", or "ANTHROPIC_API_KEY not set — skipping classification, posting all unconfirmed comments".
- Cause: after the session, buffered comments are classified by `claude-haiku-4-5`; comments judged to be probes are dropped and `confirmed: false` comments are never posted. Classification runs only when the `anthropic_api_key` input is set. With an OAuth token, workload identity federation, Bedrock, Vertex or Foundry it is skipped and every unconfirmed comment is posted; a failed classification call does the same.
- Fix: read the warning lines before concluding that the review found nothing; with a non-API-key profile, expect unfiltered comments, or set `classify_inline_comments: false` knowingly.
- Facts: [Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output)

## SE-17. Authentication fails before Claude starts

- Symptom: the step fails before Claude runs; in tag mode the tracking comment is already posted.
- Signal: "Environment variable validation failed:" followed by one of: "Cannot use multiple providers simultaneously", "Workload identity federation requires both ANTHROPIC_FEDERATION_RULE_ID and ANTHROPIC_ORGANIZATION_ID to be set", "Either ANTHROPIC_API_KEY, CLAUDE_CODE_OAUTH_TOKEN, or workload identity federation (...) is required when using direct Anthropic API", "AWS_REGION is required when using AWS Bedrock", "Either AWS_BEARER_TOKEN_BEDROCK or both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required when using AWS Bedrock", a missing Vertex variable (`ANTHROPIC_VERTEX_PROJECT_ID`, `CLOUD_ML_REGION`), or a missing Foundry resource. For the OIDC token: "Could not fetch an OIDC token. Did you remember to add `id-token: write` to your workflow permissions?" on the default App token path, or "Failed to fetch a GitHub Actions OIDC token for workload identity federation: <message>. Did you remember to add `id-token: write` to your workflow permissions?" for workload identity. A warning that does not fail the step: "Workload identity federation inputs are set alongside anthropic_api_key or claude_code_oauth_token. The API key/OAuth token takes precedence, so federation will not be used."
- Cause: no credential, a partial workload identity configuration, more than one of Bedrock, Vertex and Foundry, a provider's required variable missing, or no `id-token: write` on a job whose OIDC token the action fetches itself (the default App token, workload identity). Bedrock, Vertex and Foundry take their credentials from the job's environment; when an earlier OIDC login step sets them, a missing `id-token: write` shows in that step's log, not with either message above. After the warning, the run authenticates with the static credential, which can come from the job's `env:` (`ANTHROPIC_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`) as well as from the inputs. The credential checks and the workload identity token run only after the trigger check: a run that logged "No trigger found" (SE-04) never reaches them, so a green no-op says nothing about the credentials.
- Fix: set exactly one profile as `auth-and-permissions.md` describes, with its variables, and grant `id-token: write` when the profile needs it. An empty secret on a fork or Dependabot run is SE-11.

- Facts: [Inference credentials](action-contract.md#inference-credentials)
## SE-18. Auto mode by default, and its fallbacks

- Symptom: since v1.0.273 a step edits files or runs commands its `--allowedTools` never listed; or a mention run warns about auto mode; or a prompt run on Foundry, or on an older model, denies every call.
- Signal: "Auto mode is not available for this run, for example because of its model. Using acceptEdits instead."; "Could not switch to acceptEdits, so tool calls that need permission will be denied." A prompt run whose auto mode is unavailable logs no warning: look for denied calls in the result.
- Cause: claude-code-action runs sessions in auto mode unless one of its exclusions holds, so `--allowedTools` pre-approves rather than limits. Auto is unavailable on an unsupported model (Claude Code's default on Foundry among them), when settings turn it off, or when the server refuses it; tag runs then fall back to acceptEdits and prompt runs stay in Manual.
- Fix: decide the mode knowingly. Patches freeze the current mode ([Permission mode in patches](auth-and-permissions.md#permission-mode-in-patches)); a workflow left in auto gets [auto-mode-audit.md](auto-mode-audit.md). For unavailable auto, name a supported `--model` or set the mode explicitly.
- Facts: [Permission mode](action-contract.md#permission-mode), [Claude Code version, models and auto availability](action-contract.md#claude-code-version-models-and-auto-availability)

## SE-19. Code-running commands denied on an untrusted pull request

- Symptom: a review of an outside contributor's pull request is green, but Claude says it couldn't run the tests, the build or an interpreter.
- Signal: "The author of pull request #N is not confirmed to have write access, so commands that run code from the checkout are denied. Set restrict_untrusted_prs to \"false\" to turn this off."; "Could not check repository access for pull request author X, treating them as untrusted: HTTP <status>"; "N Bash rule(s) in claude_args are not on the deny list and stay allowed."; "claude_args turns off permission checks, so commands that are not on the deny list run without approval."
- Cause: `restrict_untrusted_prs`, on by default, denies package managers, test runners, interpreters, shells, `git config` and `git -c` when the pull request's author isn't confirmed to have write access. The step still succeeds.
- Fix: report the run as "green, degraded: no code ran", not as a passing review. Get test results from a separate `pull_request` workflow, as the documented path says. Never set the input to `false` on a workflow outside authors reach (C-17).
- Facts: [Untrusted pull requests](action-contract.md#untrusted-pull-requests)

## SE-20. Actor and text trust

- Symptom: a maintainer labels or assigns an outsider's issue and the slash command in its body doesn't run; editing someone else's comment starts no mention run but does start a prompt run; a bot's pull request event fails; a `workflow_run` from a fork fails.
- Signal: "Trigger result: false"; "<bot> acted on a pull request by <author>, who is not allowed to start a run" then "A bot acted on this pull request, but its author does not have write access"; "workflow_run does not say which repository it ran from" then "Actor does not have write permissions to the repository".
- Cause: since v1.0.273 only the actor's own text is the request, tag mode ignores edits and deletions of other people's comments, a bot acting on a pull request needs a qualifying author, and `workflow_run` checks the fork's owner. Agent mode skips the edit check, against the action's own documentation.
- Fix: the person who wants the run writes the request. Give agent workflows on comment events a job-level `if:` on `github.event.action` (C-02). A bot's pull requests need an author with write access, or the bot in `allowed_bots`.
- Facts: [Actor and text trust](action-contract.md#actor-and-text-trust)

## SE-21. Session guard, git wrappers and credentials for later steps

- Symptom: a later step lost a variable or `PATH` entry the session set, or the upstream from `git push -u`; a later step can't push or fetch through `origin`; one of Claude's git commands is refused; a push over SSH fails.
- Signal: "The session changed files that later steps trust, so they were restored: …"; "Could not restore …"; "Error: only -A, -u, -v, --chmod and file paths are allowed (got: …)"; "Error: only -m with a literal message and basic commit flags are allowed (got: …)"; "Error: this session can only push to <branch> (got: …)"; "Later steps that use the origin remote need their own credentials: GH_TOKEN, GIT_ASKPASS, a credential saved for the username x-access-token, or their own remote URL".
- Cause: since v1.0.273 the action restores the files later steps trust, commits through wrapper scripts that refuse risky flags and other branches, and, with `allowed_bots` or `allowed_non_write_users`, keeps its token out of `.git/config`. Since v1.0.275 the wrappers also ignore the session's `GIT_*` variables, `GIT_SSH_COMMAND` among them. The Claude App token is revoked when the action ends.
- Fix: pass results through `--json-schema` or the step's outputs, not `GITHUB_ENV`. Give later steps their own credentials. For SSH pushes, allow the workflow's own `Bash(git push:*)` knowingly: it gives up the wrappers' protection.
- Facts: [Session guard](action-contract.md#session-guard), [Git, branches and credentials](action-contract.md#git-branches-and-credentials)

## SE-22. A pull request updated after the trigger

- Symptom: a mention or progress-tracking run on a pull request fails before Claude starts, right after someone pushed to it.
- Signal: "PR #N was updated after the trigger (<event commit> -> <head commit>). Push again or mention Claude to run on the latest version." or "PR #N was updated after the trigger (<pushed at> >= <trigger time>). Mention Claude again to run on the latest version."; "PR #N: checked out <commit>, expected <commit>"; "Unexpected head SHA for PR #N: <commit>".
- Cause: tag mode checks out the pull request's head itself and refuses a head newer than the event that started the run, so Claude never reviews code nobody asked about.
- Fix: mention Claude again, or push again for a `pull_request` run. It isn't a workflow defect: propose no patch.
- Facts: [Configuration restored from the base branch](action-contract.md#configuration-restored-from-the-base-branch)

## Verify against

- `anthropics/claude-code-action`, at the pin: the files on each entry's Facts topics (see [Source files](version-drift.md#source-files)), `docs/security.md`, and `docs/usage.md` "Permission Mode": https://github.com/anthropics/claude-code-action
- GitHub, `GITHUB_TOKEN`: https://docs.github.com/en/actions/concepts/security/github_token

The action's version these entries were checked against is in [the Snapshot](version-drift.md#snapshot).
