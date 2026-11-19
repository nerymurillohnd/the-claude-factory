# Phase 2: Embedding

How to embed commands, calls to bundled scripts, templates and schemas in the skill, so Claude runs or fills them exactly as written.

## Gotchas

- A fenced block inside a fenced block closes the outer one at its first three backticks. Open the outer block with four.

## Commands and code

- Put each command in a fenced block with its language tag, such as `bash`.
- Write each placeholder in square brackets, and say what it is on the line after the block.
- Pin the version in a command that fetches a package.
- Show code only as long as the pattern needs: the call and its arguments, not a whole program.
- Call a bundled script through the path variable of its location, as the scripts file of Phase 2 shows.
- In `SKILL.md`, escape a literal dollar sign before a digit, and show a command you only mention without the exclamation mark in front of it.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/to_csv.py [input-pdf] [output-csv]
```

`[input-pdf]` is the invoice to read. `[output-csv]` is the file to write.

```markdown
<!-- Weak: in SKILL.md, the price becomes the first argument, and the shown command runs at load -->
Charge $1.00 per page. To see the changes, Claude Code runs !`git status`.

<!-- Strong -->
Charge \$1.00 per page. To see the changes, run `git status`.
```

## Templates

- Give a template when the output has a fixed shape: Claude follows a template more reliably than a description of the format.
- Say whether it is strict, "Use exactly this structure", or flexible, "This is the default; adapt the sections to what you find".
- Put a short template every run uses inline. Put a long one, or one only some runs need, in `assets/`, with a pointer that says when to fill it in.
- Make each placeholder say what goes there: `[what failed, for whom, for how long]`, not `[text]`.

````markdown
<!-- Weak: a description of the format, and placeholders that say nothing -->
Write a short incident note with the impact and the cause: [text], [text].

<!-- Strong -->
Write the incident note in exactly this structure:

```markdown
# [Service] incident, [date]

## Impact
[What failed, for whom, for how long]

## Cause
[The first change or event that led to it, with its evidence]
```
````

## Schemas

A schema is a template for structured data.

- Show it in a fenced `json` block, with one filled example, and a line after it for each field that isn't obvious: what it means and whether it is required.
- Put a long schema in `assets/` and point to it, saying when to read it.
- When a script produces or checks the data, say that the script is the check, and show its command.

```json
{ "invoice_id": "INV-0042", "total": 118.50, "currency": "USD", "lines": [] }
```

`total` is the sum of `lines`, in `currency`. `lines` is empty when no line items were found.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [Available string substitutions](https://code.claude.com/docs/en/skills#available-string-substitutions) when `SKILL.md` holds a dollar sign, an argument or a path variable. It lists each substitution and how to escape a literal dollar sign.
- Read [Inject dynamic context](https://code.claude.com/docs/en/skills#inject-dynamic-context) when a command must run as the skill loads. It shows both forms, how they run, and what aborts the skill.
- Read [Template pattern](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#template-pattern) and [Templates for output format](https://agentskills.io/skill-creation/best-practices#templates-for-output-format) when the output has a fixed shape. They show strict and flexible templates, inline and in `assets/`.
- Read [Provide utility scripts](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#provide-utility-scripts) when the skill embeds a call to a bundled script. It shows how to say whether Claude runs a script or reads it.
