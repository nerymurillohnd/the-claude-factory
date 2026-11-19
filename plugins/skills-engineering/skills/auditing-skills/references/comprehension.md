# Comprehension

This file teaches you how to audit whether a Claude that loads the skill with no prior context can understand it and act on it from its text alone: whether it forms the right picture of what to do, in what order, with which concepts and toward which end; whether the skill holds together, with no contradictions, drifting terms or duplicates; whether it leaves Claude anywhere to guess; and whether each passage speaks in the register its job needs. Each section gives you the principle, why it matters, and what to do when you audit.

## Contents

- How to use this file
  - Before auditing: establish the context
  - Then, audit area by area
- 1. Read the skill as Claude does
  - 1.1 Before the body, Claude has only the description
  - 1.2 The body is read once, whole, and stays as it was read
  - 1.3 Other files open only when pointed to, and scripts run unread
  - 1.4 Forked and preloaded runs start with no history
  - 1.5 Walk the skill top to bottom and build the model Claude would form
  - 1.6 When the model can't be formed
- 2. Order and dependencies
  - 2.1 Load-bearing instructions near the top
  - 2.2 No rule after the step it governs
  - 2.3 Every concept introduced before it is used, close to its use, and used
  - 2.4 Each phase's instructions in that phase, neither earlier nor later
  - 2.5 Pointers placed at the step that needs them
  - 2.6 Standing instructions say they stand
  - 2.7 A phased skill's files organized by phase
- 3. Coherence across the skill
  - 3.1 Contradictions
  - 3.2 One term per concept
  - 3.3 Literal and semantic duplication
  - 3.4 Each fact once, where Claude first needs it
- 4. Gaps where Claude is left to guess
  - 4.1 Dead ends
  - 4.2 Loops with no way out
  - 4.3 What the skill relies on but never defines
  - 4.4 Assumptions Claude must invent
  - 4.5 Catch-all phrasing
  - 4.6 Instructions with two readings
- 5. Register and language
  - 5.1 Shape follows what the content is
  - 5.2 Directive, context, and the reason why
  - 5.3 Directive strength and weak wording
  - 5.4 Emphasis: capitals and piled-on absolutes
  - 5.5 Say what to do, not only what to avoid
  - 5.6 Tone and grammatical person
  - 5.7 Wording that goes out of date
  - 5.8 Closing loopholes in a discipline skill
  - 5.9 What a link says about its file, and links to other skills
- Classifying findings
- Improvement opportunities
- Delivering the report

## How to use this file

Read this whole file, through its final section, "Delivering the report", before you judge anything. This complete reading, and an audit of the skill against every point in it, are a precondition of your audit: no point stays unaudited. Keep to the file's order: establish the context, walk the skill as Claude reads it (§1), then judge order (§2), coherence (§3), gaps (§4) and register (§5), then classify what you found.

Audit from the seat of a Claude that loads the skill with no prior context and has to carry it out. Your method differs from a line-by-line review: you read the skill from its first line to its last, opening each file where the skill points to it, and build the model of the task that Claude would form. Every point where that model breaks, or forms only from your own guess, is where the skill fails its reader. Having understood the skill, also judge where its own logic and purpose call for clearer, stronger or more complete writing than it has.

You judge by reading. When the prompt passes a mechanical result, such as where the part of the body kept after compaction ends or where capitalized absolutes and time-sensitive words appear, take it as verified and judge what it means. When a result a point needs is missing, record it under Checklist exceptions as blocked and judge everything else by reading.

### Before auditing: establish the context

How Claude reads the skill depends on the skill in front of you, so settle these four points first.

1. **Where the skill lives and which surfaces load it.** Some reading behavior, such as what is kept after compaction, is documented for Claude Code only; apply it where the skill runs there.
2. **How the skill gets invoked.** Inline in the main conversation, where Claude has the conversation so far, or forked or preloaded into a subagent, where it starts with no history (§1.4).
3. **What the skill is for**, from its description and body: the task it does or teaches, the output it delivers, and the situations it distinguishes. You judge every passage against this purpose.
4. **Its files and phases.** Which files it points to and at which steps, and whether it works in phases. This sets the walk in §1.5.

### Then, audit area by area

Audit what the skill has and what it should have, with the same care for each: finding a passage that needs to be clearer, a missing outcome, definition or reason, or a stronger version of what the skill already says, is as much your job as finding a defect. For every point in this file, give exactly one of these outcomes:

- **Present and optimal.** Claude reads it as meant, at the point it needs it. Record no finding.
- **Present but wrong or excess.** It misleads Claude, contradicts or repeats another passage, sits where Claude can't use it, or says nothing Claude can act on. Record it as a defect, classify it (see "Classifying findings"), and say whether it must be deleted, rewritten or moved.
- **Present, right, but improvable.** It works, but a clearer or stronger version would serve the skill's purpose better. Record it as an improvement opportunity, with the exact replacement written out.
- **Absent, and the skill needs it.** A definition, outcome, failure path, reason, pointer or link the skill's purpose calls for and doesn't state. Record it as an improvement opportunity, or as a defect where its absence makes Claude act wrongly: write out the exact text and where it goes, and cite the point of this file it rests on.
- **Absent, and the skill doesn't need it.** Record no finding. Never recommend text by default, and leave open what the skill deliberately leaves to Claude's judgment.

Work only from what is written in the skill. If you have no line to point to, you have no finding; for missing text, point to where it belongs. Where the skill gives no basis for what the missing text should say, name the decision the author has to make, and invent nothing.

---

## 1. Read the skill as Claude does

### 1.1 Before the body, Claude has only the description

Until a skill loads, the name and description are all Claude has of it. Claude matches the request against the description and loads the skill on that basis. When Claude opens the body, it knows only what the description promised and what the request asked for. The body has to take up that task from its first lines. A body that opens on background, history or a different framing of the job makes Claude reconcile the two before it can start.

When you audit:

- Read the description once, before the body, as the only thing Claude carries into it. Don't judge it here. Use it to fix the task Claude believes it was loaded for.
- Flag a body whose opening doesn't take up that task: it starts elsewhere, names a different job, or only reaches the announced task several sections down.
- Recommend, when the opening is weak or missing, one opening sentence that states the task in the description's own terms and Claude's first move, for example "Review the staged diff for the risks listed below, starting with `git diff --cached`." Write it only from the skill's actual purpose, and propose nothing when the opening already does this.

### 1.2 The body is read once, whole, and stays as it was read

When the skill loads, Claude reads all of `SKILL.md` and it enters the conversation as a single message. It stays there on later turns, and Claude does not re-read the file. If the skill is invoked again with identical content, Claude Code adds only a note that it is already loaded. Two consequences follow for the reader you simulate. First, everything in the body is in context from the moment Claude starts, but Claude meets it in written order and won't come back to look again. Second, when Claude Code compacts the conversation, it re-attaches only the start of each invoked skill, and it can drop older skills entirely. What sits late in a long body is what disappears first.

When you audit:

- Walk the body as one pass that goes forward, as 1.5 describes. Don't credit Claude with a second reading that would resolve an early confusion.
- When the prompt gives the point where the part kept after compaction ends, treat everything past it as text Claude may no longer have on later turns.
- Recommend, when a skill's behaviour depends on a passage that Claude would only use correctly on a second reading, wording that makes the passage work on the first pass, quoting the passage and its replacement.

### 1.3 Other files open only when pointed to, and scripts run unread

Claude opens a bundled file only when the instructions reference it, and only when the task at that moment calls for it. In the documented PDF example, Claude decides that form filling isn't needed and never reads `FORMS.md`. A file the body never points to is a file Claude never reads. A script Claude runs is executed, not read: its code never enters context, only its output does.

When you audit:

- Open each referenced file at the point the body points to it, and only when the condition Claude would meet holds in the scenario you are walking. Leave unread every file the body never points to, and judge the skill without it.
- Never count a script's source as something Claude knows. If a later step depends on what a script does or prints, the instructions must say it.
- Recommend, where a step depends on a script's behaviour that the instructions don't state, the sentence that states it, for example "`analyze_form.py` writes every field's name, type and position to `fields.json`," written from what the step needs.

### 1.4 Forked and preloaded runs start with no history

A skill run with `context: fork`, or preloaded into a subagent, starts with no conversation history. The subagent doesn't see what was discussed, the files the main conversation read, or the skills invoked earlier. Everything it needs has to be in the skill itself. A reference to "the plan we agreed on" or "the file above" points at nothing there. A skill that runs inline, in the main conversation, can lean on that conversation. Read it under the conditions it actually runs in.

When you audit:

- Establish how the skill runs: `context: fork` in its frontmatter, or the prompt saying that a subagent preloads it. If neither applies, treat the run as inline.
- In a forked or preloaded skill, flag every passage that relies on conversation history, on files read earlier, or on a skill invoked earlier.
- Recommend the self-contained replacement for each passage that relies on history, naming where the missing input now comes from.

Recognize the difference:

- **Relies on history:** "Apply the plan we agreed on."
- **Self-contained:** "Apply the plan in `plan.md`; read it first."

### 1.5 Walk the skill top to bottom and build the model Claude would form

Judge the skill as a capable colleague with no context on this task would: someone who has Claude's general knowledge but not the author's intent, the conversation the skill was written in, or any file the skill doesn't point to. If that reader would be confused, Claude will be too. Leftover context from authoring a skill hides gaps in what it says, which is why you read as a fresh instance. Walk once through `SKILL.md`. At each line, use only the description and the lines above it, and open files as 1.3 describes. For a skill whose instructions differ by situation, walk it once for each situation it names. As you go, build the six parts of the model Claude would form:

- **Purpose:** what the skill is for and what problem it solves.
- **Entry point:** where Claude starts, and what decides which part applies.
- **First action:** the concrete first thing Claude does.
- **Sequence:** what follows what, and what each step needs from earlier ones.
- **Concepts:** the terms, files and values Claude must hold to follow it.
- **End state:** what done looks like, what Claude delivers, and what it does next, so that it isn't left guessing.

When you audit:

- Record each part of the model at the line where Claude first has it. If confusion arises at a line, note it there, even when a later line resolves it, and note where it is resolved.
- Ask, at the end of the walk, whether all six parts formed, and whether they formed from the skill's text or from your own guesses.
- Recommend, for each part that formed only weakly, the exact sentence that would make it explicit, at the place Claude first needs it, grounded in what the rest of the skill shows its purpose to be.

### 1.6 When the model can't be formed

A part of the model that can't be formed is a point where Claude falls back to guessing. Different runs then guess differently, so the skill behaves inconsistently. The finding has to let the author fix it without re-reading the skill.

When you audit:

- Record, for each part that can't be formed: which part it is, the line where Claude first needs it, what Claude has there instead, and the readings Claude would choose between.
- Separate a part that is absent from one that is present but arrives too late, and judge the second under section 2.
- Name the run that would settle a point that reading can't settle, such as whether Claude follows a pointer or opens files in the order the skill expects. Observing which files a fresh run reads, and in what order, is that run.
- Recommend the missing text, with its exact wording and where it goes, derived from what the rest of the skill shows its purpose to be. Where the skill gives no basis for the content, say what the author has to decide, and invent nothing.

## 2. Order and dependencies

### 2.1 Load-bearing instructions near the top

The instructions the whole task depends on belong at the top of the body: what the skill is for, how Claude starts, the critical constraints, and guidance that holds throughout. Truncation after compaction keeps the start of each skill, and the official guidance is to put the most important instructions near the top of `SKILL.md`. A rule buried deep in the body is also easy to under-weight: the documented fix for a skill whose rule Claude skipped is to make the rule more prominent. Detailed how-to for particular steps can sit lower.

When you audit:

- Flag each load-bearing instruction that sits deep in the body, below material that only some runs need.
- When the prompt gives the point where the part kept after compaction ends, flag every instruction past it that the skill still needs on later turns.
- Recommend the move: quote the instruction, and give the position near the top where it goes and the one-sentence form it takes there.

### 2.2 No rule after the step it governs

A constraint, exception or gotcha belongs at or before the step it governs. A gotcha placed in a reference file that Claude opens only later, or one whose trigger Claude won't recognize, arrives after Claude has already acted. Inside `SKILL.md` the whole body is already in context when Claude acts, so a late rule isn't unseen. But Claude follows the steps in order and reaches the governed step with nothing there to signal that a later line changes it. After compaction, the late rule may also be gone. No official source states the case inside the body. That case is an inference from how Claude reads; the case of a file opened later is sourced.

When you audit:

- Flag every rule that first appears after the step it governs, giving both locations.
- Flag a gotcha that lives only in a file Claude opens after the situation it covers, or that lives behind a trigger Claude wouldn't recognize before it hits the problem.
- Recommend the rule's text placed at the governed step, for example "Before step 3, exclude test accounts: add `WHERE is_test = false`." Use the skill's own wording, and delete the late copy.

Recognize the difference:

- **Rule after its step:** "3. Run the migration. … Note: back up the database before any migration."
- **Rule at its step:** "3. Back up the database, then run the migration."

### 2.3 Every concept introduced before it is used, close to its use, and used

Claude meets each term, file and value in written order. A term used before it is defined forces a guess at its first appearance. A value set long before the step that uses it has to be carried across unrelated material. A term, file or value that is introduced and never used costs attention and invites Claude to act on it. Instructions that don't apply to the task get followed anyway, and a bundled file that Claude never opens is either unnecessary or poorly signalled. The rule for definition before use and for distance is an inference from the order in which Claude reads, since no source states it. The cost of unused material is sourced.

When you audit:

- Flag each term, file or value used before it is introduced, giving its first use and its introduction.
- Flag each one introduced far from its only use, so that Claude must carry it across unrelated steps.
- Flag each one introduced and never used, including a file listed but never pointed to at a step.
- Recommend, for each, the one-line definition at the first use, or the deletion. Where a term Claude needs is never defined, give the definition the skill's own usage implies.

### 2.4 Each phase's instructions in that phase, neither earlier nor later

A skill that works in phases (gather, then decide, then produce) should keep each phase's instructions inside that phase. Instructions for a later phase placed early sit in context before Claude can use them, and they may be acted on too soon: Claude follows instructions that don't apply to the current task. Instructions for an earlier phase placed later arrive after Claude has moved on. Phase content that only some runs need can live in a file that Claude is told to read when that phase applies. The rule for keeping instructions inside their phase is an inference and the owner's doctrine. The cost of instructions that don't apply, and splitting by situation, are sourced.

When you audit:

- Map each instruction to the phase it serves, and flag every one that sits in another phase, in either direction.
- Flag an introduction that front-loads detail belonging to a later phase.
- Recommend the relocation: quote the instruction and name the phase heading or step it moves to. Where a phase lacks the instruction it needs, give the sentence that belongs there.

### 2.5 Pointers placed at the step that needs them

A pointer to a file belongs at the step where Claude should use the file, and it names when to open it: "Fill in `assets/report-template.md`" in the reporting step, not a list of files at the top. Claude opens a file when it is pointed to and the moment calls for it. A pointer placed too early makes Claude load context before it can use it, or forget the pointer by the time it matters. A pointer placed too late, or one that is missing, leaves Claude to do that step without the file.

When you audit:

- Flag each pointer that sits away from the step that uses its file, and each step that needs a file the body points to only elsewhere, or never.
- Flag a pointer that doesn't say when to open the file.
- Recommend the pointer rewritten at its step with its condition, for example "If the API returns a non-200 status, read `references/api-errors.md`," and the removal of the distant copy.

### 2.6 Standing instructions say they stand

Because the body is not re-read, guidance meant to hold for the whole task has to say so, and it has to sit where it covers the whole task. "Run the tests" reads as a single step. "Run the tests after every edit" holds throughout. A standing instruction placed inside one step reads as part of that step only. That placement point is an inference, and the wording point is sourced.

When you audit:

- Find every instruction meant to hold for the whole task. Flag each one worded as a single step, and each one placed inside a single step.
- Recommend the standing wording, which names when it applies ("after every edit," "whenever you open a new file"), placed near the top as 2.1 describes.

### 2.7 A phased skill's files organized by phase

Section 2.4 keeps each phase's instructions in that phase; the same holds for the files a phased skill points to. Claude opens a file at the step that points to it and applies what fits that step, so a file that holds the rules of two phases delivers the other phase's rules late or never. Where a phase reads several files, Claude applies them in the order it opens them, and when the skill doesn't state that order, Claude picks one. A name that carries the phase as well as the topic, such as `phase-2-placements.md`, shows from the file listing which phase a file serves. Focused reference files, files organized by domain or feature, descriptive names, and saying when to load each file are sourced. Cutting the files by phase, putting the phase in the name and stating the reading order are an inference and the owner's doctrine.

When you audit:

- Apply this section only to a skill that works in phases and keeps phase content in supporting files. A file serves a phase when that phase's steps apply its content; deciding something in one phase and writing it in a later one are two phases. A phase's own file, such as `phase-3-design-and-plan.md`, counts among the files that phase reads, first.
- Map each file to the phases whose steps use its content. Flag every file whose content serves more than one phase, quoting a passage for each phase, even a single rule when a step of the other phase decides or writes with it and none of that phase's files states it, and recommend moving each passage to a file of the phase it serves, splitting the file when each phase holds a section of it, with each passage's destination and every pointer updated. A passage the steps of two phases both apply goes once in the earlier phase's file, and the later step points back to it. A lookup that every phase consults on purpose, such as a glossary, a table of values or a template, is not a mixed file. Flag a rule stated in the files of two phases as a duplicate under 3.3.
- Flag every phase that reads more than one file without stating their order, and recommend listing the files under that phase in the order of the steps that read them, each with its condition and, where the phase's steps are numbered, the step that reads it, and one line telling Claude to read them in that order, under the phase or once as a standing instruction that covers every phase.
- Record a phase-specific file whose name doesn't carry its phase as an improvement opportunity, not a defect, and recommend the name `phase-<n>-<topic>.md`, with every pointer to it updated. Judge whether the name says what the file holds under 5.9.
- Judge a file that makes Claude apply a rule after the step it governs as 2.2 does. Judge a missing order as a defect when the order of the files changes the result, because one file's rule decides how Claude applies another's, and as an improvement opportunity otherwise.

---

## 3. Coherence across the skill

Claude builds one picture of the task from everything the skill says, in SKILL.md and in every file it opens. That picture holds only when the passages agree with each other, each concept keeps one name, and each fact sits in one place. The defects in this section live between two passages, and neither passage looks wrong on its own. So read the skill as a whole before you judge any single line, and keep a running list of every rule, value and term along with where it appears.

### 3.1 Contradictions

When two instructions contradict each other, Claude may pick either one arbitrarily. It doesn't stop to ask, and it doesn't reliably pick the one the author meant. The same is true when two files give different guidance for the same behavior. Loading makes it worse. SKILL.md is in context every time the skill runs, but a reference file is read only when Claude opens it. A reference that disagrees with SKILL.md therefore makes Claude's behavior depend on whether it happened to open that file on this run.

When you audit:

- Flag every pair of passages that give different guidance for the same behavior, quoting both locations. Look for direct opposites (do X / never do X), two values for the same thing (a path, a count, a format, a name), and two orders for the same actions.
- Compare each reference file with SKILL.md on every point they both cover. Flag each disagreement, including where one states the rule more loosely or more strictly than the other.
- Flag a rule that is stated as binding in one place and as a preference in another. Claude can't tell whether it may bend the rule.
- Flag a general rule and an exception to it when the skill never says where the exception applies or which one wins.
- Flag a summary list or checklist that states a rule differently from the body that teaches it.
- Recommend one resolution with its exact text: the version to keep, the one to delete, and the reason. The reason is that it agrees with the official documentation, or with the rest of the skill and its purpose. If nothing in the skill or the sources shows which version the author meant, give both readings and name the decision the author has to make. Don't pick one yourself.
- Where the skill states a general rule and its purpose plainly calls for an exception that it never addresses, recommend the exact sentence that says where the exception applies and which one wins. Recommend nothing when no such case follows from the skill's purpose.

Recognize the difference:

- Contradiction: SKILL.md says "Write the report to `out/report.md`." `references/format.md` says "Save the report next to the input file."
- Resolved: SKILL.md says "Write the report to `out/report.md`, unless the user names another path." The reference doesn't restate the location.

### 3.2 One term per concept

Choose one term for each concept and use it throughout the skill, in every file. Consistency helps Claude parse and follow the instructions. When the word for one thing shifts ("field", "box", "element", "control"), Claude has to decide whether each new word names the same thing or a different one, and it can decide either way. The reverse failure, one term used for two concepts, leads Claude to apply a rule meant for one concept to the other. Sometimes the environment itself uses several names for one thing, such as an ID that has a different name in each system. In that case the skill states the mapping once, explicitly, and otherwise keeps to its own single term.

When you audit:

- List the skill's key concepts (the objects, actions, inputs, outputs and roles it talks about) and every term used for each one, across SKILL.md and every file it points to. Flag each concept that has more than one term, with every location.
- Flag drifting verbs for the same operation ("extract", "pull", "get", "retrieve").
- Flag each term used for two different concepts.
- Recommend the one term to keep and list each replacement in exact text. Prefer the term the skill introduces first, or the one the tool, user or official documentation uses (this is inference, not stated by a source).
- Where the skill works with a system that uses several names for one thing and never maps them, recommend the exact mapping sentence. Don't flag an explicit mapping as drift.

Recognize the difference:

- Drift: "Call the endpoint… then retry the URL… and log the route."
- Explicit mapping: "The user ID is `user_id` in the database, `uid` in the auth service, and `accountId` in the billing API. All three refer to the same value."

### 3.3 Literal and semantic duplication

Once Claude has read a fact, a second statement of it gives Claude nothing it would get wrong without it. The copy still costs context on every turn the skill stays loaded. Copies also drift: when one is updated and the other isn't, the duplicate becomes a contradiction (3.1).

Duplication comes in two forms:

- **Literal duplication** is the same sentence stated twice.
- **Semantic duplication** is two passages that tell Claude the same thing in different words. They often sit under different headings, or one is in SKILL.md and the other in a reference. Semantic duplication is harder to see and does more harm, because the two wordings rarely match in scope or strength. Claude may read them as two separate rules.

Two things are not duplication:

- A short summary list whose job is to be checked against, such as a checklist that names the rules or steps the body teaches. Official guidance pairs a copyable checklist with the steps it summarizes.
- A later passage that refers to an earlier rule by name without restating it.

When you audit:

- Flag every fact, rule or instruction stated more than once across the skill's files, literally or semantically, with every location.
- To find semantic duplicates, reduce each instruction to what it makes Claude do, and compare those reductions, not the wording.
- When copies differ in scope or strength, treat them as a contradiction first (3.1). Settle which version is right before you merge them.
- Don't flag a summary list meant to be checked against, as long as it names the rules without teaching them again. Do flag one that teaches them again or has drifted from the body.
- Recommend keeping one statement (3.4) and deleting the others. Where a later passage needs the fact, recommend a pointer by name in exact text, such as "apply the naming rule in Conventions".

Recognize the difference:

- Semantic duplicate: "Don't commit anything in `dist/`" under Rules, and later, under Committing: "Files under `dist/` are build output; keep them out of git."
- Summary list: a closing "Before you finish" checklist with the line "`dist/` left out of the commit", next to the one body passage that teaches the rule.

### 3.4 Each fact once, where Claude first needs it

When you remove duplicates, the copy you keep matters. Keep the one at the point where Claude first needs the fact, so Claude has it before it acts. Official guidance places facts at the point of need. Gotchas stay in SKILL.md, where the agent reads them before it meets the situation. Each file is mentioned at the step where Claude should use it. A fact that is stated in full only after a passage that already depends on it leaves Claude two choices at that passage: act without the fact, or guess it.

When you audit:

- For each duplicated fact, recommend keeping the statement at its first point of need and turning each later copy into a pointer or deleting it.
- Flag a fact whose only full statement comes after the first passage that relies on it. Recommend moving it to that first use, with the exact text at its new place.
- When SKILL.md and a reference both need the same fact, recommend keeping it in the one Claude reads first and pointing to it from the other.

## 4. Gaps where Claude is left to guess

Claude reads a skill the way a brilliant new colleague who doesn't know your norms reads a procedure. It does what the text says and fills every gap with its own guess. Claude reads vague or conflicting instructions and tries to follow them, but nothing guarantees it follows them as meant. The test for this section is: if a careful colleague with no context would have to stop and ask the author something to do this right, and the skill doesn't answer it, that is a gap.

This section doesn't cover steps, branches, gates or return points inside a marked workflow, or the validator, fix branch and exit of a validation loop. It covers everything else: prose instructions, standing rules, reference files, and the skill as a whole. Don't treat every open point as a gap. Where several approaches are valid and Claude's judgment is the point, an open instruction is right, and covering every edge case can hurt more than it helps. Rate that case absent and not needed.

### 4.1 Dead ends

An instruction that starts an action leaves Claude hanging when the skill doesn't tell it four things that it can't work out alone:

- what the action produces
- what comes next
- what to do when the action fails or doesn't apply
- how to tell that it's done

Claude stops when the work looks done. If nothing says what done is, "looks done" is all it has. The same applies to the whole skill: it has to say what a finished result is and what Claude delivers.

When you audit:

- For each instruction outside a marked workflow, ask the four questions above. Flag each one that the skill doesn't answer and that Claude would get wrong by guessing.
- Flag every check that has no action for a failed result, such as "Validate the data before proceeding" with no word on what to do when the data is invalid.
- Flag every instruction that sends Claude to a file, a tool or a person without saying what to take from it or what to do with what it returns.
- Check that the skill states its end: what counts as done and what Claude delivers or reports. Flag it where it's missing.
- Don't flag a standing convention, such as "Use 2-space indentation", for lacking a next step. It has none.
- Recommend the missing outcome, next step, failure path or done condition as exact text, placed next to the instruction. Derive it from what the skill is for. Where the skill doesn't contain the fact the fix needs, name what the author has to supply instead of inventing it.

Recognize the difference:

- Dead end: "Validate the data before proceeding."
- Closed: "Run `python scripts/validate.py --input {filename}` to check data format. If validation fails, common issues include: missing required fields (add them to the CSV); invalid date formats (use YYYY-MM-DD)."

### 4.2 Loops with no way out

Prose sometimes sends Claude back to repeat an action ("search again", "keep refining until it's right", "retry") without saying when to stop. Claude then either stops at an arbitrary point or keeps working past the point of use. Telling Claude to keep going until done is more likely to cause over-work than to fix a stall. Persistence the skill wants has to come from a condition Claude can check, not from blind retries or endless searching.

When you audit:

- Flag every prose instruction that repeats an action with no condition that ends it, or with a condition that may never hold and no fallback.
- Flag an end condition that Claude can't check by reading or running anything, such as "until it's good" or "until the user is happy" with no sign of either.
- Flag two passages that send Claude to each other, where A says to decide by B and B says to decide by A.
- Recommend an exit in exact text with two parts: the condition that ends the loop, and what Claude does when that condition can't be met (a limit, plus what to report or whom to ask). Take both from the skill's purpose.

Recognize the difference:

- No way out: "If the search finds nothing, refine the query and search again."
- With an exit: "If the search finds nothing, refine the query and search again, up to three times. Then report the queries you tried and that nothing matched."

### 4.3 What the skill relies on but never defines

Claude can't see the author's norms, the team's decisions, or the conversation the skill was written in. Anything the skill depends on but never states, Claude has to make up. That includes:

- a term the skill coins or uses in a project-specific sense
- a tool or service it refers to only generically
- a decision it calls "agreed" or "approved" without giving its content

When you audit:

- Flag each term the skill coins, abbreviates, or uses in a project-specific sense without defining it at or before its first use. Don't flag a term Claude already knows in the sense used.
- Flag each tool, script or service the skill tells Claude to use without naming which one.
- Flag each decision the skill depends on but doesn't state, such as "the agreed format", "our convention", or "the approved library".
- Recommend the definition, location or name in exact text at the first use. Where the skill doesn't contain it, name what the author has to supply.

Recognize the difference:

- Undefined: "Use the approved error helpers."
- Stated: "Use the error helpers in `src/lib/errors.ts`; never throw raw strings."

### 4.4 Assumptions Claude must invent

Some instructions are complete in form but leave out something the task needs: a value, a scope, a format, or a choice. A preference between two reasonable approaches is something Claude can't read from its surroundings, so a skill that doesn't state it gets whichever approach Claude picks. If the author didn't settle a value, Claude has no better way to settle it. A menu of equal options with no default makes Claude try options when it should be doing the work.

When you audit:

- Flag each relative word with no measure where the result depends on it, such as "large", "recent", "a few", "short", or "important".
- Flag each instruction whose object or scope is open, such as "update the files" or "the relevant tests", where more than one set fits.
- Flag each deliverable whose format, location or reader the task depends on but the skill doesn't state.
- Flag each list of equal options with no default.
- Don't flag a point the skill leaves to Claude on purpose, where several approaches are valid.
- Recommend the missing value, scope or format in exact text, derived from the skill's purpose. For a menu, recommend one default and the condition that calls for the alternative. Where the skill doesn't contain the answer, name the decision the author has to make.

Recognize the difference:

- Menu: "You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image…"
- Default: "Use pdfplumber for text extraction. For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."

### 4.5 Catch-all phrasing

Phrases such as "handle errors appropriately", "follow best practices", "format code properly", "be thorough" or "make sure it's correct" name a quality or a duty without saying what satisfies it. They give Claude nothing to execute and nothing to check its result against. The fix is the specific pattern, edge case, convention or decision criterion that applies, written concretely enough to verify.

A catch-all is different from deliberate freedom. A general direction is right where multiple approaches are valid and context decides. A catch-all stands in for a specific requirement that Claude can't know.

When you audit:

- Flag every phrase that names a quality or duty without saying what satisfies it.
- Apply this test: could two careful readers check the same result against the phrase and agree whether it passes? If not, flag it.
- Don't flag a general direction where the skill deliberately leaves the approach to Claude and Claude's judgment is enough.
- Recommend the concrete replacement in exact text, drawn from the skill's domain and purpose. Where the skill doesn't contain what the requirement actually is, such as which errors or which practice, name what the author has to supply instead of inventing it.

Recognize the difference:

- Catch-all: "Format code properly."
- Verifiable: "Use 2-space indentation."

### 4.6 Instructions with two readings

An instruction that a careful reader can take two ways gets either reading, and it may get a different one on different runs. When the same request gives inconsistent results across runs, ambiguous instructions are one cause. When Claude ignores an instruction, the instruction itself may be ambiguous. The usual sources are:

- a verb that can mean advise or act ("suggest changes" yields suggestions, not edits)
- a pronoun or "this" with more than one antecedent
- a negation or condition whose reach is unclear
- an "or" where it matters whether one option applies or all of them do

When you audit:

- For each instruction, try to write a second reading that a careful Claude could act on and that leads to a different result. If you can, flag the instruction with both readings.
- Where the prompt reports that Claude ignored or misapplied an instruction, look first for a second reading in that instruction.
- Where only a run would show whether the readings diverge in practice, name the check: run the skill several times on a prompt that reaches the passage, and compare the results.
- Recommend wording that leaves one reading, in exact text, choosing the reading the rest of the skill and its purpose support. Where nothing supports either reading, give both and name the decision the author has to make.

Recognize the difference:

- Two readings: "Can you suggest some changes to improve this function?"
- One reading: "Change this function to improve its performance."

---

## 5. Register and language

### 5.1 Shape follows what the content is

No format is required or banned in a skill's body; the official guidance leaves it to whatever helps Claude do the task, and plain paragraphs work as well as lists. What matters is that each block's shape matches what the block is. Related standing rules read best as bullets under a heading, because Claude can take them one at a time. Context and reasoning read best as prose, because the meaning sits in the connections ("because", "unless", "so") that bullets cut out; split into fragments, a chain of reasoning turns into a pile of separate claims, and Claude has to rebuild the links itself. A table earns its place only for a real grid: several items, each compared on the same few properties. Steps that must run in order need numbering; whether a task needs a marked workflow is a separate question, and here you check only that the shape fits the content. The style of the skill can also carry over into Claude's output: a body written in heavy markdown pulls the output toward markdown, which matters when the skill wants prose out.

When you audit:

- Name what each block is (standing rules, context, reasoning, a lookup grid, an ordered sequence), compare it with the shape it has, and flag every mismatch. Never flag a shape just because it differs from a house style.
- Flag reasoning or context broken into bullet fragments where the connecting logic is lost, and recommend the paragraph that puts the links back, written from the bullets' own content.
- Flag a dense paragraph that buries several separate standing rules, and recommend the bullet list, one rule per bullet, in the paragraph's own words.
- Flag a table with no real grid, such as one row or one compared property, and recommend the sentence that replaces it. Where several items really are compared on the same properties but are written as repeated prose, recommend the table.
- Where the skill asks for prose output but its own body is mostly lists and bold, flag the mismatch and recommend rewriting the blocks that model the output in the register the output should have.

Recognize the difference:

- **Fragmented:** "- Prefer the smaller library. - Bundle size limit. - Applies to new dependencies."
- **Prose that keeps the logic:** "When two libraries do the same job, add the smaller one, because this package ships inside a bundle with a hard size limit."

### 5.2 Directive, context, and the reason why

Every passage does one of three jobs, and each job has its own register. Where Claude must act, the passage is a directive: an imperative that names the action and its object. A question or a suggestion ("you could", "it may help to") reads as optional, and current models take wording literally: asked to suggest, Claude suggests instead of doing, and they don't infer an action the text didn't ask for. Where Claude must understand something, the passage is context: a fact stated as a fact, tied to what it changes ("The `users` table uses soft deletes, so every query filters `deleted_at IS NULL`"). Where Claude must judge, the directive carries its reason, because a reason is what lets Claude handle a case the skill never named.

The sources point two ways on reasons, and the two can be reconciled. Claude Code's skills page says "State what to do rather than narrating how or why", in a paragraph about conciseness: once a skill loads, every line costs tokens on every turn. The platform and agentskills.io guidance says to explain why, but agentskills.io scopes it to flexible instructions, the platform's low-freedom examples give no reason, and the platform says the value of a reason is that Claude "can generalize from the explanation". Read together, a reason earns its tokens only where there is something to generalize to, which means a judgment call. What Claude Code rules out is narration: an account of how the process unfolds, why the skill exists, or why a fixed step is fixed, none of which changes a decision. One clause that settles a judgment call isn't narration. A paragraph justifying a step Claude must carry out exactly the same way every time is.

When you audit:

- Classify each passage as act, understand or judge, and flag every one whose register doesn't fit: an action written as a question, a suggestion or a description of what "is usually done"; context written as an order with nothing to execute; a judgment call stated as a bare rule.
- Flag every judgment step that gives Claude no basis for an unnamed case. Recommend the shortest reason that would decide such a case, taken from the skill's own purpose, written as "…, because …" on the same line.
- Flag narration: process descriptions, motivation and history that change no decision, and reasons attached to fixed steps. Recommend deleting them, or cutting them to the single clause a judgment needs.
- Flag context that says what is true but not what follows for Claude's work, and recommend the "so …" clause that names the consequence.
- Where a directive is softened into a suggestion even though the skill's purpose needs the action, recommend the imperative, for example "Run `scripts/validate.py` on the output" instead of "You may want to validate the output."

Recognize the difference:

- **Narration:** "This step exists because in the past releases sometimes went out untagged, which caused confusion, so the team decided tags matter."
- **Reason that decides a case:** "Tag the release before you push it, because CI publishes only tagged commits."

### 5.3 Directive strength and weak wording

How firmly a directive is worded should match what one deviation costs. A fragile operation, one where consistency is critical or a sequence must be followed exactly, takes exact, prescriptive wording ("Run exactly this script… Do not modify the command or add additional flags"). A task that allows several valid approaches takes a default plus the room to adapt ("Here is a sensible default format, but use your best judgment"). Most skills mix both, so check each part on its own. A mismatch fails either way: an exact-sounding rule on a matter of taste makes Claude over-constrain, and a soft rule on a fragile step makes the step optional.

Weak wording is a mismatch in the soft direction. Hedges ("try to", "if possible", "consider", "where appropriate") hand Claude the choice of whether to act, and current models follow such qualifiers faithfully: told to "be conservative" or "don't nitpick", a reviewer still finds the issues but reports fewer of them. Catch-all wording and menus of equal options are judged in §4.5 and §4.4. A hedge is correct only where the choice really is Claude's, such as a template it may adapt.

When you audit:

- For each directive, ask what one deviation would cost, given the skill's purpose, and flag every directive whose wording is firmer or softer than that cost.
- Flag every hedge on a step the skill's purpose depends on, and recommend the unhedged directive. Where a real exception exists, recommend naming it: "Run the full suite; run only the changed file's tests when the suite takes longer than five minutes" instead of "Try to run the tests if possible."
- Don't flag a hedge that marks real latitude, such as a template Claude may adapt or a judgment the skill leaves open.

### 5.4 Emphasis: capitals and piled-on absolutes

Current guidance from Anthropic retires emphasis as a tool. Older models sometimes needed IMPORTANT, CRITICAL or ALL CAPS; current ones follow a plainly worded line, and piling on emphasis mostly makes Claude over-apply the rule, carrying it into cases where it shouldn't hold. Anthropic gives the same advice for tool and skill triggering: replace "CRITICAL: You MUST use this tool when…" with "Use this tool when…". An emphasized line that Claude still misses isn't a wording problem. Either the line is lost in a long file, or it's a rule that has to hold with no exceptions, and no wording at any strength guarantees that. A plain absolute word ("never", "always", "exactly") is still the right wording for a rule where any deviation is a failure; what goes is the shouting around it.

When you audit:

- Flag every use of capitals, "CRITICAL", "IMPORTANT", repeated "MUST", or stacked absolutes used for emphasis, and recommend the same rule in plain words at the strength §5.3 calls for: "Never commit `.env`" instead of "NEVER, UNDER ANY CIRCUMSTANCES, commit .env!!!"
- Where emphasis guards a rule that has real exceptions, flag the over-application risk and recommend the plain rule with its exception named.
- Never recommend adding emphasis so a rule gets noticed. Where a rule seems at risk of being missed, recommend plain wording, and where the rule is buried, recommend moving it to where Claude reads it before it acts.
- Don't flag capitals that are literal values, such as a field name, a constant or a command's exact output.

### 5.5 Say what to do, not only what to avoid

To steer what Claude produces, telling it what to do works better than telling it what not to do: "Your response should be composed of smoothly flowing prose paragraphs" works better than "Do not use markdown in your response." A list of prohibitions names the shapes to avoid and leaves the target shape for Claude to guess. Current models follow a short positive instruction about as well as a list of every behavior to avoid, so the list costs lines and buys nothing. A prohibition still belongs where it names one real hazard that Claude would otherwise walk into, like a hard constraint ("never output PII") or a specific trap. Even then, a "don't" with no alternative leaves Claude knowing what to avoid but not what to do instead.

When you audit:

- Flag a run of prohibitions that aims to shape output, style or approach, and recommend the one positive instruction that states what the result contains, written from the skill's purpose, for example "Write the summary as three to five sentences of plain prose, findings first" instead of "Don't use bullets. Don't add headings. Don't be verbose."
- Flag every prohibition that leaves Claude with no permitted path, and recommend adding the alternative in the same sentence: "Don't edit `src/gen/`; regenerate it with `npm run gen` instead."
- Keep prohibitions that guard a specific hazard or a hard constraint; don't recommend turning these into positive phrasing that loses the boundary.

### 5.6 Tone and grammatical person

No official source sets the tone or grammatical person of a skill's body. The third-person rule that applies to the description doesn't extend to the body. The official examples address Claude directly in the imperative ("Use pdfplumber…", "Run exactly this script…"), and that is the pattern to expect, though it's an observed convention, not a stated rule. What matters to Claude is consistency of reference: when "you" means Claude in one paragraph and the user, or the skill's author, in the next, or when "Claude", "you", "the agent" and "the assistant" alternate, Claude has to work out who each sentence is addressed to. A common cause is text pasted from authoring guides that addresses the human writing the skill ("you'll want to test this with your team"). Tone also carries over: the style of a prompt tends to shape the style of the response.

When you audit:

- Check that the body addresses one reader in one person throughout, and flag every switch. Mark a switch that changes who an instruction is for, or that addresses the skill's author instead of Claude, as a real ambiguity, and any other switch as minor.
- Recommend rewriting each off-pattern sentence in the skill's dominant person and mood, with its exact replacement: "Test the output on a real file" instead of "You'll want to make sure your skill gets tested."
- Where the skill produces user-facing text and its own tone contradicts the tone it asks for, flag it and recommend rewriting the examples or instructions that model that output in the target tone.

### 5.7 Wording that goes out of date

Anything time-sensitive in the main instructions becomes wrong without warning: a date cutoff ("before August 2025, use the old API"), "the latest" version, "currently", "the new" anything, or a UI detail likely to be redesigned. Claude can't tell a statement that has gone stale from one that is still true, so it acts on the stale one. The current method belongs in the main instructions, stated without a date. History that is still worth keeping goes in a clearly labeled section, such as "Old patterns", where it can't be mistaken for the current instruction.

When you audit:

- Flag every time-relative claim in the main instructions: dates used as conditions, "latest", "current", "new", "recently", "soon", and version or UI details stated as permanent when they aren't.
- Recommend the stable form: the current method stated without a time reference ("Use the v2 API endpoint: `api.example.com/v2/messages`"), with any history still needed moved under an "Old patterns" heading and labeled deprecated.
- Flag a claim about a specific model's behavior that the instructions depend on, because it goes stale as models change. Recommend stating the behavior the skill needs instead.

### 5.8 Closing loopholes in a discipline skill

Some skills enforce a discipline Claude knows and is tempted to skip under pressure: writing the test before the code, verifying before claiming success, following an exact sequence. In these skills, stating the rule leaves open the workaround it didn't name, so the known workarounds are closed in so many words, next to the rule. The platform's own fragile-step example does this ("Run exactly this script… Do not modify the command or add additional flags"), and Anthropic's agentic guidance names the specific shortcuts to refuse ("don't bypass safety checks (e.g. --no-verify)"; "It is unacceptable to remove or edit tests"). The owner's doctrine goes further. It asks the skill to anticipate the situations in which Claude might rationalize ignoring the rule (user pressure, time pressure, a case that seems different) and to say why the rule still holds under them. The bound comes from current models: a short instruction steers as well as an exhaustive list, so close the workarounds that are likely and leave out the rest. This tool is for disciplines only. Applied to output that comes out in the wrong shape, it turns into the prohibition list of §5.5.

When you audit:

- Decide first whether the skill enforces a discipline Claude is tempted to skip. If it doesn't, don't recommend loophole closing.
- In a discipline skill, check each core rule for the workarounds Claude would plausibly take, and flag each one left open. Recommend the closing sentence next to the rule, grounded in the skill's purpose: "Wrote code before the test? Delete it and start over from the test; don't keep it as a reference."
- Following the owner's doctrine, check that the rule says why it holds under the pressures that tempt Claude to skip it. Where it doesn't, recommend the one sentence that says so, or a short list of the thoughts that signal a rationalization ("It's too simple to test"; "I'll test after").
- Flag loophole lists that run to unlikely cases, and recommend cutting them back to the workarounds Claude would actually take.

Recognize the difference:

- **Open:** "Run the migration script."
- **Closed:** "Run exactly `python scripts/migrate.py --verify --backup`. Don't modify the command or add flags, even when a flag looks harmless."

### 5.9 What a link says about its file, and links to other skills

A pointer is placed at the step that needs it and says when to open the file (§2.5). It also has to say what the file holds, because Claude decides from the pointer alone whether opening the file is worth it, and a file named only by its path gives it nothing to decide with. A descriptive file name carries part of that: `form_validation_rules.md` tells Claude what it will find, `doc2.md` doesn't. Official sources say nothing about how to reference another skill. By the same logic (inference), the reference names the skill the way Claude invokes it, including the plugin prefix where one applies, and says when to use it and what it does for this task.

When you audit:

- Flag every file reference that doesn't say what the file holds, and recommend a short list of its contents: "Before writing queries, consult `references/api-patterns.md` for rate limits, pagination and error codes."
- Flag a supporting file whose name doesn't say what it holds, such as `doc2.md` or `notes.md`, and recommend the descriptive name, with every pointer to it updated.
- Flag every reference to another skill that doesn't name it the way Claude invokes it, or doesn't say when to use it and what it contributes, and recommend the full form: "Before writing implementation code, use `my-plugin:test-driven-development` to write the failing test first."
- In a skill distributed to third parties, flag every reliance on a skill outside its own plugin and the plugins its manifest lists in `dependencies` ("Plugins that must be enabled for this one to work"), because the user may not have it. Recommend naming the skill's plugin in `dependencies`, or writing what the step needs into the skill itself.

---

## Classifying findings

Give every finding four things: the exact file and line(s) in the skill under audit, or where missing text belongs; the point in this file it violates or falls short of; why it is a defect, stated as what Claude would do wrong at that point; and a specific fix, written out, with the reason it's the right one.

Classify each defect into one of four levels by its actual consequence. The examples anchor each level; a finding that doesn't match one verbatim still gets the level its own consequence earns.

- **Critical.** Claude can't form the task at all, or the skill drives it to an action the author never meant that does damage or makes every run fail. For example: a body that never says what Claude is to do; two contradictory instructions for a destructive or irreversible step; a forked skill that depends on conversation history for its whole task.
- **High.** Claude acts wrongly or inconsistently in some runs. For example: a contradiction between `SKILL.md` and a reference; a rule placed after the step it governs; a dead end with no failure path on a step the task depends on; an instruction with two readings that lead to different results; a term used for two concepts; a directive softened into a suggestion where the purpose needs the action; a loop in prose with no way out.
- **Medium.** Claude gets there, but with guesswork, wasted context or less consistency than it should. For example: a duplicate, literal or semantic; a drifting term; a load-bearing instruction buried low; a catch-all phrase; a relative word with no measure; narration that changes no decision; emphasis by capitals; a pointer that doesn't say what its file holds.
- **Low.** A minor weakness with no real consequence. For example: a switch of grammatical person that doesn't change who an instruction is for; a table with one row.

Tie-breaks:

- If a finding fits two levels, the higher level wins.
- Text the skill doesn't need is Medium at most, unless it makes Claude act wrongly.
- When several defects share one root cause, such as a reference file written against an older version of `SKILL.md`, report the root cause once and list every location.
- Never invent impact, never inflate a severity to make the report look decisive, and never lower one because Claude might read the passage correctly anyway.

## Improvement opportunities

Separate improvement opportunities from defects: an opportunity is text the skill's purpose needs and the skill lacks, or a passage that works and a clearer or stronger version from this file would improve. Report every one that genuinely applies to this skill; this section may stay empty only when nothing does. For each one, give what exists now (or that it is absent, and where it belongs), the exact text written out in full, and why it is better for this skill.

This file gives you the criteria, the context to establish, and the severity model. The gotchas and the verification checklist live in your own instructions, and the report template lives in this skill's `assets/` folder, so they aren't repeated here.

## Delivering the report

Deliver every defect and improvement opportunity in the shared findings template, `assets/audit-report.md` in this skill. Fill one defect block per defect, with every field, and keep the template's structure exactly. Defects with one root cause are one defect: give its first location in File and Lines, and list every other location, as `path:lines`, in Finding.
