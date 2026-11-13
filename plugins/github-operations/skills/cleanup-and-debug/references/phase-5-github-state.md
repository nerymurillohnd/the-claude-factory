# Phase 5: GitHub state

## Contents

- Pull requests
- Issues and discussions
- Branches on GitHub
- Actions
- Actions settings
- Storage
- Environments, secrets and runners
- Dependabot
- Other security alerts
- Integrations and access
- Distribution
- Forks
- Done when
- Sources

Audit the repository on GitHub. This phase is read-only: every list is paginated and aware of rate limits, and every call the identity cannot make goes to the coverage ledger.

## Pull requests

Inventory pull requests in every state (open, draft, closed and merged), each with its head and base SHAs, age, author, review state and checks. Flag:

- Open or draft pull requests that were abandoned.
- Pull requests closed without merging whose branch still exists.
- Merged pull requests whose branch still exists.
- Pull requests from forks.

## Issues and discussions

- Open for a long time.
- Waiting for an answer.
- Stale.
- With no labels.

## Branches on GitHub

- Stale branches.
- Branches whose pull request was merged or closed.
- Branch protections and rulesets, with their bypass lists.

## Actions

- Every workflow, enabled or disabled, with its latest result.
- Workflows whose last run on the default branch failed, with no success after it. A green run that did nothing is not a success and does not close an earlier failure: a Claude step that logged "No trigger found", or "Skipping action due to workflow validation: …" and "Exiting due to workflow validation skip".
- Failed jobs that were never rerun or fixed.
- Scheduled workflows that stopped running.
- Runs stuck in queued or in progress.
- Runs waiting for approval.
- Workflows that point to deleted branches, files or secrets: branches in `on:` filters, files under `paths:`, and secret names found at no level the job reads them from (`gh secret list`, `--env <environment>`, `--org <org>` when readable, `--app dependabot` for Dependabot runs). A level that can't be read leaves the name unverified, not missing.

List disabled workflows too: `gh workflow list --all`. A filtered run list returns at most 1,000 results ([GitHub REST: workflow runs][workflow-runs]), so split the runs of the default branch by creation date (`gh run list --branch <default> --created '<from>..<to>' --limit 1000`) until each window returns fewer than 1,000. In a public repository, GitHub disables scheduled workflows after 60 days with no repository activity ([GitHub: disabling workflows][disable-workflows]).

## Actions settings

- Allowed actions and whether Actions is enabled: `gh api repos/<owner>/<repo>/actions/permissions` (`allowed_actions`).
- The default `GITHUB_TOKEN` permissions and whether workflows can approve pull requests: `.../actions/permissions/workflow` (`default_workflow_permissions`, `can_approve_pull_request_reviews`).
- The approval policy for workflows from fork pull requests: `.../actions/permissions/fork-pr-contributor-approval` (`approval_policy`).
- On a private repository, whether fork pull requests run workflows and receive write tokens or secrets: `.../actions/permissions/fork-pr-workflows-private-repos` (`run_workflows_from_fork_pull_requests`, `send_write_tokens_to_workflows`). Write tokens sent to fork pull requests are a security finding, report-only.

Security findings inside workflow files (injection, permissions, unpinned actions, `pull_request_target`, claude-code-action configuration) are not part of this inventory: they go to `github-operations:claude-github-actions`.

## Storage

- Artifacts and caches, with their size and age.

## Environments, secrets and runners

- Environments and their protection rules.
- Secrets and variables, by name only.
- Self-hosted runners that are offline or unused, with their labels.

## Dependabot

- Open alerts.
- Update pull requests that are open, failed or ignored.
- Update jobs that failed, for version and security updates, with their error.
- Its configuration.

## Other security alerts

- Secret scanning alerts.
- Code scanning alerts.

## Integrations and access

- Webhooks, with their failed deliveries.
- Deploy keys, with their last use from the `last_used` field ([GitHub REST: deploy keys][deploy-keys]).
- Installed GitHub Apps.
- Collaborators, pending invitations and teams.

## Distribution

- Releases and their assets.
- Packages.
- Pages, Codespaces and the wiki.

## Forks

- The whole fork network.
- Each fork ahead of or behind this repository's default branch, by commit count.
- Forks holding work that was never sent back.

## Done when

- [ ] Pull requests in every state are listed with their SHAs, read from every page.
- [ ] Every section above was read from every page, or is in the coverage ledger with the call that failed.
- [ ] Secrets and variables appear by name only.
- [ ] Every fork has its ahead and behind counts, or is in the coverage ledger.

## Sources

Checked on 2026-11-04.

- [GitHub REST: deploy keys][deploy-keys]: the response includes "last_used: string or null, format: date-time".
- [GitHub REST: workflow runs][workflow-runs]: "This endpoint will return up to 1,000 results for each search when using the following parameters: actor, branch, check_suite_id, created, event, head_sha, status."
- [GitHub REST: Actions permissions][actions-permissions]: the repository endpoints `actions/permissions`, `actions/permissions/workflow`, `actions/permissions/fork-pr-contributor-approval` and `actions/permissions/fork-pr-workflows-private-repos`, with the fields named above.
- [GitHub: disabling workflows][disable-workflows]: "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days."

[deploy-keys]: https://docs.github.com/en/rest/deploy-keys/deploy-keys
[actions-permissions]: https://docs.github.com/en/rest/actions/permissions
[workflow-runs]: https://docs.github.com/en/rest/actions/workflow-runs
[disable-workflows]: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows
