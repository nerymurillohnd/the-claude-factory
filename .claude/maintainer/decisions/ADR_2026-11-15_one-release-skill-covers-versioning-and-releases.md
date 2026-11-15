---
status: accepted
date: 2026-11-15
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# One skill, plugin-releases, covers the version bump and the release

## Scope

`.claude/skills/plugin-releases/`, the deleted `.claude/skills/plugin-versioning/`, and the documents that name them: `.claude/CLAUDE.md`, `.claude/rules/plugins/categories.md`, and the `docs-maintenance`, `plugin-catalog-changes` and `plugin-icons` skills. `plugin-catalog-changes` stays separate.

## Context and problem statement

Versioning and releasing were two skills that referred to each other at every step. Their split broke the flow. `plugin-versioning` had to pass `check:consistency`, whose catalog check (PC-08) only the later release step satisfied. `plugin-releases` told Claude to stop before every merge while `validate.yml` was missing. The owner asked for one definitive skill for the repeated process, built from the corrected release guide, and left its structure to Claude.

## Decision drivers

- One procedure from "a plugin changed" to "users can update", repeatable in any session.
- No step that a later step of another skill must satisfy.

## Considered options

- **Merge both into `plugin-releases`, in phases: version, before the merge, merge and release, verify, backfill**: chosen.
- **Keep two skills and fix the cross-references**: rejected, because the pipeline would still be split across two skills that change together.

## Decision outcome

Chosen option: **one skill**, because the two parts change together and the merged body is about 120 lines. Phase A sets the catalog's version cell together with `plugin.json`. Phase B adds the reviews, the merge-day date and the release-notes checks.

### Consequences

- Good, because the version bump, its catalog cell and its release live in one procedure.
- Bad, because the skill triggers on more phrasings, from "bump it" to "ship it", and its description has to cover both.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The skill passes the linter | `npm run lint:skills -- .claude/skills/plugin-releases` | 2026-11-15: 0 errors, 0 warnings | Every change to the skill |
| No file names the deleted skill | `grep -rn plugin-versioning .claude/CLAUDE.md .claude/rules .claude/skills` | 2026-11-15: no match | After a rename |

## More information

- The owner delegated the structure on 2026-11-15: "the guide will become a skill, because it is a repeated process".
