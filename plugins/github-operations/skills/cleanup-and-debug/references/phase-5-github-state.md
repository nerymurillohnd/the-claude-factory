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
- Workflows that point to deleted branches, files or secrets.

## Storage

- Artifacts and caches, with their size and age.

## Environments, secrets and runners

- Environments and their protection rules.
- Secrets and variables, by name only.
- Self-hosted runners that are offline or unused.

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

[deploy-keys]: https://docs.github.com/en/rest/deploy-keys/deploy-keys
