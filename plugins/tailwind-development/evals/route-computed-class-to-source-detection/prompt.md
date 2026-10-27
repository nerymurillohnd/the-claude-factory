---
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
tags: [routing]
---

My badge component does class={`bg-${color}-500 text-white`} with color coming from props (red, green, amber). In dev some colors show, but in the production build most badges have no background at all. Tailwind 4. What is going on and how should I fix it?
