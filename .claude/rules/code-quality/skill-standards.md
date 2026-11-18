---
paths:
  - "**/skills/**"
  - "**/agents/**"
---

# Skill and subagent standards

Write and edit every skill with `skills-engineering:authoring-skills`; these are the owner's criteria on top of it.

## Before and after an edit

- Before writing or editing a skill or subagent, understand what it is for: its goal, its users and how it is invoked.
- Read each file you will edit in full before changing it, and read the whole file again after the change.

## Skills

- Prioritize progressive disclosure: keep in `SKILL.md` what every run needs, and move the rest to reference files linked directly from `SKILL.md`, one level deep.
- Keep the `SKILL.md` body under about 5,000 tokens.
- Use examples where they change the output, and embed each command, template, snippet or quote in its proper form: a fenced block with its language, a template file in `assets/`, a quote marked with its source.
- Keep the scripts a plugin skill runs inside its own folder, because users receive only `plugins/<plugin>/`; write a project skill in `.claude/skills/` as a procedure that calls maintainer scripts through `npm run`.
- Never set `disable-model-invocation: true` on a skill that other skills or subagents load.

## Descriptions

- State explicitly and specifically what the skill or subagent covers and does: the more precise, the better Claude triggers it.
- Prefer opening with a "Use…" clause that says when to use it, for skills and subagents alike; write the rest in the third person.

## Subagents

- Write the body in plain language with a clear hierarchy, and no Markdown headings (`#`):
  - open with the role and its areas of expertise, then the `GOAL:` section;
  - mark every later section with an uppercase label, choosing the sections the subagent's kind of work needs;
  - use numbered steps for a sequence, and bullets for separate actions or facts.
- Model a new subagent on the `skills-engineering` reviewer agents.

## Names and checks

- In the frontmatter, write `name` as the bare name, with no backticks or plugin prefix: `name: write-records`.
- In prose, cite a project skill by its name in backticks, such as `docs-maintenance`, and a plugin skill with its prefix, such as `project-maintainer:write-records`.
- Run `npm run lint:skills -- <skill folder>` after each change, and report each defect to the owner, one question per rule id, before fixing it or recording it as debt.
