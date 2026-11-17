# Knowledge delta

This file teaches you how to audit whether every passage of a skill gives Claude something it lacks without the skill, and how to tell a passage that only spends context from one that must stay. Each section gives you the principle, why it matters, and what to do when you audit.

## Contents

- How to use this file
  - Before auditing: establish the context
  - Then, audit passage by passage
- 1. What a skill is for
  - 1.1 The one test every passage answers
  - 1.2 What Claude lacks without the skill
  - 1.3 What the skill should add
- 2. Passages that add nothing
  - 2.1 General knowledge
  - 2.2 Behavior Claude already has
  - 2.3 Instructions written for older models
  - 2.4 What Claude can find on its own
- 3. Passages that must stay
  - 3.1 Facts that are new or that changed
  - 3.2 Gotchas and corrections
  - 3.3 The reasons behind a judgment
- 4. When the delta is uncertain
  - 4.1 Mark it for a baseline instead of cutting it
  - 4.2 The models the skill serves
- 5. Passages that make Claude worse
- 6. The skill as a whole
- Classifying findings
- Improvement opportunities
- Delivering the report

## How to use this file

Read this whole file, through its final section, "Delivering the report", before you judge anything. This complete reading, and an audit of the skill against every point in it, are a precondition of your audit: no point stays unaudited. Keep to the file's order: first establish the context, then audit passage by passage, then classify what you found.

Audit from the seat of a Claude that loads the skill with no prior context and has to use it. For every passage, ask what that Claude would do if the passage weren't there. Where it would do the same thing, the passage costs context and gives nothing back. Where it would do something worse, the passage earns its place.

The prompt you receive may carry leads from Claude Code's own instruction audit, such as wording written for older models. Treat them as leads to verify against this file, never as findings. You never run or measure anything yourself, and you never run the skill: a point that only running the skill can settle is reported as unverified, with the check that would settle it (§4.1).

### Before auditing: establish the context

What Claude lacks depends on the skill in front of you, so settle these five points before you judge any passage.

1. **Where the skill lives.** A personal, project, plugin or managed skill, or one uploaded to an account. A project skill can count on the repository being readable; an uploaded skill may not, which changes what Claude can find on its own (§2.4).
2. **How the skill gets invoked.** In the main conversation it sees the history so far; forked or preloaded into a subagent it starts with no history, so it can count on less, and context the conversation would have supplied becomes content it lacks.
3. **Which surfaces load it.** What the runtime around the skill provides, such as a repository, a shell or the network, decides what Claude can look up instead of being told.
4. **What the skill is for**, from its own description and body: the task, the user it serves, and the domain. A passage is judged against this purpose, never in the abstract.
5. **Which models it serves.** A `model` field, the plugin's or the user's stated models, or none named. Less capable models need more guidance than more capable ones (§4.2).

### Then, audit passage by passage

Audit what the skill has and what it should have: cutting what adds nothing is half the audit, and finding what Claude lacks and the skill doesn't say is the other half. Go through every passage of `SKILL.md` and of every file it points to that Claude reads, then walk the task the skill covers for what it should add (§1.3), and give each item exactly one of these outcomes:

- **Present and optimal.** It gives Claude something it lacks, and only that. Record no finding.
- **Present but wrong.** It restates what Claude already knows or does, or misleads Claude where its own default was right. Record it as a defect, classify it (see "Classifying findings"), and say whether it must be deleted or rewritten.
- **Present, right, but improvable.** It carries something Claude lacks, wrapped in material Claude doesn't need. Record it as an improvement opportunity, with the passage reduced to what Claude lacks.
- **Absent, and the skill's purpose needs it.** Claude would fail at a point of the task the skill covers, and the skill is silent. Record it as an improvement opportunity: say where it belongs, what it should contain, and the point of this file it rests on.
- **Absent, and the skill's purpose doesn't need it.** Record no finding.

Work only from what is written in the skill. If you have no passage to point to, you have no finding; for a gap, point to the step where it belongs.

---

## 1. What a skill is for

### 1.1 The one test every passage answers

A skill exists to change what Claude does. Once invoked, its content stays in the conversation for the rest of the session and competes with the conversation, the system prompt and every other loaded skill for Claude's attention, so every line is a recurring cost. A passage that changes nothing pays that cost every turn for nothing, and it dilutes the passages that do matter.

The test for every passage is one question: would Claude get this wrong without it? If not, the passage goes. If you can't tell, the passage is tested before it goes, never cut on a guess (§4.1).

When you audit:

- Ask the question of every passage, including headings that only announce, transitions and closing summaries.
- Judge the passage against the skill's purpose and runtime, from §"Before auditing", not against what a skill in general would need.
- Flag a passage that changes nothing. Recommend deleting it, or reducing it to the clause that does change something.

### 1.2 What Claude lacks without the skill

The content that earns its place is what Claude can't know or infer without the skill:

- conventions specific to this project, team or organization;
- procedures specific to this domain, and the order they must follow;
- non-obvious edge cases and the corrections the author had to make;
- which tool, API, script or library to use, when several would work;
- decisions that aren't written anywhere Claude can read;
- facts about the environment that defy a reasonable assumption;
- facts that are new, or that changed, since Claude learned the subject (§3.1).

When you audit:

- Confirm that each passage you keep falls in one of these, and name which one when it is not obvious.

Recognize the difference:

**Adds nothing:** "PDF (Portable Document Format) files are a common file format that contains text, images and other content. To extract text, you'll need a library."

**What Claude lacks:** "Use pdfplumber for text extraction. For scanned documents, fall back to pdf2image with pytesseract."

### 1.3 What the skill should add

A skill is written to close the gap between what Claude knows and what the task needs. A skill that only avoids waste can still leave Claude failing where it is silent, so look for those gaps as hard as for waste: each one is knowledge Claude lacks, at a step where it acts on it.

When you audit:

- Walk the task the skill covers step by step, and at each step ask what Claude needs there that it can't know or infer on its own, by the categories of §1.2.
- Look first where Claude is most likely to be wrong: tools and platforms whose versions, limits, fields and defaults change; choices of this project or organization; facts about the environment that defy a reasonable assumption; and points where several tools or approaches would work and only one is right here.
- Recommend each addition at the step that needs it, with its content written out and its grounds in the skill's purpose. Verify every fact you propose against its current official source.
- When reading can't confirm that Claude would fail without the addition, recommend it as unverified, with the baseline comparison that would settle it (§4.1).
- Never propose an addition the skill's purpose doesn't call for, and never one that is general knowledge or default behavior (§2).

Recognize the difference:

**Silent where Claude would fail:** "Bump the version, then tag the release."

**What Claude lacks, at the step:** "Bump the version only in `plugin.json`; the catalog carries none. Tags take the form `<plugin>--v<version>`."

## 2. Passages that add nothing

### 2.1 General knowledge

Claude already knows what common file formats, protocols, languages and tools are and how they work in general. Explaining them spends the context the skill needs for what Claude doesn't know.

When you audit:

- Flag definitions of common terms, explanations of how a well-known technology works, and background a practitioner of the domain wouldn't need.
- Flag a reason that only states general knowledge, such as "because tests catch bugs before production".
- Keep a definition the skill uses in a sense specific to the project, and say so in the outcome.

### 2.2 Behavior Claude already has

A line that asks Claude to do what it does by default doesn't change what it does: "write clean, readable code", "be careful", "make sure the output is correct", "think through the problem", "be thorough".

When you audit:

- Flag each instruction that asks for behavior Claude shows without being told.
- Keep an instruction that sets a specific bar Claude couldn't guess, such as a project's own definition of done or the exact check to run. Recognize it by whether it names something concrete.

Recognize the difference:

**Default behavior:** "Remember to write clean, readable code with meaningful variable names."

**A specific bar:** "This repository's lint configuration forbids default exports: use named exports only."

### 2.3 Instructions written for older models

Some instructions were workarounds for what older models couldn't do reliably, and current models no longer need them. Claude Code's own documentation lists them: emphasis such as IMPORTANT or capitals added because a rule kept being missed, "keep going", "loop until done" or "don't be lazy", phrases such as "think hard" used to raise effort, and descriptions of an architecture or file layout Claude can read itself. They spend context and, in the case of emphasis and of telling Claude to keep going, push it to over-apply a rule or over-work a task.

When you audit:

- Flag each such instruction, and say what it costs: the context alone, or the over-application the documentation describes.
- Where the instruction protects a rule that must hold every time, or a check the task must pass, say that the need is real and the instruction is the wrong carrier for it, and leave the choice of carrier out of your fix: delete the workaround and keep the rule or check stated once, plainly.
- Note that `ultrathink` still works as a request for deeper reasoning on one turn: it is not a leftover.

### 2.4 What Claude can find on its own

A skill doesn't need to copy what Claude can read when it needs it: a project's files and layout, a tool's built-in help, a file the skill already bundles. A copy goes stale when the original changes, and the original was always there.

When you audit:

- Flag a passage that copies what Claude can reach on the skill's runtime, and recommend telling Claude where to look and when, in one line.
- Before you flag, confirm from §"Before auditing" that Claude can reach the original on every runtime the skill targets. A skill that runs where the repository or the tool isn't available, or that runs without network access, may need the copy: then it stays.
- Keep what the original doesn't say and the skill must: which option to use, which output to trust, which step comes first.

## 3. Passages that must stay

### 3.1 Facts that are new or that changed

What Claude knows about a tool, platform or library comes from what it learned, which stops at a date and may describe an older version. A version number, a limit, a field, a flag, a default, a renamed command or a deprecated pattern that changed is something Claude would get wrong without the skill, even when the subject looks familiar. This is an inference from the test in §1.1: Claude would get an outdated fact wrong without the passage, so the passage passes the test.

When you audit:

- Never flag as general knowledge a passage that states a current version, limit, field, flag, default, name or deprecation of a tool or platform.
- Verify each such fact against the current official source. When it is wrong, report it as content that makes Claude worse (§5), not as content to cut.
- Recognize that a passage can be familiar in subject and new in detail: keep the detail and cut the familiar wrapping around it.

### 3.2 Gotchas and corrections

A gotcha is a concrete fact about the environment that defies a reasonable assumption, such as a table with soft deletes, an identifier with a different name in each service, or a health check that reports healthy while a dependency is down. It is often the most valuable content in a skill, because it is exactly what Claude gets wrong without being told. A correction the author had to make while using the skill belongs to the same kind.

When you audit:

- Never flag a real gotcha or correction as redundant.
- Flag a "gotcha" that is general advice, such as "handle errors appropriately": it has the form of a gotcha and the content of default behavior (§2.2).

### 3.3 The reasons behind a judgment

The reason attached to a step that calls for judgment tells Claude something it can't know: why this skill makes this choice, so it can extend the choice to a case the skill didn't name. That reason is the author's knowledge, not Claude's.

When you audit:

- Keep the reason attached to a judgment step when it is specific to this skill, its users or its environment.
- Flag the reason only when it states general knowledge (§2.1).

Recognize the difference:

**A reason Claude lacks:** "Pick the lighter dependency when two libraries do the same job: this skill runs inside a size-constrained bundle."

**A reason Claude has:** "Pick the lighter dependency, because smaller dependencies are generally better."

## 4. When the delta is uncertain

### 4.1 Mark it for a baseline instead of cutting it

Your own knowledge is not proof of what the model running the skill knows or does by default. When you can't tell whether Claude would get a passage wrong without it, the official guidance is to test it. The test runs the same realistic tasks with the skill and without it, or with the previous version, and compares the results: a check that passes in both runs shows the content behind it isn't what made it pass, and one that passes only with the skill shows where the skill adds value. Claude Code's `claude plugin eval` runs this comparison for a plugin and reports both scores and the difference.

When you audit:

- Mark a passage whose delta you can't settle by reading as unverified, and recommend the baseline comparison that would settle it, naming the task and what to compare.
- Never recommend cutting an uncertain passage on your own judgment.
- When the skill ships evaluations or a recorded baseline, read them: a check the skill's own baseline shows passing without the skill is evidence that its content adds nothing there.

### 4.2 The models the skill serves

A skill is an addition to a model, so what it must add depends on the model. Guidance that a more capable model doesn't need can be what a less capable one needs to succeed.

When you audit:

- Judge each passage against the least capable model the skill states it serves.
- When the skill names no model, judge against current models, and mark as unverified any cut whose safety depends on which model runs it.
- Never flag as redundant guidance the skill keeps on purpose for a model it names.

## 5. Passages that make Claude worse

A passage can do more than add nothing: it can replace a correct default with a wrong one. A restated tool syntax that is outdated, a general rule narrowed in a way that doesn't fit the task, or a workaround that pushes Claude to over-apply a rule, all lead Claude to do worse than it would without the skill.

When you audit:

- Flag every passage that tells Claude something it would have gotten right on its own, and gets it wrong. Verify the correct version against the current official source and give it with its URL and section.
- Choose the fix by what Claude lacks: when Claude's default was right and nothing remains to add, delete the passage; when the skill needs the fact, rewrite it correctly.
- Flag an instruction from §2.3 whose documented effect is over-application or over-work as harm, not only as a cost.

## 6. The skill as a whole

When Claude already handles the skill's whole task well without it, the skill may not be adding value. When most of a skill is general knowledge or default behavior, the few passages Claude lacks are buried among those that add nothing.

When you audit:

- After the passage-by-passage audit, judge what remains: list what the skill would keep if every flagged passage went.
- Flag a skill in which almost nothing Claude lacks remains, and recommend the baseline comparison (§4.1) before anyone keeps or retires it.
- Flag a skill whose purpose needs knowledge Claude lacks and that carries little of it, with what is missing and where it belongs.

---

## Classifying findings

Give every finding four things: the exact file and line(s) in the skill under audit, the point in this file it violates or falls short of, why it is a defect stated as a consequence, and a specific fix with the reason it's the right one. If you have no passage to point to, you have no finding.

Classify each defect into one of four levels by its actual consequence. The examples below anchor each level; a finding that doesn't match one verbatim still gets the level its own consequence earns.

- **Critical.** Makes Claude do the task wrong every time it follows the skill, where it would have done it right without the skill. For example: a restated command, field or flag that is outdated or wrong, in a step Claude follows on every run.
- **High.** Makes Claude do worse than without the skill in some runs, or defeats the skill's purpose. For example: emphasis or "keep going" instructions whose documented effect is over-application or over-work; a general rule narrowed in a way that misleads Claude in cases the skill covers; a skill whose content is almost all general knowledge or default behavior, so it adds nearly nothing it was written for.
- **Medium.** Spends context on content Claude already has, without making it wrong. For example: definitions of common terms; instructions for default behavior; instructions written for older models with no documented harm; content Claude can read on the skill's runtime; the same fact stated in two places; a passage whose delta you couldn't settle by reading (§4.1).
- **Low.** A clause or sentence of filler inside a passage that is otherwise needed. For example: an announcing sentence before a list, or a closing restatement of the section above it.

Tie-breaks:

- If a finding fits two levels, the higher level wins.
- A passage that only spends context never rises above Medium; only a passage that makes Claude worse can be Critical or High.
- An unverified passage is Medium. Name in its finding the level it would reach if the baseline shows it adds nothing, and the level it keeps if the baseline shows it is needed.
- Never invent impact, never inflate a severity to make the report look decisive, and never lower one because Claude might ignore the passage. When several passages share one root cause, such as a skill written for an older model throughout, report the root cause once and list every location.

## Improvement opportunities

Separate improvement opportunities from defects: an opportunity is a passage that gives Claude something it lacks but could give it in less, or knowledge the skill's purpose needs and the skill lacks. Report one only where it genuinely applies to this skill; this section of your report may stay empty. For each one, give what exists now (or that it is absent, and where it belongs), what this file recommends instead, as the actual reduced passage or the content to add, and why that's better for this specific skill, given its purpose, its runtime and its models.

This file gives you the test, the categories, the context to establish, and the severity model. The gotchas and the verification checklist live in your own instructions, and the report template lives in this skill's `assets/` folder, so they aren't repeated here.

## Delivering the report

Deliver every defect and improvement opportunity in the shared findings template, `assets/audit-report.md` in this skill. Fill one defect block per defect, with every field, and keep the template's structure exactly. Passages with one root cause are one defect: give its first location in File and Lines, and list every other location, as `path:lines`, in Finding.
