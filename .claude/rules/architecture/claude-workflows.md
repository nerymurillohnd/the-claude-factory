---
paths:
  - ".github/workflows/**"
---

# Claude workflow credentials

- Give each Claude workflow only its own secret, by its exact name:
  - `claude-code-review.yml`: `secrets.ANTHROPIC_API_KEY`, as the action's `anthropic_api_key`. The review bills the Claude Console API account.
  - `claude.yml`: `secrets.CLAUDE_CODE_OAUTH_TOKEN`, as the action's `claude_code_oauth_token`. It bills the owner's subscription.
  - `evals.yml`: `secrets.CLAUDE_CODE_OAUTH_TOKEN`, as the `CLAUDE_CODE_OAUTH_TOKEN` env of the eval step, never `ANTHROPIC_API_KEY`: an API key takes precedence over the token and bills the API account instead.
- Reference neither secret from any other workflow; `validate.yml` and `release.yml` run no Claude model and need no credential.
- Keep both secrets in the `claude` environment, not as repository secrets, and set `environment: claude` only on a job that reads one.
- Read the on/off switches `CLAUDE_CODE_REVIEW` and `CLAUDE_EVALS` as repository variables, never environment variables: each is read in a job-level `if:`, which runs before the job enters `claude` and sees no environment variable.
