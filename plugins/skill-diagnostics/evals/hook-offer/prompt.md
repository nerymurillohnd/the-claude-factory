---
description: "Case 2, first half: writing a SKILL.md fires the plugin's hook. The prompt asks for no check, so only the hook can bring up the audit: under the default on_skill_write=suggest Claude offers /skill-diagnostics:audit and does not run it. Without the plugin nothing is offered. hook-audit covers what follows once the user accepts."
tags: [hook]
max_turns: 10
allowed_tools: [Read, Skill]
---

Write the file skills/greet/SKILL.md with exactly the content of this code block (without the fence lines), then tell me you are done:

```markdown
---
name: greet
description: Writes a two-sentence welcome for a new teammate. Use when the user asks to welcome someone.
---

Write two friendly sentences that name the teammate and the team.
```
