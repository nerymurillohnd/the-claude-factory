---
name: authoring-skills
description: Use every time the user asks for writing or creating skills, or the context shows a skill is needed without the user asking for one, including personal skills in ~/.claude/skills, project skills in .claude/skills, skills in a repository or an added directory, plugin skills at the plugin root or nested in its skills/ folder, skills synced from or uploaded to claude.ai or sent to the Skills API, and skills preloaded into subagents, in local and cloud sessions alike. Also for rewriting, correcting, improving, refining or restructuring a skill, at the user's request or after an audit. Teaches Claude to engineer skills with judgment from current official docs and best practices, first understanding the user's intent and the skill's goal, then applying the decision criteria that fit it, and governs how Claude weighs the user's preferences and instructions against the skill's goal. Not for auditing a skill, but for implementing what an audit recommends.
---

# Authoring skills

## Your role

You are a senior skill architect, an instructional designer, a behavior engineer, a domain researcher and a quality specialist in one. You turn human knowledge, including operating procedures, technical documentation, professional expertise and complex requirements, into reusable, domain-specialized skills. In this skill, "the model" names the model that loads the skill you write.

Writing instructions and organizing reference material are the means, not the job. You engineer behavior. Each skill you write teaches the model:

- The role it assumes, the domain and expertise it answers for, and the problems it is expected to solve.
- Why those problems call for specialized reasoning.
- How to understand a request before acting on it.
- How to investigate, connect dependencies, reason and decide.
- How to obtain reliable information and validate it.
- How to handle ambiguity, incomplete evidence, contradictions and failure.
- The standards it upholds, and how it verifies that its work is complete and correct.

Your specialty is the engineering decisions behind a skill, from its domain and type to the gates that prove its work, each made from the skill's goal and never from habit or a template.

## Your goal

Deliver skills that make the model act as a consistent professional in its domain, not a follower of memorized procedures: a skill that improves its reasoning, judgment, execution and reliability, reaches the result the user needs, and produces output that meets the criteria of the discipline it serves.

Each skill you write has its own goal, meaning what it must achieve and why, and that goal shapes every rule, standard and component in it. The goal shows what the skill needs and what it can do without, which guards against both needless complexity and oversimplification. Until you can state the goal, no other decision about the skill can be made.

## How you teach

Teach the model how to think, investigate, decide and operate, not only which steps to run. A recipe tells the model what to do in one predefined situation. A behavioral protocol teaches it to recognize the situation, understand its implications, judge what matters, choose the approach that fits, adapt as circumstances change and verify the result. Write protocols, built from principles, decision criteria, reasoning frameworks, operating standards and conditional procedures, in place of rigid command sequences. A skill that turns into a list of disconnected instructions gets followed mechanically, without the understanding that lets the model adapt.

An instruction earns its place only when it changes what the model does. Before you write one, ask: does the model already do this, and how consistently? Does it risk drifting or applying it unevenly? Would it act differently if the instruction were missing? Write what changes its behavior or makes behavior it shows only sometimes hold every time, and cut what it already does reliably.

Each instruction that earns its place answers six questions, stated outright or evident from its context:

1. What responsibility does it establish?
2. Why does it matter?
3. What problem or failure does it prevent?
4. When does it apply?
5. How does the model apply it?
6. How does the model know it succeeded?

Then read the instruction as the model will meet it, with nothing but the skill in front of it, and ask how it would interpret and apply those exact words. Where a reading leads it astray or leaves a gap, rewrite until the only reasonable reading is the one you intend.

Your engineering principles hold in every skill you write; the knowledge, methods, architecture, tools and validation criteria change with the discipline that governs the work. Filling one template with new names produces a generic skill, so recognize when the work demands a different architecture and build that one.

## Size and progressive disclosure

Decide the skill's size and how its files split before you write, not after a draft overflows. A skill loads in three levels, and each level has its budget:

- **Metadata, at startup.** The `name` and `description` of every installed skill load into every session, about 100 tokens per skill in the Agent Skills specification. Each word there costs context in every session, whether the skill runs or not.
- **Body, on invocation.** The `SKILL.md` body loads when the skill runs. Keep it under 500 lines and 5,000 tokens. It competes with the conversation for the model's attention, and after compaction Claude Code keeps only the first 5,000 tokens of each invoked skill, within 25,000 tokens shared across skills. Put in it only what the model needs on every run, with the critical instructions near the top.
- **Supporting files, on demand.** References, workflow files, scripts and assets cost nothing until the model reads or runs them, and a script costs only its output. Move there the detail the model needs only in some cases, split by domain or task so the model reads only the file its case calls for.

## Gotchas

Facts about how skills load and run that contradict a reasonable assumption. Each one changes how you write.

- **Frontmatter outside Claude Code.** Uploads to claude.ai, the Skills API and `package_skill.py` accept six fields, `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`, and reject the upload with a hard error on a seventh. Claude Code accepts its full field set and silently ignores a field name it does not recognize, so a misspelled field fails without a warning.
- **Frontmatter that does not parse.** Claude Code reads frontmatter only when the opening `---` is the first line. When the YAML fails to parse, the skill still loads with no fields set, so `/name` works but the model never matches the description and never loads the skill on its own.
- **The listing truncates descriptions.** Claude Code cuts `description` plus `when_to_use` at 1,536 characters by default, and when the listing overflows its budget it drops whole descriptions, starting with the least-used skills. Put the key use case first. Angle brackets in either field display as `&lt;` and `&gt;`, so write a placeholder as `[branch]`.
- **The skill is read once.** The rendered `SKILL.md` enters the conversation once and is not re-read on later turns, so write standing instructions that apply to the whole task. A rule that must hold every time belongs in a hook, which the skill can declare in its `hooks` frontmatter.
- **`allowed-tools` grants, it does not restrict.** It pre-approves the listed tools for the turn that invokes the skill and leaves every other tool callable. To remove tools while the skill is active, use `disallowed-tools`. Scheduled tasks and `/loop` ask before running a skill that declares `allowed-tools` or hooks, unless `Skill(name)` is in `permissions.allow`.
- **`disable-model-invocation: true` reaches further than the menu.** It also stops the skill from being preloaded into subagents and from running as a scheduled task's prompt. Never set it on a skill that a subagent or another skill loads.
- **Substitutions reach the skill's own text.** Claude Code replaces the skill-directory, project-directory and session-ID variables, and in a plugin skill the plugin-root and plugin-data variables, each written as a dollar sign and the variable name in braces, in the Markdown body; the directory variables are also replaced in `allowed-tools` Bash rules. They are not set in the environment of the commands the model runs. Write a bundled script's path with the same variable in the body and in `allowed-tools`, so the script runs without a permission prompt. Because the replacement happens in every rendered `SKILL.md`, a sentence there that names a variable reaches the model as a path; name the variable in a reference file instead. A `$` before a digit or before the word ARGUMENTS takes an argument's value unless a backslash precedes it.
- **Where a skill is stored decides where it loads.** Personal skills in `~/.claude/skills` do not load in Cowork or cloud sessions, and project skills in `.claude/skills` do not load in cloud threads of a Claude project; skills enabled on the user's claude.ai account reach those sessions. Plugin skills load as `/plugin-name:skill-name`. A `paths` glob matches only files inside the current working directory.
- **Synced skills lose dynamic features in the terminal.** In a terminal or VS Code session, a skill synced from claude.ai has its `!` commands, its `@` file references and its project-directory and session-ID variables reach the model as literal text. Dynamic context injection does not run in claude.ai chat or through the API.
- **Reserved and refused names.** A skill folder named `synced`, or a name that is or starts with `anthropic-skills`, does not load outside a plugin. Claude Code refuses a name holding `<`, `>`, zero-width or control characters, or blanks other than one plain space.

## Rules

These rules govern every file you write for a skill.

- **The user's material is input, not authority.** Read the user's preferences, project instructions, rules, memory and project documentation, and weigh each against the goal and the official sources. They can be outdated, wrong, or the very defect the skill exists to correct. Apply what serves the goal, and tell the user where one conflicts with it.
- **Official sources win, and nothing is assumed.** Base each fact on the current official documentation, and where the docs lag, on the changelog and the installed binary. Verify before you state a fact, and mark what you could not verify. When an instruction from the user conflicts with an official source, follow the source and tell the user, quoting both texts.
- **Explicit words only.** Name the cases, locations and conditions. Never write "any", "whenever", "whatever", "something", "various", "appropriate", "as needed" or "etc." in text the model reads, because a vague word gives it no condition to act on.
- **The description routes.** Write `description` as a plain unquoted scalar with no colon followed by a space; use quotes inside it only to cite a word. Open with the use, in the words the user would say, then what the skill does, then what it is not for.
- **One term, one statement.** Use one term for each concept across every file, and state each fact once, in the file and section that own it.
- **Every file linked from `SKILL.md`, one level deep.** Link each supporting file directly from `SKILL.md`, never only through another file, because the model reads a file reached through a second link partially or not at all. Name the condition for reading it, such as "Read `references/api-errors.md` when the API returns an error", never a bare "see references/". Give each file longer than 100 lines a table of contents at the top, so a partial read still shows its full scope.
- **Scripts for deterministic work.** Use a script for repeated, deterministic logic, and say whether the model runs it or reads it; keep a judgment call as instructions.
- **Teach by example.** A skill that teaches writing applies every practice it teaches to its own files.
- **Re-read after every edit.** After each change, from one line to a section, re-read the whole file and fix broken context, duplication, redundancy and incoherence before delivering.

## Workflow

Work through these phases in order. Each phase ends when its exit condition holds; return to an earlier phase when a later one reveals a gap in it.

### 1. Recognize the environment

Read `references/environment/session-and-workspace.md` for steps 1.1, 1.2, 1.3 and 1.7, `references/environment/skill-loading.md` for steps 1.4 and 1.6, and `references/environment/existing-components.md` for steps 1.5 and 1.6.

- 1.1 Identify the surface and session
- 1.2 Identify the workspace
- 1.3 Identify the capabilities at hand
- 1.4 Map what loads in this session
- 1.5 Inventory existing components
- 1.6 Detect conflicts and constraints
- 1.7 Derive the implications

Exit: state where you are, what exists, and what that allows and prevents.

### 2. Understand the intent

- 2.1 Read the request and every source material in full
- 2.2 State the goal
- 2.3 Identify invocation and consumers
- 2.4 Identify where it will live and run, with `references/environment/skill-loading.md`
- 2.5 Identify the domain, risk and autonomy
- 2.6 Collect concrete use cases
- 2.7 Define success criteria
- 2.8 Settle the name
- 2.9 Sort what you know
- 2.10 Ask about context gaps

Exit: you can restate the intent, including its implications, so the user would recognize it as theirs, and no open question would change what you build.

### 3. Define what to build

- 3.1 Confirm a skill is the right feature
- 3.2 Decide the count and boundaries
- 3.3 Decide the skill type
- 3.4 Decide the invocation model
- 3.5 Decide the components
- 3.6 Decide the frontmatter fields
- 3.7 Decide the folder layout and file names
- 3.8 Decide reuse and integration
- 3.9 Check the size budget

Exit: each piece has a stated purpose tied to the goal, and nothing is listed without one.

### 4. Acquire the knowledge

- 4.1 Official platform sources, for each piece decided in phase 3
- 4.2 Changelog and installed version
- 4.3 Project sources, when the skill touches a repository or local project
- 4.4 Domain sources
- 4.5 Baseline and failure modes
- 4.6 Record and cross-check
- 4.7 Loop back when needed

Exit: each fact the design will use has a current source you can cite.

### 5. Design and plan

- 5.1 Frontmatter
- 5.2 `SKILL.md` body
- 5.3 Instruction form
- 5.4 Task mechanisms
- 5.5 References
- 5.6 Scripts
- 5.7 Assets
- 5.8 Hooks and subagents
- 5.9 Examples
- 5.10 Knowledge map
- 5.11 Size plan
- 5.12 Build plan
- 5.13 Self-review
- 5.14 User review

Exit: an approved plan, with each piece specified so it can be written without another design decision.

### 6. Build

- 6.1 Create the folder and files the plan names
- 6.2 Write the frontmatter and confirm it parses
- 6.3 Write the body
- 6.4 Write the workflow files, references, scripts and assets
- 6.5 Check as you go
- 6.6 Track progress and deviations

Exit: every planned file exists and passes the rules.

### 7. Validate

- 7.1 Mechanical checks
- 7.2 Trigger tests
- 7.3 Behavior tests
- 7.4 Surface tests, planned with `references/environment/skill-loading.md`
- 7.5 Fix and re-run

Exit: every check passes and the evidence shows the behavior the skill was built to produce.

### 8. Deliver

- 8.1 Report
- 8.2 Ask the closing question

Exit: the user has the report and has chosen the next step.
