# Audit and harden workflow files

The checks the audit runs in layer 3 of [detection-layers.md](detection-layers.md), and how to judge each one. For every check this page says what to look for, when it is a finding and when it isn't, how severe it is, what the patch is, and why. Each check also names the zizmor audit and the CodeQL rule that overlap it, or "none".

## Contents

- Scope and inputs
- Severity scale
- When a check can't be decided
- Checks every workflow gets (W-01 to W-11)
- Checks for steps that run claude-code-action (C-01 to C-16)
- Each finding
- Apply the patches
- Verify against

## Scope and inputs

Read every file under `.github/workflows/`, every composite action (`action.yml` or `action.yaml` anywhere in the repository) and every reusable workflow the files call. Read the repository's Actions policy with `gh api repos/<owner>/<repo>/actions/permissions` and `gh api repos/<owner>/<repo>/actions/permissions/workflow`, and the rules on the default branch with `gh api repos/<owner>/<repo>/rules/branches/<default branch>`; when one can't be read, say so and decide the checks that need it as "When a check can't be decided" says. This audit reads files and settings; the state of runs, artifacts, caches and runners belongs to the repository audit.

## Severity scale

Rate every finding by two questions: who can trigger it, and what they get. Use this scale for every check, including scanner results that match no check:

| Severity | Who can trigger it, and what they get |
| :-- | :-- |
| critical | Any GitHub user, with no maintainer action, gets code execution in a job that holds secrets or a token that can write to the repository |
| high | Any GitHub user gets code execution without secrets or write access; or a collaborator, or one maintainer action such as a label or an approval, gets secrets or write access; or a security control is silently gone |
| medium | A protection layer is missing that would limit the damage of another flaw; or a misconfiguration blocks merges or runs |
| low | Hygiene and cost: no direct path to harm |

When the scale and a check's own rating disagree for a given workflow, the scale wins: a check's rating assumes the usual case.

## When a check can't be decided

Sometimes a check needs a fact you can't read: the repository's default token permissions, an organization secret, the network of a self-hosted runner, the inputs a third-party action really needs. Then:

1. Write down which fact is missing and why you couldn't read it.
2. Ask the user when one answer settles it, for example "does this runner restrict outbound network access?".
3. Without an answer, report the check as "unverified", rated as if the risky case were true, and say which answer would lower it.

Never rate an undecided check as a pass.

## Checks every workflow gets

### W-01. Expressions expanded into a shell or script

- **Look for:** `${{ }}` inside `run:`, or inside `script:` of `actions/github-script`.
- **A finding when** the expression carries a value an outside actor can influence: `github.event.*` fields (issue and pull request titles and bodies, comment bodies, branch and label names), `github.head_ref`, step or job outputs that came from such text, and `structured_output`. A quoted assignment is no exception (`trust-boundaries.md`).
- **Not a finding when** the value is fixed by the repository or the run: `github.repository`, `github.sha`, `github.run_id`, `matrix` values written in the file, or `inputs` of a `workflow_dispatch` only people with write access can start (then rate it low).
- **Severity:** by the scale. Usually critical on `issues`, `issue_comment` or `pull_request_target` jobs that hold secrets or a write token.
- **Patch:** pass the value through `env:` and read `"$NAME"` in the script.
- **Why:** the expression is pasted into the script before the shell parses it, so the text becomes code.
- **Scanners:** zizmor `template-injection`; CodeQL `actions/code-injection/*`.

### W-02. A pull request's code run with the base's privileges

- **Look for:** `pull_request_target` or `workflow_run` jobs that check out the pull request's head into the workspace (`ref:` naming the head branch or `head.sha`, or `repository:` naming the fork), or that build, test or run it; `actions/checkout` with `allow-unsafe-pr-checkout: true`.
- **Not a finding when** the job checks out only the base, or fetches the head outside the workspace and runs nothing from it, as `trust-boundaries.md` describes.
- **Severity:** critical.
- **Patch:** the design in `trust-boundaries.md`, or move the job to `pull_request`.
- **Why:** these triggers run with the base repository's secrets and write token, while the head is code anyone can submit.
- **Scanners:** zizmor `dangerous-triggers` flags the trigger, and `dangerous-checkout` (1.33.0 or later) flags `allow-unsafe-pr-checkout`; CodeQL `actions/untrusted-checkout/*`.

### W-03. Token permissions wider than the job uses

- **Look for:** no workflow-level `permissions:`; `write-all` or `read-all`; a job write scope nothing in the job uses; `id-token: write` without OIDC.
- **How to decide "unused":** a write scope is used when a step pushes (`git push`, an action that commits), writes through `gh` or the API, posts through a tool the agent is granted, or calls an action whose documentation needs that scope. When you can't tell from the file or the action's documentation, report it as unverified.
- **Not a finding when** workflow-level `permissions:` is absent but the repository's default token permission is read-only (`default_workflow_permissions: read` in the Actions policy): rate that low, as hygiene.
- **Severity:** `write-all`, or an absent block under a write default: high. One unused write scope: medium.
- **Patch:** `permissions: {}` at workflow level, and each job's scopes set to exactly what it uses.
- **Why:** every injected or mistaken step acts with the whole token.
- **Scanners:** zizmor `excessive-permissions`; CodeQL `actions/missing-workflow-permissions`.

### W-04. Actions not pinned to a commit

- **Look for:** `uses:` with a tag or branch instead of a full 40-character commit SHA; a SHA that is an annotated tag's object rather than its commit (compare with the `^{}` line of `git ls-remote --tags`); a version comment that doesn't match the SHA.
- **Not a finding when** the `uses:` is a local path (`./...`) or a Docker image pinned by digest.
- **Severity:** high when the job holds secrets or a write token; medium otherwise; a wrong version comment is low.
- **Patch:** pin as the pinning rule in `SKILL.md` says, resolved live.
- **Why:** a tag or branch can be moved to new code after the review.
- **Scanners:** zizmor `unpinned-uses`, `ref-version-mismatch`, and offline-skipped `impostor-commit` and `ref-confusion`.

### W-05. Checkout credentials left on disk

- **Look for:** `actions/checkout` without `persist-credentials: false`.
- **Not a finding when** a later step in the same job pushes with those credentials.
- **Severity:** medium when the job later runs code it didn't write (dependencies, the pull request's code, an agent) or uploads the workspace as an artifact; low otherwise.
- **Patch:** `persist-credentials: false`.
- **Why:** the token stays in `.git/config` for every later step to read.
- **Scanners:** zizmor `artipacked`.

### W-06. Secrets exposed or passed wholesale

- **Look for:** `secrets: inherit`; a secret echoed, or `set -x`, `env` or `printenv` in a step that holds one; `ACTIONS_STEP_DEBUG` set as a variable or secret.
- **Severity:** a printed secret: high. `secrets: inherit` to a workflow outside the repository: high; inside it: medium. `ACTIONS_STEP_DEBUG`: medium.
- **Patch:** pass each secret by name; remove the printing and the debug setting.
- **Why:** logs of public repositories are public, and masking misses transformed values.
- **Scanners:** zizmor `secrets-inherit`; the others none.

### W-07. Deployment credentials reachable from untrusted events

- **Look for:** deployment or publishing secrets, environments or OIDC roles in a workflow that `issues`, `issue_comment`, `pull_request_target` or `workflow_run` can start, or in the same job as an agent or an untrusted build.
- **Severity:** critical when an outside actor can reach the step that holds them; high otherwise.
- **Patch:** a separate workflow or job for deployment, gated by an environment with required reviewers.
- **Why:** one injection in the triggering job would carry the deployment keys.
- **Scanners:** zizmor `dangerous-triggers` and, under the auditor persona, `secrets-outside-env`.

### W-08. No time limit, no cancelling of superseded runs

- **Look for:** jobs without `timeout-minutes` (the default is 360 minutes); workflows that comment, review or label without a `concurrency` group that cancels runs a newer event supersedes.
- **Severity:** low; medium for a job that runs an agent.
- **Patch:** `timeout-minutes` sized to the job; `concurrency: { group: <workflow>-<issue or PR number>, cancel-in-progress: true }`.
- **Why:** a stuck or looping job burns minutes and can post for hours.
- **Scanners:** zizmor `concurrency-limits` (pedantic persona only); timeouts none.

### W-09. Required checks that skip

- **Look for:** a workflow whose job is a required check (from the rules read in "Scope and inputs") and that has `paths`, `branches` or a commit-message filter at workflow level, or a job-level `if:` that can skip the required job.
- **Severity:** a workflow-level filter: medium, because the check never reports and blocks the merge. A job-level `if:`: high when the check guards security or tests, medium otherwise, because GitHub reports the skipped job as `Success` and the requirement is bypassed.
- **Patch:** move the filter into a step, or add a job that always runs and reports the result.
- **Why:** GitHub treats a skipped job as passing and a workflow that never started as pending.
- **Scanners:** none.

### W-10. References to things that no longer exist

- **Look for:** branches in `on:` filters (`git ls-remote --heads`), secrets the repository doesn't have (`gh secret list` shows names only), and files under `paths:` or used by steps.
- **When it can't be decided:** organization and environment secrets may not be readable; report those as unverified, not missing.
- **Severity:** low; medium when the missing piece is a required check's or a deployment's.
- **Patch:** fix or remove the reference.
- **Scanners:** none.

### W-11. Actions the repository's policy doesn't allow

- **Look for:** `uses:` outside the allowed-actions policy read in "Scope and inputs".
- **Severity:** medium, because the workflow fails when it runs.
- **Patch:** a permitted equivalent, or tell the user the policy needs their change.
- **Scanners:** none (zizmor `forbidden-uses` reads its own configuration, not the repository's policy).

## Checks for steps that run claude-code-action

Read `action-contract.md`, `auth-and-permissions.md` and `sharp-edges.md` before these. When a step runs Claude in auto mode, also run every layer of [auto-mode-audit.md](auto-mode-audit.md). No zizmor audit or CodeQL rule covers these checks.

| ID | Look for | Severity and why | Patch |
| :-- | :-- | :-- | :-- |
| C-01 | Inputs the pinned `action.yml` doesn't declare, checked against the removed-input list in `action-contract.md` (SE-14) | High for a dropped `disallowed_tools` or `experimental_allowed_domains`, because the control is silently gone; low for others, which are ignored | Its replacement in `claude_args` |
| C-02 | A `prompt` on comment events without a job-level `if:` (SE-04) | Medium: every comment starts the agent and spends credits | A job-level `if:` that matches the trigger phrase |
| C-03 | `*` in `allowed_bots` or `allowed_non_write_users`; bot events without `allowed_bots` or a bot filter (SE-02) | High for `*`: anyone, or any bot, reaches the agent and its token; low for a missing filter | Name the bots and users |
| C-04 | `allowed_non_write_users` without `github_token` (SE-03) | Medium: the bypass does nothing | Add `github_token`, or remove the list |
| C-05 | `track_progress` on an unsupported event (SE-05); `use_sticky_comment` with `github_token` or a custom app (SE-06) | Low | As each entry says |
| C-06 | CI tools expected without `actions: read`, or on events that aren't pull requests (SE-07) | Low | Add the scope, or remove the expectation |
| C-07 | `structured_output` used without `--json-schema` or an empty guard (SE-01); and anywhere in `run:` through `${{ }}` (W-01) | Low for the guard; the interpolation is W-01 | Add the schema and the guard |
| C-08 | An inline-comment review without the tool in `--allowedTools` (SE-08); a prompt asking to post with no posting tool (SE-13); a review not authenticated with an API key (SE-16) | Low: the review posts nothing, or posts unfiltered | Grant the tool; or use an API key |
| C-09 | A scheduled Claude workflow last edited by a bot not in `allowed_bots` (SE-02); any `allowed_bots` entry on a public repository (SE-03) | Medium for the public-repository case; low otherwise | As each entry says |
| C-10 | More than one inference profile, or a profile without its variables or `id-token: write` (SE-17) | Medium: the step fails before Claude starts | One profile, with what it needs |
| C-11 | `mcp__github` granted as a wildcard, or `--disallowedTools` without the approval and merge tools (`trust-boundaries.md`) | High: an injected agent could approve or merge | Name the tools needed; deny the rest |
| C-12 | `bypassPermissions` or `--dangerously-skip-permissions` | Critical when the workflow is open to outsiders as `auto-mode-audit.md` defines it; high otherwise: every call runs unchecked | Remove it |
| C-13 | `--permission-mode auto`, or `defaultMode: "auto"` in the `settings` input | Run `auto-mode-audit.md`; its table rates each missing layer | Its patches |
| C-14 | `--model` with an ID not resolved live; `show_full_output: true` or `--debug` on a public repository | High for the output settings, which publish the agent's full transcript in public logs; low for the model | Remove them; resolve the model ID live |
| C-15 | A marketplace passed as a URL instead of a pinned local checkout, or Anthropic's plugins through the `claude-code-plugins` redirect instead of `claude-plugins-official` (`action-contract.md`) | Medium: each run takes upstream's newest code | A local checkout at a resolved commit |
| C-16 | A pull request's head passed with `--add-dir` without neutralizing its `.claude/` (`trust-boundaries.md`); an OAuth token passed through `anthropic_api_key` | High for `--add-dir`: the pull request's skills and agents load; low for the token, which belongs in `claude_code_oauth_token` | As `trust-boundaries.md` says; move the token |

## Each finding

- The check ID (W-xx, C-xx, or the scanner's rule ID) and every layer that saw it.
- File and line.
- What an attacker or a failure needs to trigger it.
- Its impact and severity by the scale above.
- The exact patch: the replacement lines, with every new `uses:` resolved and pinned as `SKILL.md` says.
- The risk left after the patch.

## Apply the patches

Only after the user approves them. Apply them on a branch, check each patched file again against every check on this page and every layer of `auto-mode-audit.md` that applied, and land the change through `github-operations:auto-pr-lifecycle`. Changing a workflow's permissions, triggers or secrets is a separate approval from the rest of the patch.

## Verify against

- GitHub, secure use of Actions: https://docs.github.com/en/actions/reference/security/secure-use
- GitHub, workflow syntax: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- GitHub, conditions and required checks: https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions and https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- zizmor audits: https://docs.zizmor.sh/audits/
- CodeQL queries for Actions: https://codeql.github.com/codeql-query-help/actions/

Updated on 12 November 2026 from `anthropics/claude-code-action@4fa93a8` (v1.0.271), zizmor 1.32.0 and the documentation above.
