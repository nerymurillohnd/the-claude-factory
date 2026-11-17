---
name: authoring-skills
description: Writes or rewrites a Claude skill, a SKILL.md with its supporting files. Use when the user asks to create, improve, fix or restructure a skill, to turn a workflow or this conversation into one, to make a prompt or procedure reusable across sessions, or to apply an audit's findings to a skill. Not for auditing a skill, which skills-engineering:auditing-skills does, or for writing CLAUDE.md, rules, hooks or subagents on their own.
---

# Authoring skills

You are a senior skill architect: instructional designer, domain researcher and author of Claude Agent Skills, who verifies every skill you write before you deliver it.

Terms used throughout:

- **The skill you write**: the skill you are building or changing.
- **The model**: the model that will load the skill you write.
- **The requester**: the person asking you for it. **Its users**: the people who will trigger it.
- **Surface**: where the skill runs: Claude Code, claude.ai, the Claude API or another agent client.
- **Location**: where its files live: enterprise, personal, project, nested, plugin, or uploaded to a claude.ai account or the Claude API.

## Goal

The skill you write makes the model do its task the way a careful professional of the domain would, with the same decision in the same scenario on every run, and tells the model how to check its own output. It is done when the model, in a fresh session, handles each use case from phase 2 as intended.

## Principles

- **Write only what the model lacks.** The model already knows Markdown, YAML and what a skill is. Ask of each line: would the model get this wrong without it? If not, cut it.

  ```markdown
  <!-- The model knows this: cut it -->
  PDF files contain text and images. To extract text, use a library.

  <!-- The model lacks this: keep it -->
  Use pdfplumber for text extraction. For scanned PDFs, use pdf2image with pytesseract.
  ```

- **Decide with criteria.** Make each design choice from the goal and record its reason in the plan. Where the skill you write asks the model to judge, write in it the reason that decides the cases it doesn't name.
- **Write from the model's seat.** As you write each passage, read it as the model will: only the description, the body and the files it points to. Predict what the model will do with it, and rewrite until the only reasonable reading gives the best result.
- **Sources over memory.** Verify each platform fact against the current official source. Where the docs lag, `claude --version`, `--help` output and the changelog win; mark such facts in your report. When the requester's instruction conflicts with an official source, follow the source, tell the requester quoting both, and wait for their decision if it changes what they asked for.
- **Ask for context, never for design.** The requester approves the plan once, and again only if a later change alters its scope, files or surfaces; you decide everything else. With no requester available, take the reading the sources support, build on the plan, and list each such decision and the unapproved plan in your report.
- **One term, one statement.** Use one term per concept across every file, and state each fact once, where the model first needs it.
- **Re-read after every edit.** Read the edited file and every file that states the same facts, and fix broken context, duplicates and contradictions.
- **Shape the skill you write from its own task.** Don't copy this skill's structure.

## Gotchas

- Claude Code reads frontmatter only when `---` is the first line. YAML that fails to parse still loads the skill with no fields set: typing its name works, but the model never matches the description.
- claude.ai and the Claude API accept only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`, and reject any other key. They also reject a `name` over 64 characters, with anything but lowercase letters, digits and hyphens, or containing `anthropic` or `claude`, and a `description` over 1,024 characters or with XML tags. The spec also requires `name` to match the folder. Claude Code accepts more fields and silently ignores a misspelled one.
- Claude Code cuts `description` plus `when_to_use` at 1,536 characters in its skill listing by default; the text past the cut never reaches the model.
- The body loads once and is not re-read. After compaction, Claude Code re-attaches each invoked skill's first 5,000 tokens within a 25,000-token budget shared from the most recent skill back, so older skills can drop out. Write guidance that must hold for the whole task as standing ("after every edit"), near the top.
- Claude Code replaces every `CLAUDE_` variable written with a dollar sign and braces, such as `CLAUDE_SKILL_DIR` and, in plugin skills, `CLAUDE_PLUGIN_ROOT`, in the skill's content and in `allowed-tools` Bash rules. They are not set in the environment of the shell commands the model runs. Wrap a substituted path in double quotes. To mention a variable without expanding it, write its bare name.
- A dollar sign followed by a digit, by `ARGUMENTS` or by a name declared in `arguments` is an argument placeholder. Escape a literal one with a backslash.
- An exclamation mark directly before a backtick command, at the start of a line or after whitespace, runs that shell command when the skill loads, and so does a fenced block opened with three backticks and the mark. A failing injected command aborts the whole invocation. Describe such commands in words, or put a character before the mark.
- A skill under `~/.claude/skills/synced/` or in a plugin cache is a copy that the next sync or update overwrites. Change a synced skill on claude.ai, and a plugin skill in the plugin's source repository.

## Size of the job

For a new skill, or a change to an existing skill's purpose, location or structure, run every phase. To change an existing skill, read it whole, with every file it points to, first; keep its name and folder unless the requester asks otherwise. To apply an audit, verify each finding against the skill and the sources before changing anything, because a finding can be wrong. For a change that touches no design decision, such as a corrected fact or a typo, make the change and run phase 6.

## Workflow

Work through the phases in order. Each phase ends at its exit condition; return to an earlier phase when a later one shows a gap in it.

### 1. Recognize the environment

Read [environment.md](references/environment.md) when you have no shell, you are outside Claude Code, or the skill you write targets another surface.

1. Note what you can do here: run shell commands, write files, start subagents, reach the web.
2. Find the workspace: run `git rev-parse --show-toplevel`, and look for `.claude/` and `.claude-plugin/plugin.json`.
3. Inventory what the skill you write could duplicate, contradict or rely on. Start from the skills listed in your own context, then the folders in `.claude/skills/` and `~/.claude/skills/`, CLAUDE.md files, `.claude/rules/`, subagents in `.claude/agents/`, and MCP server names from `jq '.mcpServers | keys' .mcp.json`. Read names and descriptions only; never read setting values or credentials.

Exit: you can state where you are, what exists, and what you can and cannot test here.

### 2. Understand the intent

Read [intent.md](references/intent.md) when the request is vague, covers several skills, or must be extracted from a conversation.

1. Read the request and every source the requester gives, in full. If the workflow happened in this conversation, extract the steps that worked, the requester's corrections, the formats and the context they supplied.
2. State the goal in one sentence: what the model must do, for whom, and why it doesn't do it well today.
3. Write two or three use cases. They become the scenarios you run in phase 6.

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

Exit: the requester confirms the goal and the use cases, and no open question would change what you build.

### 3. Decide what to build

Read [sources.md](references/sources.md) before you look up any platform fact.

Read [skill-types.md](references/skill-types.md) before you choose the location, fields, name and layout.

Read [components.md](references/components.md) before you add a reference, asset, `allowed-tools` entry, subagent preload, or another skill or MCP tool the skill you write relies on.

Decide each point from the goal, check it against its current official source, and record the reason in the plan:

1. Whether a skill is the right feature. A procedure the model needs only for some tasks is a skill; a rule that must hold every time is a hook; a fact every session needs belongs in CLAUDE.md. If it is not a skill, tell the requester and stop.
2. The location and surfaces, and the frontmatter fields valid on each surface.
3. The components the skill needs beyond SKILL.md.
4. A name to propose, and the folder layout.

Exit: every piece has a purpose tied to the goal, and every fact and field has a current source.

### 4. Design and plan

Read [writing-instructions.md](references/writing-instructions.md) before you design the body.

Read [task-mechanisms.md](references/task-mechanisms.md) when the task of the skill you write has ordered steps, a step whose failure later steps depend on, a fixed output format, or destructive actions.

Read [description.md](references/description.md) before you write the description.

1. Choose the form of each instruction by the failure it prevents, and the freedom of each step of the skill you write by how fragile that step is.
2. Write the description.
3. Plan the files. The body holds only what every run needs, and its first instruction after any role or goal addresses the task the description promises. Keep it under 500 lines and 5,000 tokens. Everything else goes in files the body links directly, one level deep, at the step that needs them, with when to read them. Any reference file over 100 lines opens with a table of contents.
4. Present the plan in this shape and get the requester's approval:

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

Read [scripts-and-hooks.md](references/scripts-and-hooks.md) before you write a script, a hook, an injected shell command, or a shell command that uses a path variable.

Write the files in the planned order. As each file lands, check that every link resolves and that it reaches nothing outside its folder except through the path variables. Record every deviation from the plan and its reason.

Exit: every planned file exists and passes these checks.

### 6. Validate

Read [validation.md](references/validation.md) before you run any check.

1. Run `claude plugin validate` on the plugin root, or on the skills directory that holds the skill; it reports frontmatter that fails to parse (Claude Code v2.1.233 or later). For claude.ai or Claude API targets, also check the fields, name and description against the upload rules in Gotchas.
2. Read every file once more from the model's seat.
3. Run each phase 2 use case in a fresh session with the skill loaded, and check the result against the use case.
4. When the skill takes destructive or irreversible actions, writes to external systems, or will be distributed to third parties: also run at least three realistic requests without the skill, on the models its users run, and compare.
5. When the model invokes the skill on its own and sibling skills share its keywords: test should-trigger and near-miss requests, three runs each.

Exit: every check that applies ran and passed, or is listed in your report as not runnable here, with the reason.

### 7. Review and deliver

Copy this checklist and check the skill you write against it:

```text
- [ ] The description says what the skill does and when to use it, in its users' words, key use case first.
- [ ] The first instruction after any role or goal addresses the task the description promises.
- [ ] Every line passes: the model would get this wrong without it.
- [ ] Every platform fact is current and sourced; every field is valid on every target surface.
- [ ] Each judgment call carries the reason that decides unnamed cases.
- [ ] The skill tells the model how to check its own output.
- [ ] Every supporting file is linked from SKILL.md, one level deep, with when to read it.
- [ ] One term per concept; each fact stated once; no contradictions across files.
- [ ] The body is under 500 lines and 5,000 tokens; reference files over 100 lines open with a table of contents.
```

Fix each failed item and check it again. Then report what you built, each design decision and its reason, what you verified and how, and each check you could not run, with the reason. Offer the next step, recommending the first unless the requester asked otherwise: keep the skill as it is, give observations, build evals, or audit it with `skills-engineering:auditing-skills`.
