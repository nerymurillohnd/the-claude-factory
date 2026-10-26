---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# A mod's README states the Claude Code version it was tested with

## Scope

The README and CHANGELOG of every plugin of this marketplace that is a mod or contains one. Other plugins keep the rule that a README writes no version number.

## Context and problem statement

`.claude/CLAUDE.md` forbade any version number in a plugin README, and its Mods block put the Claude Code version a mod was validated on in the release's CHANGELOG entry only. The mods API changes between releases, often without a changelog entry. The official docs say: "The events and methods can change between releases, so your README is the place to say which Claude Code version you tested with" (`/en/plugins/mods/create` → Share your mod). Where should a mod state that version?

## Decision drivers

- Official guidance wins over project rules.
- A user reads the README before installing. The CHANGELOG is read after.
- One fact keeps one value: the README line and the CHANGELOG entry name the same version.

## Considered options

- **README and CHANGELOG**: one line in Compatibility, "Tested with Claude Code X.Y.Z", updated in every release, plus the same version in that release's CHANGELOG entry. Chosen.
- **CHANGELOG only**: rejected, because it goes against the official guidance and hides the version from a user deciding whether to install.

## Decision outcome

Chosen option: **README and CHANGELOG**, because it follows the docs and puts the version where a user looks before installing.

- `.claude/CLAUDE.md` → Plugin Documentation → README now allows this one version number (commit eac75f2).
- The `building-mods` skill, section 5, sets the line.

### Consequences

- Good, because users see on which build the mod was proven before they install it.
- Bad, because the line must change in every release of the mod, and nothing checks it yet.
- The four mods published today lack the line. Adding it is a README-only pull request, on Nery's order.

## More information

Decided by Nery on 2026-10-25 in this session. `plugin-versions-consistency.py` checks only the Version badge, so the line does not trip it (read on 2026-10-25).
