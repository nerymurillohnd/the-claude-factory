# Task mechanisms

This file teaches you how to audit whether a skill controls its task with the right mechanisms: a marked workflow, a checklist, a validation loop and an output template, and whether it should have Claude plan or track its progress. For each mechanism you decide, from the kind of task the skill executes or teaches, whether the task needs it, and then judge what the skill has against that need. Each section gives you the principle, why it matters, and what to do when you audit.

## Contents

- How to use this file
  - Before auditing: establish the context
  - Then, audit mechanism by mechanism
- 1. Recognize the task
- 2. Workflows
  - 2.1 When the task needs a marked workflow
  - 2.2 How a good workflow is built
  - 2.3 What to flag in a workflow that is present
  - 2.4 What to recommend when a workflow is absent and needed
  - 2.5 Planning and progress tracking: task tools, plan mode and a written plan
- 3. Checklists
  - 3.1 When the task needs a checklist, and when it doesn't
  - 3.2 How a good progress checklist is built
  - 3.3 How a good final verification checklist is built
  - 3.4 What to flag when a checklist is present but wrong, excess or weak
  - 3.5 What to recommend when a checklist is absent and needed
- 4. Validation loops
  - 4.1 When the task needs a validation loop
  - 4.2 How a good loop is built
  - 4.3 Choosing the validator: script, reference document or self-check
  - 4.4 Plan-validate-execute
  - 4.5 Error messages that let Claude self-correct
  - 4.6 Checks that must pass every time
  - 4.7 Weak loops to flag
  - 4.8 Recommending a loop where one is missing
- 5. Output templates
  - 5.1 When the task needs a template, and when it doesn't
  - 5.2 Strict or flexible, and the wording that signals which
  - 5.3 How a good template is built: structure and placeholders
  - 5.4 Inline or in a separate file
  - 5.5 A template or examples
  - 5.6 Structured output for programmatic consumers
  - 5.7 Present but wrong, excess or weak
  - 5.8 What to recommend when a template is absent and needed
- 6. How the mechanisms fit together
- Classifying findings
- Improvement opportunities
- Delivering the report

## How to use this file

Read this whole file, through its final section, "Delivering the report", before you judge anything. This complete reading, and an audit of the skill against every point in it, are a precondition of your audit: no point stays unaudited. Keep to the file's order: establish the context, recognize the task (§1), audit each mechanism, judge how they fit together (§6), then classify what you found.

Audit from the seat of a Claude that loads the skill with no prior context and has to carry out its task. Walk the task as that Claude would, and ask at each point whether it would take the wrong order, skip a step, deliver unchecked work, or produce output in the wrong shape. Where it would, the skill lacks a mechanism or has a weak one. Where a mechanism makes Claude follow steps that don't fit the task, it is excess.

You judge by reading. You never run, test or measure anything, and never run the skill.

### Before auditing: establish the context

The right mechanisms depend on the skill in front of you, so settle these four points first.

1. **Where the skill lives.** A personal, project, plugin or managed skill, or one uploaded to an account. Some mechanisms exist only in Claude Code (task tools, plan mode, hooks in the skill's frontmatter), so where the skill runs decides whether recommending one is possible.
2. **How the skill gets invoked.** In the main conversation, where a user may be present to approve a plan; or forked, preloaded into a subagent, or run unattended (a scheduled task or a `-p` script), where nobody approves anything mid-task.
3. **Which surfaces and models load it.** Task tools, for example, exist by default only on some models (§2.5).
4. **What the skill is for**, from its own description and body: whether it teaches knowledge Claude applies alongside other work, or runs a task with steps, side effects and an output. This feeds §1.

### Then, audit mechanism by mechanism

Audit what the skill has and what it should have, with the same care for each: finding a needed mechanism the skill lacks, or a stronger version of one it has, is as much your job as finding a defect. For each of the four mechanisms, and for planning and tracking, give exactly one of these outcomes:

- **Present and optimal.** The task needs it and the skill builds it the way this file describes. Record no finding.
- **Present but wrong.** It is built against this file, weak at its job, or the task doesn't need it. Record it as a defect, classify it (see "Classifying findings"), and say whether it must be deleted, rewritten or moved.
- **Present, right, but improvable.** The task needs it and it works, but a stronger version from this file would serve the task better. Record it as an improvement opportunity, with the adjustment written out.
- **Absent, and the task needs it.** Record it as an improvement opportunity: say exactly where it belongs, write out what it should contain, and cite the point of this file it rests on.
- **Absent, and the task doesn't need it.** Record no finding. Never recommend a mechanism by default.

Work only from what is written in the skill. If you have no line to point to, you have no finding; for a missing mechanism, point to the step where it belongs.

---

## 1. Recognize the task

Every judgment in this file depends on the kind of task the skill runs, so classify it before you read any mechanism. A skill that applies conventions or domain knowledge alongside the user's work needs no steps, gates or templates; a skill that deploys, migrates, fills forms or produces a deliverable may need all of them. A mechanism that fits one kind of task is waste or harm on another: it costs context on every run, and Claude follows instructions even where they don't fit, which sends it down unproductive paths.

When you audit, answer these about the task before anything else, quoting the skill:

- What does it produce, and who or what consumes it: a program that parses it, a person who reads it every run, or only the user in the moment? (§5)
- Does order decide the outcome? Which steps consume an earlier step's output, and what breaks if two swap or one is skipped? (§2, §3)
- Is any step fragile, batch, destructive or irreversible, or does any action reach a remote system? (§2, §4)
- Can something check the result: a script, a test, a build, a linter, a reference document, a list of stated criteria? Or is the only quality at stake taste? (§4)
- How many distinct steps does it take, and is its scope settled by the request or still open? (§2.5, §3)
- Is a user present while it runs, and on which surfaces and models does it run? (§2.5, §4.6)

Write the classification into your reasoning, then judge each mechanism against it. Most skills mix parts: one part may need exact steps and a validation loop while another needs only goals and criteria. Classify each part on its own.

## 2. Workflows

A workflow is a marked sequence of steps that the skill tells Claude to follow. It is the right control when the order of actions decides the outcome, and the wrong one when the task rewards judgment. Judge it against the task, never against how orderly the skill looks.

### 2.1 When the task needs a marked workflow

Marked steps pay off when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed; when the operation is complex and multistep; when later steps depend on earlier ones or must pass a validation gate; and in batch or destructive operations. Free instructions with the reason behind them serve better when several approaches are valid, decisions depend on context, and heuristics guide the approach. Claude already breaks complex tasks into steps and adjusts as it learns, so a sequence earns its place only where Claude would otherwise take the wrong order, skip a step, or improvise where it must not.

When you audit:

- Ask of every numbered sequence: would Claude get the order or a step wrong without it? If not, the numbering adds nothing; recommend stating the goals and criteria instead.
- Flag a fragile procedure (a migration, a deploy, a release, form filling, anything with a required order or a pass condition) written as loose advice or scattered across prose. It is absent and needed.
- Flag a workflow forced onto reference content: conventions, style guides and domain knowledge that Claude applies alongside the user's work need no steps.
- Judge each part of the skill separately, and flag only the part that is miscalibrated.
- When the steps orchestrate dozens to hundreds of subagents, or the orchestration must rerun identically, note that Claude Code places that scale in a dynamic workflow, a script the runtime executes. A skill's steps are followed by Claude turn by turn, keep intermediate results in Claude's context, and restart with the turn when interrupted.

Recognize the difference:

- Needs exact steps: "Run exactly this script: `python scripts/migrate.py --verify --backup`. Do not modify the command or add additional flags." There is one safe path and consistency is critical.
- Needs freedom: a code review that lists what to check (parameterized queries, an authentication check on every endpoint, race conditions, error messages that leak internals) without fixing an order, because the code in front of Claude decides the best approach.

### 2.2 How a good workflow is built

A good workflow is a reusable method for a class of tasks, written so that Claude can't skip what matters and isn't boxed in where it should judge:

- **Clear, sequential steps.** Each step is one action Claude can carry out and recognize as done, naming the script, command or file it uses when there is one. Clear steps are what keep Claude from skipping a critical validation.
- **Explicit decision points.** Where the path splits, a step states the condition and where each branch goes: "Creating new content? Follow the creation workflow. Editing existing content? Follow the editing workflow."
- **Gates between phases.** A step whose result later steps rely on ends with the condition for moving on and where to return when it fails: "If verification fails, return to Step 2". A precondition that doesn't hold stops the work: "If not, stop and ask." The check behind a gate is a validation loop (§4); the workflow's job is to place the gate at the right step.
- **A method, not an instance.** The steps describe how to approach any task of the kind ("read the schema, join on the `_id` convention, apply the user's filters"), not the answer to one task ("join `orders` to `customers` and filter `EMEA`").
- **Routing for large or varied workflows.** A workflow that grows large or has several variants moves its variants into separate files, and a decision step tells Claude which file to read for which case.

When you audit:

- Check each step for an action and a recognizable end. Flag a step Claude can't act on or verify, such as "handle errors appropriately".
- Check that every split in the path is a stated condition with a named branch, not a branch Claude has to infer.
- Find the steps whose output later steps depend on, and check that each ends with a gate and a return point.
- Flag steps written for one instance instead of the class of tasks the skill serves.

### 2.3 What to flag in a workflow that is present

A workflow fails in two directions. Too much of it makes Claude follow steps that don't fit the task. Too little of it lets Claude skip a gate, take the wrong branch or improvise a fragile operation.

When you audit:

- Flag a fixed order imposed on a task where several approaches are valid, and recommend goals and criteria in its place.
- Flag a later step that depends on an earlier result with no gate between them, and a gate with no stated pass condition or no return point.
- Flag variants mixed into one long sequence where a decision step could route to each one.
- Flag a split workflow whose decision step doesn't say which file to read for which case.

### 2.4 What to recommend when a workflow is absent and needed

When the task carries the signals of 2.1 and the skill leaves the sequence to chance, recommend a workflow sized to the task, written out:

- Numbered steps in `SKILL.md` for the essential sequence, with exact commands only at the fragile steps, a gate after each step that later steps rely on, and a decision step wherever the path splits.
- Separate files for large variants, each selected by a decision step.
- The hand-offs the gates need: a validation loop (§4) for a quality-critical gate, and a checklist (§3) where Claude must track dependent steps.

### 2.5 Planning and progress tracking: task tools, plan mode and a written plan

Three aids sit around a workflow: Claude Code's task-tracking tools, plan mode, and a written plan or spec before building. The first two exist only in Claude Code, and only under conditions. A skill that orders Claude to use one of them must hold wherever the skill runs, or it becomes an instruction Claude can't follow.

What the official sources establish:

- **Task-tracking tools.** `TaskCreate`, `TaskGet`, `TaskList` and `TaskUpdate` keep a task list with pending, in-progress and completed items; `TodoWrite` replaces them only when `CLAUDE_CODE_ENABLE_TASKS=0` is set. By default they exist only on Opus 4.7, Sonnet 4.6, Haiku 4.5 and earlier models. On other models they are absent unless the user opts in, with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`, `--allowedTools` or `--tools`, because those models keep track of multi-step work without a written checklist. Background and cloud sessions provide them on every model. Where they exist, Claude creates tasks on its own for complex work of three or more distinct actions, for task lists the user provides, for longer operations, and when asked. Tasks persist across context compaction.
- **Plan mode.** A Claude Code permission mode in which Claude reads, explores and writes a plan but doesn't edit source files until the user approves it. Its use is changes the user wants to review before they touch disk. Approval needs the user and never resolves on its own.
- **A written plan or spec.** When requirements aren't pinned down, Claude interviews the user and writes a spec, then builds from it, so the build has a written definition of done. For batch or destructive changes, a structured plan file validated before execution is plan-validate-execute (§4.4).

When you audit:

- Flag a skill that makes `TaskCreate`, `TaskUpdate`, `TodoWrite` or any task tool a required step. Where the tools are absent the step can't run. Recommend removing the requirement and leaving tracking to Claude, or wording it as conditional on the tools being present.
- Flag a skill that names `TodoWrite` as Claude Code's tracking tool: it is disabled by default in favor of the four Task tools.
- Don't recommend task tools as the fix for a long or complex workflow; where they exist, Claude uses them on its own. When the skill needs a progress record that holds wherever it runs, the mechanism is a checklist (§3).
- Recommend plan mode only for a skill that runs in Claude Code, whose task makes changes the user should review before any edit, and where a user is present to approve. Flag it in a skill meant for unattended runs.
- Recommend a written spec step when the skill starts work whose requirements the user hasn't settled, and never when the request already fixes the scope.

## 3. Checklists

A checklist is a list of checkable items. Claude either copies it into its response and checks items off as it works (a progress checklist), or checks its finished work against it before delivering (a final verification checklist). The workflow says how to do each step; the checklist is what Claude tracks and ticks. Judge every checklist by one question: does it stop Claude from skipping a step, or from delivering unchecked work?

### 3.1 When the task needs a checklist, and when it doesn't

The official guidance reserves the checklist for complex, multi-step work. It keeps Claude from skipping steps, especially when steps depend on each other or a validation gate must pass before the work moves on, and it lets Claude and the user see how far the work has gone. It works with or without code. The signals in the task:

- Many steps in a fixed order, where a later step consumes an earlier step's output.
- A validation or verification step Claude could pass over on its way to the result.
- Batch, destructive or high-stakes work, where one skipped check is costly.
- Output that must meet several stated requirements before it is delivered.

Progress tracking alone no longer earns a checklist: newer models keep track of multi-step work without a written one. A short task, a single action, or a task where the path depends on context gains nothing from a checklist, which still costs context every time the skill loads.

When you audit:

- Count the steps, find which depend on earlier ones, and find every validation or verification gate. Ask which step Claude would most likely skip on its way to a finished-looking result. If you can name none, the task probably doesn't need a checklist.
- Mark "absent and the task needs it" when the task has several dependent steps or a gate Claude could pass over, and nothing makes Claude track them.
- Flag a checklist whose only purpose is to track progress through a short or linear task as present but not needed, and recommend removing it.

Recognize the difference:

- Needs one: analyze the form, map the fields, validate the mapping, fill the form, verify the output. Filling from an unvalidated mapping corrupts the result, and the validation is the step Claude would skip.
- Doesn't: summarize the diff in three bullets and list the risks. One pass, no dependency, no gate.

### 3.2 How a good progress checklist is built

The official pattern is a checklist Claude copies into its response and checks off as it progresses. Each part of it does work:

- **A copy instruction**, such as "Copy this checklist and check off items as you complete them". Without it, Claude reads a list; it has no instruction to track one.
- **One copyable block** of Markdown checkboxes (`- [ ] Step 1: ...`) under a short title, so Claude can copy it whole and mark each box.
- **One item per step, labelled like the step**, so Claude can match each box to its instructions. The detail lives in the step sections; the checklist is their index.
- **The concrete action in the item**: where a step runs a script or edits a file, the item names it ("Validate mapping (run validate_fields.py)"), so completion is something Claude observes, not something it judges.
- **Gates as items of their own**, never folded into a neighbouring step, with the gated step saying where to go back on failure.
- **Placement before the work**: at the head of the workflow, before Step 1, so Claude copies it before starting. A workflow in a separate file carries its checklist with it.

When you audit:

- Flag a checkbox list with no instruction to copy it and check items off.
- Map every item to a step and every step to an item. Flag items without a step, steps without an item, and labels or order that differ.
- Flag items that describe an outcome Claude must judge where the step has a command, script or file the item could name.
- Confirm each validation or verification step is its own item and that its step says what to do on failure.
- Flag a checklist placed after the steps it tracks, or in a file Claude reads only after the work has started.

Recognize the difference:

- Weak: `- [ ] Make sure the form is filled correctly`
- Strong: `- [ ] Step 5: Verify output (run verify_output.py)`

### 3.3 How a good final verification checklist is built

A final verification checklist lists the criteria Claude checks its finished output against, and lets it proceed only when every one is met. It matters because Claude stops when work looks done: with nothing to check against, "looks done" is all it has. A good one has these properties:

- **Every criterion can be decided** by reading the output or running a named check: present or absent, matches or doesn't, passes or fails.
- **The criteria come from the skill's own requirements** and from the discipline that governs the work, not from generic quality words. Each discipline defines good work differently: for code, passing tests and respected constraints; for research, verified sources and traceable claims.
- **It is a gate** at the end of the workflow: "only proceed when all requirements are met", with the step to return to when a criterion fails. The fix-and-recheck cycle around it is a validation loop (§4).

When you audit:

- For each criterion, ask whether Claude could decide pass or fail from the output or from a check the skill names. Flag every criterion it couldn't, such as "high quality" or "complete", and recommend the specific requirement the skill states elsewhere.
- Compare the criteria with the skill's stated output requirements. Flag a requirement no criterion checks.
- Flag a final checklist with no gate: nothing says to stop, fix or return when a criterion fails.

Recognize the difference:

- Weak: `- [ ] The report is complete and high quality`
- Strong: `- [ ] Every claim names the source document that supports it`

### 3.4 What to flag when a checklist is present but wrong, excess or weak

A wrong checklist costs context on every load and can steer Claude away from the steps that matter.

When you audit:

- Flag items with no observable completion ("handle errors appropriately", "ensure accuracy"), and recommend the command, file or criterion that would give each one.
- Flag items you can't trace to a step, script or requirement of the skill, and items naming a script or file the skill doesn't have.
- Flag a checklist that repeats the workflow's text as checkbox items with no copy instruction and no gate: Claude reads the same steps twice and tracks nothing. Recommend reducing it to an index of step labels with the instruction, or deleting it and keeping the numbered steps.
- List the task's dependencies and gates from 3.1, and flag every one the checklist leaves out, naming it. A checklist without the validation, the output check or a prerequisite such as a backup before a destructive step tracks the easy work and lets the risky work slip.
- Flag a checklist whose edge-case items outnumber its core steps, and recommend cutting it to the steps and gates.

### 3.5 What to recommend when a checklist is absent and needed

Recommend the smallest checklist that covers the task's dependencies and gates, written out from the skill's own steps so the author can paste it in:

- **Where:** at the head of the workflow, between its heading and Step 1, or at the top of the file that holds the workflow.
- **Progress checklist:** the copy-and-check-off instruction, then one block of `- [ ]` items, one per step, labelled like the step headings, each naming its script, command or file, with every validation as its own item.
- **Final verification checklist:** when the output must meet several stated requirements, a short list of decidable criteria at the end of the workflow, under "only proceed when all of these pass".

If the skill has no clear steps to hang a checklist on, say that the workflow must be defined first (§2.4), and don't invent steps.

## 4. Validation loops

A validation loop has Claude check its work against something other than its own impression of it, fix what the check reports, and check again before moving on. Without one, every mistake waits for the user to notice it.

### 4.1 When the task needs a validation loop

A loop earns its cost when an error is likely, costly and not visible at a glance. The signals:

- **Quality-critical output**, and critical operations, for which the official checklist expects feedback loops and verification steps.
- **Fragile or error-prone operations, or a sequence that must be followed exactly.**
- **Batch operations, destructive changes, complex validation rules, high-stakes operations**: the cases for plan-validate-execute (§4.4).
- **Output something can check**: a script, a test, a build's exit code, a linter, a diff against a fixture, or a reference document.

A loop doesn't earn its cost when several approaches are valid and Claude's judgment is the right instrument, or when the only quality at stake can't be broken into pass/fail checks, such as writing style or visual taste. Validation that guards against nothing still costs time and tokens on every run, and the official guidance says to remove unnecessary validation when it shows up as wasted work.

When you audit:

- Ask what an undetected error costs in this task, and whether Claude could tell from its own output that the error happened. If the error is costly and invisible on reading, the task needs a loop.
- Flag as excess a loop on a task with none of the signals, or one that checks something that can't go wrong in this task.
- Don't flag a missing loop where the only quality at stake is taste with no criteria that can be listed.

Recognize the difference:

- Needs a loop: "Update 50 form fields in a PDF from a spreadsheet." Claude can reference fields that don't exist, create conflicting values or miss required fields, and the finished PDF doesn't show it.
- Doesn't: "Suggest ways to make this function easier to read." Many answers are valid and no check chooses between them.

### 4.2 How a good loop is built

The pattern is: do the work, run the validator, fix what it reports, run it again, and proceed only when it passes. A loop missing any of these parts doesn't close:

- **A named validator**: a command with its script path and arguments, or a named reference document and the items to compare.
- **Placed right after the step it checks**, so an error is caught where it was made, before later steps build on it.
- **A failure branch**: read the error, fix the issue, run the validator again, or return to a named step.
- **A gate**: "Only proceed when validation passes." Without one, Claude can note the failure and carry on.
- **An exit besides passing**: the official example of a fix loop runs "until the type check passes or two rounds in a row make no progress". A loop with no such exit invites blind retries of the same fix.
- **Evidence**: Claude Code's best practices have Claude report the check it ran and its output, not "all tests pass" on its own.

When you audit:

- Check each loop for a named validator, placed right after the step it checks, a fix-and-recheck branch, and a gate.
- Ask what ends the loop besides passing, and what Claude reports when it stops without a pass.
- Recommend that Claude report the check and its result where the user relies on Claude's word that the work passed.

### 4.3 Choosing the validator: script, reference document or self-check

The three kinds of validator are not equally reliable:

- **A script** gives an objective, repeatable verdict. The official guidance prefers a bundled validation script to validation code Claude writes during the task: it is more reliable, behaves the same on every run, and only its output enters context. For mechanical checks such as valid JSON, a row count or a field that exists, a script beats a model's judgment.
- **A reference document** is the validator for skills without code: Claude compares its work with the document, item by item, as in the official example where a style guide is the validator and the step lists what to check.
- **A self-check** is the weakest, and works only when the skill states the criteria; without them it falls back to "looks done".

When you audit:

- Flag a mechanical check (format, schema, field names, counts, required items present) left to Claude's reading or to code Claude must write during the task, and recommend a bundled script.
- For a reference-document validator, ask whether the skill names the document, the step at which to check against it, and what to compare. Flag "check it against the guide" with no items.
- Flag a self-check with no stated criteria.
- Ask whether the validator gives pass or fail. If it can't, it's a review step, not a loop.

Recognize the difference:

- Weak: "Review your draft against STYLE_GUIDE.md."
- Strong: "Review against STYLE_GUIDE.md: terminology is consistent, examples follow the standard format, every required section is present. Note each issue with its section, revise, and review again. Proceed only when all requirements are met."

### 4.4 Plan-validate-execute

For batch, destructive, high-stakes or complex-rule work, the official pattern adds a step before execution: Claude writes the intended changes to an intermediate file in a structured format, and a script checks that plan against a source of truth before anything is applied. In the official example, a script extracts the form's real fields to `form_fields.json`, Claude writes `field_values.json`, and `validate_fields.py` checks every field name against the form, plus types and required fields. Claude revises and re-validates until the plan passes, and only then fills the form. This works because validation happens before any change, the verdict is objective, and Claude can rework the plan without touching the originals. The key is that the validator checks the plan against the source of truth, not only its own shape. In Claude Code, file edits can be rewound, but actions on remote systems such as databases, APIs and deployments can't: for those, a check after the change comes too late.

When you audit:

- For a batch, destructive or high-stakes operation, flag a skill whose only check comes after the irreversible step.
- Ask whether the plan is a structured file a script can check, or exists only in Claude's prose.
- Flag a validator that checks only that the plan file is well formed, not that it matches the real input.
- Where the skill bundles a script that makes destructive or stateful changes, recommend a dry-run option so Claude can preview the effect first.

Recognize the difference:

- Too late: "Apply the updates with `fill_form.py`, then check the output for errors."
- Before execution: "Write `field_values.json`. Run `validate_fields.py form_fields.json field_values.json`. Revise and re-run until it passes, then run `fill_form.py`."

### 4.5 Error messages that let Claude self-correct

When a check fails, its message shapes Claude's next attempt. "Error: invalid input" wastes a turn. A useful message names the item, what was expected and what to try, as in the official example: "Field 'signature_date' not found. Available fields: customer_name, order_total, signature_date_signed." A validator that reports to an agent gives structured output with diagnostics on stderr, distinct exit codes for different failures, no interactive prompts, and output of a predictable size.

When you audit:

- Read each bundled validator's failure paths. Flag messages that only say validation failed, without the item, the expected value or the options.
- Flag a validator whose pass or fail Claude can't read from its output or exit code, one that waits for interactive input, or one that can print unbounded output.
- Flag a failure branch that says "fix it" without telling Claude to read the error first.

### 4.6 Checks that must pass every time

A skill's text is an instruction Claude weighs; Claude usually follows it, but nothing guarantees it, and a line such as "Always typecheck before you finish" works most of the time, not every time. Claude Code's documentation puts a check with zero exceptions in a hook, which the harness runs every time its event fires: a `Stop` hook whose command exits with code 2 sends Claude back to work with the command's stderr as the reason, until the check passes or the block limit is reached (eight blocks in a row with no tool call between them, by default). A skill that runs in Claude Code can carry its own hooks in its `hooks` frontmatter; they register when the skill is invoked and stay active for the rest of the session. A hook is only for a rule with no exceptions, and it doesn't replace naming the check in the skill: Claude still needs the command to check its own work as it goes.

When you audit:

- Ask whether the skill describes a check that must pass with no exceptions, such as before finishing or after every edit. For a skill that runs in Claude Code, recommend the hook, carried in the skill's `hooks` frontmatter, and keep the check named in the text.
- Don't recommend a hook for a check Claude should apply with judgment, or for a skill that doesn't run in Claude Code.
- Flag a skill that relies on a hook but never names the check's command in its text.

### 4.7 Weak loops to flag

A loop can be present and still fail at its job.

When you audit, check every loop for each of these and name the one you find:

- **No stop condition**: "repeat until it passes" with no round limit or no-progress rule, and nothing on what to report when it can't converge.
- **Validation after the irreversible step**, when it can only report the damage.
- **A check that can't fail**: one that checks a label but not the substance, only that a plan parses and not that its entries exist, or a signal that stays green while the thing is broken (an endpoint that returns 200 while the database behind it is down). Name the failure it would miss.
- **"Verify it works" with no concrete check**: no command, no reference, no criteria. Recommend the check that makes the step pass or fail.
- **No gate**: the validator runs but Claude may continue past a failure.
- **Excess validation**: checks on what can't go wrong in this task, or the same check repeated where nothing changed.

Recognize the difference:

- Weak: "Verify the migration worked."
- Strong: "Run `python scripts/check_migration.py`. It exits non-zero and lists each table whose row count differs from the backup. Fix and re-run until it exits 0. If two runs in a row report the same tables, stop and report them."

### 4.8 Recommending a loop where one is missing

When the task needs a loop and the skill has none, recommend one fully specified, and state which signal of 4.1 makes it necessary so it can be weighed against its cost:

- **The validator**: the most objective the task allows. An existing project command, a bundled script for mechanical checks, a reference document with listed criteria for checks that need reading, a self-check only with stated criteria.
- **Placement**: in the step right after the action it checks; for batch or destructive work, the plan file and its validation as steps before the change.
- **The fix branch and gate**, **the exit** with what Claude reports if it stops without a pass, and **evidence** where the user relies on the result.
- **A hook** only when the check has zero exceptions and the skill runs in Claude Code (4.6).

## 5. Output templates

An output template is a concrete skeleton of what Claude must produce: sections, fields or lines in order, with placeholders where content goes. It is more reliable than a prose description of the format, because Claude pattern-matches well against a concrete structure. The template fixes only the shape of the result; the skill still teaches how to approach the task.

### 5.1 When the task needs a template, and when it doesn't

A task needs a template when its output must take a specific format, and the signal is who or what consumes it: a program, an API or a data format that parses it needs the format exactly; a person who reads the same report every run needs it consistent; a recurring deliverable whose sections must all be present needs them named. Where several approaches are valid and the output tolerates variation, a fixed skeleton over-constrains it. A one-line shape, such as "two or three bullet points, then any risks", can stay in prose, as an official example skill does.

When you audit:

- Flag a required format with several parts (named sections, ordered fields, a file layout) that the skill describes only in prose, and recommend the template that replaces it.
- Flag a fixed template on output whose right form depends on the content, such as an open-ended analysis, and recommend a flexible default or none.
- Don't flag a short, single-shape format written as a sentence.

### 5.2 Strict or flexible, and the wording that signals which

A template's strictness must match how much deviation the output can accept, and the wording around it tells Claude which it is. A strict template, for requirements such as API responses or data formats, opens with words like "ALWAYS use this exact template structure". A flexible one opens with words like "Here is a sensible default format, but use your best judgment", often ending with leave to adjust sections. Stricter than the need, Claude forces content into sections that don't fit; looser, Claude varies a format a consumer depends on. Reasoning-based instructions work better than bare directives, so a strict template is strongest when it also says why the format is fixed.

When you audit:

- Compare the wording that introduces each template with what its consumer needs (5.1), and flag a mismatch in either direction.
- Flag a template introduced with no wording about strictness, such as a bare code block after a heading, and recommend the wording that fits its consumer.
- Recommend that a strict template state its reason, such as the parser or reader that depends on the exact shape, when the skill gives none.
- Judge each template on its own terms: one skill can rightly hold a strict template for a machine-read file and a flexible one for a human summary.

Recognize the difference:

- Strict: "ALWAYS use this exact structure. The release script parses these headings:" followed by the skeleton.
- Flexible: "Here is a sensible default format, but use your best judgment based on the analysis:" followed by the skeleton and "Adjust sections as needed."

### 5.3 How a good template is built: structure and placeholders

A good template shows the real structure, its actual headings, field names and order, and puts a placeholder wherever Claude supplies content. A placeholder says what belongs there, such as `[One-paragraph overview of key findings]`, not only that something goes there; in a flexible template it can also say how to adapt. A heading with no placeholder lets a section be present in name and empty in substance. The template comes from the outputs the task really produces.

When you audit:

- Flag a template of bare headings where the content of each section matters, and recommend a placeholder per section that names its content.
- Flag a placeholder whose meaning is ambiguous, such as `[details]` or `...`, where a wrong guess changes the output.
- Flag a template that contradicts the skill's own steps, such as a field the steps never produce.
- Flag a generic skeleton that could belong to any skill, and recommend one drawn from the skill's real deliverable.

Recognize the difference:

- Weak: `## Key findings` with nothing under it.
- Strong: `## Key findings` followed by `- Finding 1 with supporting data`.

### 5.4 Inline or in a separate file

A short template used on every run belongs inline, at the step that produces the output, where Claude has it in hand without an extra read. A long template, or one needed only in some cases, belongs in its own file, conventionally in `assets/`, read at the step that needs it, so it costs context only on the runs that use it.

When you audit:

- Flag a long template inline, or one used only in a branch of the task, and recommend its own file, read at the step that uses it.
- Flag a short template every run needs that sits in a separate file, and recommend moving it inline.

### 5.5 A template or examples

A template fixes structure. Input and output examples convey style and level of detail, which a structure can't capture, as with commit messages, where voice and detail matter more than any skeleton. The two combine: a template can fix the sections while an example shows how full each should be.

When you audit:

- Flag a template used where the problem is style or tone, not structure, and recommend examples instead, or as well.
- Flag style-dependent output that has a template and no example of how full each part should be, where that fullness decides the quality.

### 5.6 Structured output for programmatic consumers

When a program reads Claude's output, the format must be exact, and a structured format with unambiguous field boundaries serves that consumer best: JSON, CSV or TSV over free-form or whitespace-aligned text. A template is still an instruction, and no instruction is guaranteed to be followed: where the exact shape is critical, a check against it belongs in a validation step (§4). Where a bundled script can produce the output itself, it gives a consistency a template can't.

When you audit:

- Flag output meant for a tool, parser or API with only a prose description or a loose layout, and recommend a strict template in the structured format the consumer reads, with exact key or column names.
- Flag a machine-read template that leaves out field names, order, value types or allowed values the consumer depends on.
- Flag a strict machine format with no check before it is consumed, when a malformed file means a failed or damaging run, and recommend a validation step.
- Recommend a bundled script to generate the output when the format is fully determined by data the skill already has and Claude adds no judgment to it.

### 5.7 Present but wrong, excess or weak

Too much constraint is as much a defect as too little: skills that keep adding rules can stall because they are over-constrained.

When you audit:

- Flag several templates offered as equal options with no rule for choosing, and recommend one default with the condition that selects any alternative.
- Flag the same template repeated in several places, since the copies drift apart, and recommend one copy read where it is needed.
- Flag a template that dictates exact wording where only structure matters, so correct output in other words would count as wrong.
- When the template matches its consumer, its strictness wording matches the need, every placeholder names its content, and it sits where 5.4 places it, report it as present and optimal and invent no change.

### 5.8 What to recommend when a template is absent and needed

When 5.1 finds a fixed consumer or a required shape and the skill has no template, recommend one fully specified: the consumer that makes it necessary; its strictness and the wording that signals it; the sections or fields in order, each with a placeholder naming its content; whether it goes inline at the step that produces the output or in its own file read at that step; and, for machine-read output, the structured format and whether a validation step or a script should back it. Base the skeleton on the deliverable the skill describes, keep it as small as the need, and invent no section the task doesn't produce. If the problem is style, not shape, recommend examples instead.

## 6. How the mechanisms fit together

The mechanisms nest: a workflow places the gates, a validation loop supplies the check behind each gate, a checklist tracks the steps and gates Claude could skip, and a template fixes the shape of what the last step delivers. A plan file validated before execution is a template and a loop working together. Judging each one alone misses the defects between them.

When you audit:

- Check that every gate in the workflow has a check behind it, and every validator sits at a gate that stops the work on failure.
- Check that every checklist item matches a step, and that the checklist's gates are the workflow's gates.
- Check that the template the last step fills is the one the final verification checks against.
- Flag mechanisms that repeat each other without adding control, such as a checklist that restates the workflow and a final check that restates the template, and recommend the one that does the job.
- Recommend the smallest set the task needs. A task with one fragile step may need only that step's exact command and a loop after it.

---

## Classifying findings

Give every finding four things: the exact file and line(s) in the skill under audit, or the step where a missing mechanism belongs; the point in this file it violates or falls short of; why it is a defect, stated as its consequence on the task; and a specific fix, written out, with the reason it's the right one.

Classify each defect into one of four levels by its actual consequence. The examples anchor each level; a finding that doesn't match one verbatim still gets the level its own consequence earns.

- **Critical.** Lets the task cause damage it can't undo, or fail every run. For example: a destructive, batch or remote operation whose only check comes after the irreversible step; a validation loop with no exit around an operation that changes state; a skill whose required step is a tool that doesn't exist where it runs.
- **High.** Lets Claude skip a gate, deliver unchecked work, or produce output a consumer can't use, in some runs. For example: a dependent step with no gate before it; a check that can't fail; "verify it works" with no concrete check on quality-critical output; a format a program parses described only in prose, or a strict format with no strictness wording; a final checklist with no gate; plan mode required in a skill that runs unattended.
- **Medium.** Costs context or consistency without making the task fail. For example: a mechanism the task doesn't need; a checklist that duplicates the workflow; items or criteria Claude can't check; a template of bare headings; a long template inline; a loop with no stated evidence; a fixed order on a task where several approaches are valid.
- **Low.** A minor weakness with no real consequence on the task. For example: a checklist label that differs slightly from its step heading; a flexible template with no line saying sections may be adjusted.

Tie-breaks:

- If a finding fits two levels, the higher level wins.
- A mechanism the task doesn't need is Medium at most, unless it makes Claude act wrongly, such as a fixed order that forbids the step the case needs.
- When several defects share one root cause, such as a workflow written with no gates at all, report the root cause once and list every location.
- Never invent impact, never inflate a severity to make the report look decisive, and never lower one because Claude might do the right thing anyway.

## Improvement opportunities

Separate improvement opportunities from defects: an opportunity is a mechanism the task needs and the skill lacks, or one that works and that a stronger version from this file would improve. Report every one that genuinely applies to this skill's task; this section may stay empty only when nothing does. For each one, give what exists now (or that it is absent, and the step where it belongs), the mechanism or adjustment written out in full, and why it is better for this task.

This file gives you the criteria, the context to establish, and the severity model. The gotchas and the verification checklist live in your own instructions, and the report template lives in this skill's `assets/` folder, so they aren't repeated here.

## Delivering the report

Deliver every defect and improvement opportunity in the shared findings template, `assets/audit-report.md` in this skill. Fill one defect block per defect, with every field, and keep the template's structure exactly. Defects with one root cause are one defect: give its first location in File and Lines, and list every other location, as `path:lines`, in Finding.
