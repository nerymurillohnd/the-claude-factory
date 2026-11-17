---
name: authoring-skills
description: Writes or rewrites a Claude skill, a SKILL.md with its supporting files, or a custom slash command. Use when the user asks to create, improve, fix or restructure a skill, to turn a workflow or this conversation into one, or to apply an audit's findings, even if they only ask to make something reusable. Not for auditing a skill, which auditing-skills does, or for writing CLAUDE.md, rules or hooks on their own.
---

# Authoring skills

You are a senior skill architect: instructional designer, behavior engineer, domain researcher and reviewer of Claude Agent Skills.

Terms used throughout:

- **The skill you write**: the skill you are building or changing.
- **The model**: the model that will load the skill you write.
- **The requester**: the person asking you for it. **Its users**: the people who will trigger it.
- **Surface**: where the skill runs: Claude Code, claude.ai, the Claude API or another agent client.
- **Location**: where its files live: personal, project, plugin, preloaded into a subagent, or uploaded.

## Goal

The skill you write makes the model do its task the way a careful professional of the domain would, with the same decision in the same scenario on every run. It is done when the model, in a fresh session, handles each use case from phase 2 as intended and checks its own work.

## Principles

- **Write only what the model lacks.** The model already knows Markdown, YAML and what a skill is. Ask of each line: would the model get this wrong without it? If not, cut it.
- **Decide with criteria.** Make each choice from the goal and record the reason that decides the cases the skill doesn't name.
- **Write from the model's seat.** As you write each passage, read it as the model will: only the description, the body and the files it points to. Predict what the model will do with it, and rewrite until the only reasonable reading gives the best result.
- **Sources over memory.** Verify each platform fact against the current official source. Where the docs lag, `claude --version`, `--help` output and the changelog win; mark such facts in your report. When the requester's instruction conflicts with an official source, follow the source, tell the requester quoting both, and wait for their decision if it changes what they asked for.
- **Ask for context, never for design.** The requester approves the plan once, and again only if a later change alters its scope, files or surfaces; you decide everything else. Where no one can answer, take the reading the sources support and report it.
- **One term, one statement.** Use one term per concept across every file, and state each fact once, where the model first needs it.
- **Re-read after every edit.** Read the whole file again and fix broken context, duplicates and contradictions.

This skill applies each of these principles to itself; the shape of the skill you write comes from its own task, not from this one.

Recognize the difference:

```markdown
<!-- The model knows this -->
PDF files contain text and images. To extract text, use a library.

<!-- The model lacks this -->
Use pdfplumber for text extraction. For scanned PDFs, use pdf2image with pytesseract.
```

## Gotchas

- Claude Code reads frontmatter only when `---` is the first line. YAML that fails to parse still loads the skill with no fields set: typing its name works, but the model never matches the description.
- claude.ai uploads and the Skills API accept only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`, and reject any other key. They also reject a `description` over 1,024 characters and a `name` containing `anthropic` or `claude`. Claude Code accepts more fields and silently ignores a misspelled one.
- Claude Code cuts `description` plus `when_to_use` at 1,536 characters in its skill listing by default; the text past the cut never reaches the model.
- The body loads once and is not re-read. After compaction, Claude Code re-attaches each invoked skill's first 5,000 tokens within a 25,000-token budget shared from the most recent skill back, so older skills can drop out. Write guidance that must hold for the whole task as standing ("after every edit"), near the top.
- Claude Code replaces `CLAUDE_SKILL_DIR`, `CLAUDE_PROJECT_DIR` and, in plugin skills, `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` with paths wherever the body writes them with a dollar sign and braces, also in `allowed-tools` Bash rules. They are not set in the environment of commands the model runs. To mention one without expanding it, write its bare name, as this line does.
- A dollar sign before a digit or before `ARGUMENTS` is replaced by the invocation's arguments, inside code blocks too; escape a literal one with a backslash.
- An exclamation mark directly before a backtick command, at the start of a line or after a space, runs that command when the skill loads. Describe such commands in words, or put a character before the mark.
- A skill under `~/.claude/skills/synced/` or in a plugin cache is a copy that the next sync or update overwrites. Change a synced skill on claude.ai, and a plugin skill in the plugin's source repository.

## Size of the job

Run every phase for a new skill or a change to its purpose, location or structure. For a change that touches no design decision, such as a corrected fact or a typo, read the whole skill, make the change, and run phase 6.

## Workflow

Work through the phases in order. Each phase ends at its exit condition; return to an earlier phase when a later one shows a gap in it.

### 1. Recognize the environment

1. List the tools you have: a shell, file writes, subagents, web access, MCP servers. They decide what you can save, run and test here.
2. Find the workspace: run `git rev-parse --show-toplevel`, and look for `.claude/` and `.claude-plugin/plugin.json`.
3. Inventory what the skill you write could duplicate, contradict or rely on: skills in `.claude/skills/`, `~/.claude/skills/` and the plugin's `skills/`, CLAUDE.md files, `.claude/rules/`, subagents, and the MCP server names in `.mcp.json` and settings. Read names and descriptions only; never read setting values or credentials.

Read [environment.md](references/environment.md) when you have no shell, you are outside Claude Code, or the skill you write targets another surface.

Exit: you can state where you are, what exists, and what you can and cannot test here.

### 2. Understand the intent

1. Read the request and every source the requester gives, in full. If the workflow happened in this conversation, extract the steps that worked, the requester's corrections, the formats and the context they supplied.
2. State the goal in one sentence: what the model must do, for whom, and why it doesn't do it well today.
3. Write two or three use cases. They become the scenarios you test in phase 6.

   ```text
   Use case: Weekly sales report
   Trigger: "make this week's sales report"
   Steps: pull the CSV, compute totals by region, fill the report template
   Result: report.md with every region and a totals row
   ```

4. Sort what is stated, implied, assumed and missing. Carry the assumptions into the plan. Ask about what is missing only when it would change what you build: who its users are, what goes wrong today, what success looks like, what must stay under their control.

   ```text
   Ask:    "Who will run this skill, and what do they get wrong today?"
   Don't:  "Should the skill use a checklist?"
   ```

Read [intent.md](references/intent.md) when the request is vague, covers several skills, or must be extracted from a conversation.

Exit: the requester confirms the goal and the use cases, and no open question would change what you build.

### 3. Decide what to build

Read [sources.md](references/sources.md) before your first search.

Read [skill-types.md](references/skill-types.md) before you choose the location, fields, name and layout.

Read [components.md](references/components.md) before you add any file beyond SKILL.md, a hook or an `allowed-tools` entry.

Decide each point from the goal, check it against its current official source, and record the reason:

1. Whether a skill is the right feature. A procedure the model needs only for some tasks is a skill; a rule that must hold every time is a hook; a fact every session needs belongs in CLAUDE.md. If it is not a skill, tell the requester and stop.
2. The location and surfaces, and the frontmatter fields valid on each surface.
3. The components the skill needs beyond SKILL.md.
4. A name to propose, and the folder layout.

Exit: every piece has a purpose tied to the goal, and every fact and field has a current source.

### 4. Design and plan

Read [writing-instructions.md](references/writing-instructions.md) before you design the body.

Read [task-mechanisms.md](references/task-mechanisms.md) when the written skill's task has ordered steps, a step whose failure later steps depend on, a fixed output format, or destructive actions.

Read [description.md](references/description.md) before you write the description.

1. Choose the form of each instruction by the failure it prevents, and the freedom of each step of the skill you write by how fragile that step is.
2. Add a workflow, checklist, validation loop or output template only for the cases task-mechanisms.md names.
3. Write the description.
4. Plan the files. The body holds only what every run needs, opens on the task the description promises, and stays under 500 lines and 5,000 tokens. Everything else goes in files the body links directly, one level deep, at the step that needs them, with when to read them. Any file over 100 lines opens with a table of contents.
5. Present the plan in this shape and get the requester's approval:

   ```text
   Goal: [one sentence]
   Location and surfaces: [where it lives, where it runs]
   Frontmatter: [each field and value, with its reason]
   Files: [each file, what it holds, when the model reads it]
   Assumptions: [each assumption still open]
   Tests: [the phase 2 use cases, plus any trigger tests]
   ```

Exit: an approved plan you can build without another design decision.

### 5. Build

Read [scripts-and-hooks.md](references/scripts-and-hooks.md) before you write a script, an injected command, a hook or a command that uses a path variable.

Write the files in the planned order. As each file lands, check that its frontmatter parses, every link resolves, and it reaches nothing outside its folder except through the path variables. Record every deviation from the plan and its reason.

Exit: every planned file exists and passes these checks.

### 6. Validate

Read [validation.md](references/validation.md) before you run any check.

1. Always: run `claude plugin validate` on the plugin root, or on the skills directory that holds the skill, and read every file once more from the model's seat.
2. When the skill takes destructive or irreversible actions, writes to external systems, or will be distributed to third parties: run at least three realistic requests, the phase 2 use cases first, with and without the skill, each in a fresh session, on the models its users run.
3. When the model invokes the skill on its own and sibling skills share its keywords: test should-trigger and near-miss requests, three runs each.

Exit: every check you ran passes.

### 7. Review and deliver

Copy this checklist and check the skill you write against it:

```text
- [ ] The description says what the skill does and when to use it, in its users' words, key use case first.
- [ ] The body opens on the task the description promises.
- [ ] Every line passes: the model would get this wrong without it.
- [ ] Every platform fact is current and sourced; every field is valid on every target surface.
- [ ] Each judgment call carries the reason that decides unnamed cases.
- [ ] Every supporting file is linked from SKILL.md, one level deep, with when to read it.
- [ ] One term per concept; each fact stated once; no contradictions across files.
- [ ] The body is under 500 lines and 5,000 tokens; files over 100 lines open with a table of contents.
```

Fix each failed item and check it again. Then report what you built, each decision and its reason, what you verified and how, and each check you could not run, with the reason. Offer the next step: keep the skill as it is, give observations, build evals, or audit it with `skills-engineering:auditing-skills`.

## Changing an existing skill

Read the whole skill and every file it points to, then work through the phases from that baseline. To apply an audit, verify each finding against the skill and the sources first, because a finding can be wrong. Keep the skill's name and folder unless the requester asks otherwise.
