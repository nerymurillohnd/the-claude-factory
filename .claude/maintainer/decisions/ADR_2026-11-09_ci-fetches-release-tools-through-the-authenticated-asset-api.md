---
status: accepted
date: 2026-11-09
decision-makers:
  - "Nery Murillo"
supersedes: none
superseded-by: none
---

# CI fetches shfmt and actionlint through the authenticated release-asset API

## Scope

`.github/workflows/validate.yml`: the "shellcheck and shfmt" step of the policy job and the "actionlint" step of the lint job. Out of scope: `actions/setup-node`'s own Node download, the `downloads.claude.ai` key fetch and the `gh api …/releases/latest` lookups.

## Context and problem statement

Both steps took the latest GitHub release asset's `browser_download_url` and fetched it anonymously with `curl`. During GitHub's incident [c9px7cw2ghrs](https://www.githubstatus.com/incidents/c9px7cw2ghrs), "Increased timeouts due to surge in anonymous users" (from 2026-11-09 05:59 UTC), anonymous release downloads returned 504. GitHub's 08:16 UTC update says "Logged-in users and authenticated requests are unaffected."

- **What failed:** Validate failed on PR #97 and twice on `main`.
- **First fix:** `curl --retry 6`, added in PR [#98](https://github.com/nerymurillohnd/the-claude-factory/pull/98). It then failed all 7 attempts over about 66 s (run 42583217353).
- **Release impact:** `release.yml` was skipped three times and `plugin-engineering--v0.2.1` stayed untagged.

How should CI install these tools so that a GitHub incident on anonymous downloads does not block releases?

## Decision drivers

- Keep integrity verification: `sha256sum --check --strict` against the digest GitHub records. shfmt publishes no other checksum (mvdan/sh#901).
- Smallest change: no new action, permission, trigger or secret.
- Keep installing the latest release, which matches the maintainer's local versions (shfmt v3.14.1, actionlint 1.7.12).
- Do not depend on the failing path.

## Considered options

- **REST asset endpoint with the job token**: chosen. `.url` replaces `browser_download_url`, and the asset is fetched with `Accept: application/octet-stream` and `Authorization: Bearer ${GH_TOKEN}`, the endpoint `gh release download` uses. `--retry 6` and the digest check are unchanged.
- **Retries only (`curl --retry 6`)**: rejected because it failed during a sustained outage.
- **`actions/setup-go` plus `go install …@latest`**: rejected as the main path. It is shfmt's documented install and is verified by sum.golang.org, but it adds an action. On a tool-cache miss, `setup-go` downloads Go from GitHub releases, which is the same failing path. It also compiles on every run. It stays the fallback.
- **Docker image `mvdan/shfmt`**: rejected because it adds Docker Hub, with its anonymous pull limits, and needs the binary copied out of the container.
- **Ubuntu apt `shfmt`**: rejected because noble ships 3.8.0, behind the local v3.14.1.
- **Third-party shfmt actions** (reviewdog/action-shfmt, luizm/action-sh-checker, mfinelli/setup-shfmt, webinstall.dev): rejected because they download the same GitHub release assets, and webinstall pipes a script into bash without a checksum.

## Decision outcome

Chosen option: **REST asset endpoint with the job token**. It sends only authenticated requests, which GitHub states are unaffected. It keeps the digest check, and it adds no dependency or permission. curl sends the `Authorization` header only to api.github.com, not to the storage host it redirects to (curl 7.58.0 and later; the runner has 8.5.0).

### Consequences

- Good, because a GitHub incident on anonymous downloads no longer fails Validate or skips `release.yml`.
- Good, because nothing new enters the workflow's supply chain.
- Bad, because the asset still comes from GitHub's storage host behind the redirect.
- Bad, because the log does not print the asset URL, so the endpoint used is shown only indirectly, by the digest match.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Both downloads use the authenticated endpoint and pass the digest check | Validate logs: echoed curl with `Accept` and `Authorization: ***`, then `<file>: OK` | PR #99 run 42586305102 and `main` run 42586860807 passed, during the open incident | When either download fails again |
| Releases are no longer blocked | `release.yml` after Validate on `main` | Run 42586957169 created `plugin-engineering--v0.2.1` | Each release |

## More information

Shipped in PR [#99](https://github.com/nerymurillohnd/the-claude-factory/pull/99), merge commit 633fae7. PR #98 (merge commit c4bf0e9) added the retries that remain in place. Nery approved this option after comparing it with `go install`, Docker and third-party actions, and after a parallel research session reached the same recommendation.
