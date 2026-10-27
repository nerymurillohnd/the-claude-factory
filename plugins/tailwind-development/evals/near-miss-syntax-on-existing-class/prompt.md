---
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
tags: [near-miss]
---

In our Tailwind 4 project, `md:p-6` on this div never applies at any width, even though `p-2` works:

```html
<div class="p-2 md-p-6 rounded bg-white">…</div>
```

Why, and what is the fix?
