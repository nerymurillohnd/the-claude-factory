---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-15_loading-evals-live-in-their-own-eval-directory
superseded-by: none
---

# CI runs extra eval suites with one arm

## Scope

`.github/workflows/evals.yml`, `.gitignore`, `scripts/validators/plugin_consistency/evals.py` and `.claude/rules/plugins/evals.md`.

## Context and problem statement

ADR_2026-11-15_loading-evals-live-in-their-own-eval-directory kept hook-engineering's loading cases in `evals-loading/`, apart from the two-arm quality suite, and accepted that CI never ran them. The evals audit of 2026-11-15 (item 9) found that a description change that stops the skill from loading would then go unnoticed, against the docs' purpose of catching regressions when a plugin changes; the docs provide `--eval-dir` for another directory of cases (<https://code.claude.com/docs/en/plugin-evals>, Use a different eval directory).

## Decision drivers

- CI catches a skill that stops loading.
- Loading cases don't move the quality suite's mean delta.

## Considered options

- **Run each `evals-*/` suite in CI with `--eval-dir <dir> --ablation none`, without a delta gate**: chosen.
- **Move the loading cases into `evals/`**: rejected, for the reason the earlier ADR gives: they would move the quality suite's delta.

## Decision outcome

Chosen option: **one-arm extra suites in CI**, as part of the owner's instruction on 2026-11-15 to fix every finding of the audit:
- `evals.yml` runs `evals/` in two arms with the plugin's delta floor, then each `evals-*/` folder that has a case for the effort group with `--eval-dir <dir> --ablation none`, gated only on comparability.
- Suite discovery searches cases at any depth, as the docs allow grouping, and fails the job on a plugin that sets `experimental.evals`.
- `.gitignore` adds `plugins/*/evals-*/results/`.

### Consequences

- Good, because a loading regression fails CI.
- Bad, because each extra suite adds model calls to every run of its plugin's suites.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Nested cases need effort tags | `scripts/testers/plugin_consistency/test_checks.py` (`test_pc14_finds_cases_nested_in_groups`) | 2026-11-15: 44 tests OK | After `evals.py` changes |
| Extra results are ignored | `git check-ignore -v plugins/hook-engineering/evals-loading/results/x` | 2026-11-15: matched `.gitignore:33` | After `.gitignore` changes |
| The loading suite runs in CI | The first CI run of hook-engineering's suites | pending | On the next pull request that changes hook-engineering |
