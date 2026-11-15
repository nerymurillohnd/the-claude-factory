---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_validate-calls-the-reusable-release-workflow
superseded-by: none
---

# Validate calls the reusable release.yml, which tags only commits on main

## Scope

`.github/workflows/release.yml`, the `Release` job of `.github/workflows/validate.yml`, `scripts/release/publish-releases.sh` (`npm run release:publish`), and the release-notes step of Validate.

## Context and problem statement

ADR_2026-11-15_validate-calls-the-reusable-release-workflow made `release.yml` a reusable workflow, which Validate calls after its checks and which can backfill one version through `workflow_dispatch`. The whole-branch review of 2026-11-15 found three gaps:
- A dispatch on a feature branch would tag that branch's tip, a commit `main` doesn't have.
- The backfill commit was checked against the dispatched branch's history, not `main`'s.
- Validate built every plugin's release notes strictly on pull requests, so every pull request with a version bump stayed red until merge day.

## Decision drivers

- A tag and a GitHub Release exist only for code that reached `main`.
- A pull request's checks fail only for real defects.

## Considered options

- **Refuse any target or backfill commit that isn't an ancestor of `origin/main`; build release notes with `--pending` on pull requests**: chosen.
- **Allow dispatches only on `main`**: rejected, because a backfill sometimes has to run the `release.yml` of the branch that fixes it.

## Decision outcome

Chosen option: **tags only on commits of `main`**:
- `publish-releases.sh` fetches `origin/main`. It exits 1 when `TARGET_SHA`, or `BACKFILL_TARGET` in a backfill, isn't an ancestor of it.
- The script runs `release-notes` through `uv run --no-project`, so the step that holds the write token installs no project dependencies.
- Validate runs `release:notes -- <plugin> --pending` on pull requests, which lets the `[Unreleased]` notes stand for a version not dated yet, and runs it strictly on `main`.
- Everything else in ADR_2026-11-15_validate-calls-the-reusable-release-workflow still holds: `workflow_call` and `workflow_dispatch`, the `plugin` and `backfill_target` inputs, the permissions, the timeout and the concurrency group.

### Consequences

- Good, because a mistaken dispatch creates nothing.
- Good, because a pull request in review shows red only for defects.
- Bad, because the concurrency group keeps one release waiting, so a third merge in quick succession cancels the waiting one; the next release then tags that version at a later commit. The `plugin-releases` skill says so.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| A target outside `main` is refused | `npm run test:scripts` (`test_a_target_outside_main_is_refused`) | 2026-11-15: pass | Every change to the script |
| `--pending` accepts `[Unreleased]` notes and still fails without notes | `npm run test:scripts` (`test_pending_*`) | 2026-11-15: pass | Every change to `release-notes` |
| The first merge tags every untagged current version | `git ls-remote --tags origin` after the merge | pending | The first merge after this change |

## More information

- Found by the whole-branch review of 2026-11-15 and fixed as part of the release pipeline plan the owner approved.
