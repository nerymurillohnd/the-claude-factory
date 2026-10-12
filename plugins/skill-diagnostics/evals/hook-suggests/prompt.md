---
description: "Difference: a user who just wrote a skill and would not think to audit it. Hypothesis: without the plugin nothing is offered; with it, Claude offers /skill-diagnostics:audit and, under the default on_skill_write=suggest, does not run it unasked."
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
