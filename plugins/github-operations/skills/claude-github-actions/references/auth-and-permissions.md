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
- Anthropic workload identity federation: `anthropic_federation_rule_id` and `anthropic_organization_id`, with optional `anthropic_service_account_id` and `anthropic_workspace_id`. It needs `id-token: write`. The IDs are not credentials and may live in the workflow or in repository variables.
- Amazon Bedrock, Google Vertex AI and Microsoft Foundry through OIDC: `use_bedrock`, `use_vertex`, `use_foundry`, each with `id-token: write`.

None of these works on fork or Dependabot pull requests (SE-11).

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
- The action sets `--permission-mode acceptEdits` for mention runs and appends the user's `claude_args` after it. Whether a later mode flag replaces it is `[unverified]`.
- `--permission-mode auto` lets a call run when Claude Code's safety review passes it, so it widens what the agent can do compared with explicit allow lists. Auto mode is available on all plans; it needs, on the Anthropic API, Claude Opus 4.6 or later, Sonnet 4.6 or later, Haiku 5.5 or a Fable model, and on Bedrock, Vertex and Foundry, Sonnet 5 or later, Opus 4.7 or later, Haiku 5.5 or a Fable model. An organization can turn it off.
- Rules for workflows this skill writes or fixes:
  - set no permission mode unless the user asks for one;
  - never `bypassPermissions` or `--dangerously-skip-permissions`;
  - `auto` only on the user's request, with the capability change stated, on triggers untrusted actors cannot reach, and recommended only with an egress-controlled runner and minimal tools and token.

## Verify against

- Claude Code, GitHub Actions: https://code.claude.com/docs/en/github-actions
- Claude Code, permission modes: https://code.claude.com/docs/en/permission-modes
- GitHub, `GITHUB_TOKEN`: https://docs.github.com/en/actions/concepts/security/github_token
- `anthropics/claude-code-action`, `action.yml`, `docs/setup.md` and `src/github/token.ts`: https://github.com/anthropics/claude-code-action

Verified at `anthropics/claude-code-action@c0949c5` and the documentation above on 4 November 2026.
