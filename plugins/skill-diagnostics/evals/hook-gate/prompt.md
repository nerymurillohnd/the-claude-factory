---
description: "Gate mode (the default), cheap half, judge-free. The prompt asks for no check, so only the plugin's hooks can bring up the audit: after the Write, Claude must invoke skills-best-practices before it finishes (the PostToolUse context itself is not in the trace, so write-then-skill grades its effect), and the Stop gate must hold the turn and then release it with its warning, because this case grants no Bash and the audit can't record a verdict. Run with --allow-tools Write only. Plugin options can't be set in an eval run (no case field sets them, env keys must be EVAL_*, and the operator's CLAUDE_PLUGIN_OPTION_* doesn't reach the run), so every run is in the default gate mode; scripts/testers/skill-diagnostics/by_path.sh covers suggest and off. hook-gate-audit covers the full audit and the recorded verdict."
tags: [hook, gate, smoke]
max_turns: 8
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write]
---

Write the file skills/greet/SKILL.md with exactly the content of this code block (without the fence lines), then tell me you are done:

```markdown
---
name: greet
description: Writes a two-sentence welcome for a new teammate. Use when the user asks to welcome someone.
---

Write two friendly sentences that name the teammate and the team.
```
