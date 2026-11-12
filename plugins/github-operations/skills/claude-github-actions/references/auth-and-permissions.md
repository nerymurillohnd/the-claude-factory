# Authentication and permissions for Claude in Actions

## Contents

- Inference authentication
- GitHub authentication
- Separate controls
- Permission mode
- Verify against

## Inference authentication

Use the profile the repository already uses. When none is configured, the documented default is the Claude GitHub App with an `ANTHROPIC_API_KEY` secret: say so, and list the secret as required setup.

- Claude API key: the `anthropic_api_key` input.
- Subscription OAuth token: the `claude_code_oauth_token` input, generated with `claude setup-token`. It is tied to the subscription of the person who generated it, so a secret shared across repositories uses an API key instead. Never pass an OAuth token through `anthropic_api_key`.
- Anthropic workload identity federation: `anthropic_federation_rule_id` and `anthropic_organization_id`, with optional `anthropic_service_account_id`, `anthropic_workspace_id` and `anthropic_oidc_audience` (default `https://api.anthropic.com`). It needs `id-token: write`. The IDs are not credentials and may live in the workflow or in repository variables. Never set `anthropic_api_key` or `claude_code_oauth_token` beside them: a static credential takes precedence. Inline-comment classification is then skipped (SE-16).
- Amazon Bedrock, Google Vertex AI and Microsoft Foundry through OIDC: `use_bedrock`, `use_vertex`, `use_foundry`, each with `id-token: write`.

Set exactly one profile. The action's credential checks fail the step before Claude starts only when the direct Anthropic API has no API key, no OAuth token and not both workload identity IDs, when more than one of Bedrock, Vertex and Foundry is enabled, or when the enabled provider lacks a variable it requires (SE-17). Other mixes pass its checks: an API key beside an OAuth token is not rejected, and a static key or token beside the workload identity IDs, from the inputs or the job's `env:`, only logs a warning and wins, so federation is not used. None of these works on fork or Dependabot pull requests (SE-11).

## GitHub authentication

Keep it apart from inference credentials and from deployment credentials.

- The Claude GitHub App is the default. Its permission set is shared with Code Review and web auto-fix, and GitHub does not let the installer accept a subset.
- A custom GitHub App with Contents, Issues and Pull requests covers only the action; Code Review and web auto-fix still need the official app.
- `GITHUB_TOKEN`, passed as `github_token`, is scoped to the job's `permissions` and expires with the job. Events it causes start no workflow runs, except `workflow_dispatch` and `repository_dispatch`, and except a workflow-created or workflow-updated pull request's `opened`, `synchronize` and `reopened` events, whose runs wait for approval by a user with write access (SE-10).
- A GitHub App token does start workflows, so a workflow that pushes with it can loop on `pull_request` `synchronize`. Guard it with an actor filter or a job-level `if:`.

## Separate controls

Explain each one on its own; none replaces another.

- The job's `permissions`: start from `permissions: {}` at workflow level and grant each job only what it uses.
- `additional_permissions`: adds permissions to the Claude App token requested through OIDC, and is ignored when `github_token` is provided. It does not enable the CI tools; the job token's `actions: read` does (SE-07).
- The App's installation permissions.
- The token's scope and lifetime.
- OIDC trust conditions, scoped to repository, ref and environment.
- Tool grants: `--allowedTools` and `--disallowedTools` in `claude_args`, `permissions.allow` in `settings`, and a skill's `allowed-tools`. A plugin command's `allowed-tools` grants tools that do not appear in the workflow file: list them in the output.

## Permission mode

- It is a capability setting, not a hardening control by itself. In a run nobody can answer, a tool call that needs permission and that no allow rule covers does not run.
- Which mode a run starts in: the action runs Claude Code through the Agent SDK, whose built-in starting mode is `default` (Manual). Since Claude Code 2.1.302 such a run with no mode set starts in Manual and denies every call that no allow rule covers; before 2.1.302 it could start in `auto` when it didn't fetch feature flags (a third-party provider, `DISABLE_TELEMETRY`). The `auto` default of interactive terminal and VS Code sessions doesn't apply. A `permissions.defaultMode` passed through the `settings` input applies.
- For mention runs the action sets `--permission-mode acceptEdits` and appends the user's `claude_args` after it; a later `--permission-mode` in `claude_args` replaces it.
- `--permission-mode auto` lets a call run when Claude Code's safety review passes it, so it widens what the agent can do compared with explicit allow lists; the `settings` input's `permissions.defaultMode: "auto"` turns it on too. How to audit a workflow that uses it, which layers it needs and how to rate each missing one: [auto-mode-audit.md](auto-mode-audit.md).
- Rules for workflows this skill writes or fixes:
  - set no permission mode unless the user asks for one;
  - never `bypassPermissions` or `--dangerously-skip-permissions`;
  - `auto` only on the user's request, with the capability change stated, on triggers untrusted actors cannot reach, and recommended only with an egress-controlled runner and minimal tools and token.

## Verify against

- Claude Code, GitHub Actions: https://code.claude.com/docs/en/github-actions
- Claude Code, permission modes: https://code.claude.com/docs/en/permission-modes
- GitHub, `GITHUB_TOKEN`: https://docs.github.com/en/actions/concepts/security/github_token
- `anthropics/claude-code-action`, `action.yml`, `docs/setup.md`, `src/github/token.ts`, `base-action/src/validate-env.ts` and `base-action/src/workload-identity.ts`: https://github.com/anthropics/claude-code-action

Verified at `anthropics/claude-code-action@4fa93a8` (v1.0.271) and the documentation above on 12 November 2026.
