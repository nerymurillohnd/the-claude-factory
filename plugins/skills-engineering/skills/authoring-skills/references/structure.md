# Structure

How to lay out a skill's files so the model loads only what each run needs, and how `SKILL.md` points to the rest.

## Contents

- How a skill loads
- What goes where
- Decide what stays in SKILL.md
- Build the pointers in SKILL.md
- Inside a supporting file
- Size budgets
- Files that don't belong

## How a skill loads

Three levels, each loaded only when needed:

1. **Name and description**: always in context, about 100 tokens per skill.
2. **The `SKILL.md` body**: loaded when the skill is invoked. In Claude Code it then stays in the conversation as one message and is not re-read on later turns. After compaction Claude Code re-attaches only the first 5,000 tokens of each invoked skill, within 25,000 tokens shared from the most recent skill back.
3. **Supporting files**: cost nothing until the model reads one. A script the model runs costs only its output; its code never enters context.

So the body is a recurring cost on every turn after it loads, and supporting files are free until used. Design from that: what every run needs goes in the body, near the top if it must survive compaction; everything else goes in a file the body names, with when to read it.

## What goes where

A skill folder needs only `SKILL.md`. Add a supporting file when the skill needs it, never to fill a template:

- **`SKILL.md`**: the frontmatter, then what every run needs: the gotchas, the workflow or rules, and the pointers to the other files.
- **`references/`**: documentation the model reads into context: API details, schemas, domain rules, long examples, variant procedures. One topic per file.
- **`scripts/`**: code the model runs: deterministic, repeated or fragile operations. Read [scripts-and-hooks.md](scripts-and-hooks.md) before adding one.
- **`assets/`**: files used in the output, not read as instructions: templates, boilerplate, images, fonts, data files, schemas a script consumes.
- **A capitalized guide at the root**, such as `FORMS.md` or `REFERENCE.md`: the same role as a file in `references/`. Use the root for a skill with one to three such guides, each a distinct mode of the task (`FORMS.md` for form filling beside the text-extraction body). Use `references/` once there are more, or when they are variants of one topic.

Organize files by domain or variant so a task reads only its own: `references/finance.md`, `references/sales.md`, not `docs/file1.md`. Name each file for what it holds, such as `form_validation_rules.md`. Use forward slashes in every path, even on Windows.

Correct, split by variant:

```text
cloud-deploy/
├── SKILL.md            # shared workflow, then: read the file for your provider
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

Incorrect, split by size:

```text
cloud-deploy/
├── SKILL.md
└── references/
    ├── part1.md        # the model can't tell which part holds what it needs
    └── part2.md
```

## Decide what stays in SKILL.md

Split by how the content is used, not by how long it is:

- Keep in the body what every run needs and what must hold for the whole task: gotchas, the steps, the standing rules, the output format if it is short.
- Move to a file what only some runs need: a variant, an error catalog, a long template, an API reference, a domain the request may not touch.
- Move to a file content that is mutually exclusive with other content: two providers, two document types. The model then loads one and not the other.
- Keep together what is always used together; splitting it only adds a read.
- Keep in the body anything the model must know before it would think to look: a gotcha placed in a reference is read only after the mistake.

A large reference is free while unread. Bundle full API documentation, datasets or long example sets when the task may need them, except on surfaces with an upload size limit (30 MB on the Skills API).

## Build the pointers in SKILL.md

A file the body doesn't name is never read. Each pointer tells the model what the file holds and exactly when to read it.

1. Put the pointer at the step that needs the file, not in a list at the end. A closing list is acceptable only for files every step may need, such as a glossary.
2. One pointer per line, as a Markdown link to the path from the skill root.
3. Use the verb for what the model does with the file: **read** a reference, **run** a script, **fill in** or **copy** a template from `assets/`. Never "see" or "use" when the model must run the file.
4. State the condition that sends the model there, as a fact it can check: "if the API returns a non-200 status", "when the form has signature fields".
5. Say what the file holds when the file name doesn't make it obvious.

Correct:

```markdown
Read [references/api-errors.md](references/api-errors.md) if the API returns a non-200 status.

Run `python scripts/validate.py output/` after every edit; fix each reported error before continuing.

Fill in [assets/report.md](assets/report.md) for the final report.
```

Incorrect:

```markdown
For more details, see the references folder.
```

The model can't tell which file holds what, or when it is needed.

```markdown
When working with forms, which can be complex and have many field types such as text, checkboxes and signatures that each behave differently, it's important to consult [the forms guide](FORMS.md) along with the validation notes.
```

The pointer is buried in a paragraph, the condition is vague, and "the validation notes" names no file.

```markdown
See [advanced.md](advanced.md)       ← SKILL.md
See [details.md](details.md)         ← advanced.md
```

A chain: the model may preview `details.md` with a partial read and miss what it needs. Link every file directly from `SKILL.md`.

In Claude Code, an `@path` mention attaches the file to the prompt when the skill loads, so it costs tokens on every run and doesn't work in synced skills. Use a Markdown link so the model reads the file only when its condition holds.

## Inside a supporting file

- Keep every file one link away from `SKILL.md`. A reference may mention another reference only as a sibling that `SKILL.md` also links.
- Open any file over 100 lines with a table of contents, so a partial read still shows everything it covers.
- Start with one line on what the file is for, then sections in the order the model uses them.
- Write the same register as the body: instructions and facts, no restatement of `SKILL.md`.
- Spell every link exactly as the file is named, case included: Linux is case-sensitive.

## Size budgets

- Keep the body under 500 lines and about 5,000 tokens. Past that, move the content only some runs need into files.
- Put the instructions that must survive compaction in the first 5,000 tokens of the body.
- No budget applies to supporting files, but each one should cover one topic; split a file that serves unrelated tasks.

When the body is over budget, move content out in this order: long examples, variant procedures, reference tables and catalogs, background explanations (cut these first if the model already knows them).

## Files that don't belong

- A `README.md` for humans inside the skill folder. The model reads `SKILL.md`; human documentation belongs in the repository or plugin README.
- Copies of official documentation the model can read at its source. Point to the URL and say when to consult it.
- Build artifacts, caches, test outputs, `node_modules/` or virtual environments.
- Credentials, tokens or personal data.
- Files no pointer in `SKILL.md` names.
