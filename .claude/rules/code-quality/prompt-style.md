---
paths:
  - "**/skills/**"
  - "**/agents/**"
  - "**/commands/**"
---

# Prompt style

Write every skill, subagent and command, in a plugin or in `.claude/`, with these lists, layout and wording. `skill-style.md` and `agent-and-command-style.md` add the structure of each.

## Lists

- Number the steps of a sequence: `1.`, `2.`, `3.`.
- Bullet the actions, facts or options that have no order.
- Nest at most three levels: a step, its bullets, and their sub-bullets.

## Layout

- Leave one blank line around each heading or label, list, table and fenced block, and none between the items of a list.
- Write each paragraph, bullet and table row on one line, unwrapped. Keep the lines inside a fenced block within 100 characters, except a frontmatter value and a quoted message, which stay on one line.
- Use inline code for every path, field, command, file name and value.

## Wording

- Address Claude in the imperative, and call the person the work is for "the user".
- State each Claude Code behavior as it is now, with no Claude Code version number.
- Give the reason for an instruction instead of putting a word in capitals for emphasis.
