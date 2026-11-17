---
name: authoring-skills
description: Writes new Claude Agent Skills and changes existing ones, for every kind of skill and location, grounded in the domain's own material and the current platform docs. Use when the user asks to create, write, build, draft or design a skill, turn a workflow, prompt or repeated correction into one, or extend, rewrite or apply review findings to one. Not for auditing or reviewing a skill.
---

# Authoring skills

You engineer a skill: a set of files that changes how another Claude behaves, in sessions and on machines you will never see. You own the result, from the request to the delivered files. The failure this skill prevents is the common one: a skill that restates what Claude already does, follows a generic template, guesses at platform facts, and reads clearly only to its author.

## Gotchas

- Claude writes the skill format without help. The value you add is in the decisions (whether a skill is the right feature, what goes where, what the description routes) and in grounding, never in the format itself.
- A skill drafted from general knowledge adds nothing: the reader is the same model that wrote it. What Claude lacks is the user's domain, their corrections, their environment and the platform facts that changed after training.
- The user's own corrections ("no, we always do it this way") are the highest-value content a skill can hold. Ask for them, and look for them in the material they give you.
- After writing, you know what you meant, so gaps stay invisible to you. The reread step reads the files as a Claude who has only the description and the text.
- A skill that ships to other people runs where paths, tools, plugins and account skills differ from yours. Write for the target environment, never for the session you are in.
- Platform facts move faster than training data: field names, limits, which surface accepts what. Check each one against the current official page before you write it.

## 1. Understand the request

Before designing anything, establish these, from the request, the material provided and the workspace first, and ask the user only what none of those answers:

- The job: what the skill makes Claude do or know, for whom, and what its output feeds.
- The gap: two or three realistic requests the skill must handle, and what Claude does wrong on each today without it. These are the gap requests; the later steps and the guides test the design against them. If you can't name a gap, the skill may not be needed: say so, and wait for the user to decide whether to proceed.
- The discipline: which profession or professions govern the work, how each defines good work, and what errors are frequent and costly in it. The higher the cost of an error, the more evidence, verification and human control the skill must require.
- The setting: which surfaces will run it (Claude Code, the Claude app, the API, the Agent SDK), how it is invoked (by Claude, by the user, both, or by another skill or subagent), where it will live (personal, project, plugin, managed, an upload) and who else receives it.
- The material: the user's documents, examples, corrections, project files and existing skills on the topic. Read what's relevant in full; keep its terms, distinctions and requirements instead of replacing them with generic practice.
- The control line: which actions the skill may take on its own and which stay with the user.

When the request is to change an existing skill, first find where its source lives: the repository or plugin source it is built from, or the claude.ai account for a synced skill. Never edit a synced copy or an installed plugin copy: the next sync or update replaces it and the change is lost. If only such a copy is reachable, say so and deliver the changed files for the user to upload or commit. Then read the whole skill, every file, and treat a list of findings as input to weigh, not as orders: a finding can be wrong for this skill's setting. For a change confined to one part of a skill, research only the platform facts the change touches, and read only the guides in step 3 that govern that part.

Separate what is stated, what is implied, what you assume and what is missing. Ask focused questions only for what changes the design; state every assumption you take.

## 2. Research

Research the domain and the platform before writing, and keep track of which fact came from where.

- Domain first: the user's material, the project's own files and conventions, and the official documentation or standards of the field the skill serves.
- Platform: read these whole, not as search snippets, because the detail that decides a case is rarely in the first paragraph:
  - Claude Code skills: `https://code.claude.com/docs/en/skills` (append `.md` to any `code.claude.com/docs` page for its Markdown source).
  - Skill authoring best practices: `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`.
  - Agent Skills specification: `https://agentskills.io/specification`.
  - The pages for any other feature the design touches: subagents, hooks, plugins, permissions, settings.
- How to read them: if a documentation server for Claude Code is connected, use it to find the right pages; read each page whole by downloading its Markdown when you have a shell or fetch tool, because a summarizing fetch can drop the sentence you need. If nothing can reach the web, write the platform facts you rely on as unverified and say so in the delivery.
- Versions: when the skill targets Claude Code, find the installed version (`claude --version`) and read the changelog entries for it and the releases around it; a release note beats an older docs sentence and your memory.
- Tools: discover what the target environment has (connectors, MCP servers, CLIs, other skills) instead of assuming. When a source or tool fails, find out why, use an equivalent route, and report what stayed unverified; never retry blindly or route around a security boundary.

A source applies only within its own scope, date and surface: a fact for the Claude app may not hold in Claude Code, and the reverse.

## 3. Decide the design

Read each guide below when its condition holds, before writing the part it governs. Each one gives the decisions, the criteria, what each choice costs, and the questions to ask yourself.

- Always, first: [references/scope-and-type.md](references/scope-and-type.md), whether this should be a skill, its boundaries, type, location, surfaces, and how it runs alongside subagents and other skills.
- Always: [references/name-and-description.md](references/name-and-description.md), the name, the description that routes requests to the skill, `when_to_use`, and arguments.
- When any frontmatter field beyond `name` and `description` is on the table, or the skill must load on more than one surface: [references/frontmatter.md](references/frontmatter.md). For the facts about each field (which surface accepts it, its values, its defaults), read the shared table at `${CLAUDE_PLUGIN_ROOT}/skills/auditing-skills/references/skill-types-and-frontmatter.md`, whole; if that path doesn't resolve, take the field facts from the official pages in step 2 instead.
- Always: [references/structure-and-files.md](references/structure-and-files.md), the body's order, what goes in `SKILL.md` and what in other files, how files point to each other, path variables and size budgets.
- When the skill runs a task with steps, side effects or an output someone consumes: [references/task-mechanisms.md](references/task-mechanisms.md), workflows, checklists, validation loops, plan-validate-execute and output templates.
- When any computation repeats the same way every run, a command runs before Claude reads the body, or a rule must hold every time: [references/scripts-and-hooks.md](references/scripts-and-hooks.md).
- Always, before writing prose: [references/writing-the-body.md](references/writing-the-body.md), what earns a place in the text, and how to word it so Claude reads it one way.

Adapt the design to the discipline from step 1. A skill usually needs some of these, weighted by its job: who Claude is in the task and what it owns; the mission and the failures it prevents; principles with their reasons; how it gathers information; how it decides and acts; how it verifies; what it delivers. These are dimensions to weigh, not sections to fill: a reference skill may need two of them, a release skill all of them.

## 4. Write

Write the files from the decisions, in this order: the frontmatter, the body of `SKILL.md`, then each supporting file at the moment the body first points to it. Keep a short note, for the delivery, of why you made each structural choice (why this content sits in a reference, why this step has a checklist, why this field is set).

When you change an existing skill, change the smallest set of passages that fixes the problem, and carry each change through every place that states the same fact.

## 5. Reread as a fresh Claude

Read the result the way Claude meets it, forward only and with no memory of writing it: the description alone first, then the body top to bottom, then each file only at the step that points to it. After the pass, write down the model you'd form:

- Purpose: what the skill is for, from the description alone, and whether it would be invoked for the gap requests from step 1.
- Entry point: where Claude starts, and what it needs to know before starting.
- First action: the first thing Claude does, unambiguously.
- Sequence: each step, its input and its exit, with no step that depends on a later one.
- Concepts: every term, file and tool named, each defined before it is used.
- End state: what done looks like, and what Claude delivers.

Where you can't fill one of the six, or have to guess to fill it, that's a defect: fix the text and read again from the top. Stop when two passes in a row find no new defect. If the same defect returns three times, the design is the problem, not the wording: go back to step 3. If it returns after the redesign, stop and report the defect to the user.

## 6. Verify before delivering

Every item must be true, with the file and line you checked. On a failed item, fix it and return to step 5. If an item can't be made true, such as a fact no source can confirm, deliver with that item listed under what you couldn't verify.

- Each platform fact (field, limit, path, behavior) traces to a source you read in this task, or is marked unverified.
- Every passage you judged Claude would do correctly without it is cut; every passage you couldn't judge is marked for comparison.
- Every file in the skill's folder is pointed to from `SKILL.md`, with what it holds and when to read it, and every pointer resolves.
- No frontmatter field is one a target surface rejects, and the YAML parses with no quoting surprises.
- The description says what the skill does and when to use it, in the words users type, with a boundary wherever a sibling skill competes, inside the length limits.
- Each rule sits at the step it governs; no fact is stated twice; one term per concept.
- Every action with an outside effect states who decides it.
- Every script runs non-interactively, and you ran each one at least once.
- The skill depends on nothing that exists only in your own session: no personal paths, account skills or tools the target environment lacks.

A file that passes a validator only proves it parses; the validator doesn't read the instructions.

## 7. Deliver

Give the user:

- The files, with their paths.
- The decisions and their reasons, from your notes in step 4.
- What you assumed and what you couldn't verify, and what each affects, including the passages marked for comparison.
- The next steps: run `skills-engineering:auditing-skills` on the result, then test the behavior on the gap requests from step 1, with `claude plugin eval` for a skill inside a plugin or with a skill-testing tool such as skill-creator otherwise. Don't claim the skill was tested unless it was.
