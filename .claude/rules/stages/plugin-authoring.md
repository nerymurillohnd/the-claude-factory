---
paths:
  - "plugins/**"
  - ".claude/templates/plugin/**"
---

# Plugin authoring rules

## Skills inside plugins

- Description: what it does + when to use it, third person, ≤ ~500 characters, specific trigger phrases.
- Body: headers, numbered steps, bullets; under 500 lines and ~5,000 tokens. Follow [agentskills.io best practices](https://agentskills.io/skill-creation/best-practices):
  - Moderate detail: each line must be something the model would get wrong without it. The main path stays in `SKILL.md`; situational paths go to `references/` with a "read when …" trigger. Leave layout and rare cases to the model.
  - Prescriptive only where the task is fragile (exact commands, sequences, formats); elsewhere state the goal and why.
  - Defaults, not menus: one default with a short escape hatch.
  - A short input/output example; a template for output that must keep its shape.
- Word guidance that needs judgment for the whole task ("after every edit", not "once").
- Audit our own skills with `/skill-diagnostics:audit`, and re-audit after any rewrite: slimming can drop a load-bearing rule.

## Hooks and scripts

- Scripts start with `#!/usr/bin/env <interpreter>` (no version), are committed as `100755`, and are called by path (`${CLAUDE_SKILL_DIR}` or `${CLAUDE_PLUGIN_ROOT}`).
- Network calls only when the plugin's purpose requires them and the README discloses them.
