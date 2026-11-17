# Task mechanisms

A skill that runs a task may need controls around it: marked steps, a checklist, a validation loop, a plan checked before execution, a template for the output. Each one costs context on every run and Claude follows it even where it doesn't fit, so add one only where the task's own shape asks for it, and build it so it actually closes.

## Contents

- 1. Classify the task first
- 2. Freedom per step
- 3. Workflows
- 4. Checklists
- 5. Validation loops
- 6. Plan, validate, then execute
- 7. Output templates
- 8. Fitting them together
- 9. Questions to ask yourself

## 1. Classify the task first

Answer these from the gap requests before choosing any mechanism, and answer them for each part of the skill separately, because one part may need exact steps while another needs only goals:

- What does it produce, and who consumes it: a program that parses it, a person who reads it every run, or only the user in the moment?
- Does order decide the outcome? Which steps use an earlier step's result, and what breaks if two swap or one is skipped?
- Is any step fragile, batch, destructive or irreversible, or does any action reach a remote system?
- Can something check the result (a script, a test, a build, a linter, a reference document, stated criteria), or is the only quality at stake taste?
- Is a user present while it runs, and on which surfaces and models?

A skill that only applies conventions or domain knowledge alongside the user's work needs none of the mechanisms below.

## 2. Freedom per step

Match how much latitude each step gives to how fragile it is.

- Many valid approaches, nothing fragile: say the goal and what good looks like, with no fixed command. "Review the diff for naming, dead code and readability."
- A known shape with varying details: a command template with the parameters named. "Run `pytest [file] -k [test]` for the test that failed."
- One safe path: the exact command, marked as not to be altered. "Run exactly `./scripts/migrate.sh --dry-run`; add no flags."
- A one-off command hard to get right first time belongs in a tested script (see the scripts-and-hooks guide), not inline.

## 3. Workflows

- Mark steps when the order decides the outcome: fragile or error-prone operations, a sequence that must be followed exactly, later steps that depend on earlier ones or on a gate, batch or destructive work.
- Don't mark steps for work where several approaches are valid and the context decides: Claude already breaks tasks into steps, and a fixed order there forces the wrong path.
- Make each step one action Claude can carry out and recognize as done, naming the command, script or file it uses.
- Where the path splits, state the condition and where each branch goes: "Creating a new page? Follow section 4. Editing one? Follow section 5."
- End each step whose result later steps rely on with its condition for moving on and where to go back when it fails. When a precondition doesn't hold, say to stop and ask.
- Write the method for the whole class of tasks, never the answer to one instance.
- When the workflow has large variants, move each into its own file and add a decision step that says which file to read for which case.
- Don't require Claude Code's task-tracking tools or plan mode. Task tools may be absent depending on the model and settings, and newer models track multi-step work without them; plan mode needs Claude Code and a user present to approve. Where a record must hold on every surface, use a checklist instead.
- When the request leaves the scope open, start with a step that settles requirements with the user and writes them down; skip it when the request already fixes the scope.

## 4. Checklists

Use a checklist when the task has several dependent steps, a gate Claude could pass over on its way to a finished-looking result, batch or high-stakes work, or output that must meet several stated requirements. Tracking progress through a short or linear task doesn't earn one.

A progress checklist:

- Opens with an instruction to copy it and check items off as each completes; without that, it's a list Claude reads once.
- Is one copyable block of Markdown checkboxes, one item per step, labelled like the step it tracks.
- Names in each item the observable action ("Validate the mapping, run `validate_fields.py`"), not an outcome Claude must judge ("make sure it's correct").
- Gives each gate its own item.
- Sits before the first step, so Claude copies it before starting.

A final verification checklist:

- Lists criteria Claude can decide by reading the output or running a named check: present or absent, passes or fails. "Every claim names its source document," not "the report is high quality".
- Takes its criteria from the skill's own requirements and from how the discipline defines good work.
- Is a gate: proceed only when every item passes, and say which step to return to on a failure.

## 5. Validation loops

Add a loop when an error is likely, costly and not visible on reading the output, and something can check it. Don't add one where judgment is the right instrument or the only quality is taste: validation that guards against nothing costs time on every run.

Build every loop with all of these:

- A named validator: a command with its path and arguments, or a named reference document and the items to compare. Prefer a bundled script for mechanical checks (format, schema, counts, required fields): it's objective and repeatable, and only its output enters context. A reference document suits checks that need reading. A self-check works only with stated criteria.
- Placement right after the step it checks, before later steps build on the error.
- A failure branch: read the error, fix, run the check again, or return to a named step.
- A gate: proceed only when the check passes.
- An exit besides passing: a round limit or a no-progress rule ("stop when two runs in a row report the same failures"), and what Claude reports when it stops without a pass. A loop with no exit invites blind retries; one whose end condition Claude can't check ("until it's good") never ends cleanly.
- Evidence: Claude reports the check it ran and its result, not "all tests pass" alone.

Don't build a check that can't fail: one that tests a label and not the substance, or a signal that stays green while the thing is broken.

## 6. Plan, validate, then execute

For batch, destructive, high-stakes or complex-rule work, a check after the change only reports the damage. Instead:

- Claude writes the intended changes to a structured file (JSON, CSV) before touching anything.
- A script checks that plan against the source of truth (the real form fields, the real table names, the real accounts), not only that the file parses.
- Claude revises and re-runs the check until it passes, then executes.
- Write the validator's failures so Claude can act on them: the item, what was expected, the valid options. "Field `signature_date` not found; available: `customer_name`, `signed_on`."

File edits in Claude Code can be rewound; actions on remote systems (databases, APIs, deployments, messages) can't, which is why the check comes first.

## 7. Output templates

- Give a template when the output's consumer needs a fixed shape: a program that parses it, a person who reads the same report every run, a recurring deliverable whose sections must all be present. Leave a one-line shape in prose, and give no fixed skeleton to output whose right form depends on the content.
- Signal strictness in the words that introduce it. Strict, with its reason: "Always use this exact structure; the release script parses these headings." Flexible: "A sensible default; adjust sections to the analysis."
- Show the real headings, fields and order, and a placeholder wherever Claude supplies content that says what goes there (`[one-paragraph summary of the main finding]`), never a bare heading or `...`.
- For a program consumer, use a structured format with exact keys or columns, types and allowed values, and back it with a check before the output is consumed. When the output is fully determined by data the skill already has, a script should generate it.
- Put a short template every run uses inline at the step that produces the output; put a long or conditional one in `assets/`, named at that step.
- When the problem is style or level of detail rather than shape, give input and output examples instead of, or beside, the template (see the writing-the-body guide).
- Keep one template per output. Several offered as equals with no rule for choosing, or copies in several places, drift.

## 8. Fitting them together

- The workflow places the gates; a loop supplies the check behind each gate; a checklist tracks the steps and gates Claude could skip; a template fixes what the last step delivers.
- Every gate has a check, every check sits at a gate that stops the work, every checklist item matches a step, and the final verification checks the template the last step fills.
- Use the smallest set the task needs. A task with one fragile step may need only that step's exact command and a loop after it.

## 9. Questions to ask yourself

- Which step would Claude most likely skip on its way to a result that looks done, and what stops it?
- For each gate: what checks it, and what happens when the check fails twice in the same way?
- Which actions can't be undone, and does every check on them come first?
- Who consumes the output, and does its template's strictness match that consumer?
- Could I remove any mechanism here without Claude doing worse?
