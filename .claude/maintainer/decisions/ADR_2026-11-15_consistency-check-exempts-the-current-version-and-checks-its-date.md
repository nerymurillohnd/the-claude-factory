---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# check:consistency exempts only the current version from PC-04, runs PC-05 on demand, and checks the release date

## Scope

`scripts/validators/plugin_consistency/` (`checks.py`, `cli.py`), and how Validate calls `npm run check:consistency`.

## Context and problem statement

PC-04 required a tag for every dated changelog version except one that differed from `origin/main`. Right after a merge the branch equals `origin/main`, so the new version had no exemption and the check failed before `release.yml` could tag it: a deadlock for a gate that runs on push. PC-05, which keeps `[Unreleased]` empty on `main`, ran only when the checked-out branch was named `main`, never in CI, which checks out a commit. Nothing caught a release dated on another day than its tag.

## Decision drivers

- The gate on `main` must pass after a correct merge.
- An older version that never got its tag stays a finding.
- A release is dated the UTC day its tag is created.

## Considered options

- **Exempt each plugin's current version; add `--main` for PC-05 and `--date-check` for a new PC-11**: chosen.
- **Run `--offline` in CI and skip PC-04**: rejected, because it would never catch a version that missed its tag.

## Decision outcome

Chosen option: **exempt only the current version**:
- PC-04 exempts the version in the plugin's `plugin.json`, the one `release.yml` tags next.
- `--main` runs PC-05 on a detached commit.
- `--date-check` adds PC-11: an untagged current version must be dated today in UTC. Validate runs it on pull requests.
- The tests are in `scripts/testers/plugin_consistency/test_checks.py`.

### Consequences

- Good, because the push to `main` passes and the merge releases.
- Good, because a pull request whose merge slips past midnight UTC goes red until the date changes.
- Bad, because every pull request that carries an untagged version is red under PC-11 until its release day, by design.

## More information

- Decided on 2026-11-15, when the owner approved the release pipeline plan.
- On 2026-11-15 the only remaining PC-04 finding is `skill-diagnostics` 0.4.0, which waits for its backfill.
