---
paths:
  - "**/skills/**"
---

# Skill style

Write every file of a skill, in a plugin or in `.claude/skills/`, in this one style, so the files read alike and follow what `skills-engineering:authoring-skills` teaches.

## Headings and case

- Write every heading, phase name, standard label and link text in sentence case. Keep capitals for proper names, acronyms and code, and never put a word in capitals for emphasis.
- Give each file one `#` title, `Phase N: Topic` in a phase reference, then `##` sections and `###` subsections, no deeper than `####`.
- Write a numbered label as `1. Label: text`, with the label in sentence case.
- Use the target file's title as the text of a link to it, such as `[Phase 2: Skill location](references/phase-2-skill-location.md)`, not its path.

## Reference layout

- Order a reference file as: the `#` title; one sentence on what the file holds; `## Contents` with links to its sections when the file is over 100 lines; `## Gotchas`; the procedure sections; `## Official sources` last.
- Open `## Official sources` with "This file condenses these pages. Read the page whose condition holds before you decide", then one bullet per page: "Read [Title](url#anchor) when [condition]. It gives [what the page adds]." Check each anchor against the page before you commit it.
- Number the steps of a sequence, and bullet the actions or facts that have no order.

## Wording

- Address Claude in the imperative, and call the person who asks for the skill "the user".
- State each Claude Code behavior as it is now, with no Claude Code version number.
- Show examples as 3 or 4 weak and strong pairs in one fenced block, each labeled with a `# Weak:` or `# Strong` comment that says why.
