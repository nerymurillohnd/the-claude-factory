# Writing patterns

The rules for writing a skill's description and its instructions, with correct and incorrect pairs and the reason each difference matters, and how to write the examples and command snippets a skill embeds. Write your own examples from the skill's domain: an example taken from documentation teaches its domain, not the skill's.

## Contents

- Descriptions
- Pointers
- Register
- Instructions
- Examples and snippets
- Anti-patterns

## Descriptions

- Write what the skill does in its key use case first. Then "Use when", with the situations and the words its users actually say, including requests that never name the domain. Then the boundary with any sibling skill that shares its keywords.
- Write it in the third person.
- Leave out a summary of the workflow, which the model may follow instead of the body, and any claim of quality.
- Keep it within 1,024 characters for a skill that may leave Claude Code. Claude Code's skill listing cuts the text at 1,536.
- Write placeholders in square brackets: angle brackets show as escaped text.

Vague, so it triggers on everything or nothing:

```yaml
description: Handles invoices.
```

Specific about what it does and when:

```yaml
description: Extracts line items, totals and tax from supplier invoices in PDF or image form and exports them to CSV. Use when the user shares an invoice, asks to digitize receipts, or needs invoice data in a spreadsheet.
```

Mechanics instead of intent, so it matches no request a user would type:

```yaml
description: Runs parse_csv.py, then aggregate.py, then renders report.md from the template.
```

Intent, in the users' words, including a request that never names the domain:

```yaml
description: Builds the weekly sales report from the CRM export. Use when the user asks for this week's sales numbers, a sales summary or the regional report, even if they only paste a CSV.
```

Overlapping a sibling skill, so the model picks either one:

```yaml
description: Works with pull requests.
```

With the boundary that separates it:

```yaml
description: Reviews a pull request's code for bugs and style. Use when the user asks to review, check or comment on a PR. Not for merging or fixing CI, which pr-lifecycle does.
```

## Pointers

Correct: on its own line, at the step that needs it, with its verb and a condition the model can check:

```markdown
Read [references/rate-limits.md](references/rate-limits.md) if the API answers 429.

Run `python3 scripts/check_totals.py out/` after every export, and fix each row it reports before you continue.

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
- Give the reason only where it decides a case the line doesn't name.
- No narration, and no capitals for emphasis.
- Use one term per concept, no time-sensitive wording, and lists over tables.
- State each fact in one file only.

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
Export with the accounting system's CSV importer. For systems without one, write the journal file from assets/journal.csv.
```

A menu, which the model resolves differently on each run:

```markdown
You could use the CSV importer, the API, a manual journal entry or a spreadsheet macro.
```

An action with its condition and fallback:

```markdown
Run `python3 scripts/check_totals.py invoices.csv`. If it fails, the error names the row and the column: fix that value and run it again.
```

An instruction with no way to act or check:

```markdown
Make sure the data is valid before you continue.
```

## Examples and snippets

Add an example only where the output depends on seeing it: a tone, a level of detail, a format. The model imitates examples closely, including their accidents.

- Show input and output pairs, then a rule line that says what to imitate.
- Give two or three examples that differ where the output varies, so the model learns the pattern rather than one instance.
- Put commands in a fenced block with the language tag, versions pinned, and each placeholder in square brackets saying what goes there: `python3 scripts/to_csv.py [invoice.pdf] [out.csv]`.
- Show code only as long as the pattern needs: the call and its arguments, not a whole program.
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

Each with what to write instead.

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
