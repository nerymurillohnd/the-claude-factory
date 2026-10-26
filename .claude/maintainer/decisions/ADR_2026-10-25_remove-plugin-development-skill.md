---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Remove the plugin-development skill

## Scope

The project skill `.claude/skills/plugin-development/`. Out of scope: the skills that mentioned it, whose references were corrected separately.

## Context and problem statement

`plugin-development` guided writing any file of a plugin. Earlier on 2026-10-25 it was cut down to what the rebuilt skills did not cover yet: staging Nery's own versions of plugin files, the claude.ai sync gotcha, recalling the agent and MCP rules, skill naming, justifying a dependency, a `--plugin-dir` try, and hand-offs. Creating and writing a plugin is governed by `building-plugins`, which `.claude/rules/workflow.md` names for that stage. Should the remnant stay?

## Decision drivers

- One skill per stage, as `workflow.md` names it.
- New, validated skills outrank the older files, which adapt or go.

## Considered options

- **Remove the skill**: chosen.
- **Keep the remnant**: rejected because Nery ordered its removal. Not stated by the user beyond the order itself.

## Decision outcome

Chosen option: **Remove the skill**, on Nery's order (commit `88da8b1`).

### Consequences

- Good, because plugin work has one procedure, `building-plugins`.
- Bad, because its remaining items no longer live in a skill: staging Nery's files and the claude.ai sync gotcha remain only in project memory, and skill naming and dependency justification in no skill.

## More information

Nery gave the order on 2026-10-25 ("eliminar @.claude/skills/plugin-development"). The references to it in `plugin-hooks-guidance`, `building-plugins` and `.claude/rules/readme-md.md` were removed in later commits (`74f8df4`, `d95ea62`).
