# Sharp edges of anthropics/claude-code-action

## Contents

- How to use this catalog
- SE-01 to SE-17
- Verify against

## How to use this catalog

Each entry gives the symptom, the log signal, the cause and the fix. Match a run against the whole catalog, by its log lines and its workflow file, before forming a general hypothesis. Name the matched ID in the report, or say that no entry matched.

## SE-01. Missing or empty `structured_output`

- Symptom: a step that reads `fromJSON(steps.<id>.outputs.structured_output)` fails, or the Claude step fails after a run that looked complete.
- Signal: "--json-schema was provided but Claude did not return structured_output".
- Cause: with `--json-schema` in `claude_args`, the action fails the step when the result is unsuccessful or carries no structured output; without the flag the output is never set. The flag is found only after `claude_args` is shell-parsed, so quoting can drop or split the schema.
- Fix: quote the schema as one argument, guard every consumer with `if: steps.<id>.outputs.structured_output != ''`, and read it through `env:`.

## SE-02. Bot actors rejected

- Symptom: runs triggered by Dependabot, Renovate, `github-actions[bot]`, Copilot or another app fail at once.
- Signal: "Workflow initiated by non-human actor: <name> (type: Bot)" or "(actor not found on GitHub)".
- Cause: `allowed_bots` is empty by default, and any actor whose account type is not `User`, or that the Users API cannot resolve, is rejected. The check runs on every event, scheduled runs included: GitHub attributes a scheduled run to a repository user, usually the one who last changed the workflow's `cron`, and a bot there is rejected too.
- Fix: decide per bot whether Claude should run. Skip unwanted bot events with a job-level `if:` before a runner starts, and list only the needed bots in `allowed_bots`. Never `*` by default. For a scheduled workflow last edited by a bot, list that bot or have a person edit the schedule.

## SE-03. The write-access gate, and a bypass that does nothing

- Symptom: runs for contributors without write access fail, even with `allowed_non_write_users` set.
- Signal: "Actor does not have write permissions to the repository".
- Cause: issue, pull request and `workflow_run` events check the actor's write access, and for `workflow_run` the upstream run's actor too. `allowed_non_write_users` is honored only when the `github_token` input is provided; otherwise the bypass is skipped. An actor whose login ends in `[bot]` passes the write check without one, and the action's security notes say allowed bots are not checked for repository permissions: an `allowed_bots` entry lets that bot run Claude without write access.
- Fix: use the bypass only with `github_token: ${{ secrets.GITHUB_TOKEN }}`, minimal permissions and minimal tools, never with a personal access token. On a public repository, treat every `allowed_bots` entry as a grant to an actor without write access.

## SE-04. Mode surprises and green no-ops

- Symptom: Claude answers every comment, ignores `@claude`, or the run is green while nothing happened.
- Signal: "Mode: tag" or "Mode: agent", "Trigger result: false", "No trigger found, skipping remaining steps"; the step still succeeds.
- Cause: on comment and review events a `prompt` selects agent mode, so the trigger phrase stops mattering; a `pull_request` event without `prompt` or `track_progress` does nothing.
- Fix: pair every `prompt` on comment events with a job-level `if:`. Report a green run with "No trigger found" as a no-op, never as a success.

## SE-05. `track_progress` on unsupported events

- Symptom: the step fails before Claude starts, or tools and comments change once `track_progress` is added.
- Signal: "track_progress is only supported for events: ..." or "track_progress for pull_request events is only supported for actions: ...".
- Cause: it accepts `pull_request` (opened, synchronize, ready_for_review, reopened, labeled), `issues`, `issue_comment`, `pull_request_review_comment` and `pull_request_review`; on them it forces tag mode.
- Fix: use it only there, and review the tools and the tracking comment it brings.

## SE-06. Sticky comments that do not stick

- Symptom: `use_sticky_comment: true` still posts a new comment each run.
- Cause: the sticky path runs only for `pull_request` events, and finds the previous comment by a bot login containing `claude` or by the exact initial body. With `github_token` (`github-actions[bot]`) or a custom app without `claude` in its login, nothing matches.
- Fix: rely on sticky comments only with the Claude GitHub App.

## SE-07. CI tools missing

- Symptom: Claude says it cannot see CI results.
- Signal: "The github_ci MCP server requires 'actions: read' permission. Skipping CI server installation." The run continues.
- Cause: the CI server is installed only on a pull request, in tag mode or in agent mode with `mcp__github_ci__*` named in `--allowedTools`, and only when the job's own token has `actions: read`. `additional_permissions` widens the Claude App token, not the job token.
- Fix: grant `actions: read` in the job's `permissions`, and name the CI tools in agent mode. Outside pull requests the server never starts.

## SE-08. Review findings in the log, nothing on the PR

- Symptom: a review run is green and its log holds findings, but the PR shows no inline comments.
- Cause: the inline-comment server starts only on a pull request, and only when `--allowedTools` names an inline-comment tool (`mcp__github_inline_comment` or `mcp__github_inline_comment__…`) or a GitHub MCP tool (`mcp__github` or `mcp__github__…`). Without either, no tool can post inline. With `classify_inline_comments` at its default `true`, comments are buffered and classified after the session (SE-16); `confirmed: true` posts at once.
- Fix: name `mcp__github_inline_comment__create_inline_comment` in `claude_args`.

## SE-09. Run outcome edge cases

- Signal: an error result subtype from the Claude Code SDK, such as `error_max_turns` `[unverified: not in the action's source]`; "Claude reported a successful result after <n> turns, exceeding the configured maximum of <m>"; "Claude result reported subtype success with is_error:true"; "No result message received from Claude".
- Cause: the step fails when `--max-turns` is exceeded even on a success result, and treats `success` with `is_error` as a failure. Budget exhaustion and a turn overrun need opposite answers: more budget, or less scope.
- Fix: decide from the result subtype and `is_error` together, never from the red check alone. Read `conclusion` and `execution_file` before any retry, and rerun an errored-but-completed run at most once.

## SE-10. Claude's commits run no CI, or wait for approval

- Symptom: Claude's commits on a PR show no checks, or checks waiting for "Approve workflows to run".
- Cause: events caused by `GITHUB_TOKEN` start no runs, except `workflow_dispatch` and `repository_dispatch`, and a workflow-created or workflow-updated pull request's `opened`, `synchronize` and `reopened` events, which start runs that a user with write access must approve.
- Fix: choose the token knowingly (see `auth-and-permissions.md`). Report "awaiting approval" as such, never as passing or failing.

## SE-11. Fork and Dependabot pull requests without secrets or OIDC

- Symptom: authentication fails only on fork PRs, or only on Dependabot PRs.
- Cause: GitHub gives fork pull request runs a read-only token unless an admin enabled "Send write tokens to workflows from pull requests", issues them no `id-token`, and withholds secrets; Dependabot pull requests are treated as forks. API-key, OAuth, workload-identity, Bedrock, Vertex and Foundry profiles all fail there, and so does the default App token, which needs `id-token: write`.
- Fix: skip those events with a job-level `if:`, or use the fork-safe pattern in `trust-boundaries.md`. Never check out the head under `pull_request_target`. Report "Send write tokens" as a risk.

## SE-12. Restored configuration confuses the agent

- Symptom: on a PR that edits `.claude/`, `CLAUDE.md` or another restored path, Claude reports files missing or unchanged.
- Signal: "Restoring ... from origin/<base> (PR head is untrusted)".
- Cause: on pull request events the action restores `.claude`, `.mcp.json`, `.claude.json`, `.gitmodules`, `.ripgreprc`, `CLAUDE.md`, `CLAUDE.local.md` and `.husky` from the base branch and keeps the PR's versions in `.claude-pr/`.
- Fix: one prompt line naming the restore and pointing to `.claude-pr/`.

## SE-13. Findings that cannot be published

- Symptom: the check is red or green, the PR shows no review, and the findings are only in the log.
- Cause: the prompt asks Claude to comment, but no posting tool is granted, so every attempt is denied.
- Fix: grant the posting tool the prompt relies on (SE-08), or have the prompt write only to the run log and the step summary.

## SE-14. Removed inputs ignored

- Symptom: a workflow that still passes a removed input runs green without what that input configured.
- Signal: GitHub's "Unexpected input(s)" warning annotation on the step `[unverified wording]`.
- Cause: the input is no longer declared in `action.yml`. A dropped `disallowed_tools` widens what the agent may do, and a dropped `experimental_allowed_domains` removes the network restriction: both are security regressions. The replacements are in `action-contract.md`.
- Fix: replace every input the resolved `action.yml` does not declare.

## SE-15. Workflow validation skip: green, and nothing ran

- Symptom: the Claude step is green, posts nothing and leaves no Claude output, typically on the pull request that adds or edits the Claude workflow.
- Signal: "Skipping action due to workflow validation: <message>", then "Exiting due to workflow validation skip"; the step output `skipped_due_to_workflow_validation_mismatch` is `true`.
- Cause: on the default GitHub App path (no `github_token` input), the action exchanges the job's OIDC token for an App token. GitHub's validation refuses it when the workflow differs from the one on the default branch (`workflow_not_found_on_default_branch`, or a 401 saying "workflow validation failed"), and the action treats that as a skip that succeeds. With `github_token` set, this path never runs.
- Fix: merge the workflow change to the default branch first and judge the workflow on the next run there; report the skip as a no-op, never as a pass. Accept the skip on the pull request that changes the workflow.

## SE-16. Inline comments dropped, or posted unfiltered

- Symptom: a review run's log shows inline comments that never reach the pull request, or test-like comments appear on it.
- Signal: "::warning::<n> buffered comment(s) classified as test/probe — NOT posted", "<n> with confirmed=false — not posting", or "ANTHROPIC_API_KEY not set — skipping classification, posting all unconfirmed comments".
- Cause: after the session, buffered comments are classified by `claude-haiku-4-5`; comments judged to be probes are dropped and `confirmed: false` comments are never posted. Classification runs only when the `anthropic_api_key` input is set. With an OAuth token, workload identity federation, Bedrock, Vertex or Foundry it is skipped and every unconfirmed comment is posted; a failed classification call does the same.
- Fix: read the warning lines before concluding that the review found nothing; with a non-API-key profile, expect unfiltered comments, or set `classify_inline_comments: false` knowingly.

## SE-17. Authentication fails before Claude starts

- Symptom: the step fails at once, before any Claude output.
- Signal: "Environment variable validation failed:" followed by one of: "Cannot use multiple providers simultaneously", "Workload identity federation requires both ANTHROPIC_FEDERATION_RULE_ID and ANTHROPIC_ORGANIZATION_ID to be set", "Either ANTHROPIC_API_KEY, CLAUDE_CODE_OAUTH_TOKEN, or workload identity federation (...) is required when using direct Anthropic API", "AWS_REGION is required when using AWS Bedrock", a missing Vertex variable (`ANTHROPIC_VERTEX_PROJECT_ID`, `CLOUD_ML_REGION`), or a missing Foundry resource; or "Could not fetch an OIDC token. Did you remember to add `id-token: write` to your workflow permissions?".
- Cause: no credential, a partial workload identity configuration, more than one provider, a provider's required variable missing, or no `id-token: write` on the job that needs the OIDC token (the default App token, workload identity, cloud providers).
- Fix: set exactly one profile as `auth-and-permissions.md` describes, with its variables, and grant `id-token: write` when the profile needs it. An empty secret on a fork or Dependabot run is SE-11.

## Verify against

- `anthropics/claude-code-action`, source and `action.yml`: https://github.com/anthropics/claude-code-action
- GitHub, `GITHUB_TOKEN`: https://docs.github.com/en/actions/concepts/security/github_token

Verified at `anthropics/claude-code-action@4fa93a8` (v1.0.271) and GitHub's documentation on 12 November 2026.
