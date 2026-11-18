# Phase 2: Writing patterns

Learn how to write the text of a skill before you write anything. This file covers:

- [Pointers to files](#pointers-to-files)
- [Register](#register)
- [Instructions](#instructions)
- [Examples](#examples)
- [Anti-patterns](#anti-patterns)

Write your own examples from the skill's domain: an example taken from documentation teaches its domain, not the skill's.

## Pointers to files

A pointer goes on its own line, at the step that needs the file, with a verb and a condition the model can check. Point to a file, never to a folder, and don't use an at-mention: it loads the file on every run. In a skill that works in phases, list each phase's files under that phase, in the order its steps read them.

Correct:

```markdown
Read [references/rate-limits.md](references/rate-limits.md) if the API answers 429.

Fill in [assets/summary.md](assets/summary.md) for the final summary.
```

Incorrect, because the model can't tell which file holds what, or when it is needed:

```markdown
For more details, see the references folder.
```

Incorrect, because the link is buried, the condition vague, and "the tax notes" names no file:

```markdown
When working with invoices, which can come in many layouts such as scans, multi-page PDFs and emails that each behave differently, it's important to consult [the layouts guide](LAYOUTS.md) along with the tax notes.
```

Incorrect, because the model may only preview the second file and miss what it needs:

```markdown
Read [auth.md](auth.md)        ← in SKILL.md
Read [tokens.md](tokens.md)    ← in auth.md
```

## Register

- Use the imperative: one action per line, with its condition and fallback, and concrete names instead of categories.
- Give a reason only where the model must judge, so it can decide the cases the line doesn't name. In a fixed step, say what to do without narrating why.
- No narration, and no capitals for emphasis.
- Use one term per concept and no time-sensitive wording.
- State each fact in one file only.
- State a prohibition as one sentence beside the instruction it limits, or as a gotcha. Don't write it as a correct and incorrect pair: the pairs in this file teach authors, not the model running a skill.

## Instructions

Adds what the model lacks:

```markdown
Read invoice dates as DD/MM/YYYY: the suppliers are in Central America. A date that only parses as MM/DD is a data-entry error; flag it, don't swap it.
```

Tells the model what it knows:

```markdown
Dates can be written in many formats around the world. It's important to parse dates carefully, because getting them wrong can cause problems.
```

A default with its exception:

```markdown
Export with the accounting system's CSV importer. For systems without one, write the journal file from [assets/journal.csv](assets/journal.csv).
```

A menu, which the model resolves differently on each run:

```markdown
You could use the CSV importer, the API, a manual journal entry or a spreadsheet macro.
```

An action with its condition and fallback:

```markdown
Run `python3 ${CLAUDE_SKILL_DIR}/scripts/check_totals.py invoices.csv`. If it fails, the error names the row and the column: fix that value and run it again.
```

An instruction with no way to act or check:

```markdown
Make sure the data is valid before you continue.
```

Freedom matched to each step's fragility, from many valid approaches to one exact sequence:

```markdown
Review the line items for amounts that look out of place, and list each with the reason.

Run `python3 ${CLAUDE_SKILL_DIR}/scripts/to_csv.py [input-pdf] [output-csv]`, where `[input-pdf]` is the invoice and `[output-csv]` the file to write.

Run exactly `python3 ${CLAUDE_SKILL_DIR}/scripts/post_journal.py --dry-run`. Don't add flags.
```

## Examples

Add an example only where the output depends on seeing it: a tone, a level of detail, a format.

- Show input and output pairs, then a rule line that says what to imitate.
- Give two or three examples that differ where the output varies, so the model learns the pattern and not one instance.
- When the output drifts across runs, sharpen the instruction that allows it instead of adding an example for the case that failed.
- Keep an example inline when it is short and every run needs it. Put it in a file when it is long or only some runs need it, with a pointer that says when to read it.

````markdown
Write each changelog line like these:

Input: PR "Add CSV export to the invoices page" (label: feature)
Output:
```text
- Added CSV export on the invoices page.
```

Input: PR "Fix rounding of tax on multi-currency invoices" (label: bug)
Output:
```text
- Fixed tax rounding on invoices with more than one currency.
```

Follow this style: past-tense verb, what changed for the user, one line, no PR jargon.
````

## Anti-patterns

General knowledge:

```markdown
Incorrect: Git is a version control system. Commits record changes.
Correct:   Commit with `git commit -s`: this repository requires sign-off.
```

Catch-all advice:

```markdown
Incorrect: Handle errors appropriately and follow best practices.
Correct:   On a 429, wait the seconds in the Retry-After header, then retry once.
```

Time-sensitive wording:

```markdown
Incorrect: Until the migration finishes next quarter, use the old endpoint.
Correct:   Use api.example.com/v2/invoices.
```

Two terms for one concept:

```markdown
Incorrect: Extract the line items ... then total the rows ... then check each entry.
Correct:   Extract the line items ... then total the line items ... then check each line item.
```

A rule after the step it governs:

```markdown
Incorrect: 3. Write the file.  ...  7. Note: never overwrite existing files.
Correct:   3. Write the file under a new name; never overwrite an existing one.
```

Standing guidance written as one step:

```markdown
Incorrect: 5. Run the tests.
Correct:   Run the tests after every edit.    (near the top, before the steps)
```

Emphasis instead of a reason:

```markdown
Incorrect: ALWAYS CHECK THE TOTALS!!!
Correct:   Check that the totals match before you export: a mismatch means a line item was missed.
```

Read [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices#patterns-for-effective-instructions) when you need more instruction patterns.

Read [Common patterns](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#common-patterns) when you need the examples pattern.
