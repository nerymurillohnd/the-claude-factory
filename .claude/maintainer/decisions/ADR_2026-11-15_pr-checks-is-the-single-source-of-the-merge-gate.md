---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# pr-checks.sh is the single source of the merge gate's checks, and Biome gates the files a pull request changes

## Scope

`scripts/validators/pr-checks.sh`, the `check:pr` npm script, every step of the `Checks` job and the DEBT-003 validate step of the `Debt` job in `.github/workflows/validate.yml`, and the local check named in `.claude/rules/architecture/github.md`. The pre-push hook that runs it is its own decision (ADR_2026-11-15_git-push-is-blocked-until-pr-checks-passes). The `Debt` job's other steps and `lint:js` itself are out of scope.

## Context and problem statement

[nerymurillohnd/the-claude-factory#109](https://github.com/nerymurillohnd/the-claude-factory/pull/109) failed Validate's `Checks` job on `lint:github`: the four plugin dropdowns of the issue forms lacked the new plugin. The new README also added a Biome format error. Both had passed every local check, because:

- the rule's local check was `npm run lint`, which runs `lint:js` first, and `lint:js` always fails on DEBT-006, so `&&` stopped before `lint:github` ran;
- the `Checks` job ran its own inline commands, so the local check and CI had already drifted apart;
- Biome ran only in the non-blocking `Debt` job, so a new format error never blocked a merge.

How can the local check and CI stay identical, and how can Biome gate new errors while DEBT-006 is open?

## Decision drivers

- A branch that passes locally must pass `Checks`, with no second copy to drift.
- New Biome findings must block, while DEBT-006's existing findings must not.
- One run reports every failing check, as the `Checks` job does.
- Blueprint rule 1 of `.claude/architecture/refactor.md`: one script, with every caller only calling it.

## Considered options

- **One script with named steps, called by CI, npm and the hook; Biome run with `--changed --since=<base>`**: chosen.
- **Fix `npm run lint` and leave CI's inline steps**: rejected, because the two would keep drifting and `lint` would still stop at the first failure.
- **Gate Biome with a baseline count of errors**: rejected, because a count lets a new error through when another one is fixed in the same branch, and it doesn't name the file.

## Decision outcome

Chosen option: **one script with named steps**, because every caller runs the same commands and Biome then sees only the files a branch changed.

### Consequences

- Good, because `npm run check:pr` runs exactly the `Checks` job's steps, keeps going after a failure and names each failed step.
- Good, because a format error in a changed file now blocks the pull request.
- Good, because the DEBT-003 plugin list lives only in the script.
- Bad, because `biome check --changed` reads committed changes only, so an uncommitted edit is not gated until it is committed (observed with Biome 2.6.6).
- Bad, because a CI step now hides its commands behind a script name; the script's `case` lists each step's commands.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| `npm run check:pr` passes on a clean branch | Full run on `claude/friendly-volta-voo5dd` after the #109 merge | Every step passed, 73 s | After each change to the script |
| A missing dropdown fails the script | `pr-checks.sh lint` with one form edited | `plugin dropdown lacks work-lifecycle`, exit 1 | Same |
| `biome-changed` catches the #109 README and passes the fixed one | Biome 2.6.6 `--changed --since=origin/main` | Fails on the old README, 0 errors on the 24 changed files | When Biome is upgraded |
| The `Checks` job passes with the script | Validate run on the pull request that brings this change | pending | That pull request |

## More information

- Related: ADR_2026-11-15_validate-gates-merges-on-passing-checks-with-consistency-as-main-will-be (the `Checks` and `Debt` split, unchanged) and ADR_2026-11-15_biome-lints-all-markdown-and-skips-only-formatting-instructions.
- When DEBT-006 closes, `lint:js` moves into the script's `lint` step, and `biome-changed` can go.
