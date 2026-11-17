# Existing components

This file teaches you how to take stock of what already surrounds the skill you write, and how to find where it would collide with that environment before you build it. It serves workflow steps 1.5 and 1.6. Each section gives the facts, why they matter for the skill you write, the questions to answer, and what to do with the answers.

## Contents

- How to use this file
- 1. Inventory the components
- 2. Name conflicts
- 3. Trigger overlap and the listing budget
- 4. Project conventions
- Verify and go deeper

## How to use this file

Read it in phase 1, after you know which locations your session loads. Inventory the environment where the model will load the skill, not only your own session: a project skill meets the repository's components, a plugin skill meets the skills, plugins and instructions its users have installed. You cannot see that second environment, so reason about it from the users the plugin is built for, and say in your report that it was not inspected.

---

## 1. Inventory the components

A new skill joins an environment that already instructs the model. Other skills compete for the same requests. `CLAUDE.md` files and rules load in each session and can repeat, contradict or already cover what the skill would say. Claude Code applies hooks and permission rules regardless of what the model decides, so an instruction that fights one fails every time. Subagents, MCP servers, commands and output styles can already do part of the skill's job. What you miss here becomes duplication, contradiction or a skill that never runs.

Some of these components live in files that can hold credential values: `settings.json`, `settings.local.json` and `managed-settings.json` can hold an `env` block or an `apiKeyHelper`, and `.mcp.json` and `~/.claude.json` can hold server tokens and headers. Reading such a file whole puts its secrets into the conversation.

Ask yourself:

1. Which skills reach the target sessions, with which names and descriptions? Your session lists the skills it loaded in the Skill tool's listing.
2. Which plugins are installed, and which skills, agents, hooks and MCP servers do they bring?
3. Which `CLAUDE.md` files, rules, subagents, commands and output styles load in the target sessions?
4. Which hooks and permission rules apply there, and on which events, tools and paths?
5. Which MCP servers and connectors does the skill's work touch?

Then:

- Read each Markdown instruction file in full: `CLAUDE.md` files, rules, skills, subagent definitions and commands.
- List installed plugins with `claude plugin list --json`, and take the connected MCP servers from your tool list.
- Read a settings file only through a filter that prints the keys you need, for example `jq '{hooks, permissions, enabledPlugins, skillOverrides}' .claude/settings.json`. Never print an `env` block, an `apiKeyHelper`, an `.mcp.json` file or `~/.claude.json`.
- Write the inventory down as a list grouped by component type, with each entry's location and a one-line summary of what it does.

## 2. Name conflicts

When two skills share a name, where each came from decides which one runs:

- Enterprise runs over personal, and personal over project.
- A personal or project skill replaces a bundled skill or a built-in command of the same name, but not its aliases: a project skill named `usage` replaces `/usage`, and `/cost` still runs the built-in command.
- A skill runs over a file of the same name in `.claude/commands/`.
- A project-root skill and a nested skill with the same name both load: `/deploy` runs the root skill, and `/apps/web:deploy` runs the nested one.
- A skill in an added directory whose name clashes runs under a prefix, `/<folder>:<name>` (v2.1.309 or later).
- A plugin skill loads beside a skill of the same name, because plugin skills are namespaced as `/plugin-name:skill-name`. The frontmatter `name` of a plugin skill replaces its directory name in the last segment.
- A synced skill whose short name another command uses runs only under its full name, `/anthropic-skills:<name>`.

Claude Code ignores case, spacing, invisible characters and compatibility forms when it compares names, so `Commit` and `commit` are the same name.

Ask yourself:

1. Does the name I plan collide with a skill, command, bundled skill or built-in command in the target sessions?
2. If it collides, which one runs when the user types the name, and is that the one the user expects?
3. Does the name break the reserved-name rules in the gotchas of `SKILL.md`?

Then:

- Choose a name that collides with nothing in the target sessions, or record which skill runs and why that outcome is intended.
- Check the plan against the bundled skills and built-in commands of the installed version too, since a skill that replaces one changes what the user's familiar command does.

## 3. Trigger overlap and the listing budget

The model picks a skill by matching the request against the descriptions in its listing. When two descriptions claim the same requests, the choice between them is unpredictable, and the user cannot tell which skill ran. The listing always holds each skill's name, but its descriptions share a character budget of 1% of the context window. The user can raise it with the `skillListingBudgetFraction` setting or set a fixed count with `SLASH_COMMAND_TOOL_CHAR_BUDGET`, and can list a skill without its description by setting it to `name-only` in `skillOverrides`. A skill whose description was dropped keeps only its name for the model to match.

Ask yourself:

1. Which existing descriptions cover requests the new skill would cover?
2. Should the new skill take those requests, leave them, or absorb the existing skill?
3. How full is the listing in the target sessions, and does the new description push another skill out?

Then:

- Write down each overlapping skill and the requests both would claim, and settle the boundary in phase 3, where you decide the count and boundaries of the skills.
- Ask the user, when the listing could be near its budget, to run `/doctor`, which estimates the listing's context cost and its largest contributors, and `/skill-doctor` (v2.1.252 or later), which reports each skill's cost and how often it runs. `/skill-doctor` answers only in the terminal of the machine where the session runs, not over Remote Control.

## 4. Project conventions

A skill stored in a repository or a plugin has to pass that project's own checks and match its conventions: how skills are named, where their folders sit, which lint, validation and test commands run on each change, and what CI checks before a merge. A skill that ignores them fails review or breaks a build.

Ask yourself:

1. Which naming and folder conventions do the existing skills follow?
2. Which commands lint, validate or test a skill in this project, and which run in CI?
3. Do the conventions conflict with the official sources or with the skill's goal?

Then:

- Find the checks in `package.json` scripts, the Makefile, the CI workflows, `CONTRIBUTING.md` and the project's `CLAUDE.md` and rules, and run each one's `--help` before you plan to use it.
- Record each convention with its source, and weigh it as the rule on the user's material requires.

## Verify and go deeper

Read these pages to confirm a fact in this file against the current official guidance, or to go deeper than this file does.

- Claude Code docs, Skills: "Resolve skills that share a name", "How a skill gets its command name", "When a synced skill name matches another command", "Skill descriptions are cut short", "Find unused skills". https://code.claude.com/docs/en/skills
- Claude Code docs, Environment variables: `SLASH_COMMAND_TOOL_CHAR_BUDGET`. https://code.claude.com/docs/en/env-vars
- Claude Code docs, Settings: `skillOverrides`, `skillListingBudgetFraction`, `enabledPlugins`, `apiKeyHelper`. https://code.claude.com/docs/en/settings-reference
