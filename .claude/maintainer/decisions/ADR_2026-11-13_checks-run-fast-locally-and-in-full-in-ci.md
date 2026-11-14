---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Each check is defined once; it runs fast and only on what changed locally, and in full in CI

## Scope

Which repository and plugin checks run on the maintainer's machine, and which run in CI:
- lint, type checks and maintainer script tests;
- plugin validation and mod tests;
- consistency, install checks and evals.

Out of scope: the design of the pull-request workflow itself (`validate.yml`), a separate decision.

## Context and problem statement

The owner kept running into confusion between maintenance checks and plugin checks, and between what to run locally and what in CI. The repository has no pull-request workflow yet: `release.yml` is the only workflow. As a result, every check ran locally, sometimes twice, and the slow ones (install checks, evals) cost time and money on each run.

Which checks belong where, without one place repeating the other?

## Decision drivers

- No check is defined twice: local runs and CI call the same npm script or `claude plugin` command.
- Local runs stay fast, so they happen before every commit.
- CI is the gate before a merge.
- Evals cost the owner a model call per case, so they run only when the owner approves (`.claude/rules/plugins/evals.md`).

## Considered options

- **Locally, before each commit: the fast checks on what changed. In CI, on each pull request: everything, on the whole repository. Both call the same definitions**: chosen.
- **Run every check locally before each commit**: rejected because the install checks and the evals make each commit slow and costly.
- **Run every check only in CI**: rejected because there is no pull-request workflow yet, and slow feedback lets defects pile up between pushes.

## Decision outcome

Chosen option: **fast and scoped locally, full in CI, one definition per check**, because it keeps each commit cheap and makes CI the single gate. `.claude/rules/testing.md` (Local and CI) holds the table.
- **Locally, on what changed:**
  - `npm run lint` and `npm run typecheck`;
  - `npm run test:scripts` when `scripts/` changed;
  - `claude plugin validate --strict` on each changed plugin, plus `claude plugin test` for a mod;
  - `npm run check:consistency -- --offline`;
  - an eval smoke run only with the owner's approval.
- **In CI:**
  - `npm run check`;
  - `npm run check:install` for each changed plugin;
  - the full eval suite of each changed plugin that has evals.
- **Until a pull-request workflow exists:** the CI-only checks run locally before a merge, as the `plugin-releases` skill already does.

### Consequences

- Good, because each check has one definition and runs where its cost fits.
- Good, because the local and CI checks no longer overlap or diverge.
- Bad, because until the pull-request workflow exists the gate is manual, and it holds only if the release procedure is followed.

## More information

- Decided by the owner on 2026-11-13: run only the command-line checks and fast scripts locally, leave the heavy ones to CI, and keep the two from repeating each other.
- Pending: the pull-request workflow (`validate.yml`). `release.yml` already waits for a workflow named `Validate`.
- Related: ADR_2026-11-13_claude-md-points-each-stack-area-to-its-rule, ADR_2026-11-13_plugin-command-hook-tests-ship-in-the-plugin.
