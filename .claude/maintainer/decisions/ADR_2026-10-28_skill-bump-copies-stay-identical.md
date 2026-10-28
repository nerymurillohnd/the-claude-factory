---
status: accepted
date: 2026-10-28
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The release and plugin-renames skills keep identical copies of the bump scripts, and a test keeps them identical

## Scope

- In scope: `bump-version.py` and `check-version-bump.py` in `.claude/skills/release-and-versioning/scripts/` and in `.claude/skills/plugin-renames-and-removals/scripts/`; the test that compares them in `scripts/testers/scripts.test.mjs`; the step-10 row of the plugin-renames `SKILL.md`.
- Out of scope: the `version-bump` gate of `scripts/gates.mjs`, which runs the release skill's `check-version-bump.py` under ADR_2026-10-28_version-gate-runs-the-release-skill-script.

## Context and problem statement

The release skill and the plugin-renames skill each carry their own copy of the bump and the bump check. The copies of `bump-version.py` were identical, but the copies of `check-version-bump.py` had drifted: the plugin-renames copy accepted a skipped version (for example 0.1.0 to 0.3.0) that the release copy rejects. A test run on 2026-10-28 confirmed it: the release copy exited 1 with "version jumps from 0.1.0 to 0.3.0", and the plugin-renames copy exited 0. DEBT-038 logged it. Should the plugin-renames skill call the release skill's script, or keep its own copy?

## Decision drivers

- A skill runs the scripts it governs from its own folder, and each skill keeps its own copy of the scripts it runs. The rule came from Nery's memory of 2026-10-25, removed on 2026-10-28.
- The two copies must enforce the same rule, and a future change must not reopen the drift silently.

## Considered options

- **Keep two copies and make them identical; a test compares them**: chosen.
- **The plugin-renames skill runs the release skill's `check-version-bump.py`**: rejected because one skill would call another's script, against the rule above.
- **Keep the copies as they are**: rejected because the drift already caused a rule to pass in one skill and fail in the other.

## Decision outcome

Chosen option: **identical copies, enforced by a test**, because each skill then stays self-contained and the test fails at the first drift.

- `.claude/skills/plugin-renames-and-removals/scripts/check-version-bump.py` is replaced by the release skill's file, byte for byte.
- The step-10 row of the plugin-renames `SKILL.md` states the same rule: one patch, minor or major step above `origin/main`, and a skipped version fails.
- The test `skill copies of the bump rules` in `scripts/testers/scripts.test.mjs` asserts that both copies of each of the two scripts are equal. It runs with the maintainer node tests, so `npm test` and CI catch a drift.

### Consequences

- Good, because the drift that DEBT-038 records cannot recur without a failing test.
- Good, because each skill still runs only its own scripts.
- Bad, because a change to either script has to be made in both copies; the test forces the second copy.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The two skill copies of each script are identical | `node --test --test-name-pattern="skill copies" scripts/testers/scripts.test.mjs` | 2026-10-28: 2 of 2 pass | Each change to either script |
| A skipped version fails in the plugin-renames copy | Run its `check-version-bump.py` on a repository with a 0.1.0 to 0.3.0 bump | 2026-10-28: the release copy exited 1 before the copy was replaced; the copy is now identical, so the same result is expected | Each change to either script |

## More information

- Decided by Nery Samuel Murillo on 2026-10-28, who left the choice between the two options to the assistant in the session that closed DEBT-025.
- Logged as DEBT-038 on 2026-10-28; closed as resolved in `.claude/maintainer/technical-debt/closed-debt.md`.
- The memory that said gates and skills do not call each other was removed on 2026-10-28 by Nery. The `version-bump` gate keeps running the release skill's script, as ADR_2026-10-28_version-gate-runs-the-release-skill-script records.
