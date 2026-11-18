# Phase 2: Embedding

Learn how code, commands, templates, schemas and Markdown go into the skill before you write anything. This file covers:

- commands and code
- templates
- JSON schemas
- Markdown

## Commands and code

- Put a command in a fenced block with its language tag. Pin versions in commands that fetch a package.
- Write each placeholder in square brackets and explain it on the line after the block.
- Show code only as long as the pattern needs: the call and its arguments, not a whole program.
- Write the path to a bundled script with the variable of its location. The scripts file has the forms.

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/to_csv.py [input-pdf] [output-csv]
```

`[input-pdf]` is the invoice to read. `[output-csv]` is the file to write.

## Templates

- Put a short template that every run uses inline, in a fenced block. Put a long one, or one used only in some cases, in `assets/` with a pointer that says when to fill it in.
- Each placeholder says what goes there. The body file says when a template is strict or flexible.

````markdown
Write the incident note in this structure:

```markdown
# [Service] incident, [date]

## Impact
[What failed, for whom, for how long]

## Cause
[The first change or event that led to it, with its evidence]
```
````

## JSON schemas

A schema is a template for structured data. Apply the same pattern:

- Show the schema in a fenced `json` block, with one line after it for each field that isn't obvious: its meaning and whether it is required.
- Show one filled example next to it.
- Put a long schema in `assets/` and point to it, saying when to read it.
- When a script produces or checks the data, say that the script is the check and show its command.

````markdown
Write the result as JSON:

```json
{ "invoice_id": "INV-0042", "total": 118.50, "currency": "USD", "lines": [] }
```

`total` is the sum of `lines`, in `currency`. `lines` is empty when no line items were found.
````

## Markdown

- Use headings, lists and tables only where they help the model find or follow something.
- Link a file with a relative path from the skill root: `[reference](references/guide.md)`.
- To show a fenced block inside a fenced block, open the outer one with four backticks.
- Write file paths with forward slashes.

Read [Common patterns](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#common-patterns) when you need the template and examples patterns.

Read [Specification](https://agentskills.io/specification#file-references) when you need the rules for referencing files.
