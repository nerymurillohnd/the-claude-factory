---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_consistency-check-exempts-the-current-version-and-checks-its-date
superseded-by: none
---

# A changelog date is the day a version is prepared, and check:consistency no longer compares it with today

## Scope

`check:consistency` (`scripts/validators/plugin_consistency/`), `release:changelog` (`scripts/release/release_tools/changelog.py`), Validate's `Consistency` step and the `plugin-releases` skill.

## Context and problem statement

ADR_2026-11-15_consistency-check-exempts-the-current-version-and-checks-its-date added PC-11 (`--date-check`), which Validate ran on pull requests. PC-11 required each untagged current version to be dated today in UTC, and `release:changelog --redate` moved a dated version to a new day.

On 2026-11-15, Validate #456 on the pull request that adds the pipeline failed at `Consistency`, with nine PC-11 findings: versions dated 2026-11-14, checked on 2026-11-15. A pull request with a version bump would stay red on every day but its merge day. It also had to be re-dated and re-run that same UTC day. Before this pipeline, the marketplace never dealt with dates: a merge to `main` released and tagged the version on its own.

## Decision drivers

- A pull request turns green once its checks pass, whatever day it merges.
- Claude Code never reads a changelog date. The GitHub Release records when a version was published.
- An older version without a tag is still caught.

## Considered options

- **Drop PC-11 and `--redate`, and keep PC-04's current-version exemption and PC-05's `--main`**: chosen by the owner.
- **Re-date the versions on each merge day and keep PC-11**: rejected. It adds a manual step, and a pull request is red on every other day.
- **Report PC-11 without blocking**: rejected. A date that nothing reads doesn't earn a check.

## Decision outcome

Chosen option: **drop PC-11 and `--redate`**:
- `release:changelog` dates a version the day it is run, before the merge, and nothing changes that date afterwards.
- PC-04 still exempts each plugin's current version, which `release.yml` tags next, and reports any older version that has no tag.
- `--main` still runs PC-05 on a detached commit, and Validate passes it on a push to `main`.
- Validate runs plain `check:consistency` on a pull request.
- Tests: `test_date_check_flag_is_gone` in `scripts/testers/plugin_consistency/test_checks.py`, and `test_redate_flag_is_gone` in `scripts/testers/release/test_changelog.py`.

### Consequences

- Good, because a pull request's date no longer turns it red, and a merge needs no step on its day.
- Bad, because a changelog date can be earlier than the tag's day. The GitHub Release shows the publication day.
- Neutral, because the `--date-check` bullet of ADR_2026-11-15_validate-gates-merges-on-passing-checks-and-reports-debt no longer holds; this record replaces it.

## More information

- Decided by the owner on 2026-11-15: "Recomiendo eliminar PC-11, no cambiar las nueve fechas… Mantendría PC-04."
- On 2026-11-15 the only remaining PC-04 finding is `skill-diagnostics` 0.4.0, which waits for its backfill at `ced195b`.
