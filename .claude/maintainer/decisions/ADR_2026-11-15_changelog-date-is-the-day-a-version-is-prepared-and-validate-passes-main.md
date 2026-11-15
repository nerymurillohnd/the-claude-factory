---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_changelog-date-is-the-day-a-version-is-prepared
superseded-by: none
---

# A changelog date is the day a version is prepared, and Validate checks consistency as main will be

## Scope

`check:consistency` (`scripts/validators/plugin_consistency/`), `release:changelog` (`scripts/release/release_tools/changelog.py`), Validate's `Consistency` step (`.github/workflows/validate.yml`) and the `plugin-releases` skill.

## Context and problem statement

ADR_2026-11-15_consistency-check-exempts-the-current-version-and-checks-its-date added PC-11 (`--date-check`), which Validate ran on pull requests. PC-11 required each untagged current version to be dated today in UTC, and `release:changelog --redate` moved a dated version to a new day.

On 2026-11-15, Validate #456 on the pull request that adds the pipeline failed at `Consistency`, with nine PC-11 findings: versions dated 2026-11-14, checked on 2026-11-15. A pull request with a version bump would stay red on every day but its merge day. It also had to be re-dated and re-run that same UTC day. Before this pipeline, the marketplace never dealt with dates: a merge to `main` released and tagged the version on its own.

ADR_2026-11-15_changelog-date-is-the-day-a-version-is-prepared recorded the removal of PC-11 and `--redate`. Two of its lines about Validate did not survive commit 6b4ba49 ("fix(validate): check a pull request as main will be after the merge"): it said `--main` ran on a push to `main` only, and that Validate ran plain `check:consistency` on a pull request. Since 6b4ba49, `.github/workflows/validate.yml` line 81 runs `npm run check:consistency -- --main` on every event. This record restates the decision with those lines corrected.

## Decision drivers

- A pull request turns green once its checks pass, whatever day it merges.
- Claude Code never reads a changelog date. The GitHub Release records when a version was published.
- An older version without a tag is still caught.
- A pull request that passes Validate must pass it on `main` after the merge.

## Considered options

- **Drop PC-11 and `--redate`, and keep PC-04's current-version exemption and PC-05's `--main`**: chosen by the owner.
- **Re-date the versions on each merge day and keep PC-11**: rejected. It adds a manual step, and a pull request is red on every other day.
- **Report PC-11 without blocking**: rejected. A date that nothing reads doesn't earn a check.

## Decision outcome

Chosen option: **drop PC-11 and `--redate`**:
- `release:changelog` dates a version the day it is run, before the merge, and nothing changes that date afterwards.
- PC-04 still exempts each plugin's current version, which `release.yml` tags next, and reports any older version that has no tag.
- `--main` runs PC-05 on a detached commit, and Validate passes it on every event: `.github/workflows/validate.yml` line 81 runs `npm run check:consistency -- --main`, so a pull request must have an empty `[Unreleased]` as `main` will.
- Validate no longer runs plain `check:consistency` on a pull request. It stopped in commit 6b4ba49.
- Tests: `test_date_check_flag_is_gone` in `scripts/testers/plugin_consistency/test_checks.py`, and `test_redate_flag_is_gone` in `scripts/testers/release/test_changelog.py`.

### Consequences

- Good, because a pull request's date no longer turns it red, and a merge needs no step on its day.
- Bad, because a changelog date can be earlier than the tag's day. The GitHub Release shows the publication day.
- Neutral, because the `--date-check` bullet of ADR_2026-11-15_validate-gates-merges-on-passing-checks-and-reports-debt no longer holds; this record replaces it.

## More information

- Replaces ADR_2026-11-15_changelog-date-is-the-day-a-version-is-prepared, which stays as written and points here through its `superseded-by`. That record had itself replaced ADR_2026-11-15_consistency-check-exempts-the-current-version-and-checks-its-date, which keeps pointing to it; the chain reads: that record, then the changelog-date record, then this one.
- The core decision was made by the owner on 2026-11-15: "Recomiendo eliminar PC-11, no cambiar las nueve fechas… Mantendría PC-04." The owner then decided to supersede the record, after a review of pull request 107 found its two Validate lines out of date.
- The change that made Validate pass `--main` on every event is commit 6b4ba49. ADR_2026-11-15_validate-checks-a-pull-request-as-main-will-be records it.
- On 2026-11-15, `npm run check:consistency` exits 0. The `skill-diagnostics` 0.4.0 PC-04 finding that the replaced record named is closed: tag `skill-diagnostics--v0.4.0` exists on `origin` at `ced195b`.
