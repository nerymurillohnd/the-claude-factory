---
paths:
  - "plugins/*/skills/**"
  - ".claude/skills/**"
---

# Skill Authoring Rules

## Plugin skills
Plugin skills ship to users.
- Description: what it does and when to use it, third person, at most about 500 characters, with specific trigger phrases.
- Body: headers, numbered steps and bullets; under 500 lines and about 5,000 tokens, following [agentskills.io best practices](https://agentskills.io/skill-creation/best-practices):
  - Each line is something the model would get wrong without it. The main path stays in `SKILL.md`; situational paths go to `references/` with a "read when …" trigger. Leave layout and rare cases to the model.
  - Be prescriptive only where the task is fragile (exact commands, sequences, formats); elsewhere state the goal and why.
  - Give one default with a short escape hatch, not a menu.
  - Include a short input and output example, and a template for any output that must keep its shape.
- Word guidance that needs judgment for the whole task ("after every edit", not "once").
- Links: from `SKILL.md`, relative to the skill folder; from a file under `references/`, relative to that file and only to templates, such as `[template](../assets/template.md)`. References never link to each other and stay one level deep.
- Use `${CLAUDE_PLUGIN_ROOT}/...` for other files of the plugin. Never reference a file outside the plugin, and never use `../` to leave the skill folder: the install copies only the plugin.
- Audit every plugin skill with `/skill-diagnostics:audit` after writing it and again after any rewrite: slimming can drop a load-bearing rule. Install the skill-diagnostics plugin from this marketplace when the command is missing.

## Project skills
Skills in `.claude/skills/` govern work on this repository only.
- Frontmatter holds only `name` and `description`: one sentence, at most 120 characters.
- Body, in this order: title; context in two or three sentences; role; rules; gotchas (only facts the model would get wrong without them); the workflow as a checklist with one short line per step; the details of each step.
- Be exact where the task is fragile (commands, sources, formats); where several methods work, state the goal and why. Write procedures, not declarations, and add a validation loop where the skill produces claims.
- Never write a `${CLAUDE_*}` variable literally in the body: Claude Code substitutes it when the skill loads.
- Pair every project skill with a row in `.claude/rules/skill-triggers.md`.
- Before relying on a skill, dry-run it with a read-only subagent on a realistic scenario and fix the gaps. A new skill loads only after the session restarts.
