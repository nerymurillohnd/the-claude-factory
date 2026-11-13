# Choose authentication and the permission mode

How to choose a workflow's inference profile, its GitHub token and its permission mode, and what each change costs. The facts these decisions rest on are in [action-contract.md](action-contract.md); check them against the step's pin first ([version-drift.md](version-drift.md#compare-with-the-snapshot)).

## Inference credentials: which profile

1. **Keep the profile the repository already uses.** Changing it is the user's decision, not a fix.
2. **When none is configured**, the documented default is the Claude GitHub App with an `ANTHROPIC_API_KEY` secret. Say so, and list the secret as setup the user does; secrets never pass through Claude.
3. **Exactly one profile per step.** Which mixes fail the step and which pass silently: [Inference credentials](action-contract.md#inference-credentials). A static key or token beside the federation IDs is a finding (C-10), because federation is then never used.
4. **A shared secret uses an API key.** A `claude_code_oauth_token` is tied to the subscription of the person who generated it with `claude setup-token`. Never pass an OAuth token through `anthropic_api_key` (C-16).
5. **Inline reviews need the API key input.** When a workflow posts inline review comments with any profile other than `anthropic_api_key`, its comments post unclassified ([Comments, reviews and structured output](action-contract.md#comments-reviews-and-structured-output); C-08).
6. **Fork and Dependabot pull requests are different.** Fork runs get no secrets and no OIDC write by default; Dependabot runs get Dependabot secrets, not Actions secrets (SE-11). Don't recommend a profile change as the fix for those runs.

## GitHub token: App token or github_token

| Choose | When | Because |
| :-- | :-- | :-- |
| The Claude App token (no `github_token`) | The default, and whenever Claude's pushes must start CI or a tracking comment must stay sticky | It starts workflows, is revoked at the end of the action, and keeps `allowed_non_write_users` inert. It needs `id-token: write`, and it is skipped green on a pull request that edits the workflow (SE-15) |
| A custom GitHub App token | The organization can't install the official app | It covers only the action. Code Review and web auto-fix still need the official app, whose permission set the installer can't narrow |
| `github_token: ${{ github.token }}` | The user wants the job's own token, scoped by `permissions:` and expiring with the job | Events it causes start no workflow runs, except `workflow_dispatch`, `repository_dispatch`, and a pull request's `opened`, `synchronize` and `reopened`, whose runs wait for approval (SE-10). Read its other costs in [Costs of each change](#costs-of-each-change) |
| A PAT as `github_token` | Never as a fix | It outlives the job, the action never revokes it, and by default it stays in `origin`'s URL for later steps |

- A token that starts workflows can loop: a workflow that pushes with the App token and runs on `pull_request` `synchronize` needs an actor filter or a job-level `if:`.
- Keep these controls apart; none replaces another: the job's `permissions` (start from `permissions: {}` and grant each job what it uses); `additional_permissions` (widens only the Claude App token, and doesn't enable the CI tools); the App's installation permissions; the token's lifetime; OIDC trust conditions scoped to repository, ref and environment; and tool rules (`--allowedTools` and `--disallowedTools`, `permissions` in the `settings` input, a skill's `allowed-tools`). A plugin command's `allowed-tools` grants tools the workflow file doesn't show: list them in the report.

## Costs of each change

Many fixes change something else in the step. Before writing a patch, find its row; the patch carries what the last column says. [Build the patches](workflow-audit.md#build-the-patches) combines them.

| Change | What else changes | The patch must add |
| :-- | :-- | :-- |
| Add `github_token` | Sticky comments stop matching (SE-06). Claude's pushes start no CI (SE-10). The token is never revoked. The `allowed_non_write_users` bypass turns on ([Actor and text trust](action-contract.md#actor-and-text-trust)) | Nothing more, unless `allowed_non_write_users` holds `*`: resolve that first, because adding the token would admit every actor |
| Empty or remove `allowed_non_write_users` | Auto may turn on ([Permission mode](action-contract.md#permission-mode)). The automatic subprocess scrub and the isolation step go ([Environment variables the action passes](action-contract.md#environment-variables-the-action-passes)). The credential helper goes unless `allowed_bots` stays ([Git, branches and credentials](action-contract.md#git-branches-and-credentials)) | The frozen mode. The scrub, set explicitly, when the step relies on script caps |
| Empty or remove `allowed_bots` | Auto may turn on. The credential helper goes unless `allowed_non_write_users` stays | The frozen mode |
| Remove `bypassPermissions` or `--dangerously-skip-permissions` | The action's default mode returns, which may be auto | The frozen mode, chosen by [Permission mode in patches](#permission-mode-in-patches) |
| Bump the pinned version | Whatever the releases in between changed ([A version bump is a patch](version-drift.md#a-version-bump-is-a-patch)) | The frozen mode, and every C-check run again on the bumped file |
| Narrow `--tools` | In tag mode, `Edit` and `Write` disappear unless listed ([Tools the action grants](action-contract.md#tools-the-action-grants-and-the-mcp-servers-it-starts)) | `Edit` and `Write` in the list for mention workflows that change code |
| Set `persist-credentials: false` | Tag mode on a private repository may fail to fetch the pull request ([Git, branches and credentials](action-contract.md#git-branches-and-credentials)) | A line in the finding: confirm on the first run |
| Set `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB: '1'` | Subprocesses lose `NPM_TOKEN`, `DATABASE_URL` and similar variables; the GitHub token stays. On a pin that bundles Claude Code older than 2.1.323, read-only git can break on Linux | Only on a pin at v1.0.274 or later, or bump the pin in the same patch |

## Permission mode in patches

**Freeze the mode.** Every patch that changes a claude-code-action step (its `uses:`, `with:` or `env:`), or a setting its effective mode depends on, writes the step's current effective mode explicitly in `claude_args`, in the space form. A fix never changes the mode as a side effect; changing the mode is its own proposal, which the user approves on its own.

1. **Find the effective mode** from the pin (the drift check) and the table in [Permission mode](action-contract.md#permission-mode). Record it in the finding as "mode before".
2. **Write it:**

   | Effective mode | Add to `claude_args` |
   | :-- | :-- |
   | auto | `--permission-mode auto` |
   | acceptEdits | `--permission-mode acceptEdits` |
   | Manual | `--permission-mode default` |
   | A mode from the `settings` input (agent runs only) | That mode, as `--permission-mode <mode>` |

   - When `claude_args` already sets the mode in the space form, it is the effective mode: keep it.
   - When it uses the equals form, rewrite it to the space form with the same value, and say why: the equals form isn't verified to take effect.
   - Put the flag in `claude_args`, never only in the `settings` input, which tag runs ignore.
3. **When the effective mode can't be known** (the pin can't be resolved, or the mode depends on an `env:` value the audit can't read), don't guess. Add one Questions row for it ([When a check can't be decided](workflow-audit.md#when-a-check-cant-be-decided)), and hold back every patch whose row in [Costs of each change](#costs-of-each-change) says "the frozen mode" until it is answered.
4. **Changing the mode** is a separate finding with its own patch, stating what the agent can do before and after. Never propose `bypassPermissions` or `--dangerously-skip-permissions`.
5. **Auto is acceptable** when every layer in [auto-mode-audit.md](auto-mode-audit.md) is in place. It is never assumed off, and never refused by default. When a workflow sets `allowed_non_write_users` or `allowed_bots`, say in the report that upstream keeps auto off by default for such workflows, because anyone's text reaches them.

After the patch, re-derive the mode by [Validate the patches](workflow-audit.md#validate-the-patches): the "mode after" must equal the "mode before" unless the user approved a change.

## Verify against

- Claude Code, permission modes: https://code.claude.com/docs/en/permission-modes
- Claude Code, GitHub Actions: https://code.claude.com/docs/en/github-actions
- GitHub, `GITHUB_TOKEN`: https://docs.github.com/en/actions/concepts/security/github_token
- `anthropics/claude-code-action`, `docs/usage.md` and `docs/security.md`, at the pin: https://github.com/anthropics/claude-code-action
