---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# A change limited to a plugin's CHANGELOG takes no version bump

## Scope

Version bumps of the plugins under `plugins/`:
- the `plugin-versioning` skill (step 1);
- `.claude/rules/plugins.md` (Version bumps);
- `.claude/rules/plugins/versioning.md`;
- the `docs-maintenance` small-fix event.

Out of scope: the release itself, where `npm run release:changelog` dates the CHANGELOG as part of a version that is already bumped.

## Context and problem statement

Two sources disagree on whether a change that touches only a plugin's `CHANGELOG.md` needs a new version:
- **Bump:** step 1 of the `plugin-versioning` skill says "Anything else in `plugins/<plugin>/` changed, `CHANGELOG.md` included: bump".
- **No bump:**
  - `.claude/rules/plugins.md:57` and `.claude/rules/plugins/versioning.md:16` give no bump to changes confined to documentation;
  - the `docs-maintenance` small-fix event gives none to a documentation fix that changes nothing about how the plugin works.

Does a CHANGELOG-only change, such as a typo or a broken link in a past entry, take a version bump?

## Decision drivers

- Users receive a change only when the version string changes, so a bump must mean something users install.
- One rule, stated the same way in the rule and the skill.

## Considered options

- **No bump for a change limited to the CHANGELOG**: chosen.
- **Bump whenever the CHANGELOG changes**: rejected. It ships a new version that changes nothing a user installs, and it contradicts the rule in force and the small-fix event.

## Decision outcome

Chosen option: **no bump for a change limited to the CHANGELOG**. The CHANGELOG is documentation: editing it changes no behavior and nothing users have installed. The rule in force and the small-fix event already say this.

### Consequences

- Good, because the skill, the rule and the small-fix event give one answer.
- Neutral, because a CHANGELOG that changes together with a component still goes with that component's bump.
- Bad, because `plugin-versioning` step 1 says otherwise until migration step 2 corrects it.

## More information

- **Decided:** by the owner on 2026-11-13, as decision D3 of `.claude/maintainer/plans/2026-11-13-claude-architecture-proposal.md`, by approving the recommended answer.
- **Related:** ADR_2026-11-13_claude-configuration-architecture.
- **Pending:** the correction of `plugin-versioning` step 1 in migration step 2.
