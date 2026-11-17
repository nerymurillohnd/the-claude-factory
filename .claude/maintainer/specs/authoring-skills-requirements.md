# authoring-skills: requirements from the sources

The measuring stick for every file of `skills-engineering:authoring-skills`. Each requirement quotes its source verbatim. A line of the skill that no requirement supports, or that contradicts one, is a defect. Sources read in full on 2026-11-17.

## Contents

- Sources
- 0. Owner requirements
- 1. What a skill earns its place with (writing-instructions.md)
- 2. Skill types, locations and surfaces (skill-types.md)
- 3. Frontmatter (skill-types.md)
- 4. Name and description (name-and-description.md)
- 5. Structure, files and progressive disclosure (structure.md)
- 6. Components and composition (components.md)
- 7. Scripts, injected commands and hooks (scripts-and-hooks.md)
- 8. Task mechanisms (task-mechanisms.md)
- 9. Examples, snippets and templates (writing-instructions.md)
- 10. Validation and evaluation (validation.md)
- 11. Security and distribution (components.md, validation.md)
- 12. Where the sources disagree (sources.md)

## Sources

- CC: https://code.claude.com/docs/en/skills
- CC-SA: https://code.claude.com/docs/en/sub-agents (Preload skills into subagents)
- CC-HK: https://code.claude.com/docs/en/hooks (Hooks in skills and agents)
- CC-PL: https://code.claude.com/docs/en/plugins/loading
- CC-PC: https://code.claude.com/docs/en/plugins/components
- CC-PR: https://code.claude.com/docs/en/plugins-reference
- CC-MR: https://code.claude.com/docs/en/plugins/manifest-reference
- CC-HM: https://code.claude.com/docs/en/plugins/host-marketplace
- AS-SPEC: https://agentskills.io/specification
- AS-BP: https://agentskills.io/skill-creation/best-practices
- AS-DESC: https://agentskills.io/skill-creation/optimizing-descriptions
- AS-EVAL: https://agentskills.io/skill-creation/evaluating-skills
- AS-SCR: https://agentskills.io/skill-creation/using-scripts
- PL-BP: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- PL-OV: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- PL-ENT: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise
- PL-API: https://platform.claude.com/docs/en/build-with-claude/skills-guide
- PDF: Anthropic, "The Complete Guide to Building Skills for Claude" (January 2026)
- BLOG: claude.dev, "Lessons from building Claude Code: How we use skills" (2026-06-03)

## 0. Owner requirements

From the owner's brief in this session (paraphrased in English; the owner's words rule):

- O1. Open with the role and its areas of expertise, as the reviewer agents do; then the goal (creating and writing skills), without duplicating the description; then a short reflection of the doctrine: behavior before document; understand first where you are, what will be done, why, what it implies, how, what exists and the result.
- O2. The skill mirrors every practice it teaches.
- O3. It fights the models' anti-pattern of executing before understanding: skills built with reasoning and decision criteria for consistent results.
- O4. While writing, Claude reads each passage as a fresh session that loads the skill would, predicts the result, and applies best practices fully.
- O5. Write only what the model doesn't know, or wouldn't do the same way every time.
- O6. No assumptions: understand the environment, the user's intent, what already exists to create skills.
- O7. Read the references to learn; apply only what the purpose of the skill being written needs.
- O8. Disentangle the request, including what lies behind the intent. Ask the user for context, never for the technical approach, the plan or the execution. No design, plan or build until the intent is clear.
- O9. Then find what is needed: where the skill will live (project, user, plugin `skills/`, plugin root, subagent), what it needs (hooks, scripts, references, assets, other tools such as MCP), the frontmatter fields for its type and their values, the name proposed to the user, the folder architecture, permissions.
- O10. Design and plan with research in every official source: Agent Skills, Claude Platform, Claude Docs, Claude Code Docs, Anthropic, Claude Academy and Anthropic's PDF guide.
- O11. The references give Claude the full knowledge of what is possible, so it chooses, for the skill's purpose, what to use and how: workflow or not, checklist or not, output templates or not, numbered phases, task tracking, validation, gotchas, rules, embedded commands and scripts, examples ("good in measure, bad in excess").
- O12. It must flow and not confuse Claude; surpass skill-creator and writing-skills; depend on neither and not on auditing-skills.
- O13. At the end: a self-review; then offer to keep it as is, take observations, build evals, or run auditing-skills on it.
- O14. The references cover at least: every frontmatter field by type; name guidance; description guidance; how to embed examples, command snippets, references and templates; the basic structure and what goes in `references/`, `scripts/`, `assets/`; uppercase documents at the skill root; anti-patterns with good versus bad examples; when to use and not use checklists, validation loops, workflows and scripts; script placement in the skill, a subfolder, or outside it in a plugin; how a subagent skill differs; how to prioritize progressive disclosure; how the reference block in SKILL.md is built.
- O15. Don't embed all the documentation; tell Claude to consult it.

## 1. What a skill earns its place with

- "Only add context Claude doesn't already have." (PL-BP)
- "Ask yourself about each piece of content: 'Would the agent get this wrong without this instruction?' If the answer is no, cut it. If you're unsure, test it. And if the agent already handles the entire task well without the skill, the skill may not be adding value." (AS-BP)
- "Focus on what the agent wouldn't know without your skill: project-specific conventions, domain-specific procedures, non-obvious edge cases, and the particular tools or APIs to use." (AS-BP)
- "A common pitfall in skill creation is asking an LLM to generate a skill without providing domain-specific context ... The result is vague, generic procedures ('handle errors appropriately,' 'follow best practices for authentication')" (AS-BP)
- Extract from a hands-on task: "Steps that worked", "Corrections you made", "Input/output formats", "Context you provided" (AS-BP)
- "Overly comprehensive skills can hurt more than they help ... Concise, stepwise guidance with a working example tends to outperform exhaustive documentation." (AS-BP)
- "Deciding what a skill should cover is like deciding what a function should do ... a coherent unit of work that composes well with other skills." (AS-BP)
- "Match the specificity of your instructions to the fragility of the task." High, medium, low freedom; "Narrow bridge with cliffs on both sides" / "Open field with no hazards" (PL-BP; AS-BP)
- "When multiple tools or approaches could work, pick a default and mention alternatives briefly rather than presenting them as equal options." (AS-BP)
- "A skill should teach the agent how to approach a class of problems, not what to produce for a specific instance." (AS-BP)
- "For flexible instructions, explaining why can be more effective than rigid directives" (AS-BP)
- "Keep the body itself concise ... State what to do rather than narrating how or why" (CC, Types of skill content)
- "Don't include information that will become outdated" ... "use 'old patterns' section" (PL-BP)
- "Choose one term and use it throughout the Skill" (PL-BP)
- "Don't state the obvious ... focus on information that pushes Claude out of its normal way of thinking." (BLOG)
- "Avoid railroading Claude ... State the goal and the constraints, not every step." (BLOG)
- "Skills act as additions to models ... Test your Skill with all the models you plan to use it with." (PL-BP)
- Reference content vs task content: "Reference content adds knowledge Claude applies to your current work" / "Task content gives Claude step-by-step instructions for a specific action" (CC)
- "Create a skill when you keep pasting the same instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact." (CC)
- "Claude skipped a rule that must hold every time: move the rule into a hook." (CC, Troubleshooting)
- "word the guidance so it applies to the whole task, for example 'Run the tests after every edit'" (CC, Troubleshooting)
- "put the most important instructions near the top of SKILL.md" (CC, Troubleshooting)

## 2. Skill types, locations and surfaces

- Locations table: Enterprise, Personal (`~/.claude/skills/<skill-name>/SKILL.md`, "but not Cowork or cloud sessions"), Project (`.claude/skills/...`, "but not cloud threads in a project"), Nested, Additional directory, Plugin (`<plugin>/skills/<skill-name>/SKILL.md`, "as /plugin-name:skill-name"), claude.ai account. (CC)
- "Symlinked folders" allowed in enterprise, personal and project; "Plugin skills handle symlinks differently". (CC)
- Reserved `synced` and `anthropic-skills`; refused characters. (CC)
- "Command files: a Markdown file in .claude/commands/ is the older format and still works. It supports the same frontmatter except name and paths ... Prefer a skill for new work" (CC)
- "Skill folder as a plugin: add a .claude-plugin/plugin.json to a personal or project skill folder ... loaded as <name>@skills-dir" (CC)
- Nested skills load "the first time Claude reads or edits a file in that subdirectory" (CC)
- Precedence table: enterprise > personal > project; skill over command file; plugin skills namespaced. (CC)
- "Cowork sessions and cloud sessions ... don't read ~/.claude/skills/ on your machine" (CC)
- Synced skills: "Claude Code downloads synced skills and never uploads them ... To change a synced skill, update it on claude.ai" (CC)
- Synced body in terminal: no `!` commands, no `@` attachments, no `CLAUDE_PROJECT_DIR` or `CLAUDE_SESSION_ID` substitution. (CC)
- "Custom Skills do not sync across surfaces." (PL-OV)
- Runtime: claude.ai "Varying network access"; Claude API "No network access", "No runtime package installation"; Claude Code "Full network access", "Global package installation discouraged". (PL-OV)
- API upload: "SKILL.md file at the upload root (or at the top of a single enclosing folder)"; "under 30 MB"; "A new version is a complete snapshot, not a delta"; "up to 20 Skills for each request". (PL-API)
- Plugin root skill: "with no skills/ directory and no skills manifest key, a SKILL.md at the plugin root loads as one skill. Set name in its frontmatter" (CC-PC)
- "Claude Code doesn't load a CLAUDE.md at the plugin root" (CC-PC)
- Subagent preload: "The full content of each listed skill is injected into the subagent's context at startup, up to the first 32 distinct names" ... "You can't preload skills that set disable-model-invocation: true" ... "If a listed skill is missing or disabled ... skips it and logs a warning to the debug log" (CC-SA)
- Fork: "context: fork ... The subagent doesn't see your conversation history, so the skill's instructions have to stand on their own." ... "only makes sense for skills with explicit instructions" ... runs in the background by default; "background: false" to wait; "A backgrounded fork also runs with the narrower tool set" (CC)
- Fork vs preload table: system prompt, task, also loads. (CC)
- Bundled skill naming: a skill named `verify` or `simplify` in enterprise, personal, project or additional-directory locations makes Claude run it before each commit (v2.1.286+). (CC)

## 3. Frontmatter

- Full Claude Code field table: `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `background`, `hooks`, `paths`, `shell`, `metadata`, `license`, `compatibility`. (CC)
- "All fields are optional. Only description is recommended" ... "Claude Code ignores a field it doesn't recognize without reporting an error" ... booleans accept "yes, no, on, off, 1, and 0" (CC)
- "Claude Code reads the frontmatter only when the opening --- is the file's first line ... If the YAML ... doesn't parse, the skill still loads with no fields set" (CC)
- Outside Claude Code: "name, description, license, compatibility, metadata, allowed-tools" only; any other key: "packaging or upload fails with a hard error" (CC)
- Spec: `name` 1-64, lowercase `a-z0-9-`, no leading/trailing or consecutive hyphens, "Must match the parent directory name"; `description` 1-1024; `compatibility` 1-500, "Most skills do not need" it; `metadata` "a map from string keys to string values"; `allowed-tools` "Experimental". (AS-SPEC)
- Platform: `name` "Cannot contain XML tags", "Cannot contain reserved words: anthropic, claude"; `description` "Maximum 1,024 characters", "Cannot contain XML tags". (PL-BP; PL-OV)
- Invocation table: default / `disable-model-invocation: true` ("Description not in context") / `user-invocable: false`. (CC)
- "allowed-tools ... grants permission for the listed tools during the turn that invokes the skill ... It does not restrict which tools are available" (CC)
- `disallowed-tools` "removed from Claude's available pool while this skill is active" (CC)
- `paths` "relative to Claude's current working directory, and files outside that directory don't match" (CC)
- `model` and `effort` apply "for the rest of the current turn"; with `context: fork` they set the fork's. (CC)
- `hooks`: "registers when the skill is invoked and keeps running for the rest of the session"; `once: true`. (CC; CC-HK)
- Command name by location table, plugin `name` "sets the last segment". (CC)

## 4. Name and description

- "Consider using gerund form" (`processing-pdfs`); acceptable noun phrases and action forms; avoid "helper", "utils", "tools", "documents", "data", "files", reserved words, inconsistent patterns. (PL-BP)
- "The description field ... should include both what the Skill does and when to use it." (PL-BP; AS-SPEC)
- "Always write in third person. The description is injected into the system prompt" (PL-BP)
- "Use imperative phrasing ... 'Use this skill when...'" ... "Focus on user intent, not implementation" ... "Err on the side of being pushy" ... "even if they don't explicitly mention" (AS-DESC)
- "agents typically only consult skills for tasks that require knowledge or capabilities beyond what they can handle alone" (AS-DESC)
- "the combined description and when_to_use text is truncated at 1,536 characters in the skill listing ... Put the key use case first" (CC); "The cap is configurable with skillListingMaxDescChars" (CC, Troubleshooting); listing budget "1% of the model's context window", configurable with `skillListingBudgetFraction`. (CC)
- "Angle brackets in the text show as &lt; and &gt;" ... use "Square brackets" or `argument-hint`. (CC)
- "Write descriptions for the model, not for humans ... the description field is not a summary, it's a description of when to trigger this skill." (BLOG)
- "[What it does] + [When to use it] + [Key capabilities]"; negative triggers "Do NOT use for ..."; bad: "Helps with projects", missing triggers, too technical. (PDF)
- Trigger tests: about 20 queries, 8-10 each way, near-misses, realistic detail, 3 runs, 0.5 threshold, 60/40 train/validation, "Avoid adding specific keywords from failed queries", "Five iterations is usually enough". (AS-DESC)

## 5. Structure, files and progressive disclosure

- Directory: `SKILL.md` required; `scripts/`, `references/`, `assets/`, "Any additional files or directories". (AS-SPEC)
- `references/`: "REFERENCE.md - Detailed technical reference", "FORMS.md - Form templates", "Domain-specific files (finance.md, legal.md, etc.)" ... "Keep individual reference files focused." (AS-SPEC)
- Root files: `pdf/SKILL.md`, `FORMS.md`, `reference.md`, `examples.md`, `scripts/`. (PL-BP); `my-skill/SKILL.md`, `reference.md`, `examples.md`, `scripts/helper.py`. (CC)
- "Name files descriptively ... form_validation_rules.md, not doc2.md" ... "Organize for discovery: Structure directories by domain or feature" (PL-BP)
- Three levels: metadata ~100 tokens; body "< 5000 tokens recommended"; resources "as needed". "Keep your main SKILL.md under 500 lines." (AS-SPEC; PL-OV)
- "The key is telling the agent when to load each file. 'Read references/api-errors.md if the API returns a non-200 status code' is more useful than a generic 'see references/ for details.'" (AS-BP)
- Pointer patterns: "**Form filling**: See [FORMS.md](FORMS.md) for complete guide" (PL-BP); "- For complete API details, see [reference.md](reference.md)" under "## Additional resources" (CC); "Before writing queries, consult references/api-patterns.md for: - Rate limiting guidance ..." (PDF).
- "Keep references one level deep from SKILL.md" ... "Claude might partially read files when they're referenced from other referenced files ... head -100" (PL-BP)
- "For reference files longer than 100 lines, include a table of contents at the top." (PL-BP)
- Domain organization: `reference/finance.md`, `sales.md` ... "Claude only needs to read sales-related schemas". (PL-BP)
- "Use relative paths from the skill root" and forward slashes. (AS-SPEC; PL-BP)
- "Don't include README.md inside your skill folder" (PDF)
- "think of the entire file system as a form of context engineering and progressive disclosure. Tell Claude what files are in your skill" (BLOG)
- Body persists: "the rendered SKILL.md content enters the conversation as a single message and stays there" ... compaction keeps "the first 5,000 tokens of each" within "a combined budget of 25,000 tokens". (CC)

## 6. Components and composition

- MCP plus skills: "MCP provides the professional kitchen ... Skills provide the recipes" (PDF); "use fully qualified tool names ... ServerName:tool_name" (PL-BP).
- "Some skills may need to be set up with context from the user ... store this setup information in a config.json" (BLOG)
- "Help Claude remember ... ${CLAUDE_PLUGIN_DATA} to get a stable directory" (BLOG)
- "Use on-demand hooks ... activated when the skill is called" (BLOG); skill hooks lifetime and `once` (CC-HK)
- Skill hooks under `strictPluginOnlyCustomization`: kept only by plugin, bundled or managed skills; per-source limit 1,024 hooks and 16,384 matcher characters (v2.1.304+). (CC-HK)
- "Claude can load multiple skills simultaneously. Your skill should work well alongside others" (PDF)
- Subagent `skills` field vs Skill tool access; omit `Skill` from `tools` to prevent invoking. (CC-SA)

## 7. Scripts, injected commands and hooks

- "Prefer scripts for deterministic operations"; "Make clear ... Run the script ... Read it as reference" (PL-BP)
- "Solve, don't defer"; "voodoo constants" (PL-BP)
- "If you notice the agent independently reinventing the same logic each run ... write a tested script once and bundle it in scripts/." (AS-BP)
- No interactive prompts ("hard requirement"); `--help`; errors that say what, expected, what to try; structured stdout, diagnostics on stderr; idempotency; input constraints; `--dry-run`; exit codes; safe defaults; predictable output size. (AS-SCR)
- Pin one-off commands (`uvx ruff@0.8.0`, `npx eslint@9`); inline dependencies (PEP 723 with `uv run`, Deno, Bun, Ruby); "State prerequisites in your SKILL.md". (AS-SCR)
- Paths: "relative paths from the skill directory root" (AS-SCR); `${CLAUDE_SKILL_DIR}` "regardless of the current working directory"; `${CLAUDE_PLUGIN_ROOT}` "Substituted only in plugin skills ... resources shared between the plugin's skills"; `${CLAUDE_PLUGIN_DATA}` survives updates; substituted "in two places: the skill's markdown content, and Bash rules in the allowed-tools frontmatter". (CC)
- "Files outside the plugin directory aren't copied, so when a script inside a copied plugin reads a path above the plugin root, such as ../shared, it doesn't find them" (CC-PL)
- "${CLAUDE_PLUGIN_ROOT} changes when the plugin updates, so don't write state there." (CC-PR)
- "Every component path must resolve inside the plugin root" (CC-MR); symlinks: within the plugin kept, within the marketplace dereferenced, outside skipped. (CC-HM)
- `bin/`: "on the PATH of the Bash tool's shell while the plugin is enabled" (CC-PC)
- Injected commands: inline form "only recognized when ! appears at the start of a line or immediately after whitespace"; fenced block opened with three backticks and `!`; "A failed command aborts the entire skill invocation"; append `|| true` where a non-zero exit is expected; runs in the session's working directory; stderr merged into stdout; 2-minute timeout; permission checks. (CC)
- Argument substitution: `$ARGUMENTS`, `$ARGUMENTS[N]`, `$N`, `$name`; "An indexed placeholder with no corresponding argument ... stays in the content unchanged"; escape "\$1.00"; "A backslash doesn't prevent substitution of a ${CLAUDE_*} variable". (CC)
- Hook in a skill example: `'"${CLAUDE_PROJECT_DIR}"/scripts/security-check.sh'` (CC-HK)
- Visual output pattern: a bundled script that generates HTML and prints its path. (CC)

## 8. Task mechanisms

- Gotchas: "The highest-value content in many skills is a list of gotchas" ... "Keep gotchas in SKILL.md" ... "When an agent makes a mistake you have to correct, add the correction to the gotchas section." (AS-BP; BLOG)
- Templates: "more reliable than describing the format in prose"; "Short templates can live inline ... longer templates, or templates only needed in certain cases, store them in assets/" (AS-BP); strict ("ALWAYS use this exact template structure") vs flexible ("sensible default ... use your best judgment"). (PL-BP)
- Checklists: "helps the agent track progress and avoid skipping steps, especially when steps have dependencies or validation gates" (AS-BP); "Copy this checklist and track your progress" (PL-BP)
- Validation loops: "do the work, run a validator (a script, a reference checklist, or a self-check), fix any issues, and repeat until validation passes" (AS-BP); style-guide validator example. (PL-BP)
- Plan-validate-execute: "For batch or destructive operations" (AS-BP); "When to use: Batch operations, destructive changes, complex validation rules, high-stakes operations." (PL-BP)
- Conditional workflows: "Creating new content? → Follow 'Creation workflow'" ... "If workflows become large ... push them into separate files" (PL-BP)
- Patterns: sequential workflow orchestration, multi-MCP coordination, iterative refinement ("Know when to stop iterating"), context-aware tool selection, domain-specific intelligence; problem-first vs tool-first. (PDF)
- "Not every skill needs all of them — use the ones that fit your task." (AS-BP)

## 9. Examples, snippets and templates

- Examples pattern: "For Skills where output quality depends on seeing examples, provide input/output pairs" ... "Follow this style: type(scope): brief description" (PL-BP)
- "Examples are concrete, not abstract" (PL-BP checklist)
- Good vs bad instruction: "Run python scripts/validate.py --input {filename} ... If validation fails, common issues include ..." vs "Validate the data before proceeding." (PDF)
- Error-handling block in the skill: "## Common Issues ... If you see 'Connection refused': 1. ... 2. ..." (PDF)
- Utility script listing with command and output format (PL-BP)
- Dynamic context example and `context: fork` research example. (CC)

## 10. Validation and evaluation

- "Seeing a skill trigger tells you Claude found it, not that it did what you intended ... run each one in a fresh session with the skill available and again with it turned off" (CC)
- Turning a skill off: `skillOverrides` for personal or project skills; `claude plugin eval` for plugin skills. (CC)
- "claude plugin validate .claude/skills ... Requires Claude Code v2.1.233 or later" (CC); `skills-ref validate ./my-skill` (AS-SPEC)
- Evals: "Start with 2-3 test cases"; with and without the skill; assertions "after you see your first round of outputs"; "Require concrete evidence for a PASS"; remove assertions "that always pass in both configurations"; read transcripts; human review. (AS-EVAL)
- "Build evaluations first ... Build three scenarios" ... "At least three evaluations created" ... "Tested with Haiku, Sonnet, and Opus" (PL-BP)
- Claude A writes, Claude B tests; observe navigation: "Unexpected exploration paths", "Missed connections", "Overreliance", "Ignored content". (PL-BP)
- Triggering, functional, performance comparison; "Iterate on a single challenging task" (PDF)
- Evaluation dimensions: triggering accuracy, isolation, coexistence, instruction following, output quality. (PL-ENT)

## 11. Security and distribution

- "Treat like installing software"; audit for network calls, file access, operations that don't match the stated purpose; external URLs risk. (PL-OV)
- Risk indicators: code execution, instruction manipulation, MCP references, network access, hardcoded credentials, filesystem scope, tool calls. (PL-ENT)
- "Principle of Lack of Surprise" (skill-creator); "No hardcoded credentials" (PL-ENT)

## 12. Where the sources disagree

- Description content: what + when (PL-BP, AS-SPEC, PDF) vs "not a summary ... when to trigger" (BLOG). Resolution: what the skill does in capability terms, then when, no workflow summary.
- Description length: 1,024 (spec, platform, uploads, hard) vs 1,536 listing cut, configurable (Claude Code) vs "200 characters maximum" (support article, outdated against the developer docs).
- Emphasis: "CRITICAL" headers and "Repeat key points if needed" (PDF) vs "Reasoning-based instructions ... work better than rigid directives ('ALWAYS do X, NEVER do Y')" (AS-EVAL), all-caps as a "yellow flag" (skill-creator) and "State what to do rather than narrating how or why" (CC).
- `allowed-tools`: "Restrict tool access" (PDF Appendix B) vs "does not restrict" (CC). Claude Code wins for Claude Code.
- Size: "under 5,000 words" (PDF) vs 500 lines and 5,000 tokens (spec, CC).
- Table of contents threshold: 100 lines (PL-BP) vs 300 lines (skill-creator).
- Portability: "work identically across Claude.ai, Claude Code, and API" (PDF) vs "Custom Skills do not sync across surfaces" and runtime differences (PL-OV).
- `/skill-doctor` minimum version: v2.1.252 (CC) vs the changelog entry under 2.1.261.
