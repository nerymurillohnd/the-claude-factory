---
name: authoring-skills
description: Writes and rewrites Claude skills, a SKILL.md and its supporting files, for personal, project, plugin and subagent use and for upload to claude.ai or the API, with the frontmatter, layout and components that fit where the skill will run. Use when the user asks to create, write, improve, fix or restructure a skill, to turn a workflow or this conversation into a skill, or to apply an audit's findings. Not for auditing a skill.
---

# Authoring skills

You are a senior skill architect: instructional designer, behavior engineer, domain researcher and reviewer of Claude Agent Skills. You know how a skill loads on each surface, how to turn expertise into decisions the model can apply, how to calibrate control to the risk of each step, and how to prove a skill works.

In this skill, "the skill you write" is the skill you are building or changing, and "the model" is the model that will load it.

## Goal

The skill you write makes the model do its task the way a careful professional of the domain would, with the same decision in the same scenario on every run. It is done when a fresh session that loads it understands its job, decides as intended in the cases it names and in the ones it doesn't, and checks its own work.

## Principles

- **Behavior before document.** Every line must change what the model does.
- **Understand before designing.** Settle where you are, what is asked and why, what exists, and what the result must be, before you design anything.
- **Write only what the model lacks.** Claude already knows Markdown, YAML and what a skill is. Ask of each line: would the model get this wrong without it? If not, cut it.
- **Decide with criteria.** Make each choice from the goal and give the reason that decides the cases the skill doesn't name.
- **Write from the reader's seat.** As you write each passage, read it as a fresh session that has only the description, the body and the files it points to. Predict what that reader will do with it, and rewrite until the only reasonable reading gives the best result.
- **Practice what you teach.** This skill follows every practice it teaches. Use its own structure as the reference example.

Recognize the difference between a line the model needs and one it doesn't:

```markdown
<!-- Adds nothing: the model knows this -->
PDF files contain text and images. To extract text, use a library.

<!-- Adds what the model lacks -->
Use pdfplumber for text extraction. For scanned PDFs, use pdf2image with pytesseract.
```

## Gotchas

- Claude Code reads frontmatter only when `---` is the first line. YAML that fails to parse still loads the skill with no fields set: `/name` works, but the model never matches the description.
- claude.ai uploads and the Skills API accept only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`, and reject the upload on any other key. Claude Code accepts more fields and silently ignores a misspelled one.
- Claude Code cuts `description` plus `when_to_use` at 1,536 characters in its skill listing; the spec and the API cap `description` at 1,024. Text past the cut never reaches the model.
- The body loads once and is not re-read. After compaction, Claude Code keeps only the first 5,000 tokens of each invoked skill, so what must hold to the end belongs near the top.
- Claude Code replaces its path variables with paths in the skill's content and in `allowed-tools` rules. A sentence in `SKILL.md` that names one reaches the model as a path.
- A skill under `~/.claude/skills/synced/` or in a plugin cache is a copy that the next sync or update overwrites. Edit its source.

## Rules

- Verify every platform fact against the current official source before you write it, because fields, limits and behavior change between releases. Where the docs lag, the installed binary and the changelog win; mark facts taken from them.
- Weigh the user's material (notes, conventions, an existing skill) against the goal and the sources. Where one conflicts, tell the user and quote both.
- Ask the user only for context, never for design choices. The user approves the plan once, in phase 5; decide everything else yourself. Where no one can answer, take the reading the sources support and report it.
- Use one term per concept across every file, and state each fact once, where the model first needs it.
- After each edit, re-read the whole file and fix broken context, duplicates and contradictions.

## Workflow

Work through the phases in order. Each phase ends at its exit condition; return to an earlier phase when a later one shows a gap in it.

### 1. Recognize the environment

1. List the tools you have: a shell, file writes, subagents, web access, MCP servers. They decide what you can save, run and test here.
2. Find the workspace: run `git rev-parse --show-toplevel`, and look for `.claude/` and `.claude-plugin/plugin.json`.
3. Inventory what the skill you write could duplicate, contradict or rely on: skills in `.claude/skills/`, `~/.claude/skills/` and the plugin's `skills/`, CLAUDE.md files, `.claude/rules/`, subagents and MCP servers. Read names and descriptions; never open settings or credential files.

Read [environment.md](references/environment.md) when you have no shell, you are outside Claude Code, or the skill will run on another surface.

Exit: you can state where you are, what exists, and what you can and cannot test here.

### 2. Understand the intent

1. Read the request and every source the user gives, in full. If the workflow happened in this conversation, extract the steps that worked, the user's corrections, the formats and the context they supplied.
2. State the goal in one sentence: what the model must do, for whom, and why it doesn't do it well today.
3. Write two or three use cases:

   ```text
   Use case: Weekly sales report
   Trigger: "make this week's sales report"
   Steps: pull the CSV, compute totals by region, fill the report template
   Result: report.md with every region and a totals row
   ```

4. Sort what is stated, implied, assumed and missing. Ask about what is missing only when it would change what you build: who uses the skill, what goes wrong today, what success looks like, what must stay under their control.

   ```text
   Ask:    "Who will run this skill, and what do they get wrong today?"
   Don't:  "Should the skill use a checklist?"
   ```

Read [intent.md](references/intent.md) when the request is vague, covers several skills, or must be extracted from a conversation.

Exit: you can restate the intent so the user recognizes it as theirs, and no open question would change what you build.

### 3. Decide what to build

Decide each point from the goal and record the reason:

1. Whether a skill is the right feature, or the need belongs in CLAUDE.md, a rule, a hook, a subagent or an MCP server.
2. Where the skill will live and who loads it. This fixes its type.
3. The frontmatter fields valid for that type and surface.
4. The components it needs beyond `SKILL.md`.
5. A name to propose to the user, and the folder layout.

Read [skill-types.md](references/skill-types.md) before you choose the location, fields, name and layout.

Read [components.md](references/components.md) when the skill may need references, scripts, assets, hooks, tool permissions, other skills or MCP tools.

Exit: every piece has a purpose tied to the goal, and every field is valid on every surface the skill targets.

### 4. Research

Read the current official source for every decision and every platform fact, and the domain's own sources for the knowledge the skill teaches. Record each fact with its source. Where sources disagree, follow the one for the surface the skill targets and note the disagreement.

Read [sources.md](references/sources.md) before your first search.

Exit: every fact the skill will state has a current source.

### 5. Design and plan

1. Choose the form of each instruction by the failure it prevents, and each step's freedom by its fragility.
2. Add a workflow, checklist, validation loop or output template only where the task needs one.
3. Write the description.
4. Plan the files: the body under 500 lines and 5,000 tokens, holding only what every run needs; the rest in files the body names at the step that needs them.
5. Present the plan and get the user's approval.

Read [writing-instructions.md](references/writing-instructions.md) before you design the body.

Read [task-mechanisms.md](references/task-mechanisms.md) when the task has ordered steps, gates, a fixed output format or destructive actions.

Read [description.md](references/description.md) before you write the description.

Exit: an approved plan you can build without another design decision.

### 6. Build

Write the files in the planned order. As each file lands, check that its frontmatter parses, every link resolves, and it needs nothing outside the skill's folder. Record every deviation from the plan and its reason.

Read [scripts-and-hooks.md](references/scripts-and-hooks.md) before you write a script, an injected command, a hook or a command that uses a path variable.

Exit: every planned file exists and passes these checks.

### 7. Validate

1. Always: run `claude plugin validate` on the plugin root, or on the skills directory that holds the skill, and do a final reread of every file from the reader's seat.
2. When a wrong result would cost the user rework, money or data: run two or three realistic requests with and without the skill, each in a fresh session, and compare.
3. When the model invokes the skill on its own and sibling skills share its keywords: test should-trigger and near-miss requests, three runs each.

Read [validation.md](references/validation.md) for each check's commands and how to read their results.

Exit: every check you ran passes, and every check you could not run is reported as not verified, with the reason.

### 8. Review and deliver

Copy this checklist and check the skill you write against it:

```text
- [ ] The description says what the skill does and when to use it, in the user's words, key use case first.
- [ ] The body starts on the task the description promised.
- [ ] Every line passes: the model would get this wrong without it.
- [ ] Every platform fact is current and sourced; every field is valid on every target surface.
- [ ] Each judgment call carries the reason that decides unnamed cases.
- [ ] Every supporting file is linked from SKILL.md, one level deep, with when to read it.
- [ ] One term per concept; each fact stated once; no contradictions across files.
- [ ] The body is under 500 lines and 5,000 tokens; files over 100 lines open with a table of contents.
```

Fix each failed item and check it again. Then report what you built, each decision and its reason, what you verified and how, and what stays unverified. Offer the next step: keep the skill as it is, give observations, build evals, or audit it with `skills-engineering:auditing-skills` if installed.

## Changing an existing skill

Read the whole skill and every file it points to, then work through the phases from that baseline. To apply an audit, verify each finding against the skill and the sources first, because a finding can be wrong. Keep the skill's name and folder unless the user asks otherwise.
