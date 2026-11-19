# Phase 2: Style and format

How to lay out the text of every file of the skill: headings, lists, checklists, tables, pointers, links and line layout. Use these as the default, and follow the user's own conventions instead when the environment shows them.

## Contents

- [Gotchas](#gotchas)
- [Headings and case](#headings-and-case)
- [Lists and checklists](#lists-and-checklists)
- [Tables](#tables)
- [Pointers to files](#pointers-to-files)
- [Links to web pages](#links-to-web-pages)
- [Layout](#layout)
- [Official sources](#official-sources)

## Gotchas

- The skill's formatting can carry into what Claude writes with it: removing Markdown from a prompt reduces the Markdown in the output. Format the skill the way its output should look.
- Claude may read only part of a file it reaches through another reference instead of from `SKILL.md`: link every file from `SKILL.md`. The level counts hops, not folders, so `FORMS.md` at the root and `references/forms.md` are both one level deep.

## Headings and case

- Give each file one `#` title, then `##` sections and `###` subsections. Group the content inside a `###` under a bold label on its own line, not a `####`.
- Write headings and labels in sentence case. Keep capitals for proper names, acronyms and code, and never for emphasis.
- Open each reference file with its title, then one sentence on what it holds, and a `## Contents` list of links to its sections when it is over 100 lines.

```markdown
<!-- Weak: capitals for emphasis, a fourth level, and a title that says nothing -->
# REFERENCE
#### IMPORTANT STEPS

<!-- Strong -->
# Invoice exports
**A. Monthly export**
```

## Lists and checklists

- Number the steps of a sequence. Bullet the actions, facts or options that have no order.
- Letter with capitals the parallel parts or scenarios a step chooses between, such as `Scenario A`.
- Nest at most three levels: a step, its bullets, and their sub-bullets.
- Write a checklist, or a to-do list whose every item must be done, as task items that open with an empty box, so Claude copies it and ticks each item.

```markdown
<!-- Weak: bullets for an ordered procedure, and a checklist Claude can't tick -->
- Export the invoices
- Check the totals
Make sure everything is done.

<!-- Strong -->
1. Export the invoices.
2. Check the totals.

- [ ] The CSV has one row per line item.
- [ ] The totals match the PDF, to the cent.
```

## Tables

- Use a table for facts that compare along the same columns, such as options and their effects. Keep prose for a sequence or a reason.
- Write each cell as wide as its text, with `| :-- |` separators, and no padding to align the columns.

```markdown
<!-- Weak: padded to look aligned -->
| Field      | Meaning              |
| ---------- | -------------------- |
| `total`    | Sum of the lines     |

<!-- Strong -->
| Field | Meaning |
| :-- | :-- |
| `total` | Sum of the lines |
```

## Pointers to files

- Point to each file at the step that needs it, at the start of the sentence, with its verb and a condition Claude can check: `Read [Title](path) when…`, `See [Title](path) to…`, `Fill in [Title](path) for…`.
- Keep each pointer on its own line in `SKILL.md`. Use a Markdown link whose path is relative to the skill's folder and whose text is the file's title.
- In a skill whose work runs in phases, list each phase's files under that phase in `SKILL.md`, in the order of the steps that read them, each with its step and condition, and tell Claude to read them in that order.
- In a reference file, name another file of the skill in plain text, such as "the hooks file of Phase 2", and only one that `SKILL.md` already links: Claude still reaches it in one step from `SKILL.md`, while a link would start a second one. This holds for a supporting file at the skill's root, such as `WORKFLOW.md`, as for one in `references/`.
- A reference file may tell Claude to run a script: a script runs without being read, so it adds no level. How the command reaches the script is in the scripts file of Phase 2.
- Point to a file, not a folder. Leave out an at-mention such as `@references/guide.md`: it loads the file on every run.

```markdown
<!-- Weak: a folder, a link buried in a sentence, and no condition -->
For more details, see the references folder, and keep the [layouts guide](LAYOUTS.md) in mind.

<!-- Strong -->
Read [Invoice layouts](references/invoice-layouts.md) when an invoice is a scan or spans several pages.

<!-- Weak: in references/forms.md, a link that reaches the field rules only through this file -->
Before you fill a field, see [Field rules](field-rules.md).

<!-- Strong: in references/forms.md, and SKILL.md links the field rules file -->
Before you fill a field, check it against the field rules file.

<!-- Weak: in SKILL.md, only the root file is linked, so the field rules sit two levels deep -->
Follow [Workflow](WORKFLOW.md) when you fill a PDF form.

<!-- Strong: in SKILL.md, the root file and the file it sends Claude to, both one level deep -->
Follow [Workflow](WORKFLOW.md) when you fill a PDF form.
Read [Field rules](references/field-rules.md) when the workflow asks you to check a field.
```

## Links to web pages

- Link a page with a Markdown link whose text is the page or section title and whose URL is the full `https://` address with the section's anchor.
- Check that the anchor exists on the page: a heading's anchor can differ from its title.
- Write no bare URL.

```markdown
<!-- Weak: a bare URL to the top of a long page -->
See https://code.claude.com/docs/en/skills for the fields.

<!-- Strong -->
Read [Frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference) when you set a field.
```

## Layout

- Leave one blank line around each heading, list, table and fenced block, and none between the items of a list.
- Write each paragraph, bullet and table row on one line. Aim for 100 characters per line of code in a fenced block, such as a command, a script or a JSON or YAML line: it is a target, as formatters wrap on a best effort, not a hard cut. Break a line only where its language allows it, and never split a string, a URL, a command argument or a frontmatter value to fit. Prose and quoted messages inside a block stay on one line.
- Use bold only for a group label, and inline code for every path, field, command, file name and value.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [Control the format of responses](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#control-the-format-of-responses) when the skill's output must follow a format. It explains why a prompt's own style shapes the output, and how to steer Markdown and prose.
- Read [Avoid deeply nested references](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#avoid-deeply-nested-references) when one reference would point to another. It says how Claude previews a nested file and why every file links from `SKILL.md`.
- Read [Structure longer reference files with a table of contents](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#structure-longer-reference-files-with-table-of-contents) when a reference grows past 100 lines. It shows the contents list Claude uses to find a section.
- Read [Avoid Windows-style paths](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#avoid-windows-style-paths) when the skill names paths. It gives the forward-slash rule and why it holds on every system.
- Read [File references](https://agentskills.io/specification#file-references) when the skill must work in other Agent Skills clients. It gives the standard's rule for relative paths from the skill root.
