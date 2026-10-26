---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-22_mod-knowledge-in-a-path-scoped-rule
superseded-by: none
---

# The building-mods skill holds how a mod is built

## Scope

What this project tells Claude about creating, scaffolding, editing and documenting a mod: a plugin whose `hooks/hooks.json` lists a hooks module under `modules`. Testing and troubleshooting a mod stay in the `testing-mods` skill. The catalog rule on the `mods` category stays in `.claude/CLAUDE.md`.

## Context and problem statement

ADR_2026-10-22_mod-knowledge-in-a-path-scoped-rule put mod knowledge in `.claude/rules/mods.md`. That rule was later removed, and its authoring part moved into `.claude/CLAUDE.md` → `## Mods`, about 60 bullets that loaded in every session. On 2026-10-25 a review against the changelog (2.1.295 to 2.1.310, read raw), the ten mods docs pages, the built-in `plugin-authoring` skill and the 2.1.310 declarations found that the block mixed four things:

- facts the docs and `plugin-authoring` already state;
- lessons observed live here;
- project decisions;
- three wrong statements:
  - `agent.spawn` runs on resume since 2.1.299;
  - `--safe-mode` stops every plugin, not only the mod;
  - validate's `hooks:` and `calls:` lines are cut and are not a full inventory.

Nothing told a session to start from the tools Claude Code ships for mods. Where should the project's mod guidance live, and what should it hold?

## Decision drivers

- What Claude Code ships for mods, the built-in `plugin-authoring` skill and the installed build's declarations, is current for the installed build and comes first.
- Instructions loaded in every session should hold only what applies to every session.
- Creating a mod and testing a mod are separate stages of `.claude/rules/workflow.md`.
- Only what is true and actionable today, for mods published from a public GitHub marketplace, is kept.

## Considered options

- **A `building-mods` skill that puts the native tools first and holds only the project's verified decisions and lessons, with the mod block removed from CLAUDE.md**: chosen.
- **Keep the `## Mods` block in CLAUDE.md, corrected**: rejected, because it loads in every session and repeats what `plugin-authoring` and the docs state.
- **Fold authoring into `testing-mods`**: rejected, because building and testing are separate stages with separate triggers.

## Decision outcome

Chosen option: **a `building-mods` skill**, because it routes each case to the native tool and leaves the project only what nothing else decides.

- `.claude/skills/building-mods/SKILL.md` (commit c7d956a) holds:
  - the native tools;
  - where this marketplace departs from `plugin-authoring` (where a mod is written, how it is shared);
  - a decision per case;
  - the minimum versions from the changelog;
  - the lessons verified live;
  - what a mod's README discloses.
- `.claude/CLAUDE.md` drops `## Mods` and the Plugin Tooling line on `claude plugin test` (commit eac75f2). `.claude/rules/workflow.md` → Plugin creation routes mod work to the skill.

### Consequences

- Good, because a session that builds a mod starts from what the installed build ships, and every other session no longer loads mod rules.
- Good, because the three wrong statements are gone.
- Bad, because the skill copies minimum versions and live lessons that drift with each release; it states which source wins and asks to be corrected when it loses.

## More information

Decided by Nery on 2026-10-25, after approving the research and the plan in this session. Revisit after a Claude Code release that changes how mods are written, loaded or shared, or when `plugin-authoring` covers what the skill's own sections hold.
