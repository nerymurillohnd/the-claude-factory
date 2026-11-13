---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Five consolidated scripts cover the release and consistency checks

## Scope

The maintainer scripts that do the mechanical steps of the `plugin-versioning`, `plugin-releases`, `plugin-catalog-changes` and `docs-maintenance` skills:

| Script | npm script |
| --- | --- |
| `scripts/release/release-notes.py` | `release:notes` |
| `scripts/release/release-status.py` | `release:status` |
| `scripts/release/check-install.sh` | `check:install` |
| `scripts/release/release-changelog.py` | `release:changelog` |
| `scripts/validators/plugin-consistency.py` | `check:consistency` |

The shared Python lives in `scripts/release/release_tools/` and `scripts/validators/plugin_consistency/`, with tests in `scripts/testers/release/` and `scripts/testers/plugin_consistency/`.

Out of scope:
- the schema validators, `check-plugin-name.py`, the catalog generator and the URL checker, which stay Pending in `.claude/architecture/refactor.md`
- any change under `plugins/`

## Context and problem statement

The skills ran their mechanical steps as inline bash. Examples:
- loops over `origin/main` for changed and untagged versions
- a `jq | grep` semver test
- the same throwaway-install block copied into three skills
- a hand edit to date `[Unreleased]`

`release.yml` called `scripts/release/release-notes.py`, which did not exist.

`.claude/architecture/refactor.md` planned about fifteen per-check scripts, rebuilt from `main`. Six of them were pairs that repeated the same check. The audits `maintainer-scripts-inventory-2026-11-09.md` and `scripts-vs-cli-2026-11-09.md` show that those pairs drifted apart on `main`. They also show which steps no `claude plugin` command covers. Those findings were re-checked on Claude Code 2.1.323 on 2026-11-13.

## Decision drivers

- A script covers only what no `claude plugin` command does (blueprint rule 2 in `refactor.md`).
- One copy of each check, so that two scripts can't disagree.
- Skills keep the judgment, and scripts give the facts:
  - the semver level
  - the release notes
  - whether a dependency range still fits
- Every script is tested before it is used, and runs through an npm script (ADR_2026-11-12_npm-scripts-are-the-single-entry-point).

## Considered options

- **Five consolidated scripts, with shared readers**: chosen.
- **The ~15 per-check scripts that `refactor.md` lists**: rejected, because six of them overlap, and the pairs on `main` drifted.
- **Keep the inline bash in the skills**: rejected, because the blocks were copied into several skills, can't be tested, and needed every reader to run them exactly.

## Decision outcome

Chosen option: **five consolidated scripts**, because each mechanical step then has one tested owner, and the skills call it by its npm script. The owner chose this on 2026-11-13.

### Consequences

- Good, because `release.yml` now has its `release-notes.py`. Its output for `block-no-verify` 0.1.5 matched the published GitHub Release body byte for byte.
- Good, because `npm run test:scripts` covers the five scripts with offline tests. Those tests use throwaway git repositories and a stub `claude`.
- Good, because `plugin-consistency.py` builds the mechanical part of DEBT-001.
- Bad, because `refactor.md`'s per-check plan no longer matches the files, until its lines are marked Replaced by.
- Bad, because `release-status.py` lists dependency ranges without judging them. No plugin declares `dependencies` today, and a range parser would need a package beyond the stdlib.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The scripts pass their tests | `npm run test:scripts` | 2026-11-13: 236 tests, OK | Every change under `scripts/` |
| The repository is consistent | `npm run check:consistency` | 2026-11-13: exit 0 on the branch; a planted catalog version drift was reported | Every plugin or catalog change |
| The release dry run works | `release:status`, `check:install -- --from local block-no-verify`, `release:notes -- block-no-verify --tag` | 2026-11-13: exit 0, tag `block-no-verify--v0.1.5` | Before each release |

## More information

The plan is `.claude/maintainer/plans/2026-11-13-release-and-consistency-scripts.md`. The CI side is ADR_2026-11-13_release-workflow-runs-python-through-uv.
