---
paths:
  - "**/agents/**"
  - "**/commands/**"
---

# Agent and command style

Write the body of every subagent and command, in a plugin or in `.claude/`, as a prompt in natural language with a clear hierarchy, on top of `prompt-style.md`, modeled on the `skills-engineering` reviewer agents. Its frontmatter keeps the checks `markdown.md` sets for every agent and command.

- Write no Markdown headings (`#`) and no bold or italic: a prompt's structure comes from labels and lists.
- Open every subagent with the same three parts, in this order, as the `skills-engineering` reviewer agents do: its role, in a paragraph that names what it knows and its focus; its expertise, as `Your expertise:` with a bullet per area; and its goal, in the `GOAL:` section, with the purpose it must reach.
- In a command, open with one sentence on what the command authorizes and does, then its sections.
- Mark each later section with an uppercase label on its own line, followed by a colon, such as `GOTCHAS:`, `WORKFLOW:`, `RULES:` or `REPORT:`, and choose the sections the kind of work needs. These labels are the only words in capitals.
