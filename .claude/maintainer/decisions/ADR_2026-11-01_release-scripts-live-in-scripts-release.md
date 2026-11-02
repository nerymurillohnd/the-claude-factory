---
status: accepted
date: 2026-11-01
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-28_skill-bump-copies-stay-identical
superseded-by: none
---

# The version and release scripts live in `scripts/release/`, one copy each

## Scope

Applies to `bump-version.py`, `check-version-bump.py`, `release-notes.py`, `check-changelog-entry.py` and `check-marketplace-unversioned.py`, and to everything that runs them: `.github/workflows/release.yml`, the `version-bump` gate in `scripts/gates.mjs`, `npm run version:bump`, `scripts/testers/scripts.test.mjs` and `.github/pull_request_template.md`. The release procedure itself stays in the `versioning` and `releases` skills.

## Context and problem statement

870c335 retired `release-and-versioning` and 2e634ac split `plugin-renames-and-removals`. Both kept their `scripts/` folder with no `SKILL.md`, because CI and the tests still ran it. So the release workflow ran Python from a skill the records called retired: deleting the retired folder would have broken the next release. The seven scripts left in `plugin-renames-and-removals` had no runner except a test that kept two of them byte-identical with the other copy. The new skills describe the scripts' logic as steps and name no script.

## Decision drivers

- Removing a retired skill must never break a release.
- One copy of each rule, so two copies cannot drift apart.
- The scripts serve the maintainer only.

## Considered options

- **Move the five scripts to `scripts/release/` and delete the unused copies and their identity test**: chosen.
- **Keep the folders and record that they are still live**: rejected because a folder with no `SKILL.md` under `.claude/skills/` still looks retired, and the copies would keep needing their test.

## Decision outcome

Chosen option: **move them to `scripts/release/`**, because they are maintainer tooling with a home of their own, and nothing under `.claude/skills/` runs a release any more.

- The scripts resolve the root two levels up, or `TCF_ROOT`.
- They still run on the `python3` of CI's runner, so `ruff.toml` and `pyrightconfig.json` check `scripts/release/` against Python 3.12.
- The `skill copies of the bump rules` test is removed with the copies.

### Consequences

- Good, because a skill can be retired or renamed without touching a release.
- Good, because each rule has one copy, so the drift DEBT-038 recorded cannot come back.
- Bad, because `check-changelog-entry.py` and `check-marketplace-unversioned.py` move with the others although nothing runs them today.

## More information

Nery decided on 2026-11-01, from the consolidated audit of 2026-11-01 (finding M-05). The move is commit e36afa5. ADR_2026-10-28_version-gate-runs-the-release-skill-script and ADR_2026-10-25_release-workflow-runs-the-release-skill-script still hold: the gate and `version:bump` run these `.py` scripts, and `release.yml` runs `release-notes.py`, now from `scripts/release/`.
