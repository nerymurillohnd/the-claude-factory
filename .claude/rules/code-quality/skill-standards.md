---
paths:
  - ".claude/skills/**"
  - "plugins/*/skills/**"
---

# Skill standards

## Placement and names

- Write a project skill in `.claude/skills/` as a procedure that calls maintainer scripts through `npm run`; keep no scripts in its folder.
- Keep the scripts a plugin skill runs inside its own folder: users receive only `plugins/<plugin>/`.
- Name a project skill by its bare name in backticks, such as `docs-maintenance`, and a plugin skill with its prefix, such as `project-maintainer:write-records`.
- Write `/name` only where you tell the user what to type.
- Never set `disable-model-invocation: true` on a skill other skills load.
- Cite another skill by name, never a path inside its folder.

## Content

- Add an instruction only where Claude would act differently without it; cut what Claude already does.
- Put the gotchas in `SKILL.md`, before the instructions: environment-specific facts that defy reasonable assumptions. Add each correction you have to make to Claude to that list.
- Leave out information that will become outdated, such as counts and "today"; put a deprecated method under an "Old patterns" section, if anywhere.
- Where output quality depends on seeing examples, add an input and output pair for each case.
- Use lists, not tables.
- Use one term for each thing throughout the skill.
- State each fact once, and keep each phase's instructions in that phase.
- Base every fact on the official documentation. Where it lags, the installed binary (`--help`, real output) and the changelog win; mark each fact taken from them as such.
- Put each CLI command, flag and message at the step that uses it, not in a separate list.
- Use a script only for deterministic, repeated logic, such as a fixture run, and say whether Claude runs it or reads it; keep a judgment step as instructions.

## Size and references

- Keep the `SKILL.md` body under 500 lines, and move detail to reference files.
- Link every reference file directly from `SKILL.md`, one level deep, and say there what each file holds and when to read it.
- Split reference files by domain or task, and give each one longer than 100 lines a table of contents at the top.

## Description

- Write it in third person, stating what the skill does and when to use it.
- Put the key use case first, in the words users would naturally say: Claude Code cuts `description` plus `when_to_use` at 1,536 characters, and `description` takes at most 1,024.

## Checks

- Run `npm run lint:skills -- <skill folder>` after each change, and report each defect to the owner, one question per rule id, before fixing it or recording it as debt.
- Run the `skill-diagnostics:skills-best-practices` audit only when the owner asks for it.
