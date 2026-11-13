# Audit a workflow that runs Claude in auto mode

In auto mode Claude Code runs a tool call no rule covers when its safety review passes it. In a workflow nobody can answer a prompt, so auto mode decides most of what the agent does. It is a review, not a boundary: what limits an injected or mistaken agent is what the job lets it reach. Since claude-code-action v1.0.273 auto is the default, so most workflows that run Claude are in scope here, whether or not they ask for it.

**Contents**
- [1. Is auto mode the effective mode?](#1-is-auto-mode-the-effective-mode)
- [2. Who can start the run?](#2-who-can-start-the-run)
- [3. Check each layer](#3-check-each-layer)
- [4. Rate and report](#4-rate-and-report)
- [What auto mode can't be relied on for](#what-auto-mode-cant-be-relied-on-for)

## 1. Is auto mode the effective mode?

1. Take the commit the step runs from [the drift check](version-drift.md#find-the-commit-a-step-runs).
2. Read the step's inputs, its `env:`, its `claude_args` and its `settings` input, and find its row in the effective-mode table in [Permission mode](action-contract.md#permission-mode). A `--permission-mode` in `claude_args`, in the space form, decides it.
3. Decide:
   - **auto:** run this reference.
   - **A floating ref that can't be resolved** (`v1`, `main`, with no way to read upstream): count it as auto and say why.
   - **Not an upstream commit** (a fork, or a SHA upstream doesn't have): the mode can't be derived. Record it as unknown, add one Questions row for it, and don't run this reference for that step.
   - **acceptEdits or Manual:** this reference doesn't apply, unless a patch would turn auto on; then [Validate the patches](workflow-audit.md#validate-the-patches) runs it on the patched file.
4. Record the effective mode and the row that decided it. It is the "mode before" of every finding on the step.

A `defaultMode` in the repository's own `.claude/settings.json` doesn't change what the action decides.

## 2. Who can start the run?

The severity of every missing layer depends on who can reach the agent. Classify the workflow before checking the layers:

- **Open to outsiders** when any GitHub user can start it or put text in front of Claude: triggers `issues`, `issue_comment`, `discussion`, `discussion_comment`, `pull_request_review`, `pull_request_review_comment` or `pull_request_target`; any `allowed_non_write_users`; `allowed_bots: "*"`; a public repository where the job reads issue, comment or pull request text; or a `workflow_run` whose prompt reads a pull request run's artifacts or logs.
- **Collaborators only** when only people with write access can start it and no outside text reaches the prompt, as with tag mode's actor check on a private repository, or `workflow_dispatch` and `schedule` with no outside text in the prompt.

When you can't tell, treat the workflow as open to outsiders and say why.

## 3. Check each layer

Check every layer, and record for each one the line that proves it, or "missing". The patch for a missing layer comes from the "What proves it" column; its costs are in [Costs of each change](auth-and-permissions.md#costs-of-each-change), and every patch freezes the mode ([Permission mode in patches](auth-and-permissions.md#permission-mode-in-patches)).

| Layer | What proves it in the workflow | When it is missing |
| :-- | :-- | :-- |
| A. Token and permissions | `github_token: ${{ github.token }}` on the step, so the agent's token has only the job's permissions and expires with the job; workflow-level `permissions: {}`; job write scopes only where a tool uses them; `id-token: write` only for an OIDC profile | The step has no `github_token`, so it runs on the Claude App token, whose `contents`, `pull_requests` and `issues` write the job's `permissions:` don't limit ([GitHub token and the Claude App token](action-contract.md#github-token-and-the-claude-app-token)); or the job has write scopes nothing uses |
| B. Tools really limited | Deny rules for what the job mustn't do: `WebFetch`, `WebSearch` and `Monitor`, which reach the network; `Edit`, `Write` and `NotebookEdit` when the job mustn't change files; the approval, merge and branch-write class from [trust-boundaries.md](trust-boundaries.md#approval-merge-and-branch-write-tools). On pull requests from outside authors, the untrusted-PR deny list in force ([Untrusted pull requests](action-contract.md#untrusted-pull-requests)) | Only `--allowedTools` is set: under auto it pre-approves, it doesn't limit. Or `restrict_untrusted_prs: false` on a workflow outside authors reach (C-17). Raw `gh` with the job's token stays reachable unless the token's scope stops it |
| C. Script caps | The script-caps variable named in [Environment variables the action passes](action-contract.md#environment-variables-the-action-passes), as JSON giving every script that writes a call limit, **and** the subprocess scrub on (`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB: '1'`, or a non-empty `allowed_non_write_users`) | Missing when the agent can write through anything other than a capped script, when the JSON doesn't parse, or when a cap names a script that doesn't exist (W-10). Caps without the scrub do nothing. Caps are documented only by the action, so count them as defense in depth |
| D. Network out of the runner | Evidence that the runner reaches only the hosts the job needs: a runner group whose network configuration restricts egress, a self-hosted runner behind a firewall, or a first step of `step-security/harden-runner` with `egress-policy: block` | A `runs-on` label alone proves nothing, whatever its name. Ask the user how the runner's network is restricted; until they confirm, it is a Questions row. A self-hosted runner on a public repository is a finding by itself |
| E. Time and repetition | `timeout-minutes` on the job (the default is 360 minutes); a `concurrency` group with `cancel-in-progress: true` for runs a new event supersedes | No timeout, or no concurrency group on a workflow that comments or labels. This is W-08's finding: report it once, as W-08 |
| F. Configuration Claude reads | Nothing of the pull request's head that Claude can load: no tag-mode run on pull request events (`pull_request`, `pull_request_target`, the review events, or `issue_comment`, which also fires on pull request comments), no head checkout in the workspace, and no `--add-dir` on a head copy that keeps its `.claude/` ([trust-boundaries.md](trust-boundaries.md#configuration-claude-reads)) | Tag mode on a pull request event checks out the head itself, and nested `CLAUDE.md`, `.claude/rules/` and `.claude/skills/` load from it; or the job checks out the head; or `--add-dir` loads it. Its `CLAUDE.md` reaches the safety review, which reads it. Patch, as its own approval: keep the tag-mode step off pull request events (for `issue_comment`, a job-level `if: ${{ !github.event.issue.pull_request }}`), or use the base-branch design |
| G. A model that supports auto | The model the step really runs supports auto ([Claude Code version, models and auto availability](action-contract.md#claude-code-version-models-and-auto-availability)). With no `--model`, it is Claude Code's default for the profile | An unsupported model: tag runs fall back to acceptEdits with a warning, agent runs stay in Manual and deny what no rule covers. A functional finding, not a security one |

**Costs to state with each patch:**
- A: adding `github_token` has the costs in its row of [Costs of each change](auth-and-permissions.md#costs-of-each-change), and is never added while `allowed_non_write_users` holds `*`.
- B: a `--tools` list without `Edit` and `Write` removes code editing from tag runs. Keep them in tag workflows that change code, and use a tight `--tools` list only on agent workflows that mustn't change files. When you can't tell what the workflow is for, ask: it is a Questions row.
- C: the scrub removes `NPM_TOKEN`, `DATABASE_URL` and similar variables from Claude's subprocesses, never the GitHub token, and it needs a pin at v1.0.274 or later.

## 4. Rate and report

This table applies [the severity scale](workflow-audit.md#severity-scale) to auto mode's layers. Rate each missing layer with it:

| Missing layer | Open to outsiders | Collaborators only |
| :-- | :-- | :-- |
| A, B or F | high | medium |
| C or D | medium | low |
| E (reported as W-08) | medium | low |
| G | low | low |

- A layer you can't decide is a Questions row, not a finding ([When a check can't be decided](workflow-audit.md#when-a-check-cant-be-decided)).
- For each missing layer, write its patch adapted to the workflow, with its costs. A narrower tool list can break a prompt that relied on a tool: read the prompt and keep the tools it uses.
- Every workflow in auto mode also gets this residual risk in its report, whatever its layers: auto mode is a review, not a boundary; and on a runner without managed settings, a Claude Code mod that handles `tool.check` can approve a call that a deny rule refuses.

## What auto mode can't be relied on for

- It blocks nothing it can't see: tool results are stripped from what the safety review reads, and a run with no one to ask keeps working after a call is refused.
- It doesn't replace any layer above. It lowers how often a mistake becomes an action; the layers decide what a mistake can reach.

## Verify against

- Claude Code, permission modes and auto mode: https://code.claude.com/docs/en/permission-modes
- Claude Code, permissions, rule precedence and mods: https://code.claude.com/docs/en/permissions
- Claude Code, environment variables: https://code.claude.com/docs/en/env-vars
- Claude Code, CLI reference (`--tools`, `--disallowedTools`): https://code.claude.com/docs/en/cli-reference
- GitHub, private networking for GitHub-hosted runners: https://docs.github.com/en/actions/concepts/runners/private-networking
