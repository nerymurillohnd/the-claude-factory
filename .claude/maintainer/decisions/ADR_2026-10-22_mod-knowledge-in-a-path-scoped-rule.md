---
status: accepted
date: 2026-10-22
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# Mod knowledge lives in a path-scoped rule, not a skill

## Scope

Applies to `.claude/rules/mods.md`, its `paths`, and the pointers to it in `.claude/CLAUDE.md` and the `plugin-development` skill. The procedures in project skills (ADR_2026-10-20_procedures-live-in-project-skills) are unchanged.

## Context and problem statement

DEBT-005 produced about thirty verified facts about mods: the `tool.check` contract, the test kit, failure handling, loading and diagnosis, surfaces and copies of a plugin. A clean session would have to research them again. They are facts and constraints, not a procedure. Where should they live so that they are present whenever a mod is touched?

## Decision drivers

- The facts must load when Claude works on a mod's files, without depending on Claude choosing to load them.
- They cost context, so they should not load in sessions that never touch a mod.
- The live official docs win over the file, so it must name its sources and say so.

## Considered options

- **A path-scoped rule (`.claude/rules/mods.md`)**: chosen. Its `paths` follow Reference → Files: the manifest, `hooks/hooks.json`, the hooks module in every allowed extension, `types/index.d.ts`, tests, the engine's declarations and graders.
- **A project skill**: rejected because a skill loads when invoked or when Claude judges it relevant (Memory docs, "Organize rules with `.claude/rules/`"). The cost of a skill that did not load is the kind of mistake these facts prevent.
- **A section in `.claude/CLAUDE.md`**: rejected because it would load in every session.

## Decision outcome

Chosen option: **a path-scoped rule**, because it loads on Read, Write or Edit of a matching file, and only then.

### Consequences

- Good, because the facts and their sources reach every session that touches a mod.
- Bad, because the rule does not load while Claude plans before opening a mod file; `plugin-development` points to it for that case.
- Bad, because `plugin.json` and `hooks/hooks.json` exist in every plugin, so the rule also loads in sessions on plugins without a mod. Nery chose that coverage.

## More information

The rule says, at its top, that it was verified on 2026-10-22 and that the live sources win over it. Added in [PR #43](https://github.com/nerymurillohnd/the-claude-factory/pull/43). Related: ADR_2026-10-20_procedures-live-in-project-skills.
