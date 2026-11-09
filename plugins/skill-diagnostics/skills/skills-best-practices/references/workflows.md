# Workflows

Sequential steps, copyable checklists, validation loops and the other workflow patterns, and when a skill needs each.

## Contents

- [When to use these patterns](#when-to-use-these-patterns)
- [Checklist for a multi-step workflow](#checklist-for-a-multi-step-workflow)
- [Checklist examples](#checklist-examples)
- [Validation loop](#validation-loop)
- [Plan-validate-execute](#plan-validate-execute)
- [Fit each pattern to the skill](#fit-each-pattern-to-the-skill)
- [Conditional workflow](#conditional-workflow)
- [Say when the work is done](#say-when-the-work-is-done)

## When to use these patterns

For multi-step or quality-critical work, give clear sequential steps, a copyable checklist and a loop that validates before moving on; this "greatly improves output quality" \[PL\]\[AS\]. A rule that must hold every time goes in a hook, not in a step: see [body-and-structure.md](body-and-structure.md#writing-the-body), **Write standing instructions.**

## Checklist for a multi-step workflow

Use one "especially when steps have dependencies or validation gates" \[AS\]; Platform reserves it "for particularly complex workflows" \[PL\] `rec`. It prevents skipped steps and works for skills without code too \[PL\]. Its shape \[PL\]\[AS\] `rec`:

1. At the start of the workflow, one line telling Claude to copy the checklist into its response and tick each item as it completes it \[PL\].
2. The checklist in its own fenced code block, under a short title line such as `Task Progress:` \[PL\].
3. One item per step, in order, as `Step N: <action> (<file to edit or script to run>)`, with script and file paths in backticks \[AS\]; each validation or verification step gets an item of its own \[PL\]\[AS\].
4. Under the checklist, one section per step with the exact action, the command or file, and what the step produces \[PL\]. Inside the fenced checklist, paths go in backticks; a file Claude must read gets its Markdown link in that step's section `default`.
5. The workflow ends with the step to return to when a verification fails ("If verification fails, return to Step 2") \[PL\].

## Checklist examples

````markdown
## Form processing workflow

Copy this checklist and tick each item as you complete it:

```
Task Progress:
- [ ] Step 1: Analyze the form (run `scripts/analyze_form.py`)
- [ ] Step 2: Create the field mapping (edit `fields.json`)
- [ ] Step 3: Validate the mapping (run `scripts/validate_fields.py`)
- [ ] Step 4: Fill the form (run `scripts/fill_form.py`)
- [ ] Step 5: Verify the output (run `scripts/verify_output.py`)
```

**Step 1: Analyze the form.** Run `python3 ${CLAUDE_SKILL_DIR}/scripts/analyze_form.py input.pdf`. It writes the form's fields to `fields.json`.

**Step 3: Validate the mapping.** Run `python3 ${CLAUDE_SKILL_DIR}/scripts/validate_fields.py fields.json`. Fix every error before Step 4.

If Step 5 fails, return to Step 2.
````

The same shape without code, for analysis, review or writing:

````markdown
## Vendor comparison workflow

Copy this checklist and tick each item as you complete it:

```
Comparison Progress:
- [ ] Step 1: Collect each vendor's quote from `inputs/`
- [ ] Step 2: Fill one row per vendor in `assets/comparison-template.md`
- [ ] Step 3: Check every figure against its quote
- [ ] Step 4: Write the recommendation
- [ ] Step 5: Check the recommendation against `references/criteria.md`
```

**Step 3: Check every figure.** For each figure in the table, find it in the vendor's quote and note the page. A figure you can't find goes back to Step 2.

**Step 5: Check the recommendation.** Read [references/criteria.md](references/criteria.md) and check the recommendation against each criterion.

If Step 5 finds a criterion the recommendation doesn't meet, return to Step 4.
````

## Validation loop

Do the work, run a validator ("a script, a reference checklist, or a self-check"), fix any issues, and repeat until validation passes \[AS\]\[PL\]; Platform asks for one in "quality-critical tasks" \[PL\] `rec`. How to write it `default`:

1. Place the loop right after the step that produces the output, before any step that uses it.
2. Name the validator: a script when the check can be mechanical, a reference file (a style guide or a list of requirements) when it needs judgment, a self-check against stated criteria only when neither exists.
3. Write it as numbered steps: validate; on failure read the error, or note each issue with the section of the reference it breaks \[PL\], fix, and validate again; proceed only when validation passes.
4. Say what passing means: exit 0 with no errors, or every requirement in the reference met.

```markdown
## Editing workflow

1. Make your edits
2. Validate immediately: `python3 ${CLAUDE_SKILL_DIR}/scripts/validate.py output/`
3. If validation fails:
   - Read the error message
   - Fix the issues
   - Run validation again
4. Only proceed when validation passes
```

With a reference file as the validator, Claude checks by reading and comparing \[PL\]:

```markdown
## Review workflow

1. Draft the text by the rules in [references/style-guide.md](references/style-guide.md)
2. Check the draft against each rule in that file
3. If a rule fails:
   - Note the rule and the passage that breaks it
   - Revise the passage
   - Check every rule again
4. Only proceed when every rule passes
```

## Plan-validate-execute

Use it for "batch operations, destructive changes, complex validation rules, high-stakes operations" \[PL\]; the open standard names batch or destructive operations \[AS\] `rec`. Create a structured plan file (for example `changes.json`), validate it against the source of truth with a script, and only then execute and verify \[AS\]\[PL\]. It catches errors before changes land, keeps originals untouched while Claude iterates, and gives machine-checkable results. Make validator errors specific: "Field 'signature\_date' not found. Available fields: customer\_name, order\_total, signature\_date\_signed" \[PL\]\[AS\].

## Fit each pattern to the skill

`default`. The examples above show the shape, not content to copy: rebuild each pattern from the skill's own steps, files, scripts and outputs. A one-step skill or a reference-only skill needs none of these patterns, and adding one there is a finding \[SD\].

## Conditional workflow

Branch at decision points ("Creating new content? → Creation workflow. Editing? → Editing workflow") and move large branches into their own files \[PL\].

## Say when the work is done

Multi-step work names its completion condition, so the agent neither stops early nor loops \[SD\] `rec`.
