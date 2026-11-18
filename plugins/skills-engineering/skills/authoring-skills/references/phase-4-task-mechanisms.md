# Phase 4: Task mechanisms

How to build each mechanism phase 3 chose: the steps and their controls, the checklists, the loop and its exit, the steps of plan, validate, execute, the template and the gotchas.

## Contents

- Workflows
- Checklists
- Validation loops
- Plan, validate, execute
- Output templates
- Gotchas

## Workflows

Build each step as one action, with its input, its command or method, and its output. Then add only the controls the step needs:

- **A gate** where a step must succeed before the next: "Don't continue until the check passes."
- **A decision point** where the path forks, with a condition the model can check and where each branch goes:

  ```markdown
  1. Check the supplier:
     - New supplier: follow "Add a supplier" below.
     - Existing supplier: follow "Update a supplier" below.
  ```

- **An exit condition** for each phase of a long workflow: what must be true before moving on.
- **A loop back** when a later step can reveal a gap: "If the totals don't match, return to step 2."

## Checklists

**A progress checklist**:

````markdown
Copy this checklist and check off each step as you finish it:

```text
- [ ] 1. Collect the month's invoices (run list_invoices.py)
- [ ] 2. Extract the line items (run to_csv.py on each)
- [ ] 3. Check the totals (run check_totals.py)
- [ ] 4. Map the accounts (edit accounts.json)
- [ ] 5. Write the journal (run build_journal.py)
```
````

**A verification checklist**:

Build each item to fail when the work is wrong:

- Name something observable: a file, a field, a count, a section.
- Say how to check it: the command to run, or where to look.
- Keep only items a bad output would fail.

Correct:

```text
- [ ] Every invoice in the month's folder has rows in out.csv (run check_totals.py --coverage).
- [ ] The journal's debits equal its credits, to the cent.
```

Incorrect, because both items pass whatever the output:

```text
- [ ] The output is high quality.
- [ ] All requirements are met.
```

## Validation loops

Give the loop its exit:

```markdown
1. Edit accounts.json.
2. Run `python3 scripts/check_accounts.py accounts.json`.
3. If it reports errors, fix each listed account and run it again.
4. Continue only when it passes.
```

When the bar is quality rather than a pass, add the rule that stops the loop: a number of rounds, or no gain over the last round. When the same error returns after a fix, stop and report it instead of looping.

## Plan, validate, execute

Build its steps:

1. Analyze the input.
2. Write the changes to a structured file, such as `changes.json`.
3. Validate the file: every target exists, nothing conflicts, nothing required is missing.
4. Apply the changes.
5. Verify the result.

Where the user must approve before anything changes, show them the plan file at step 3.

## Output templates

- Write each placeholder to say what goes there: `[what failed, for whom, for how long]`, not `[text]`.

````markdown
Write the incident note in this structure:

```markdown
# [Service] incident, [date]

## Impact
[What failed, for whom, for how long]

## Cause
[The first change or event that led to it, with its evidence]

## Follow-ups
- [Action, owner, due date]
```
````

## Gotchas

- Write each as the fact and what to do about it, in one or two lines.
- Add each correction its users have to make to the model.
- Leave out general advice: it isn't a gotcha unless a capable model would get it wrong.
