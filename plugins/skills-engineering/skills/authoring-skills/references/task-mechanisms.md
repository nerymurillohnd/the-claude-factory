# Task mechanisms

When a skill needs a workflow, a checklist, a validation loop, a plan checked before acting, an output template, or a gotchas list, and how to build each so it changes what the model does. Each one costs attention: use only the ones the task needs, and remove any the model wouldn't need to do its step reliably.

## Contents

- Name the task's parts
- Workflows
- Checklists
- Validation loops
- Plan, validate, execute
- Output templates
- Gotchas

## Name the task's parts

Most skills mix parts, and each part calls for different mechanisms:

- **Knowledge** the model applies to whatever it is doing, such as conventions or domain rules: rules and gotchas, rarely a workflow.
- **Ordered work**, where a later step depends on an earlier one: steps with gates.
- **Output in a fixed shape**, such as a report or a message: a template or examples, and a final check.
- **Destructive or outward actions**, such as deleting, deploying, sending or paying: a plan checked before acting, the user's confirmation where they must decide, and a dry run where one exists.
- **Work refined to a quality bar**: a validator and a rule for when to stop.

## Workflows

Write numbered steps when the order matters: a step uses what an earlier one produced, or skipping one breaks a later one. Write goals and criteria instead when the order depends on what the model finds, as in a review or an investigation.

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

Move a long branch or variant into its own file, and point to it from the decision point, so the model reads only the branch it takes.

## Checklists

Two tools for two failures.

**A progress checklist**, which the model copies into its reply and ticks as it works. Use it for a long workflow with dependencies or gates, where the model would lose its place among long tool outputs. Skip it for a short task: it adds ceremony and protects nothing.

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

**A verification checklist**, which the model checks its finished output against. Use it when the output can be wrong in ways the model doesn't notice while producing it. Build each item to fail when the work is wrong:

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

Do the work, run a validator, fix what it reports, and repeat until it passes. Use a loop where a step's errors are common and cheap to detect, so they are caught at the step that made them.

Choose the validator by what can check the result:

- **A script**, when the check is mechanical: a schema, a format, a cross-reference. Its errors name what to fix.
- **A document**, when the check is against written rules, such as a style guide.
- **A self-check against stated criteria**, when only judgment can check it. "Review your work" alone checks nothing.

Give the loop its exit:

```markdown
1. Edit accounts.json.
2. Run `python3 scripts/check_accounts.py accounts.json`.
3. If it reports errors, fix each listed account and run it again.
4. Continue only when it passes.
```

When the bar is quality rather than a pass, add the rule that stops the loop: a number of rounds, or no gain over the last round. When the same error returns after a fix, stop and report it instead of looping.

## Plan, validate, execute

For batch, destructive or costly work, have the model write the intended changes to a file, validate that file, and only then apply it:

1. Analyze the input.
2. Write the changes to a structured file, such as `changes.json`.
3. Validate the file: every target exists, nothing conflicts, nothing required is missing.
4. Apply the changes.
5. Verify the result.

The plan can be fixed and checked again without touching the originals. Where the user must approve before anything changes, show them the plan file at step 3.

## Output templates

Give a template when the output has a fixed shape: the model follows a template more reliably than a description of the format.

- **Strict** when a reader or a program depends on the exact shape: "Use exactly this structure."
- **Flexible** when the shape should adapt to the content: "This is the default; adapt the sections to what you find."
- **Inline** when it is short and every run uses it; **in `assets/`** when it is long or used only in some cases, with a pointer that says when to fill it in.
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

A gotcha is a fact of the environment or domain that defies a reasonable assumption, so the model gets it wrong unless told. Examples: the export whose amounts are in cents, the sandbox API that accepts any key but never sends email, the column named `customer` that holds a supplier ID.

- Put them in `SKILL.md`, before the steps they affect. The model must know them before it reaches the situation, and won't open a file about a mistake it doesn't know it is making.
- Write each as the fact and what to do about it, in one or two lines.
- Add each correction its users have to make to the model.
- Leave out general advice: it isn't a gotcha unless a capable model would get it wrong.
