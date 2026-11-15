---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_validate-gates-merges-on-passing-checks-and-reports-debt
superseded-by: none
---

# Validate gates every merge on the checks that pass today, checks consistency as main will be, and reports the checks the debt holds back

## Scope

`.github/workflows/validate.yml` and the composite action `.github/actions/setup`: the checks that run on every pull request, every push to `main` and every manual dispatch. Out of scope: the release (ADR_2026-11-15_validate-calls-the-reusable-release-workflow, and ADR_2026-11-15_validate-checks-a-pull-request-as-main-will-be for the notes check), the Claude workflows and evals.

## Context and problem statement

`validate.yml` was deleted in `ced195b` (2026-11-13) because it still ran the removed `scripts/gates.mjs`. Since then no pull request had CI, and `release.yml`, which ran on `workflows: [Validate]`, had nothing to wait for.

`npm run check` failed on logged debt: DEBT-003 (`claude plugin validate --strict` on five plugins, `validate:portable`, `validate:hooks-catch`), DEBT-005 (`lint:frontmatter`) and DEBT-006 (`lint:js`). All three are still open in `.claude/maintainer/technical-debt/pending-debt.md`. The baseline is `.claude/maintainer/plans/2026-11-15-release-pipeline-baseline.md`. How should the new gate treat them?

ADR_2026-11-15_validate-gates-merges-on-passing-checks-and-reports-debt recorded this decision. Its `check:consistency` bullet ("`--date-check` on pull requests, `--main` on push") stopped holding: `--date-check` was removed with PC-11, and since commit 6b4ba49 `.github/workflows/validate.yml` line 81 runs `npm run check:consistency -- --main` on every event. This record restates the decision with that bullet corrected and the other bullets read again against the current `validate.yml`.

## Decision drivers

- A merge gate that can pass today, so releases resume.
- Never weaken, skip or silence a check to get green.
- CI runs the same tool versions as the maintainers.
- A pull request that passes Validate must pass it on `main` after the merge.

## Considered options

- **Gate on what passes, and run the debt-held checks in a non-blocking job named by DEBT id**: chosen.
- **Fix DEBT-003 and DEBT-006 before Validate exists**: rejected, because those are per-plugin fixes with their own bumps, and no release could happen until all of them land.

## Decision outcome

Chosen option: **gate on what passes, report the rest**, because it restores a real gate now without hiding any failure.

- The `Checks` job blocks:
  - `lint:python`, `lint:shell`, `lint:workflows` and `lint:github`;
  - `typecheck`, `test:scripts` and `test:plugins`;
  - `claude plugin validate --strict` on every plugin outside DEBT-003, on `.`, and on `.claude` (`validate:claude`);
  - `validate:mods`;
  - `check:consistency -- --main` on every event (`validate.yml` line 81, commit 6b4ba49), so a pull request must have an empty `[Unreleased]` (PC-05) as `main` will;
  - `release:notes` for every plugin;
  - `check:install` for each changed plugin on a pull request, with `--no-strict` for a DEBT-003 plugin.
- The `Debt` job runs the held-back checks with `continue-on-error`, one step per DEBT id: `lint:js` (DEBT-006), `lint:frontmatter` (DEBT-005), and `claude plugin validate --strict` on the five plugins, `validate:portable` and `validate:hooks-catch` (DEBT-003). A step moves into `Checks` when its DEBT item closes.
- The toolchain matches the maintainers' machine:
  - Node from `.nvmrc` with npm 12.2.1, and Python from `.python-version` through uv;
  - ShellCheck 0.11.0, shfmt 3.14.1 and actionlint 1.7.12, each checked against its SHA-256;
  - Claude Code pinned to 2.1.325 (apt package `2.1.325-1`) from Anthropic's signed apt repository, with the key checked against fingerprint `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`. `claude plugin validate`, `test` and `install` need no sign-in: `validate.yml` reads no secret, and its run on pull request 107 passed.

### Consequences

- Good, because every pull request and every merge runs a gate, and the release can depend on it.
- Good, because the debt stays visible in every run.
- Good, because a pull request is checked as `main` will be, so a green pull request does not fail its push to `main` on PC-05.
- Bad, because a failure in a debt-held check never blocks, so a new finding there can merge unnoticed until its DEBT item closes.
- Bad, because the Claude Code pin needs a manual bump with each local upgrade (`CLAUDE_CODE_VERSION` in `.github/actions/setup/action.yml`).

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The workflow passes its linters | `npm run lint:workflows` (actionlint, `zizmor --offline .`) | 2026-11-15: no findings, 6 ignored | Every workflow change |
| `Checks` passes on a pull request | Validate run 43706203365 on 63b3b8d, pull request 107 | 2026-11-15: `Checks` success; `Release` skipped, as it runs only on a push | Every push of the branch |
| `Checks` passes on the push to `main` | The first Validate run on `main` after the merge | pending | The first merge after this change |

## More information

- The core decision was made by the owner on 2026-11-15 ("Gate what passes"). The owner then decided to supersede the record, after a review of pull request 107 found its `check:consistency` bullet out of date.
- Replaces ADR_2026-11-15_validate-gates-merges-on-passing-checks-and-reports-debt, which stays as written and points here through its `superseded-by`.
- The removal of `--date-check` is recorded in ADR_2026-11-15_changelog-date-is-the-day-a-version-is-prepared-and-validate-passes-main, which names the old bullet. This record carries the corrected bullet.
- Not carried over from the replaced record: its statement that `validate` behavior changed in Claude Code 2.1.323 and 2.1.325, which no file of the repository supports, and its claim that no tag had been created since 2026-11-10.
- Related: DEBT-003, DEBT-005, DEBT-006, ADR_2026-11-12_actionlint-and-zizmor-check-workflows.
