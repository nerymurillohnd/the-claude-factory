# Skill loading

This file teaches you which sessions load a skill, given where it is stored, the surface, and the settings and policies around it. It serves workflow step 1.4, where you map what loads in your session, the policy part of step 1.6, step 2.4, where you choose where the skill will live, and step 7.4, where you test each surface. Each section gives the facts, why they matter for the skill you write, the questions to answer, and what to do with the answers.

## Contents

- How to use this file
- 1. Storage locations
- 2. Surfaces and what reaches them
- 3. Settings and policies that change a skill
- Verify and go deeper

## How to use this file

Read sections 1 to 3 in phase 1 against your own session, then again in step 2.4 against each session where the model will load the skill, and use section 2 to plan the surface tests of step 7.4. A skill that loads in your session can be missing from the user's, and a skill missing from yours can load for the user.

---

## 1. Storage locations

Where a skill is stored decides which sessions find it. Claude Code reads these locations:

- **Enterprise**: `.claude/skills/<name>/SKILL.md` in the managed settings directory. Loads for each user on the machines where the organization deploys it.
- **Personal**: `~/.claude/skills/<name>/SKILL.md`. Loads in each project on that machine.
- **Project**: `.claude/skills/<name>/SKILL.md` in a repository. Loads in sessions started in that directory or below it.
- **Nested**: `<subdir>/.claude/skills/<name>/SKILL.md`. Loads at startup in sessions started in or below `<subdir>`, and in a session started above it the first time Claude reads or edits a file in `<subdir>`.
- **Added directory**: `.claude/skills/` inside a directory passed with `--add-dir` or `/add-dir`, or through the Agent SDK's `additionalDirectories` in TypeScript and `add_dirs` in Python. Loads in that session only.
- **Plugin**: `<plugin>/skills/<name>/SKILL.md`. Loads wherever the plugin is enabled, as `/plugin-name:skill-name`.
- **claude.ai account**: the skills enabled on the user's account at claude.ai. Load in Cowork, in cloud sessions and project threads, and in terminal sessions signed in through `/login` with that account, which download them into `~/.claude/skills/synced/` (v2.1.273 or later).

Three variants change how a stored skill behaves. A skill folder in the enterprise, personal or project location can be a symlink to a directory elsewhere, and Claude Code loads it once even when several locations point to the same target. A Markdown file in `.claude/commands/` is the older format: it takes the same frontmatter except `name` and `paths`, and it has no supporting files. A personal or project skill folder that holds `.claude-plugin/plugin.json` loads as a plugin named `<name>@skills-dir`, with its own agents, hooks and MCP servers; in a project, it loads only after the user accepts the workspace trust dialog.

Ask yourself:

1. Which of these locations does my session read, and which skills did it load from each?
2. Which location reaches each session where the model needs the skill, and stays out of each session where it must not load?
3. Does the skill need what only one location gives, such as a plugin's agents, hooks and MCP servers, or a nested skill's scope to one package?

Then:

- Map your session: for each location, write whether it loads here and why.
- Choose the location from the audience and the surfaces together. One person on one machine points to personal. Everyone who works in a repository points to project. A team or third parties across repositories point to a plugin. Cowork, cloud sessions and project threads for one account point to the claude.ai account. Confirm the choice against section 2 before you settle it.

## 2. Surfaces and what reaches them

Each surface takes skills from its own locations, and some drop features a skill can declare:

- **Cloud sessions** start from a fresh clone. The repository's `.claude/skills/`, `.claude/agents/` and `.claude/commands/` load, and so do the skills enabled on the claude.ai account. The user's `~/.claude/` content does not, and neither do plugins declared in the repository's `.claude/settings.json` or enabled only in the user's settings. A cloud scheduled task, also called a routine, starts each run as a fresh cloud session, so a skill stored only on the user's machine is reported as not found.
- **Cloud threads of a Claude project** load the repository root's `CLAUDE.md`, `.claude/CLAUDE.md` and the `.claude/rules/` files that are not path-specific. They do not load the repository's skills, agents, commands, `.mcp.json` servers, or the plugins, permission rules, hooks and `env` of its `.claude/settings.json`. Skills reach them from the claude.ai account, and plugins from the project's settings.
- **Cowork** sessions, interactive and scheduled, load the skills enabled on the claude.ai account, synced at session start, and replace each `!` command line with the `disableSkillShellExecution` placeholder.
- **Desktop scheduled tasks** run on the user's machine and load personal skills.
- **Terminal sessions** sync the account's skills only when signed in through `/login` and fetching feature flags. They do not sync with an API key, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` or an `apiKeyHelper`; on Amazon Bedrock or with `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`; in bare mode or with `--safe-mode`; under a managed lock of skills to plugin sources; or with a `--setting-sources` list that leaves out `user`. Skills synced by an earlier session stay on disk and keep loading for the same account.
- **Subagents** receive the full content of each skill named in their `skills` field at startup, up to the first 32 names, and can still invoke other project, user and plugin skills through the Skill tool unless `Skill` is left out of their tools.
- **Claude.ai chat** takes custom skills as uploaded zip files, on plans with code execution turned on, and gives them full, partial or no network access depending on the user's and the admin's settings.
- **The Claude API** takes custom skills through the Skills API (`/v1/skills`), shares them across the workspace, and runs them in a container with no network access and no package installation at run time. Managed Agents attach skills in the agent's `skills` array, or load them from a GitHub repository mounted on the session.

Uploads do not travel between claude.ai and the API: a skill uploaded to one must be uploaded to the other. The Agent Skills overview also says Claude Code skills are separate from both, while the Claude Code skills page documents the sync from the claude.ai account; the Claude Code page is the current source for Claude Code.

Ask yourself:

1. On which surfaces will the model load the skill, and through which location does it reach each one?
2. Which of the skill's features does each surface drop: frontmatter fields, `!` commands, `@` references, substitutions, network access, package installation, hooks, a person to answer?
3. Does my session load the skill the way the user's sessions will?

Then:

- List each target surface with the location that reaches it. A surface with no location is a gap: raise it with the user in step 2.10.
- Design the skill's core work for the most restrictive surface on the list, and state in the skill or its compatibility notes what changes on each other surface.
- Plan step 7.4 from the list: test each surface you can reach, and name each one you cannot as not verified.

## 3. Settings and policies that change a skill

Settings and managed policies can hide a skill, block it or strip what it declares, without a change to its files:

- **`skillOverrides`** in settings sets a skill to `on`, `name-only`, `user-invocable-only` or `off`. A skill absent from it counts as `on`. It does not affect plugin skills, which the user manages through `/plugin`.
- **Permission rules** decide which skills Claude may invoke. A deny rule on `Skill` turns off every skill. `Skill(name)` matches the exact name and `Skill(name *)` the name with arguments. A deny rule on an unqualified name also blocks a nested skill listed under its directory-qualified name (v2.1.260 or later).
- **`strictPluginOnlyCustomization`** in managed settings can lock skills to plugin sources. When it lists `hooks`, a personal or project skill that declares `hooks` loses its `allowed-tools` pre-approval, and its hooks do not run.
- **`allowManagedPermissionRulesOnly`** in managed settings makes Claude Code ignore `allowed-tools` in personal and project skills (v2.1.282 or later), so their tools go through the managed rules and the normal permission prompt.
- **`disableSkillShellExecution`** replaces each `!` command with `[shell command execution disabled by policy]` in user, project, plugin and added-directory skills. Bundled and managed skills keep running theirs.
- **Startup modes** narrow what loads. Bare mode, through `--bare` or `CLAUDE_CODE_SIMPLE`, skips skill discovery apart from skills in an `--add-dir` directory. `--safe-mode` loads no skills or plugins. A `--setting-sources` list without `project` stops the project and added-directory loads. `CLAUDE_CODE_DISABLE_POLICY_SKILLS` skips the managed skills directory.

The user can see the organization's policies with `/status`, which shows "Enterprise managed settings" when a managed policy applies.

Ask yourself:

1. Which of these apply in my session, and how do I know?
2. Which of them can apply in the users' sessions, where I cannot see them?
3. Does the skill's core work depend on a declaration a policy can strip: `allowed-tools` pre-approval, `hooks`, or `!` commands?

Then:

- Ask the user to run `/status` when a managed policy could change the skill and you cannot see one.
- For a skill distributed to third parties, give each declaration a policy can strip a fallback the model can follow: tell it to run the command itself when a `!` line arrives as the policy placeholder, and keep its work possible through normal permission prompts when `allowed-tools` is ignored.
- Avoid relying on a skill-level hook for a rule that must hold under `strictPluginOnlyCustomization`; in a plugin installed from a marketplace, the hook keeps running.

## Verify and go deeper

Read these pages to confirm a fact in this file against the current official guidance, or to go deeper than this file does.

- Claude Code docs, Skills: "Choose where skills load", "Load skills in monorepos and subdirectories", "Load skills from a directory outside the project", "Use skills in Cowork and cloud sessions", "Skills synced from claude.ai", "When managed settings lock hooks to plugins", "When only managed permission rules apply", "Inject dynamic context", "Restrict Claude's skill access", "Override skill visibility from settings". https://code.claude.com/docs/en/skills
- Claude Code docs, Subagents: "Preload skills into subagents". https://code.claude.com/docs/en/sub-agents
- Claude Code docs, Claude projects: "What threads pick up from your repositories". https://code.claude.com/docs/en/claude-projects
- Claude Code docs, Cloud environments: "What carries over from your setup". https://code.claude.com/docs/en/cloud-environments
- Claude Code docs, Environment variables: `CLAUDE_CODE_SIMPLE`, `CLAUDE_CODE_SAFE_MODE`, `CLAUDE_CODE_DISABLE_POLICY_SKILLS`. https://code.claude.com/docs/en/env-vars
- Claude Platform docs, Agent Skills overview: "Where Skills work", "Limitations and constraints". https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
