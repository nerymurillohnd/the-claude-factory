---
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
tags: [routing]
---

In a SvelteKit app with Tailwind 4, I put `@apply bg-primary px-4` inside the <style> block of Button.svelte and the build says it cannot apply unknown utility class bg-primary. bg-primary works fine in the markup. Why, and what is the recommended fix?
