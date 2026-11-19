---
paths:
  - "**/skills/**"
---

# Skill style

Structure every file of a skill, in a plugin or in `.claude/skills/`, this way, on top of `prompt-style.md`, so the files read alike and follow what `skills-engineering:authoring-skills` teaches.

## Headings and case

- Write every heading, phase name, standard label and link text in sentence case. Keep capitals for proper names, acronyms and code.
- Give each file one `#` title, `Phase N: Topic` in a phase reference, then `##` sections and `###` subsections. Go no deeper: group the content inside a `###` under a bold label on its own line, such as `**A. Identify environment and components**`, and use bold for nothing else.
- Letter with capitals the parallel parts or scenarios a step chooses between: `Scenario A`, `**A. …**`. Use no lowercase letters.
- Write a numbered label as `1. Label: text`, with the label in sentence case.
- Link every file of the skill from `SKILL.md`, with a Markdown link whose path is relative to the skill's folder and whose text is the file's title, such as `[Phase 2: Skill location](references/phase-2-skill-location.md)`, not a bare path. Claude may read only part of a file it reaches through another reference, whether that file sits beside it or deeper. The level counts hops from `SKILL.md`, not folders: a file at the skill's root and one in `references/` are both one level deep when `SKILL.md` links them.
- In a reference file, including a supporting file at the skill's root, name another file of the skill in plain text, such as "the hooks file of Phase 2", and only one that `SKILL.md` already links: Claude still reaches it in one step from `SKILL.md`, while a link would start a second one.
- Name a supporting file at a skill's root in capitals, such as `WORKFLOW.md` or `CHECKLIST.md`, and the files in `references/` in lowercase.
- In a skill whose work runs in phases, give each reference one phase and one topic, named with both, such as `phase-2-hooks.md`, and split a topic two phases use by phase; list each phase's files under that phase in `SKILL.md`, in the order of the steps that read them, and tell Claude to read them in that order.

## Reference layout

- Order a reference file as: the `#` title; one sentence on what the file holds; `## Contents` with links to its sections when the file is over 100 lines; `## Gotchas`; the procedure sections; `## Official sources`; `## Exit` last, with the condition that closes the file and a return to the step list in `SKILL.md`.
- Open `## Official sources` with "This file condenses these pages. Read the page whose condition holds before you decide", then one bullet per page: "Read [Title](url#anchor) when [condition]. It gives [what the page adds]." Check each anchor against the page before you commit it.
- Show examples as 3 or 4 weak and strong pairs in one fenced block, each labeled with a Weak or Strong comment that says why, in the block's own comment syntax: `<!-- Weak: … -->` in Markdown, where a `#` line reads as a heading, and `# Weak: …` in YAML or shell.
