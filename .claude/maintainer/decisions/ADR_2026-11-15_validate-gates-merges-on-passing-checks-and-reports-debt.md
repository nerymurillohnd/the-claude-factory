---
status: superseded
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-13_checks-run-fast-locally-and-in-full-in-ci
superseded-by: ADR_2026-11-15_validate-gates-merges-on-passing-checks-with-consistency-as-main-will-be
---

# Validate gates every merge on the checks that pass today, and reports the checks the debt holds back

## Scope

`.github/workflows/validate.yml` and the composite action `.github/actions/setup`: the checks that run on every pull request and every push to `main`. Out of scope: the release (ADR_2026-11-15_validate-calls-the-reusable-release-workflow), the Claude workflows and evals.

## Context and problem statement

`validate.yml` was deleted in `ced195b` (2026-11-13) because it still ran the removed `scripts/gates.mjs`. Since then no pull request had CI. `release.yml` waited on a workflow named `Validate`, so no tag has been created since 2026-11-10. ADR_2026-11-13_checks-run-fast-locally-and-in-full-in-ci made CI the single gate and pointed to `.claude/rules/testing.md`, which no longer exists.

`npm run check` fails today on logged debt: DEBT-003 (`validate --strict` on five mods, `validate:portable`, `validate:hooks-catch`), DEBT-005 (`lint:frontmatter`) and DEBT-006 (`lint:js`). The baseline is `.claude/maintainer/plans/2026-11-15-release-pipeline-baseline.md`. How should the new gate treat them?

## Decision drivers

- A merge gate that can pass today, so releases resume.
- Never weaken, skip or silence a check to get green.
- CI runs the same tool versions as the maintainers.

## Considered options

- **Gate on what passes, and run the debt-held checks in a non-blocking job named by DEBT id**: chosen.
- **Fix DEBT-003 and DEBT-006 before Validate exists**: rejected, because those are per-plugin fixes with their own bumps, and no release could happen until all of them land.

## Decision outcome

Chosen option: **gate on what passes, report the rest**, because it restores a real gate now without hiding any failure.

- The `Checks` job blocks:
  - `lint:python`, `lint:shell`, `lint:workflows` and `lint:github`;
  - `typecheck`, `test:scripts` and `test:plugins`;
  - `claude plugin validate --strict` on every plugin outside DEBT-003, on `.`, and on `.claude`;
  - `validate:mods`;
  - `check:consistency`: `--date-check` on pull requests, `--main` on push;
  - `release:notes` for every plugin;
  - `check:install` for each changed plugin on a pull request.
- The `Debt` job runs the held-back checks with `continue-on-error`, one step per DEBT id. A step moves into `Checks` when its DEBT item closes.
- The toolchain matches the maintainers' machine:
  - Node from `.nvmrc` with npm 12.2.1, and Python from `.python-version` through uv;
  - ShellCheck 0.11.0, shfmt 3.14.1 and actionlint 1.7.12, each checked against its SHA-256;
  - Claude Code pinned to `2.1.325-1` from Anthropic's signed apt repository, with the key checked against fingerprint `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE`. `claude plugin validate`, `test` and `install` need no sign-in; this was checked with an empty configuration on 2026-11-15.

### Consequences

- Good, because every pull request and every merge runs a gate, and the release can depend on it.
- Good, because the debt stays visible in every run.
- Bad, because a failure in a debt-held check never blocks, so a new finding there can merge unnoticed until its DEBT item closes.
- Bad, because the Claude Code pin needs a manual bump with each local upgrade; `validate` behavior changed in 2.1.323 and 2.1.325.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The workflow passes its linters | `npm run lint:workflows`, `zizmor --offline --persona auditor .` | 2026-11-15: no findings | Every workflow change |
| `Checks` passes on a pull request | The first run on the work branch's pull request | pending | The first push of the branch |

## More information

- Decided by the owner on 2026-11-15 ("Gate what passes").
- Related: DEBT-003, DEBT-005, DEBT-006, ADR_2026-11-12_actionlint-and-zizmor-check-workflows.
