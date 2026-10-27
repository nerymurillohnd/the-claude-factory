---
max_turns: 20
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
tags: [ui-trigger]
---

This "Start free trial" button gets lost next to the other links in our Tailwind 4 header. Make it stand out more.

```html
<nav class="flex items-center gap-6 text-sm text-gray-600">
  <a href="/pricing">Pricing</a>
  <a href="/docs">Docs</a>
  <a href="/login">Log in</a>
  <a href="/signup">Start free trial</a>
</nav>
```

Reply with the updated markup.
