# Phase 3: Task mechanisms

Which mechanisms the skill's task needs, chosen from the parts of the task.

Each one costs attention: use only the ones the task needs, and remove any the model wouldn't need to do its step reliably.

## Name the task's parts

Most skills mix parts, and each part calls for different mechanisms:

- **Knowledge** the model applies to whatever it is doing, such as conventions or domain rules: rules and gotchas, rarely a workflow.
- **Ordered work**, where a later step depends on an earlier one: steps with gates.
- **Output in a fixed shape**, such as a report or a message: a template or examples, and a final check.
- **Destructive or outward actions**, such as deleting, deploying, sending or paying: a plan checked before acting, the user's confirmation where they must decide, and a dry run where one exists.
- **Work refined to a quality bar**: a validator and a rule for when to stop.

## Workflows

Write numbered steps when the order matters: a step uses what an earlier one produced, or skipping one breaks a later one. Write goals and criteria instead when the order depends on what the model finds, as in a review or an investigation.

## Checklists

Two tools for two failures.

**A progress checklist**, which the model copies into its reply and ticks as it works. Use it for a long workflow with dependencies or gates, where the model would lose its place among long tool outputs. Skip it for a short task: it adds ceremony and protects nothing. Track progress with this copied checklist, not the task tools (`TaskCreate` and the rest): Claude Code provides those by default only on older models and in background and cloud sessions, so a skill that depends on them fails silently in other local sessions.

**A verification checklist**, which the model checks its finished output against. Use it when the output can be wrong in ways the model doesn't notice while producing it.

## Validation loops

Do the work, run a validator, fix what it reports, and repeat until it passes. Use a loop where a step's errors are common and cheap to detect, so they are caught at the step that made them.

Choose the validator by what can check the result:

- **A script**, when the check is mechanical: a schema, a format, a cross-reference. Its errors name what to fix.
- **A document**, when the check is against written rules, such as a style guide.
- **A self-check against stated criteria**, when only judgment can check it. "Review your work" alone checks nothing.

## Output templates

Give a template when the output has a fixed shape: the model follows a template more reliably than a description of the format.

- **Strict** when a reader or a program depends on the exact shape: "Use exactly this structure."
- **Flexible** when the shape should adapt to the content: "This is the default; adapt the sections to what you find."
- **Inline** when it is short and every run uses it; **in `assets/`** when it is long or used only in some cases, with a pointer that says when to fill it in.
