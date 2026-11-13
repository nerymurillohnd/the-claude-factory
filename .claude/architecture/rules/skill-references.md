---
paths:
  - ".claude/skills/**"
  - "plugins/*/skills/**"
---

# Referencing other skills from a skill

Claude loads another skill through the Skill tool, which takes the skill's name with no leading slash; `/name` is what a user types.

- Name a project skill by its bare name in backticks: "write the entry with the `docs-maintenance` skill".
- Name a plugin skill with its plugin prefix: `project-maintainer:write-records`.
- Write `/name` only where the instruction tells the user what to type, such as `/plugin install …`.
- Never set `disable-model-invocation: true` on a skill that other skills load: Claude could no longer invoke it through the Skill tool.
- Cite the skill, never a file path inside another skill's folder: the skill knows which reference to open, and a path that leaves the skill's folder fails `npm run lint:skills` (CO-08).
