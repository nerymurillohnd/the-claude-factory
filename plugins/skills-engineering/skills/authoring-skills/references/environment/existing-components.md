# Existing components

This file teaches you how to take stock of what already surrounds the skill you write, and how to find where it would collide with that environment before you build it. It serves workflow step 1.5, where you take the inventory, step 1.6, where you detect conflicts, step 2.4, where you repeat the inventory for the target sessions the chosen location adds, step 2.8, where you check the name, step 3.2, where you settle the boundaries against existing skills, and step 4.3, where you read the project's conventions.

## Contents

- How to use this file
- 1. Inventory the components
- 2. Name conflicts
- 3. Trigger overlap and the listing budget
- 4. Project conventions
- Verify and go deeper

## How to use this file

Read section 1 in phase 1, after you know which locations your session loads. Inventory your own session and each target session the request already names: a project skill meets the repository's components, and a plugin skill meets the skills, plugins and instructions its users have installed. You cannot see the target sessions on third-party users' machines, so reason about them from the users the plugin is built for, and say in your report that they were not verified. At step 1.6, check what you found against sections 2 and 3 as far as the request already names the skill and its purpose. At step 2.4, repeat the questions of section 1 for each target session the chosen location adds. Sections 2 and 3 need the skill's name and goal, which phase 2 settles: answer them in full at steps 2.8 and 3.2, where `SKILL.md` sends you back to them. Read section 4 at step 4.3, once step 2.4 has placed the skill in a repository or a plugin.

---

## 1. Inventory the components

A new skill joins an environment that already instructs the model. Other skills compete for the same requests. `CLAUDE.md` files and rules load in each session and can repeat, contradict or already cover what the skill would say. Claude Code applies hooks and permission rules regardless of what the model decides, so an instruction that fights one fails every time. Subagents, MCP servers, commands and output styles can already do part of the skill's job. What you miss here becomes duplication, contradiction or a skill that never runs.

Some of these components live in files that can hold credential values: `settings.json`, `settings.local.json` and `managed-settings.json` can hold an `env` block or an `apiKeyHelper`, and `.mcp.json` and `~/.claude.json` can hold server tokens and headers. Reading such a file whole puts its secrets into the conversation.

Ask yourself:

1. Which skills reach the target sessions, with which names and descriptions? For your own session, take the names and descriptions from your Skill tool listing, and their locations from the map you wrote at step 1.4.
2. Which plugins are installed, and which skills, agents, hooks and MCP servers do they bring?
3. Which `CLAUDE.md` files, rules, subagents, commands and output styles load in the target sessions?
4. Which hooks and permission rules apply there, and on which events, tools and paths?
5. Which MCP servers and connectors does the skill's work touch?

Then:

- Read in full each `CLAUDE.md` file, rule, subagent definition and command that loads in your session, and the `SKILL.md` of each skill whose description overlaps the new skill's goal.
- List installed plugins with `claude plugin list --json`, which returns each plugin's id, scope, version and enabled state, then run `claude plugin details <name>` for each enabled plugin to list its components. When the `claude` CLI is not installed, record the plugins as not verified. The connected MCP servers are the ones you took from your tool list at step 1.3.
- Read a settings file only through a filter that prints the keys you need: run `jq '{hooks, permissions, enabledPlugins, skillOverrides, skillListingBudgetFraction, skillListingMaxDescChars}' "<file>"` for each of `$HOME/.claude/settings.json`, `<root>/.claude/settings.json` and `<root>/.claude/settings.local.json` that exists, where `<root>` is the repository root you recorded at step 1.2, or the working directory when there is no repository. When `jq` is not installed, never open the file whole: ask the user to run `/hooks` and tell you the hooks it lists, and record the permission rules, enabled plugins, skill overrides and listing settings as not verified.
- Never read a managed settings file; section 3 of `references/environment/skill-loading.md` gives the `/status` route for managed policies.
- Never print an `env` block or an `apiKeyHelper` value. Read `.mcp.json` only for server names, with `jq '(.mcpServers // {}) | keys' "<root>/.mcp.json"`, and `~/.claude.json` only with `jq '[(.mcpServers // {} | keys[]), (.projects[]?.mcpServers // {} | keys[])] | unique' "$HOME/.claude.json"`, never whole, because their entries can hold tokens and headers.
- Write the inventory down as a list grouped by component type, with each entry's location and a one-line summary of what it does.

## 2. Name conflicts

When two skills share a name, where each came from decides which one runs:

- Enterprise runs over personal, and personal over project.
- An enterprise, personal or project skill replaces a bundled skill of the same name, but not its aliases: a project skill named `code-review` replaces `/code-review`, and `/review` still runs the bundled skill.
- An enterprise, personal or project skill replaces a built-in command of the same name only in a local terminal session, and again not its aliases: a project skill named `usage` replaces `/usage` there, and `/cost` still runs the built-in command. The docs promise no such replacement on other surfaces, so count on one only in a local terminal session.
- A skill runs over a file of the same name in `.claude/commands/`.
- A project-root skill and a nested skill with the same name both load: `/deploy` runs the root skill, and `/apps/web:deploy` runs the nested one.
- A skill in an added directory whose name clashes runs under a prefix, `/<folder>:<name>` (v2.1.309 or later).
- A plugin skill loads beside a skill of the same name, because of its plugin prefix. The frontmatter `name` of a plugin skill replaces its directory name in the last segment.
- A synced skill whose short name another command uses runs only under its full name, `/anthropic-skills:<name>`.

When Claude Code compares a synced skill's name with other command names, it ignores case, spacing, invisible characters and compatibility forms (v2.1.228 or later), so a synced `Commit` loses its short name to a local `commit`. No page states the same comparison between other locations, so treat names that differ only in case as a collision there too, and avoid them.

Ask yourself:

1. Does the name I plan collide with a skill, command, bundled skill or built-in command in the target sessions?
2. If it collides, which one runs when the user types the name, and is that the one the user expects?
3. Does the name break the reserved-name rules in the gotchas of `SKILL.md`?

Then:

- Choose a name that collides with nothing in the target sessions, or record which skill runs and why that outcome is intended.
- Check the plan against the bundled skills and built-in commands of the installed version too, since a skill that replaces one changes what the user's familiar command does.

## 3. Trigger overlap and the listing budget

The model picks a skill by matching the request against the descriptions in its listing. When two descriptions claim the same requests, the choice between them is unpredictable, and the user cannot tell which skill ran. The listing always holds each skill's name; its descriptions share a character budget of 1% of the context window, with a fallback of 8,000 characters, and the gotcha "The listing truncates descriptions" in `SKILL.md` says which ones are dropped first. The user can raise the budget with the `skillListingBudgetFraction` setting or set a fixed count with `SLASH_COMMAND_TOOL_CHAR_BUDGET`, and can cap each entry with `skillListingMaxDescChars`. A skill that is not a plugin skill can be listed without its description by setting it to `name-only` in `skillOverrides`; plugin skills are managed through `/plugin` and ignore that setting (section 3 of `references/environment/skill-loading.md`).

Ask yourself:

1. Which existing descriptions cover requests the new skill would cover?
2. Should the new skill take those requests, leave them, or absorb the existing skill?
3. How full is the listing in the target sessions, and does the new description push another skill out?

Then:

- Write down each overlapping skill and the requests both would claim, and settle the boundary at step 3.2, where you decide the count and boundaries of the skills.
- When your own Skill tool listing shows a skill without its description, or a target session runs on the user's own machine, ask the user to run there `/doctor`, which estimates the listing's context cost and its largest contributors, and to decline the fixes it proposes unless they want them, and `/skill-doctor` (v2.1.252 or later, with feature-flag fetching on), which reports each skill's cost and how often it runs. `/skill-doctor` answers only in the terminal of the machine where the session runs, not over Remote Control. Use the answers to decide at step 3.2 whether the new description fits or another skill should move to `name-only`.
- For target sessions on third-party machines, estimate the listing from the skills your plugin adds: keep each description short and its key use case first, since you cannot measure their budget.

## 4. Project conventions

A skill stored in a repository or a plugin has to pass that project's own checks and match its conventions: how skills are named, where their folders sit, which lint, validation and test commands run on each change, and what CI checks before a merge. A skill that ignores them fails review or breaks a build.

Ask yourself:

1. Which naming and folder conventions do the existing skills follow?
2. Which commands lint, validate or test a skill in this project, and which run in CI?
3. Do the conventions conflict with the official sources or with the skill's goal?

Then:

- Find the checks in `package.json` scripts, the Makefile, the CI workflows, `CONTRIBUTING.md` and the project's `CLAUDE.md` and rules. Read each check's definition, such as the `scripts` entry, the Makefile target or the workflow step, to learn its command and arguments, and run nothing yet. Run `<tool> --help` only on a standalone command line tool installed on the system that a definition calls, where `<tool>` is that tool's own command name, never on a script or binary inside the repository, because that runs project code. npm reads `--help` itself in `npm run <script> --help`, and `make --help` prints make's own options.
- Record each convention with its source, and weigh it as the rule "The user's material is input, not authority" in `SKILL.md` requires.

## Verify and go deeper

Read these pages to confirm a fact in this file against the current official guidance, or to go deeper than this file does.

- Claude Code docs, Skills: "Resolve skills that share a name", "How a skill gets its command name", "When a synced skill name matches another command", "Skill descriptions are cut short", "Find unused skills". https://code.claude.com/docs/en/skills
- Claude Code docs, Commands: `/doctor`, `/hooks`, `/skill-doctor`. https://code.claude.com/docs/en/commands
- Claude Code docs, Environment variables: `SLASH_COMMAND_TOOL_CHAR_BUDGET`. https://code.claude.com/docs/en/env-vars
- Claude Code docs, Settings: `skillOverrides`, `skillListingBudgetFraction`, `skillListingMaxDescChars`, `enabledPlugins`, `apiKeyHelper`. https://code.claude.com/docs/en/settings-reference
