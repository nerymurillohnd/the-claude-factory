# Phase 2: Body

Decide what the body must carry and which mechanisms the task needs. This file covers:

- [what the skill must know about its domain](#what-the-body-must-carry)
- [what earns a line](#what-earns-a-line)
- [the form each line takes](#the-form-fits-the-failure)
- [workflows](#workflows), [checklists](#checklists), [validation loops](#validation-loops), [plan-validate-execute](#plan-validate-execute), [output templates](#output-templates) and [gotchas](#gotchas)

## What the body must carry

Name the kind of work the skill serves and the disciplines that govern it. Derive from them the knowledge, methods, tools, failure modes and quality criteria the skill must carry. The costlier an error in that domain, the more evidence, verification and human control the skill must require.

## What earns a line

Ask of each line: would Claude do this differently, or not know how, without it? If not, cut it.

- Keep: the domain's procedure and its reasons, conventions, facts that defy assumptions, the exact tool or command, and the corrections the user keeps making.
- Cut: what any capable model knows, and platform facts that change nothing the model writes or does. Point to the page instead.

Once a skill loads, its content stays in context across turns, so every line is a recurring cost. Write guidance that applies to the whole task as standing instructions ("after every edit") near the top: the model reads the body once, and after compaction Claude Code keeps only the first 5,000 tokens of each skill.

Each mechanism below costs attention. Use only the ones the task needs.

## The form fits the failure

- Output in the wrong shape: a template, or input and output examples.
- An element the model can't infer: the fact where it applies, or a gotcha.
- An action that depends on a condition: the condition and both branches.
- A judgment made inconsistently: the criterion and its reason.
- A rule skipped under pressure: the rule, each shortcut around it named and closed, and a hook if it must always hold.
- Code rewritten on every run: a script.

## Freedom fits fragility

- Many valid approaches: give criteria.
- One way is better: give a preferred pattern.
- A deviation breaks something: give the exact command.

Give one default with its exception as its own condition, never a menu. Teach the class of problem, not the answer for one instance.

## Workflows

Write numbered steps when the order matters: a step uses what an earlier one produced, or skipping one breaks a later one. Write goals and criteria when the order depends on what the model finds, as in a review or an investigation.

Each step is one action with its input, its command or method, and its output. Add only the controls the step needs:

- Gate: a check that must pass before the next step starts.
- Decision point: where the path forks, with a condition the model can check and where each branch goes.
- Exit condition: what must be true before a long workflow moves on.
- Loop back: when a later step can reveal a gap, go back to an earlier step, with a limit on the rounds.

Move a long branch or variant to its own file and point to it from the decision point, so the model reads only the branch it takes.

## Checklists

- Progress checklist: the model copies it into its reply and ticks it as it works. Use it for a long workflow with dependencies or gates, where the model would lose its place. Skip it for a short task. Don't use the task tools (`TaskCreate` and the rest) for this: they aren't available in every session, and a skill that depends on them can fail silently.
- Verification checklist: the model checks its finished output against it. Use it when the output can be wrong in ways the model doesn't notice while producing it. Each item names something observable and how to check it, and fails on a bad output. "The output is high quality" fails nothing.

Progress checklist, as the model copies it:

```text
- [ ] 1. Collect the month's invoices
- [ ] 2. Extract the line items
- [ ] 3. Check the totals
```

Verification items that fail on a bad output, and items that pass whatever the output:

```text
Correct:   - [ ] The journal's debits equal its credits, to the cent.
Incorrect: - [ ] All requirements are met.
```

## Validation loops

Do the work, run a validator, fix what it reports, and repeat until it passes. Use a loop where a step's errors are common and cheap to detect, so they are caught at the step that made them.

- Script: when the check is mechanical, such as a schema, a format or a cross-reference. Its errors name what to fix.
- Document: when the check is against written rules, such as a style guide.
- Self-check against stated criteria: when only judgment can check it. "Review your work" alone checks nothing.

Give the loop its stop: a number of rounds, or no gain over the last round. When the same error returns after a fix, stop and report it.

## Plan, validate, execute

For batch, destructive or costly work, the model writes the intended changes to a changes file such as `changes.json`, validates that file, and only then applies it:

1. Analyze the input.
2. Write the changes to the changes file.
3. Validate it: every target exists, nothing conflicts, nothing required is missing.
4. Apply the changes.
5. Verify the result.

The changes file can be fixed and checked again without touching the originals. When the user must approve before anything changes, show them the changes file between steps 3 and 4. A confirmation needs someone to answer: in a subagent or an unattended run nobody can, so the skill needs a default to take.

## Output templates

Give a template when the output has a fixed shape: the model follows a template more reliably than a description of the format.

- Strict, when a reader or a program depends on the exact shape: "Use exactly this structure."
- Flexible, when the shape should adapt to the content: "This is the default; adapt the sections to what you find."
- Inline when it is short and every run uses it. In `assets/` when it is long or used only in some cases, with a pointer that says when to fill it in.
- Each placeholder says what goes there: `[what failed, for whom, for how long]`, not `[text]`.

## Gotchas

A gotcha is a fact of the environment or domain that defies a reasonable assumption, so the model gets it wrong unless told. Examples: the export whose amounts are in cents, the sandbox API that accepts any key but never sends email, the column named `customer` that holds a supplier ID.

- Write each as the fact and what to do about it, in one or two lines.
- Put it in `SKILL.md`, before the steps it affects: the model must know it before it reaches the situation, and won't open a file about a mistake it doesn't know it is making.
- A gotcha that affects only one variant goes in that variant's file, at the point where the model reads it.
- Leave out general advice: it isn't a gotcha unless a capable model would get it wrong.

Read [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices) when you need the guidance on context, control and instruction patterns.

Read [Workflows and feedback loops](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#workflows-and-feedback-loops) when the task has many steps or a loop.
