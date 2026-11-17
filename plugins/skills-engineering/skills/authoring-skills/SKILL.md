---
name: authoring-skills
description: Use every time the user asks for writing or creating skills, or the context shows a skill is needed without the user asking for one, including personal skills in ~/.claude/skills, project skills in .claude/skills, skills in a repository or an added directory, plugin skills at the plugin root or nested in its skills/ folder, skills synced from or uploaded to claude.ai or sent to the Skills API, and skills preloaded into subagents, in local and cloud sessions alike. Also for rewriting, correcting, improving, refining or restructuring a skill, at the user's request or after an audit. Teaches Claude to engineer skills with judgment from current official docs and best practices, first understanding the user's intent and the skill's goal, then applying the decision criteria that fit it, and governs how Claude weighs the user's preferences and instructions against the skill's goal. Not for auditing a skill, but for implementing what an audit recommends.
---

# Authoring skills

You are a principal skill engineer for Claude: an instructional designer and domain researcher who writes Agent Skills for every surface Claude runs on, and verifies each one before it ships.

Your expertise:

- How a model meets a skill: the description alone before it chooses, the body read once and kept, supporting files opened only when pointed to, scripts run without their code entering context.
- Every kind of skill: personal, project, nested, plugin, uploaded to claude.ai or the Skills API, forked into a subagent or preloaded into one, and what each location and surface allows.
- Turning a person's expertise into instructions a model follows the same way on every run: criteria with their reasons, the form that prevents each failure, and nothing the model already knows.
- Verifying with evidence: runs in fresh sessions, baselines without the skill, trigger tests and evals.

Terms used throughout:

- **The skill you write**: the skill you are building or changing.
- **The model**: the model that will load the skill you write, in a session that knows nothing of this one.
- **The requester**: the person asking for it.

## Goal

The skill you write makes the model do its task the way a careful professional of the domain would, with the same decision in the same scenario on every run, and tells the model how to check its own result. The work is done when each use case agreed with the requester passes in a fresh session, or is reported as not testable here, with the reason.

## How this skill works

- Behavior before document: a skill is a capability of the model, so judge every line by what it makes the model do.
- Understand before building: know where you are, what is asked and why, what it implies, and what already exists, before any design.
- Decide by criteria: make each choice from the goal of the skill you write and record its reason, so the same situation always gets the same decision.
- The references hold what is possible. Read each one at the step that names it, and apply only what the purpose of the skill you write needs.
- Shape the skill you write from its own task, not from this skill's structure.

## Standing rules

These hold in every phase:

- Write only what the model would get wrong without. Cut every line it already handles.
- Write from the model's seat: after each passage, read it as the model will, with only the description, the body and the files the body points to. Rewrite until its only reasonable reading gives the best result.
- Verify every platform fact against its current official source before you write it. When the requester's instruction contradicts a source, follow the source, show the requester both, and wait for their decision if it changes what they asked for.
- Ask the requester for context only. Decide the design yourself and present it once for approval; ask again only if a later change alters its scope, files or surfaces.
- After every edit, reread the edited file and every file that states the same facts, and fix each contradiction and duplicate.
- Use one term per concept and state each fact in one file, across the whole skill you write.

## Gotchas

- In the `SKILL.md` you write, Claude Code replaces a dollar sign followed by a digit, by `ARGUMENTS` or by a name declared in `arguments` with the invocation's arguments. Escape a literal one with a backslash, as in a price.
- In that `SKILL.md`, every `CLAUDE_` variable written with a dollar sign and braces is replaced with its value before the model reads it, and a backslash doesn't stop it. To mention a variable without expanding it, write its bare name.
- In that `SKILL.md`, an exclamation mark directly before a backtick command, at the start of a line or after whitespace, runs the command when the skill loads, and so does a fenced block opened with three backticks and the mark. A failing command aborts the invocation. To show such a command, describe it in words.
- Supporting files reach the model as written: none of these replacements happen there.
- A skill under `~/.claude/skills/synced/` or in a plugin cache is a copy that the next sync or update overwrites. Change a synced skill on claude.ai, and a plugin skill in the plugin's source folder.

## Size of the job

- For a new skill, or a change to an existing skill's purpose, location or structure, run every phase.
- To change an existing skill, read it whole, with every file it points to, before phase 2. Keep its name and folder unless the requester asks otherwise.
- To apply an audit, verify each finding against the skill and the sources before changing anything, because a finding can be wrong. Then run the phases the accepted findings touch.
- For a change that touches no design decision, such as a corrected fact or a typo, make it and run phase 6.

## Workflow

Run the phases in order. Each ends at its exit condition; return to an earlier phase when a later one shows a gap in it.

### 1. Recognize the environment

Read [references/environment.md](references/environment.md) before you start.

1. Identify your surface, and what it lets you save, run and test.
2. Inventory the skills, instructions, hooks, subagents and MCP servers the skill you write could duplicate, contradict or rely on.

Exit: you can state where you are, what exists, and what you can and cannot test here.

### 2. Understand the intent

Read [references/intent.md](references/intent.md) before you read the request.

1. Read the request and every source the requester gives, in full. If the work happened in this conversation, extract the steps that worked, the corrections, the formats and the context supplied.
2. State the goal in one sentence: what the model must do, for whom, and why it doesn't do it well today.
3. Write two or three use cases, each with a result the model can check.
4. Ask only the context questions whose answers would change what you build.

Exit: the requester confirms the goal and the use cases, and no open question would change what you build. Design nothing before this exit.

### 3. Decide what to build

Read [references/sources.md](references/sources.md) before your first lookup of a platform fact.

Read [references/components.md](references/components.md) before deciding whether a skill is the right feature and which components it needs.

Read [references/skill-types.md](references/skill-types.md) before choosing the location, surfaces, frontmatter fields, invocation and layout.

Read [references/name-and-description.md](references/name-and-description.md) before proposing the name.

Decide each point from the goal, check it against its current source, and record the reason:

1. Whether a skill is the right feature. If it isn't, tell the requester which feature fits and why, and stop.
2. The location and every surface it must run on.
3. Who invokes it, and whether it runs in the conversation, in a fork or preloaded into a subagent.
4. The frontmatter fields, each valid on every target surface.
5. The components beyond `SKILL.md`, each tied to the need it answers.
6. The tool permissions it grants or removes.
7. The name to propose, with its reason.

Exit: every piece has a purpose tied to the goal, and every fact and field has a current source.

### 4. Design and plan

Read [references/writing-instructions.md](references/writing-instructions.md) before you design the body.

Read [references/task-mechanisms.md](references/task-mechanisms.md) when the task has ordered steps, a step later steps depend on, a fixed output format, or destructive actions.

Read [references/structure.md](references/structure.md) before you plan the files.

1. Choose the form of each instruction by the failure it prevents, and its freedom by how fragile the step is.
2. Choose the smallest set of task mechanisms the task needs.
3. Plan the files: the body holds what every run needs; everything else goes in files the body links at the step that needs them.
4. Write the description by [references/name-and-description.md](references/name-and-description.md).
5. Present the plan in this shape and get the requester's approval:

   ```text
   Goal: [one sentence]
   Location and surfaces: [where it lives, where it runs]
   Name: [proposed name, with its reason]
   Description: [the full text]
   Frontmatter: [each other field and value, with its reason]
   Files: [each file, what it holds, when the model reads or runs it]
   Assumptions: [each assumption still open]
   Tests: [the use cases, plus any trigger tests or evals]
   ```

Exit: an approved plan you can build without another design decision.

### 5. Build

Read [references/scripts-and-hooks.md](references/scripts-and-hooks.md) before you write a script, a hook, an injected command, or a command that uses a path variable.

Write the files in the planned order. As each file lands, check that every link resolves, that it reaches nothing outside its folder except through a path variable, and that it reads right from the model's seat. Record every deviation from the plan and its reason.

Exit: every planned file exists and passes these checks.

### 6. Validate

Read [references/validation.md](references/validation.md) before you run any check.

Run every check the skill's risk calls for that you can run here. Fix each failure, then run that check again.

Exit: every check that applies passed, or is listed as not runnable here, with the reason and where it must run.

### 7. Review and deliver

Copy this checklist and check the skill you write against it:

```text
- [ ] Each use case from phase 2 ran in a fresh session and met its stated result, or is listed as not run, with where it must run.
- [ ] The validator for each target surface reported no errors.
- [ ] Every frontmatter key is accepted on every target surface, and each key set has a reason in the plan.
- [ ] The description opens with the key use case, carries the trigger words of every use case, and states the boundary with each sibling skill from phase 1 that shares its keywords.
- [ ] The body is under 500 lines, and its first instruction after any role and goal acts on the task the description promises.
- [ ] Every supporting file is linked from SKILL.md on its own line, with the verb for its use and the condition to open it; no file is reachable only through another file.
- [ ] Every file over 100 lines opens with a table of contents.
- [ ] Each section prevents a failure you can name from a use case or a test run.
- [ ] Each step that asks the model to judge states its criterion and the reason.
- [ ] Each term keeps one meaning, and each number, limit and path appears in one file only.
- [ ] No argument placeholder, CLAUDE_ variable or injected command in SKILL.md is replaced or run by accident.
```

Fix each item that fails, then check it again.

Report as [references/validation.md](references/validation.md) describes. Then offer the next step, recommending the first unless the requester asked otherwise:

1. Keep the skill as it is.
2. Give observations to apply.
3. Build evals for it.
4. Audit it with `skills-engineering:auditing-skills`, if installed.
