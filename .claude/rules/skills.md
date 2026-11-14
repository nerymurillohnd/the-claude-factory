---
paths:
  - ".claude/skills/**"
  - "plugins/*/skills/**"
---

# Skills

- Write a project skill in `.claude/skills/` as a procedure that calls maintainer scripts through `npm run`; keep no scripts in its folder.
- Keep the scripts a plugin skill runs inside its own folder: users receive only `plugins/<plugin>/`.
- Name a project skill by its bare name in backticks, such as `docs-maintenance`, and a plugin skill with its prefix, such as `project-maintainer:write-records`.
- Write `/name` only where you tell the user what to type.
- Never set `disable-model-invocation: true` on a skill other skills load.
- Cite another skill by name, never a path inside its folder.
- Run `npm run lint:skills -- <skill folder>` after each change, and report each defect to the owner, one question per rule id, before fixing it or recording it as debt.
- Run the `skill-diagnostics:skills-best-practices` audit only when the owner asks for it.
