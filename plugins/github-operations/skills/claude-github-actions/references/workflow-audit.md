# Audit and harden workflow files

## Contents

- Scope and inputs
- Checks every workflow gets
- Checks for steps that run claude-code-action
- Linters
- Each finding
- Apply the patches
- Verify against

## Scope and inputs

Read every file under `.github/workflows/`, every composite action (`action.yml` in the repository) and every reusable workflow the files call. Read the repository's Actions policy with `gh api repos/<owner>/<repo>/actions/permissions` and `gh api repos/<owner>/<repo>/actions/permissions/workflow`; when it cannot be read, say so. This audit reads files; the state of runs, artifacts, caches and runners belongs to the repository audit.

## Checks every workflow gets

- `${{ }}` inside `run:` with any value an outside actor can influence: event fields, titles, bodies, branch names, step outputs, `structured_output`. A quoted assignment is no exception (`trust-boundaries.md`).
- `pull_request_target` or `workflow_run` that checks out the PR's head (`ref:` naming the head or the run's head SHA) into the workspace, or builds, tests or runs it.
- `permissions:` missing at workflow level, `write-all` or `read-all`, or a job write scope nothing in the job uses (`contents: write` without a push, `pull-requests: write` without a posting tool, `id-token: write` without OIDC).
- `uses:` not pinned to a full commit SHA, pinned to a branch, or pinned to an annotated tag's object instead of its commit.
- `actions/checkout` without `persist-credentials: false` in a job that does not push.
- `secrets: inherit`; secrets echoed, `set -x`, `env` or `printenv` in a step that holds a secret; `ACTIONS_STEP_DEBUG`.
- Deployment credentials in a workflow whose agent or build job untrusted events can start.
- Jobs without `timeout-minutes`; review workflows without a `concurrency` group that cancels superseded runs.
- A required check skipped by a `paths` filter or an `if:`: it never reports and blocks the merge.
- References to branches, secrets or paths that no longer exist.
- Actions the repository's allowed-actions policy does not permit.

## Checks for steps that run claude-code-action

- Inputs the pinned `action.yml` does not declare, using the removed-input list in `action-contract.md`; rate a dropped `disallowed_tools` or `experimental_allowed_domains` as a security finding (SE-14).
- A `prompt` on comment events without a job-level `if:` (SE-04).
- Bot-triggered events without `allowed_bots` or a bot filter; `*` in `allowed_bots` or `allowed_non_write_users` (SE-02).
- `allowed_non_write_users` without `github_token` (SE-03).
- `track_progress` on an unsupported event or action (SE-05).
- `use_sticky_comment` with `github_token` or a custom app (SE-06).
- CI tools expected without `actions: read` in the job, or on events that are not pull requests (SE-07).
- `structured_output` consumers without `--json-schema` or without an empty guard (SE-01).
- An inline-comment review without the tool in `--allowedTools` (SE-08); a prompt that asks Claude to post with no posting tool granted (SE-13).
- `mcp__github` granted as a wildcard, or `--disallowedTools` missing the approval and merge tools (`trust-boundaries.md`).
- A permission mode set without the user's request; `bypassPermissions` or `--dangerously-skip-permissions` anywhere.
- `--model` with an ID not resolved live; `show_full_output: true` or `--debug` on a public repository.
- A marketplace passed as a URL instead of a pinned local checkout.
- A PR head passed with `--add-dir` without neutralizing its `.claude/` (`trust-boundaries.md`).
- An OAuth token passed through `anthropic_api_key`.

## Linters

Run `actionlint`, `zizmor` and `shellcheck` only when they are already on `PATH`, and record each one's version. When one is missing, report it as not run, with the reason; never install it. A clean lint is not proof that a workflow behaves as intended.

## Each finding

- File and line.
- What an attacker or a failure needs to trigger it.
- Its impact and severity.
- The exact patch: the replacement lines, with every new `uses:` resolved and pinned as `SKILL.md` says.
- The risk left after the patch.

## Apply the patches

Only after the user approves them. Apply them on a branch, run the linters again under the rule above, and land the change through this plugin's pull request skill. Changing a workflow's permissions, triggers or secrets is a separate approval from the rest of the patch.

## Verify against

- GitHub, secure use of Actions: https://docs.github.com/en/actions/reference/security/secure-use
- GitHub, workflow syntax: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- actionlint: https://github.com/rhysd/actionlint · zizmor: https://docs.zizmor.sh

Written on 4 November 2026 from `anthropics/claude-code-action@c0949c5`.
