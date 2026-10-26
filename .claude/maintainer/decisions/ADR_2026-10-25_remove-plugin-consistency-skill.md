---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Remove the plugin-consistency skill

## Scope

The project skill `.claude/skills/plugin-consistency/`. Out of scope: the skills that handed off to it, corrected separately.

## Context and problem statement

`plugin-consistency` checked that a plugin's components, README, manifest and marketplace entry agreed after an edit, and ran the repository's scripts. Earlier on 2026-10-25 it was rewritten to keep only what no rebuilt skill covered. The rebuilt skills now each check what they govern: `building-plugins` its components and README, `release-and-versioning` versions and changelogs, `maintaining-user-docs` the marketplace docs. Should the remnant stay?

## Decision drivers

- Each skill runs the checks of what it governs, with its own scripts.
- New, validated skills outrank the older files.

## Considered options

- **Remove the skill**: chosen.
- **Keep it as a cross-check after every edit**: rejected because Nery ordered its removal. Not stated by the user beyond the order itself.

## Decision outcome

Chosen option: **Remove the skill**, on Nery's order (commit `58d202e`).

### Consequences

- Good, because no second skill re-checks what the owning skill already checks.
- Bad, because no skill compares a plugin README with `docs/compatibility.md` or the root README catalog after an edit; each owning skill has to.

## More information

Nery gave the order on 2026-10-25 ("eliminar @.claude/skills/plugin-consistency"). The hand-off rows to it in `plugin-hooks-guidance` were removed in commit `74f8df4`.
