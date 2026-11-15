---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# A plugin's loading evals live in their own eval directory, outside the quality suite

## Scope

`plugins/hook-engineering/evals-loading/`, beside the quality suite in `plugins/hook-engineering/evals/`, and the `plugins/*/evals-*/**` patterns in `biome.jsonc` and `.claude/rules/plugins/evals.md`. Plugins whose suites already mix trigger and quality cases are out of scope.

## Context and problem statement

The owner asked for two suites for `writing-hooks`, reported separately: loading (does the skill load, and only then) and quality (five cases with and without the skill, where the 25-point target applies). A loading case's main grader is `tool_used: Skill`. In a two-arm run that grader is excluded from the score, and when every grader of a case is excluded they are scored normally, so a must-load case scores 1 with the plugin and 0 without it, and a must-not-load case scores the same in both arms. Either one would move the quality suite's mean delta. `.github/workflows/evals.yml` runs a plugin's default eval directory in two arms.

## Decision drivers

- The quality suite's delta must measure only the quality cases.
- Loading is measured with `--ablation none`, as the plugin-testing skill and the owner's case list set.
- Use only what `claude plugin eval` supports.

## Considered options

- **A second eval directory, `evals-loading/`, run with `--eval-dir evals-loading --ablation none`**: chosen.
- **Loading cases in `evals/` beside the quality cases**: rejected, because they would distort the delta the quality gate reads.
- **`experimental.evals` in `plugin.json` pointing at another folder**: rejected, because it moves the default suite rather than adding a second one, and CI reads the default.

## Decision outcome

Chosen option: **a second eval directory**, because `--eval-dir` is the documented way to run another directory of cases, and it keeps the two measurements apart:
- `evals/` stays the suite `evals.yml` runs in two arms and gates.
- `evals-loading/` runs by hand or by dispatch, with `claude plugin eval plugins/hook-engineering --eval-dir evals-loading --ablation none`.
- Decided as a technical choice the owner delegated on 2026-11-15; the owner set the two suites and their separate reporting.

### Consequences

- Good, because the quality delta and the loading results can't contaminate each other.
- Bad, because CI doesn't run the loading suite on its own, so a description change that stops the skill from loading is caught only by a manual run.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Both directories hold valid cases | Frontmatter and grader fields checked against the eval reference, regexes compiled | 2026-11-15: 13 cases, 40 graders, 0 problems | After a case changes |
| Biome treats `evals-loading/` like `evals/` | `npx biome check plugins/hook-engineering/evals-loading` | 2026-11-15: no findings | After `biome.jsonc` changes |
| The loading suite runs | A first run with the owner's approval | pending | Before each release of the plugin |
