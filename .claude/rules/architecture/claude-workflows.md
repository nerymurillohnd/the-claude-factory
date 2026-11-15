---
paths:
  - ".github/workflows/**"
---

# Claude workflow credentials

- `evals.yml` is the only workflow that runs Claude. It reads `secrets.CLAUDE_CODE_OAUTH_TOKEN` as the `CLAUDE_CODE_OAUTH_TOKEN` env of the eval step, which bills the owner's subscription.
- No workflow reads `secrets.ANTHROPIC_API_KEY`: an API key takes precedence over the token and bills the API account instead. `npm run check:consistency` (PC-13) fails on a workflow that reads a Claude secret it doesn't own.
- Keep the token in the `claude` environment, not as a repository secret, and set `environment: claude` only on the job that reads it.
- Read the on/off switch `CLAUDE_EVALS` as a repository variable, never an environment variable: it is read in a job-level `if:`, which runs before the job enters `claude` and sees no environment variable.
- Add no workflow that runs `anthropics/claude-code-action` without the owner's approval: the owner removed the review and `@claude` workflows on 2026-11-15.
