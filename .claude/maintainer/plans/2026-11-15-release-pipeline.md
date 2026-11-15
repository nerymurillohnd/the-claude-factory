# Plugin Release Pipeline: corrected guide and implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (owner chose this session as implementer) to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One working, repeatable pipeline from "a plugin changed" to "users can update", run by one consolidated skill, with a real CI gate, so releases resume and the 11 untagged versions get their tags.

**Architecture:** `validate.yml` (new) runs the checks on every pull request and push to `main`; on a push to `main` its last job calls `release.yml` (turned into a reusable workflow) to tag and publish every untagged current version. One maintainer skill, `plugin-releases`, absorbs `plugin-versioning` and carries the whole procedure; this guide is its source and does not survive as a separate document.

**Tech Stack:** GitHub Actions (SHA-pinned), Node 26 / npm 12, uv + Python 3.15 maintainer scripts (`scripts/`), Claude Code CLI 2.1.325 (`claude plugin validate|test|tag`).

**Spec:** this file. Sources read on branch `origin/ccr-7fcd6ef3-rku7l1` (005f47d) on 2026-11-15: `.claude/rules/**`, `.claude/skills/{plugin-versioning,plugin-releases,plugin-catalog-changes,docs-maintenance}`, `plugins/github-operations/skills/{claude-github-actions,github-files-setup}`, `scripts/release_tools/*`, `scripts/validators/plugin_consistency/*`, `.github/**`, ADRs, DEBT, handoff 2026-11-14-0750, git history back to c441921 (2026-10-12) through the GitHub API.

## Context

- The release guide the owner pasted (14 November 2026) explains well how Claude Code detects an update, but its pipeline is wrong for this repository: it says CI runs `Validate` on the pull request and on `main`, and cites `.claude/rules/plugins.md › Version bumps`. Neither exists.
- `validate.yml` was deleted in `ced195b` (13 November 2026, owner's decision, because it still ran the removed `gates.mjs`). Since then `release.yml` waits for a workflow that doesn't exist. No tag has been created since 10 November 2026, and the one manual run on 13 November failed at setup-node. That failure is fixed on B only, in `5737d7c`.
- The owner decided that this guide becomes the base of one definitive skill. The skill structure is my call: **consolidate `plugin-versioning` into `plugin-releases`** (reason under Decisions).
- Correction to a premise: the installed `github-operations` skills are **not** outdated. `claude-github-actions` and `github-files-setup` are byte-identical on `main`, on B and in the installed copy (checked file by file). They are still cited by their repository path. Neither has a workflow template. `claude-github-actions` says "Writing a new workflow from scratch: not covered yet", so its audit checks W-01 to W-13 are used as the design standard.

## Part 1 — The corrected guide (becomes the skill)

### How Claude Code delivers an update (kept from the pasted guide; verified)

- The installed copy changes only when the resolved version changes. The resolution order is:
  1. `version` in `plugin.json`;
  2. `version` in the marketplace entry;
  3. otherwise, the commit SHA.
- This repository keeps `version` only in `plugin.json` (`.claude/rules/plugins.md:31`). No marketplace entry has `version` (0 found).
- Tags (`<plugin>--v<version>`) matter to Claude Code only for dependency ranges. No plugin declares dependencies, so the repository's records and checks are what depend on them. GitHub Releases are notes for people; Claude Code never reads them.
- Auto-update is off by default for this marketplace. All 22 READMEs say how to turn it on.
- An unbumped merge changes what new installs receive under the old version number. So every change to a component needs a bump.

### What each artifact is (corrected)

- `plugin.json` `version`: the release switch.
- `CHANGELOG.md` `## [x.y.z] - YYYY-MM-DD`: exactly the set of tags (`docs-maintenance` `changelog.md:60`). `[Unreleased]` must be empty on `main`.
- Tag plus GitHub Release: created only by `release.yml`, unsigned and lightweight (164 existing). Never moved, deleted or reused.
- Root `CHANGELOG.md` line and catalog row: written in the same change as the version.
- `engines["claude-code"]`: set when a release depends on a newer Claude Code feature. A higher floor is a Minor bump.

### Version levels (from `plugin-versioning` step 1–2; unchanged rules, new home)

- **New plugin:** `0.1.0`.
- **No bump:** only README, CHANGELOG, LICENSE, NOTICE, `tests/`, `*.test.ts(x)` or `evals/` changed, or only `marketplace.json`.
- **Major:** a removed or renamed component, changed config keys, a new mandatory dependency, or changed behavior users rely on. In `0.x` a breaking change bumps **Minor**, and `1.0.0` needs the owner.
- **Minor:** a new backward-compatible component, option or capability, or a higher `engines` floor.
- **Patch:** a fix, wording, performance, a same-behavior refactor, or a metadata-only change (category, URLs, icon). The last case is new: it matches the patch bumps already used for the category moves, and closes the gap in `categories.md:15`.
- **Rename:** breaking. The next version is computed from the **old** name, because `release:status --next <new>` prints `0.1.0`.
- **One version per release.** Never bump a plugin again while its previous version is untagged, because `release.yml` tags only the current version (DEBT-005:150).

### The pipeline, end to end (corrected)

1. **Branch.** Work on the current work branch, never on a new branch cut from a stale `main`.
2. **Version** (skill phase A, on the branch, when the change is made):
   - choose the level;
   - write the notes under `[Unreleased]`;
   - `npm run release:status -- --next <plugin> --level <level>` gives the version, which goes into `plugin.json`;
   - **update the catalog version cell in the same change** (fixes the PC-08 contradiction);
   - checks.
3. **Pre-merge** (skill phase B, on merge day):
   - run `npm run release:changelog -- <plugin>` for every plugin whose version is untagged; it dates the version in UTC today and writes the links;
   - write the root `CHANGELOG.md` line;
   - if the merge slips to a later UTC day, re-date before merging;
   - checks, including `release:notes` for every plugin.
4. **Pull request.** `validate.yml` runs on it, and its checks must be green. Push, opening the PR and changing its title need the owner's authorization.
5. **Merge** to `main`, with the owner's authorization, green checks and resolved reviews.
6. **Release, automatic.** The push to `main` runs `validate.yml`; when its checks pass, its `release` job calls `release.yml`. That workflow tags and publishes each plugin whose current version has no tag, at the merged SHA. Nothing else is released.
7. **Verify** (skill phase C):
   - `git ls-remote --tags`;
   - each new tag is an ancestor of `main`;
   - `get_release_by_tag`;
   - `npm run check:install -- --from main <plugin>`;
   - `release:status` reports no untagged version.
8. **Failure.** If the release job fails, report it to the owner at once. The fix is a new commit on `main` (re-run with the owner's authorization), never a moved tag.
9. **Backfill.** A version that never got its tag is released with a `workflow_dispatch` of `release.yml` that passes `ref` (the commit where that version was current) and `plugin`. It needs the owner's authorization, and it runs from a cloud session with no local machine.
10. **Withdraw** (`[YANKED]`) and **what users run**: unchanged from today's `plugin-releases`.

### CI gate (owner decision: gate what passes)

- **Blocking job `checks`:** every check that passes on B today, measured in Task 1. It also runs `release:notes` for every plugin, and PC-04 under the new pending rule.
- **Non-blocking job `debt`:** the checks that the logged debt holds back, each step named with its DEBT id: DEBT-003 (`validate:portable`, `validate:hooks-catch`, and `validate --strict` on model-trace, tool-ledger and turn-meter), DEBT-005 (`lint:frontmatter`), DEBT-006 (`lint:js`). Its failures show in the run and never block. A check moves into `checks` when its DEBT item closes.

## Decisions

- **One skill, `plugin-releases`; `plugin-versioning` is deleted.** The split caused the PC-08 contradiction: one skill had to pass a check that only the other could satisfy. The two skills already cross-reference each other at every step. Together they are about 170 lines, well under 500. The phases (version, pre-merge, release, verify, backfill, withdraw) go in the body; long reference material goes in `references/`.
- **`plugin-catalog-changes` stays separate.** Renames and removals are a different job. It points at the consolidated skill for the bump.
- **`release.yml` becomes `workflow_call` plus `workflow_dispatch`** (inputs `ref`, `plugin`). This drops `workflow_run` (W-02 risk), drops both zizmor exceptions in `.github/zizmor.yml`, and makes backfill possible.
- **New PC-04 pending rule:** the heading of the **current** `plugin.json` version may lack a tag. Every older heading must have one. Today `pending` is computed against `origin/main` (`checks.py:80`), so the check fails on every push to `main` before `release.yml` can tag the version: a deadlock.
- **PC-05 also runs when CI asks for it** (`--main`), because CI checks out a detached SHA and PC-05 never runs there today.

## Global Constraints

- Work only on `ccr-7fcd6ef3-rku7l1`, tracking `origin/ccr-7fcd6ef3-rku7l1`. No new branch, nothing cut from `main`.
- Before each, the owner's explicit authorization: push, the PR title or body, any `workflow_dispatch` or re-run, the merge.
- Cloud sessions never create tags or Releases by hand. Only `release.yml` does.
- Never weaken, skip or silence a check to get green. Exclusions live only in the `debt` job, each with its DEBT id.
- Every `uses:` is pinned to a 40-character SHA with `# vX.Y.Z`, via the `version-drift.md` pipeline. `permissions: {}` at workflow level, with minimal scopes per job. `persist-credentials: false`. `timeout-minutes` on every job. Concurrency never cancels a run on `main` (lesson from b1a559e).
- New maintainer script behavior is written test-first in `scripts/testers/` (`.claude/rules/architecture/scripts.md:13-14`). Each new script gets its npm script.
- Dates are written in UTC, `YYYY-MM-DD`. Commits are grouped by topic and end with the session attribution.
- Every deliverable is in English. Every "done" shows raw output.

## Review Focus

1. **A push to `main` with no bump:** the `release` job runs, finds every tag already present, exits 0, and creates nothing. Test in Task 4 (dry-run script mode).
2. **Two plugins bumped in one merge, and the second has no notes:** caught before the merge by the `release:notes` step in `checks`, not halfway through the release loop. Test in Task 3.
3. **A merge on a later UTC day than the changelog date:** a PR check flags an untagged current version not dated today, so the PR goes red until it is re-dated. Test in Task 2 (`--date-check`).
4. **A backfill dispatch with an unknown plugin or a ref where that version isn't current:** fails with a clear message and creates nothing. Test in Task 4.
5. **PC-04 on PR #107:** the 9 versions untagged on `main` are each their plugin's current version, so they pass. skill-diagnostics 0.4.0 stays flagged until the backfill. Test in Task 2.

---

### Task 0: Get on the remote work branch

- [ ] `git fetch origin ccr-7fcd6ef3-rku7l1 && git switch -c ccr-7fcd6ef3-rku7l1 --track origin/ccr-7fcd6ef3-rku7l1`. Expected: HEAD `005f47d`, `git status` clean, 0 behind the remote.
- [ ] `npm ci`, `npm run tools:install`, `uv sync`. Then install tailwind-development's packages, so the typecheck baseline matches the ADR.

### Task 1: Baseline: which checks pass on B today

- [ ] Run each npm script that `check` and the debt list cover, separately: `lint:python`, `lint:shell`, `lint:workflows`, `lint:github`, `lint:js`, `lint:frontmatter`, `lint:skills`, `typecheck:ts`, `typecheck:python`, `check:consistency`, `validate` (per plugin), `validate:claude`, `validate:mods`, `validate:portable`, `validate:hooks-catch`, `test:scripts`, plugin hook tests. Record exit code and raw output in `.claude/maintainer/plans/2026-11-15-release-pipeline-baseline.md`.
- [ ] Classify each check as blocking (passes) or debt (fails, with its DEBT id). A failure that matches no DEBT item stops the work and goes to the owner.
- [ ] Find the commit on `main` where skill-diagnostics `plugin.json` was `0.4.0` and its CHANGELOG had a non-empty `## [0.4.0]`. Run `release-notes.py skill-diagnostics` at that commit in a temp worktree in the scratchpad. If no such commit exists, report it to the owner: backfill isn't possible as designed.
- [ ] Commit the baseline file.

### Task 2: Consistency-check fixes (test-first)

**Files:** modify `scripts/validators/plugin_consistency/checks.py` and `cli.py`; test `scripts/testers/plugin_consistency/test_checks.py`.

- [ ] Write failing tests:
  - `test_pc04_current_version_untagged_passes`: the base equals HEAD, the current heading has no tag, and there are no findings.
  - `test_pc04_older_heading_untagged_fails`: 0.4.0 has no tag, the current version is 0.4.1, and PC-04 is reported for 0.4.0.
  - `test_pc05_runs_with_main_flag_on_detached_head`.
  - `test_date_check_flags_untagged_current_version_not_dated_today`: the date is injected, not the wall clock.
- [ ] Run `npm run test:scripts`. Expected: the 4 new tests FAIL.
- [ ] Implement:
  - `_tags`: `pending = current` (no base comparison);
  - `_unreleased(root, force_main: bool)`;
  - a `--main` and a `--date-check` flag in `cli.py`, with `check(..., main=False, date_check=False, today=None)`.
- [ ] Run `npm run test:scripts`. Expected: all pass. Then run `npm run check:consistency`: only skill-diagnostics 0.4.0 remains under PC-04.
- [ ] Fix the `release-status.py:4` docstring (`release:notes` → `release:status`). Commit.

### Task 3: Plugin hook tests get an npm script

- [ ] List every `plugins/*/tests/test_*.py` and `*.test.mjs` on B. Add `test:plugins` to `package.json`: Python `unittest` per plugin through `uv run`, and `node --test` for `.mjs`. Run it and record the output. If a test fails, it goes to `debt` with a new DEBT item, and the owner is told. Commit.

### Task 4: `release.yml` as a reusable workflow

**Files:** modify `.github/workflows/release.yml` and `.github/zizmor.yml`.

- [ ] Triggers: `workflow_call` with inputs `ref` (string, default the caller SHA) and `plugin` (string, optional), and `workflow_dispatch` with the same inputs. Remove `workflow_run`.
- [ ] Settings:
  - `permissions: {}` at the top, with `contents: write` on the job;
  - `timeout-minutes: 15`;
  - `concurrency: release`, no cancel;
  - checkout at `inputs.ref` with `persist-credentials: false`;
  - inputs read only through `env:` (W-01).
- [ ] The loop:
  - when `plugin` is set, only that plugin, and exit 2 if it isn't in `marketplace.json`;
  - when a `ref` is given for a backfill, check that the plugin's version at that ref is the one being tagged;
  - the rest stays as today.
- [ ] Remove the `artipacked` and `dangerous-triggers` exceptions that no longer apply.
- [ ] Run `npm run lint:workflows`, `actionlint` and `zizmor --offline` with 0 findings. Run the loop locally with `gh` stubbed: no bump → 0 releases; unknown plugin → exit 2. Commit.

### Task 5: `validate.yml`

**Files:** create `.github/workflows/validate.yml`.

- [ ] Triggers: `pull_request` and `push` on `main`, plus `workflow_dispatch`. `permissions: {}`. Concurrency `validate-${{ github.ref }}`, cancelling only for PRs.
- [ ] Jobs:
  - `checks`: blocking, the Task 1 list, plus `check:consistency -- --date-check` on PRs and `-- --main` on push, plus `release:notes` for every plugin;
  - `debt`: `continue-on-error: true`, one named step per DEBT id;
  - `release`: `if: github.event_name == 'push'`, `needs: checks`, `uses: ./.github/workflows/release.yml`, `permissions: contents: write`.
- [ ] Install Claude Code in CI by the method the current official docs give, read in Task 5 with the docs MCP and the release notes. The old signed-apt method lives only in the deleted ADR and gets re-verified before reuse. `claude plugin validate|test` need no sign-in; check this on the runner.
- [ ] Pin every action with the `version-drift.md` pipeline. Run `npm run lint:workflows` with 0 findings. Audit by hand against W-01 to W-13 in `plugins/github-operations/skills/claude-github-actions/references/workflow-audit.md`. Commit.

### Task 6: The consolidated skill

**Files:** rewrite `.claude/skills/plugin-releases/SKILL.md` (plus `references/` as needed); delete `.claude/skills/plugin-versioning/`; update every reference.

- [ ] `grep -rn "plugin-versioning"` across the repository. Update each hit to `plugin-releases`: CLAUDE.md routing, `.claude/rules/plugins/categories.md:15`, `docs-maintenance`, `plugin-catalog-changes`, and WORKFLOW leftovers.
- [ ] Write the skill from Part 1:
  - gotchas first: one version per release; rename from the old name; cloud never tags; re-date on slip;
  - phases A to C plus backfill and withdraw;
  - remove the "Before you start" stop.
- [ ] Follow `.claude/rules/code-quality/skill-standards.md`. Run `npm run lint:skills -- .claude/skills/plugin-releases`, and report each finding by rule id to the owner before fixing. Run `npm run validate:claude` and Biome. Commit.

### Task 7: Records and stale references

- [ ] Use `project-maintainer:write-records` for the ADRs: (1) the CI gate covers what passes, with debt non-blocking; (2) release as a reusable workflow called by Validate, with dispatch backfill; (3) the PC-04 pending rule and PC-05 `--main`; (4) versioning merged into `plugin-releases`.
  - Supersede `ADR_2026-11-13_changelog-versions-link-to-release-pages`, whose line 32 contradicts the current rule.
  - Fix the dead pointers in `ADR_2026-11-13_changelog-only-changes-take-no-version-bump` and `ADR_2026-11-13_checks-run-fast-locally-and-in-full-in-ci` by supersession.
  - Confirm `release-workflow-runs-python-through-uv` after the first green run.
- [ ] DEBT: record the absent evals CI (`evals.md:14`). Fix:
  - `.claude/architecture/refactor.md:33`, and lines 20 and 179;
  - `docs-maintenance` `plugin-readme.md:51,121` and `root-readme.md:75`;
  - root `CHANGELOG.md:6` against `marketplace-changelog.md:51`;
  - `github.md:32` (`check:install` without `--from`).
- [ ] Run Biome and `check:consistency`. Commit.

### Task 8: plugin-engineering 0.3.0 through the new skill

- [ ] Phase A: Minor, for the new `plugin-testing-and-debugging` skill. `release:status -- --next plugin-engineering --level minor` gives `0.3.0`. Write the notes under `[Unreleased]` with `docs-maintenance`, then update the catalog cell.
- [ ] DEBT-006's five `useTopLevelHeading` findings in its `assets/` stay in `debt`, unless the owner chooses the override or the heading.
- [ ] Run the phase A checks with raw output. Commit.

### Task 9: Owner gates, then release

- [ ] Report to the owner: the baseline, the diffs, the check output. Ask authorization to push B. `validate.yml` then runs on PR #107.
- [ ] With authorization:
  1. retitle PR #107;
  2. backfill dispatch for skill-diagnostics 0.4.0 (`ref` from Task 1). It is dispatched on branch `ccr-7fcd6ef3-rku7l1`, so GitHub runs B's `release.yml`, not `main`'s. Before dispatching, confirm in the GitHub docs that a dispatch runs the workflow file at the chosen branch;
  3. confirm `checks` is green.
- [ ] On merge day, phase B: run `release:changelog` for the 10 untagged current versions, plus plugin-engineering 0.3.0, and write the root CHANGELOG lines. Push with authorization, and wait for green.
- [ ] Merge with authorization. Watch `validate` → `release` on `main`. Then phase C: 11 new tags and Releases, `release:status` with no untagged version, and `check:install -- --from main` for each plugin.

## Verification (end to end)

- `npm run test:scripts`, `npm run lint:workflows` and `npm run lint:skills` all exit 0, with raw output.
- `actionlint` and `zizmor --offline` report 0 findings.
- On PR #107, `validate.yml` `checks` is green and `debt` lists only DEBT-tagged failures.
- After the merge: `git ls-remote --tags origin` shows each `<plugin>--v<version>` from the `release:status` list, and `release:status` prints no `untagged:` line.
- `check:install -- --from main` passes for every released plugin.

## Not in scope

- Recreating `claude.yml`, `claude-code-review.yml`, `evals.yml` or the removed bump scripts (owner: identify, don't replicate).
- Fixing DEBT-001, DEBT-003, DEBT-005 or DEBT-006 themselves.
- Branch protection or rulesets: today none exist, under ADR `main-and-release-tags-stay-unprotected`, deleted in `ced195b`. The question is raised to the owner in the closing summary only.
