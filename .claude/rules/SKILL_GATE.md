---
paths:
  - "**/skills/**"
  - "**/SKILL.md"
---

# Skill Gate

## Files Inside the Skill

- In a file under `references/`, link with a path relative to that file, and only to templates: `[template](../assets/template.md)`.
- Never link from one reference to another. Keep references one level deep from `SKILL.md`.

## Files Outside the Skill

- Project skill in `.claude/skills/`: use `${CLAUDE_PROJECT_DIR}/...`, such as `[rule](${CLAUDE_PROJECT_DIR}/.claude/rules/QUALITY_GATE.md)`.
- Skill inside a plugin: use `${CLAUDE_PLUGIN_ROOT}/...` for files of that plugin.
- Never reference a file outside the plugin from a plugin skill. The install does not copy it.
- Personal skill: use `${CLAUDE_SKILL_DIR}/...` for its own files.
- Skill synced from claude.ai: reference no file outside the skill.
- Never use `../` to leave the skill folder.
