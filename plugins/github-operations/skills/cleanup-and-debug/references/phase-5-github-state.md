# Phase 5: GitHub state

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
- Workflows whose last run on the default branch failed, with no success after it.
- Failed jobs that were never rerun or fixed.
- Scheduled workflows that stopped running.
- Runs stuck in queued or in progress.
- Runs waiting for approval.
- Workflows that point to deleted branches, files or secrets: branches in `on:` filters, secret names that `gh secret list` does not show, files under `paths:`.

List disabled workflows too: `gh workflow list --all`. A filtered run list returns at most 1,000 results ([GitHub REST: workflow runs][workflow-runs]), so split the runs of the default branch by creation date (`gh run list --branch <default> --created '<from>..<to>' --limit 1000`) until each window returns fewer than 1,000. In a public repository, GitHub disables scheduled workflows after 60 days with no repository activity ([GitHub: disabling workflows][disable-workflows]).

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
- [GitHub: disabling workflows][disable-workflows]: "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days."

[deploy-keys]: https://docs.github.com/en/rest/deploy-keys/deploy-keys
[workflow-runs]: https://docs.github.com/en/rest/actions/workflow-runs
[disable-workflows]: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows
