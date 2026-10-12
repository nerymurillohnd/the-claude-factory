---
description: "Trigger conflict: after a SKILL.md is written, the hook makes Claude offer /skill-diagnostics:audit without running it (default on_skill_write=suggest)."
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
