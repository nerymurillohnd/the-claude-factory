---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_release-tags-only-commits-on-main
superseded-by: none
---

# Release tags only commits on main, and Validate checks a pull request as main will be

## Scope

`scripts/release/publish-releases.sh` (`npm run release:publish`), `.github/workflows/release.yml`, and Validate's `Consistency` and `Release notes for every plugin` steps in `.github/workflows/validate.yml`, with `scripts/release/release_tools/notes.py` (`npm run release:notes`). Out of scope: how a version gets its date, which ADR_2026-11-15_changelog-date-is-the-day-a-version-is-prepared records.

## Context and problem statement

ADR_2026-11-15_release-tags-only-commits-on-main made two choices. It refused any tag or backfill target that is not an ancestor of `origin/main`. It also added `release:notes --pending`, which Validate passed on pull requests so that the `[Unreleased]` notes could stand for a version not dated yet, with strict notes only on `main`.

The first choice still holds. The second does not: commit 6b4ba49 ("fix(validate): check a pull request as main will be after the merge") removed `--pending`. Its message gives the reason. A version whose notes were still under `[Unreleased]` passed on the pull request, then failed Checks on the push to `main` (PC-05 and the release notes), so its Release job never ran. PC-11 was already gone, so a version is dated when it is prepared, not on merge day, and `--pending` had no use left.

The question: what does Validate check on a pull request, now that the pull request gate and the push to `main` must agree?

## Decision drivers

- A tag and a GitHub Release exist only for code that reached `main`.
- A pull request that passes its checks must pass the same checks on `main` after the merge.
- A pull request's checks still fail only for real defects.

## Considered options

- **Keep refusing targets outside `main`; check a pull request as `main` will be, with no `--pending`**: chosen.
- **Keep `--pending` on pull requests**: rejected, because it let a pull request pass that then failed on `main` and blocked the release.
- **Allow dispatches only on `main`**: rejected, as in ADR_2026-11-15_release-tags-only-commits-on-main, because a backfill sometimes has to run the `release.yml` of the branch that fixes it.

## Decision outcome

Chosen option: **tags only on commits of `main`, and the same strict checks on every Validate event**:
- `publish-releases.sh` fetches `origin/main`. It exits 1 when `TARGET_SHA`, or `BACKFILL_TARGET` in a backfill, is not an ancestor of it.
- The script runs `release-notes` through `uv run --no-project`, so the step that holds the write token installs no project dependencies.
- Validate runs `npm run check:consistency -- --main` on every event, so a pull request must have an empty `[Unreleased]` (PC-05) as `main` will.
- Validate runs `npm run release:notes -- <plugin>` for every plugin in `marketplace.json`, with no flag, on every event. A version needs a dated section with notes.
- `--pending` no longer exists: `release:notes --pending` is a usage error, exit 2.
- The `Release notes for every plugin` loop and the strict plugin validation loop run every plugin and report every failure, not only the first.
- Everything else in ADR_2026-11-15_validate-calls-the-reusable-release-workflow still holds: `workflow_call` and `workflow_dispatch`, the `plugin` and `backfill_target` inputs, the permissions, the timeout and the concurrency group.

### Consequences

- Good, because a mistaken dispatch creates nothing.
- Good, because a pull request that passes Validate also passes it on `main`, and the Release job runs.
- Bad, because a pull request with a version bump stays red until its changelog section is dated, so the version is dated before the push, as the `plugin-releases` skill says.
- Bad, because the concurrency group keeps one release waiting, so a third merge in quick succession cancels the waiting one; the next release then tags that version at a later commit. The `plugin-releases` skill says so.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| :-- | :-- | :-- | :-- |
| A target outside `main` is refused | `npm run test:scripts` (`test_a_target_outside_main_is_refused` in `scripts/testers/release/test_publish_releases.py`) | 2026-11-15: pass | Every change to the script |
| `--pending` is a usage error | `npm run test:scripts` (`test_pending_flag_is_gone` in `scripts/testers/release/test_notes.py`) | 2026-11-15: pass | Every change to `release-notes` |
| A version whose notes are only under `[Unreleased]` builds no body | `npm run test:scripts` (`test_undated_version_builds_no_body` in `scripts/testers/release/test_notes.py`) | 2026-11-15: pass | Every change to `release-notes` |
| The first merge tags every untagged current version | `git ls-remote --tags origin` after the merge | pending | The first merge after this change |

## More information

- Replaces the `--pending` part of ADR_2026-11-15_release-tags-only-commits-on-main, which stays as written and points here through its `superseded-by`. The part that release tags only commits on `main` is kept above.
- Made in commit 6b4ba49 on the branch of pull request 107; this record was written after it, on 2026-11-15. It follows from the owner's removal of PC-11 in ADR_2026-11-15_changelog-date-is-the-day-a-version-is-prepared. Whether the owner approved the `--pending` removal separately is not stated.
- That record's line "Validate runs plain `check:consistency` on a pull request" no longer holds either: Validate passes `--main` on every event, as above.
