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
- Write a checklist, or a to-do list whose every phase must be completed, as task items that open with an empty box: `- [ ] Phase 1: Understand the user's intent`.

## Layout

- Leave one blank line around each heading or label, list, table and fenced block, and none between the items of a list.
- Write each paragraph, bullet and table row on one line, unwrapped. Keep each line of code in a fenced block, such as a command, a script or a JSON or YAML line, within 100 characters. Prose, a frontmatter value or a quoted message inside a block stays on one line.
- Use inline code for every path, field, command, file name and value.

## Pointers and links

- Put each pointer to a file or a page at the start of the sentence that uses it, with its verb, such as "Read [Phase 2: Body](references/phase-2-body.md) when…", "See […](…) to…" or "For writing descriptions, read […](…)", and keep it on its own line, not inside a paragraph.
- Link a web page with a Markdown link whose text is the page or section title and whose URL is the full `https://` address with the section's anchor, such as `[Control who invokes a skill](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill)`. Check the anchor against the page, and write no bare URL.

## Wording

- Address Claude in the imperative, and call the person the work is for "the user".
- State each Claude Code behavior as it is now, with no Claude Code version number.
- Give the reason for an instruction instead of putting a word in capitals for emphasis.
