# Task mechanisms

When a skill needs a workflow, a checklist, a validation loop, a plan to validate before acting, an output template or a gotchas list, and how to build each so it changes what the model does. Use only the mechanisms the task needs: each one costs context and attention.

## Contents

- Recognize the task
- Workflows
- Checklists
- Validation loops
- Plan, validate, execute
- Output templates
- Gotchas
- Task tracking
- Choose the smallest set

## Recognize the task

Most skills mix parts. Name each part, because each calls for different mechanisms:

- **Reference**: knowledge applied to whatever the model is doing. Needs rules and gotchas; rarely a workflow.
- **Workflow**: steps in an order, where a later step depends on an earlier one. Needs ordered steps and gates.
- **Output-producing**: a document, report, message or file in a fixed shape. Needs a template or examples, and a final check.
- **Destructive or remote**: deletes, overwrites, deploys, sends, pays, writes to an external system. Needs a plan checked before acting, explicit confirmation where the user must decide, and a dry run where one exists.
- **Iterative**: refined until a quality bar is met. Needs a validator and a stopping rule.

## Workflows

Write numbered steps when the order matters: a step consumes what an earlier one produced, or skipping one breaks a later one.

Write goals and criteria instead when the order doesn't matter or depends on what the model finds: a review, an investigation, a design.

How to build a workflow:

1. One step per action the model takes, with its input, its command or method, and its output.
2. A gate where a step must succeed before the next: "Don't continue until the validator passes."
3. A decision point where the path forks, with each condition the model can check and where each branch goes:

```markdown
1. Check the supplier:
   - New supplier? Follow "Add a supplier" below.
   - Existing supplier? Follow "Update a supplier" below.
```

4. An exit condition for each phase in a long workflow: what must be true before moving on.
5. A loop back when a later step reveals a gap: "If verification fails, return to step 2."

Move a large branch or variant into its own file and point to it from the decision point, so the model reads only the branch it takes.

## Checklists

Two different tools. Use each only for its failure.

**Progress checklist**, which the model copies into its response and ticks as it works. Use it when a workflow is long, has dependencies or gates, and the model skips steps in test runs. It keeps the model's place through long tool output.

````markdown
Copy this checklist and check off each step as you complete it:

```text
- [ ] 1. Collect the month's invoices (run list_invoices.py)
- [ ] 2. Extract the line items (run to_csv.py on each)
- [ ] 3. Check the totals (run check_totals.py)
- [ ] 4. Map accounts (edit accounts.json)
- [ ] 5. Write the journal file (run build_journal.py)
```
````

Skip it for short tasks or tasks without order: it adds ceremony and no protection.

**Verification checklist**, which the model checks its finished output against. Use it when the output can be wrong in ways the model doesn't notice while producing it. Build each item so it fails when the work is wrong:

- Name something observable in the output: a file, a field, a count, a section.
- Say how to check it: the command to run, the place to look.
- Make it discriminate: an item that passes for a bad output is noise.

Correct:

```text
- [ ] Every invoice in the month's folder has rows in out.csv (run check_totals.py --coverage).
- [ ] The journal's debits equal its credits, to the cent.
```

Incorrect:

```text
- [ ] The output is high quality.
- [ ] All requirements are met.
```

The incorrect items pass whatever the output, so they verify nothing.

## Validation loops

The loop: do the work, run a validator, fix what it reports, repeat until it passes. It catches errors at the step that made them, instead of in the final output. Use it where a step's errors are common and cheap to detect.

Choose the validator by what can check the result:

- **A script**, when the check is mechanical: a schema, a format, a cross-reference. Most reliable. Its errors should name what to fix.
- **A reference document**, when the check is against written rules: a style guide, a policy. The model compares its output with the document.
- **A self-check with stated criteria**, when only judgment can check it. State the criteria; "review your work" alone checks nothing.

Write the loop with its exit:

```markdown
1. Edit `accounts.json`.
2. Run `python3 scripts/check_accounts.py accounts.json`.
3. If it reports errors, fix each listed account and run it again.
4. Continue only when it passes.
5. Build: `python3 scripts/build_journal.py out.csv accounts.json journal.csv`.
```

For iterative refinement, add a stopping rule so the loop ends: a pass from the validator, a number of rounds, or no gain over the last round.

## Plan, validate, execute

For batch, destructive or high-stakes work, have the model write its plan to a file, validate the plan, and only then apply it:

1. Analyze the input.
2. Write the intended changes to a structured file, such as `changes.json`.
3. Validate that file with a script: every target exists, no conflicts, nothing required is missing.
4. Apply the changes.
5. Verify the result.

The plan can be fixed and re-checked without touching the originals, and a validator's error points at one entry. Use it whenever an error would be expensive to undo: updating 200 supplier records from a spreadsheet, renaming across a codebase, migrating data. Where the user must approve before anything changes, show them the plan file at step 3.

## Output templates

Give a template when the output has a fixed shape: a template is followed more reliably than a description of the format.

- **Strict** when a reader or program depends on the exact shape (an API payload, a format other people parse): "Use exactly this structure."
- **Flexible** when the shape should adapt to the content: "This is a default; adapt the sections to what you find."
- **Inline** when it is short and every run uses it.
- **In `assets/`** when it is long or used only in some cases, with a pointer that says when to fill it in.
- **Placeholders** that say what goes in them: `[what failed, for whom, for how long]`, not `[text]`.

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

A gotcha is a fact about the environment or domain that defies a reasonable assumption, so the model gets it wrong unless told: the export whose amounts are in cents, the sandbox API that accepts any key but never sends email, the column named `customer` that holds a supplier ID.

- Put them in `SKILL.md`, before the steps they affect: the model must know them before it hits the situation, and won't think to open a file about a mistake it doesn't know it is making.
- State each as the fact and what to do about it, in one or two lines.
- Grow the list from use: each time the model needs a correction, add it.
- Leave out general advice; it isn't a gotcha unless a capable model would get it wrong.

## Task tracking

- The model tracks its own progress with whatever tools its surface offers; don't require a specific task tool that may not exist on every surface.
- For a long workflow, a progress checklist in the response is the portable form.
- Don't ask the model to announce its plan before every step; ask for a plan only where a person or a validator checks it.

## Choose the smallest set

Start from the task's parts and add only what each needs:

- A reference skill: rules and gotchas.
- A short task: steps, gotchas, a final check.
- A long task with dependencies: steps with gates, a progress checklist, validation loops at the fragile steps.
- A task producing fixed output: a template or examples, plus a verification checklist.
- A destructive or batch task: plan, validate, execute, with a dry run and the user's confirmation where they must decide.

Then check each mechanism against test runs: if the model already does the step reliably without it, remove it.
