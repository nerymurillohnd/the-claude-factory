---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The release workflow runs the release skill's script

## Scope

`.github/workflows/release.yml`, which prints each plugin's tag and the notes of its GitHub Release, and `.claude/skills/release-and-versioning/scripts/release-notes.py`. Out of scope: the version-bump and marketplace checks that `scripts/gates.mjs` runs from `scripts/` in Validate, and an eval workflow.

## Context and problem statement

`release.yml` built the tag and the notes with `scripts/release-notes.mjs`. The `release-and-versioning` skill owns `release-notes.py` for the same job, and its procedure tells the maintainer to print the expected tag with it. Two scripts decided what a release publishes, with nothing keeping them equal. On 2026-10-25 both printed the same notes and tag for all 17 plugins. Which script should CI run?

## Decision drivers

- One source for what a release publishes.
- The skill that governs releasing owns the scripts its procedure runs.
- The script must run on the CI runner with no install step: it is stdlib Python run by the `python3` on `PATH`.

## Considered options

- **CI runs the skill's `release-notes.py`, and `scripts/release-notes.mjs` with its test is retired**: chosen.
- **Keep `scripts/release-notes.mjs` in CI**: rejected because two scripts would have to stay identical with nothing comparing them.

## Decision outcome

Chosen option: **CI runs the skill's `release-notes.py`**, because the script the maintainer checks a release with is then the one that publishes it.

### Consequences

- Good, because the tag and notes the skill prints are by construction the ones the release carries.
- Good, because `scripts/` loses a script that duplicated the skill's.
- Bad, because `release.yml` now depends on a path inside `.claude/skills/`; moving or renaming the skill or its script breaks the release.
- Bad, because the `release-notes.mjs` test in `scripts/tests/scripts.test.mjs` is gone, and the skill's scripts ship without tests, so no automated test covers the notes.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Both scripts printed the same notes and tag | Compared the output of both for every plugin under `plugins/` | Same for 17 of 17 plugins, 2026-10-25 | Not needed; the `.mjs` is gone |
| The skill's script refuses the marketplace | `release-notes.py marketplace --tag` | Exit 1, "No version found for marketplace" | After any change to the script |
| The workflow and the tests still pass | `actionlint`, `node --test scripts/tests/scripts.test.mjs`, `tsc -p scripts/tsconfig.json` | actionlint clean, 48 of 48 tests pass, tsc clean | — |
| The script runs under the runner's `python3` | The first release run after the push | pending | The next push of `main` that tags a plugin |

## More information

Nery chose this on 2026-10-25, together with two scope answers: the gates in `scripts/gates.mjs` keep their `scripts/` checks for a separate change, and no eval workflow is installed now. Commit `500c30e`. Related: ADR_2026-10-25_release-tags-are-created-unsigned-by-ci.
