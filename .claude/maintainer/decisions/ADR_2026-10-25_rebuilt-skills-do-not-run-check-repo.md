---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The rebuilt skills do not run or describe check-repo.mjs

## Scope

The procedures of the rebuilt skills: `release-and-versioning`, `plugin-renames-and-removals`, `maintaining-user-docs`, and the others built in the same consolidation. `scripts/check-repo.mjs` itself, and CI's use of it, are out of scope.

## Context and problem statement

Three rebuilt skills ran `node scripts/check-repo.mjs` among their checks or described what it reads:
- `release-and-versioning` step 6;
- `plugin-renames-and-removals` step 10;
- `maintaining-user-docs` step 6 and a gotcha.

The agreement for these skills is that each one runs its own self-contained scripts. `check-repo.mjs` is a repository script, and it enforces the older plugin README shape (DEBT-011). Should the skills keep running it?

## Decision drivers

- Each rebuilt skill runs its own self-contained scripts.
- A skill's procedure must not depend on a repository script that enforces what the skill has replaced.

## Considered options

- **Remove every run and mention of `check-repo.mjs` from the rebuilt skills**: chosen.
- **Keep it as "the repository checks this skill does not own"**: rejected, because it is outside the skills' self-contained scripts, and it refuses what `building-plugins` now writes.

## Decision outcome

Chosen option: **remove it from the skills** (commit 032710c). Their check lists are renumbered.

### Consequences

- Good, because the skills' procedures depend only on their own scripts and the repository's generators, and no longer on a check that enforces the old template.
- Bad, because the repository checks `check-repo.mjs` runs, such as portability and the README sections, are no longer part of a skill's procedure; they still run in Validate on CI.

## More information

Decided by Nery on 2026-10-25 in this session ("elimina toda referencia y mencion en las skills nuevas para check-repo.mjs"), with the reason he gave right after: the skills had agreed to run their own self-contained scripts. Other `node scripts/…` steps the rebuilt skills still run are the generators, which regenerate derived files as repository maintenance (ADR_2026-10-25_plugin-scaffold-belongs-to-building-plugins).
