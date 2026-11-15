---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Validate calls release.yml as a reusable workflow, which can also backfill one version

## Scope

`.github/workflows/release.yml`, the `Release` job of `.github/workflows/validate.yml`, and `scripts/release/publish-releases.sh` (`npm run release:publish`).

## Context and problem statement

`release.yml` ran on `workflow_run` of a workflow named `Validate`, which no longer existed, so merges tagged nothing. `skill-diagnostics` 0.4.0 can't be tagged by the usual loop, because the loop tags only the current version (0.4.1). Cloud sessions can't create tags or Releases. How should a merge release, and how does a skipped version get its tag?

## Decision drivers

- A merge releases on its own, only after the checks pass.
- No `workflow_run` trigger. GitHub and zizmor treat it as dangerous, and it needed two zizmor exceptions.
- A missing version can be released from a cloud session, without a local machine.

## Considered options

- **`workflow_call` from Validate's `Release` job, plus `workflow_dispatch` with `plugin` and `backfill_target` inputs**: chosen.
- **Keep `workflow_run` on the new Validate**: rejected because of the trigger's risk and its zizmor exceptions.
- **Tag missing versions by hand with `claude plugin tag --push`**: rejected because cloud sessions can't push tags and the owner's machine was not available.

## Decision outcome

Chosen option: **a reusable `release.yml`**, because one Validate run gates and releases each merge, and a dispatch covers retries and backfills.

- **The workflow:**
  - Workflow-level permissions are empty; the job gets `contents: write` only.
  - `actions/checkout` runs with `persist-credentials: false`.
  - It times out at 15 minutes and keeps `concurrency: release` without cancelling.
- **The loop lives in `publish-releases.sh`**, tested with a stub `gh` in `scripts/testers/release/test_publish_releases.py`:
  - it releases each plugin whose current version has no tag on `origin`, checked with `git ls-remote --exit-code`;
  - `PLUGIN` limits the run to one plugin, and exits 2 if the marketplace doesn't list it;
  - `BACKFILL_TARGET` tags the version that was current at that commit, with its notes from today's changelog, through `release-notes --version`. It exits 1 if the commit isn't in the branch's history.
- **`zizmor.yml`** drops its `artipacked` and `dangerous-triggers` exceptions for `release.yml`.

### Consequences

- Good, because a merge releases minutes after `Checks` passes, so the merge-day date holds.
- Good, because a backfill runs in CI, where tags can be created.
- Bad, because `workflow_dispatch` on a branch needs a workflow that has already run once; GitHub's "Events that trigger workflows" says so.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The loop releases only untagged versions, and refuses a bad plugin or commit | `npm run test:scripts` (7 cases) | 2026-11-15: pass | Every change to the script |
| The first merge tags every untagged current version | `git ls-remote --tags origin` after the merge | pending | The first merge after this change |

## More information

- Decided on 2026-11-15, when the owner approved the release pipeline plan (`.claude/maintainer/plans/2026-11-15-release-pipeline.md`).
- Related: ADR_2026-11-13_release-workflow-runs-python-through-uv, ADR_2026-11-15_validate-gates-merges-on-passing-checks-and-reports-debt.
