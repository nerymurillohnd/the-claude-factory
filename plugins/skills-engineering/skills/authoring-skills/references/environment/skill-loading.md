# Skill loading

This file teaches you which sessions load a skill, given where it is stored, the surface, and the settings and policies around it. It serves workflow step 1.4, where you map what loads in your session, the policy part of step 1.6, step 2.4, where you choose where the skill will live, and step 7.4, where you test each surface.

## Contents

- How to use this file
- 1. Storage locations
- 2. Surfaces and what reaches them
- 3. Settings and policies that change a skill
- Verify and go deeper

## How to use this file

Read sections 1 to 3 in phase 1 against your own session, then again in step 2.4 against each target session, and use section 2 to plan the surface tests of step 7.4.

---

## 1. Storage locations

Where a skill is stored decides which sessions find it. Claude Code reads these locations:

- **Enterprise**: `.claude/skills/<name>/SKILL.md` in the managed settings directory. Loads for each user on the machines where the organization deploys it.
- **Personal**: `~/.claude/skills/<name>/SKILL.md`. Loads in each project on that machine.
- **Project**: `.claude/skills/<name>/SKILL.md` in a repository. Loads in sessions started in that directory or below it, which search each parent directory up to the repository root, but not in cloud threads of a Claude project. In a linked git worktree the search stops at the worktree root, and from v2.1.277, when the worktree has no `.claude/skills` at its root, Claude Code loads the main checkout's project skills instead.
- **Nested**: `<subdir>/.claude/skills/<name>/SKILL.md`. Loads at startup in sessions started in or below `<subdir>`, and in a session started above it the first time the model reads or edits a file in `<subdir>`, but not in cloud threads of a Claude project. From v2.1.325, a `.claude/skills/` folder inside a plugin loaded with `--plugin-dir` no longer loads in a session started above the plugin folder, according to the changelog: start Claude Code in the plugin folder instead.
- **Added directory**: `.claude/skills/` inside a directory passed with `--add-dir` or `/add-dir`, or through the Agent SDK's `additionalDirectories` in TypeScript and `add_dirs` in Python. Loads in that session only. The `permissions.additionalDirectories` setting grants file access and loads none of these.
- **Plugin**: `<plugin>/skills/<name>/SKILL.md`. Loads wherever the plugin is enabled, as `/plugin-name:skill-name`.
- **claude.ai account**: the skills enabled on the user's account at claude.ai. Load in Cowork, in cloud sessions and cloud threads of a Claude project, and in terminal sessions signed in through `/login` with that account, which download them into `~/.claude/skills/synced/` (v2.1.273 or later).

Three variants change how a stored skill behaves. A skill folder in the enterprise, personal or project location can be a symlink to a directory elsewhere, and Claude Code loads it once even when several locations point to the same target. A Markdown file in `.claude/commands/` is the older format: it takes the same frontmatter except `name` and `paths`, and it has no supporting files. A personal or project skill folder that holds `.claude-plugin/plugin.json` loads as a plugin named `<name>@skills-dir`, with its own agents, hooks and MCP servers, under narrower conditions than a plain skill. Claude Code reads it only from the `.claude/skills/` of the session's primary working directory, with no parent search, so a session started in a subdirectory does not load a copy at the repository root; from the desktop app in a worktree, it reads the main checkout's copy. In a project, it loads only after the user accepts the workspace trust dialog. A same-named plugin installed from a marketplace or loaded with `--plugin-dir` replaces it. Managed settings skip it without an error when `strictPluginOnlyCustomization` locks one or more kinds of customization, or when a `strictKnownMarketplaces` allowlist leaves out `skills-dir`.

Ask yourself:

1. Which of these locations does my session read, and which skills did it load from each?
2. Which location reaches each target session, and stays out of each session where the skill must not load?
3. Does the skill need what only one location gives, such as a plugin's agents, hooks and MCP servers, or a nested skill's scope to one package?

Then:

- Map your session: for each location, write whether it loads here and why.
- Choose the location from the audience and the surfaces together. One person on one machine points to personal. Everyone who works in a repository points to project. A team or third parties across repositories point to a plugin: installed from a marketplace for local sessions, or turned on for the claude.ai account for Cowork and signed-in terminal sessions, where it loads as `<name>@synced` (v2.1.273 or later in the terminal). Cowork, cloud sessions and cloud threads of a Claude project for one account point to the claude.ai account. Confirm the choice against section 2 before you settle it.
- A plugin reaches the cloud threads of a Claude project only when the user adds it in Project settings > Plugins. Never rely on the repository's own components to reach those threads; section 2 lists what does not load there.

## 2. Surfaces and what reaches them

Each surface takes skills from its own locations, and some drop features a skill can declare:

- **Cloud sessions** start from a fresh clone. The repository's `.claude/skills/`, `.claude/agents/` and `.claude/commands/` load, and so do the skills enabled on the claude.ai account. The user's `~/.claude/` content does not, and neither do plugins declared in the repository's `.claude/settings.json` or enabled only in the user's settings. A cloud scheduled task, also called a routine, starts each run as a fresh cloud session, so a skill stored only on the user's machine is reported as not found.
- **Cloud threads of a Claude project** load the repository root's `CLAUDE.md`, `.claude/CLAUDE.md` and the `.claude/rules/` files that are not path-specific. They do not load the repository's skills, agents, commands, `.mcp.json` servers, or the plugins, permission rules, hooks and `env` of its `.claude/settings.json`. Skills reach them from the claude.ai account, and plugins from the project's settings.
- **Cowork** sessions, interactive and scheduled, do not read `~/.claude/skills/`. They load the skills enabled on the claude.ai account, synced at session start, and replace each `!` command line with the `disableSkillShellExecution` placeholder.
- **Desktop scheduled tasks** run on the user's machine and load personal skills.
- **Terminal sessions** sync the account's skills only when signed in through `/login` and fetching feature flags. They do not sync with an API key, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN` or an `apiKeyHelper`; on Amazon Bedrock or with `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`; in bare mode or with `--safe-mode`; under a managed lock of skills to plugin sources; or with a `--setting-sources` list that leaves out `user`. Skills synced by an earlier session stay on disk and keep loading for the same account.
- **Agent SDK** programs discover skills only through the filesystem setting sources. Default options load the user and project sources; an explicit `settingSources` (`setting_sources` in Python) needs `project` for project and added-directory skills and `user` for personal skills, and the `plugins` option loads skills from a given path. The `skills` option limits which discovered skills the model may invoke: omitted or `"all"`, every one; a list, only those, named by the skill's directory name or, for a plugin skill, `plugin:skill`; `[]`, none. The Skill tool rejects an unlisted skill with `Skill <name> is not in this session's skills allowlist`, while `/<name>` in a prompt still runs it. With an explicit `tools` list, `"Skill"` must be in it.
- **Subagents** receive the full content of each skill named in their `skills` field at startup, up to the first 32 names, and can still invoke other project, user and plugin skills through the Skill tool unless `Skill` is left out of their tools.
- **Claude.ai chat** takes custom skills as uploaded zip files, on plans with code execution turned on, and gives them full, partial or no network access depending on the user's and the admin's settings.
- **The Claude API** takes custom skills through the Skills API (`/v1/skills`), shares them across the workspace, and runs them in a container with no network access and no package installation at run time. Managed Agents attach skills in the agent's `skills` array, or load them from a GitHub repository mounted on the session.

Uploads do not travel between claude.ai and the API: a skill uploaded to one must be uploaded to the other. The Agent Skills overview also says Claude Code skills are separate from both, while the Claude Code skills page documents the sync from the claude.ai account; the Claude Code page is the current source for Claude Code.

Ask yourself:

1. On which surfaces will the model load the skill, and through which location does it reach each one?
2. Which of the skill's features does each surface drop: frontmatter fields, `!` commands, `@` references, substitutions, network access, package installation, hooks, a person to answer?
3. Does my session load the skill the way the target sessions will?

Then:

- List each target surface with the location that reaches it. A surface with no location is a gap: raise it with the user in step 2.10.
- Design the skill's core work for the most restrictive surface on the list. State in the `SKILL.md` body what the model does differently on each other surface, because the model never acts on the `compatibility` frontmatter field. For a skill also uploaded outside Claude Code, name the surfaces it supports in that field as well.
- Plan step 7.4 from the list: test each surface you can reach, and name each one you cannot as not verified.

## 3. Settings and policies that change a skill

Settings and managed policies can hide a skill, block it or strip what it declares, without a change to its files:

- **`skillOverrides`** in settings sets a skill to `on`, `name-only`, `user-invocable-only` or `off`. A skill absent from it counts as `on`. It does not affect plugin skills, which the user manages through `/plugin`.
- **Permission rules** decide which skills the model may invoke. A deny rule on `Skill` turns off every skill. `Skill(name)` matches the exact name and `Skill(name *)` the name with arguments. A deny rule on an unqualified name also blocks a nested skill listed under its directory-qualified name (v2.1.260 or later).
- **`strictPluginOnlyCustomization`** in managed settings can lock skills to plugin sources. When it lists `hooks`, a personal or project skill that declares `hooks` loses its `allowed-tools` pre-approval, and its hooks do not run; plugin skills, bundled skills and skills in the managed settings directory keep their frontmatter hooks.
- **`allowManagedPermissionRulesOnly`** in managed settings makes Claude Code ignore `allowed-tools` in personal and project skills and in the other sources the setting lists (v2.1.282 or later). The tools the model calls then go through the managed rules and the normal permission prompt, while a `!` command follows the checks in the next bullet.
- **Permission checks on `!` commands** run while the skill renders, and never prompt. A command that a deny rule matches aborts the invocation. Outside auto mode, a command whose check returns anything other than allow also aborts it, unless `allowed-tools` pre-approves the command, and deny and ask rules still win over that grant. When the closest repository looks bare, Claude Code ignores `allowed-tools` for a Bash command that contains `git`. In auto mode, an unapproved command does not abort: the skill loads with an instruction for the model to run the command first, except in a forked skill that sets `agent`, where it still aborts.
- **`disableSkillShellExecution`** replaces each `!` command with `[shell command execution disabled by policy]` in user, project, plugin and added-directory skills. Bundled and managed skills keep running theirs.
- **Startup modes** narrow what loads. Bare mode, through `--bare` or `CLAUDE_CODE_SIMPLE`, skips skill discovery apart from skills in an `--add-dir` directory. `--safe-mode` loads no skills or plugins. A `--setting-sources` list without `project` stops the project and added-directory loads. `CLAUDE_CODE_DISABLE_POLICY_SKILLS` skips the managed skills directory.

Ask yourself:

1. Which of these apply in my session, and how do I know?
2. Which of them can apply in the target sessions, where I cannot see them?
3. Does the skill's core work depend on a declaration a policy can strip: `allowed-tools` pre-approval, `hooks`, or `!` commands?

Then:

- When the skill's core work depends on `allowed-tools`, `hooks` or `!` commands and you cannot see the target sessions' managed policies, ask the user to run `/status`. When it shows "Enterprise managed settings", ask the user to confirm with their administrator whether `strictPluginOnlyCustomization` lists `hooks` and whether `allowManagedPermissionRulesOnly` or `disableSkillShellExecution` is set, and apply the next two bullets to each declaration one of them strips.
- For a skill distributed to third parties, put a `!` line only on a command the target sessions' rules are sure to allow, since outside auto mode the checks above abort the whole skill on a command they do not allow. Move the remaining commands into a step the model runs with its Bash tool, where a permission prompt can approve it, and tell the model to run the command itself when a `!` line arrives as the policy placeholder.
- For a rule that must hold every time, in a skill that reaches users whose organizations can lock hooks to plugins, declare the hook in a plugin skill installed from a marketplace, which keeps its frontmatter hooks under that lock.

## Verify and go deeper

Read these pages to confirm a fact in this file against the current official guidance, or to go deeper than this file does.

- Claude Code docs, Skills: "Choose where skills load", "Load skills in monorepos and subdirectories", "Load skills from a directory outside the project", "Use skills in Cowork and cloud sessions", "Skills synced from claude.ai", "When managed settings lock hooks to plugins", "When only managed permission rules apply", "Inject dynamic context", "Permission checks on injected commands", "Restrict Claude's skill access", "Override skill visibility from settings". https://code.claude.com/docs/en/skills
- Claude Code docs, Plugin loading: "Plugins synced from claude.ai", "Check why a repository plugin didn't load", "Skills-directory plugins blocked by managed settings". https://code.claude.com/docs/en/plugins/loading
- Claude Code docs, Hooks: "Limits on skill hooks". https://code.claude.com/docs/en/hooks
- Claude Code docs, Agent SDK, Extend agents with skills: "How skills work with the Agent SDK", "Allow only specific skills". https://code.claude.com/docs/en/agent-sdk/skills
- Claude Code docs, Subagents: "Preload skills into subagents". https://code.claude.com/docs/en/sub-agents
- Claude Code docs, Claude projects: "What threads pick up from your repositories". https://code.claude.com/docs/en/claude-projects
- Claude Code docs, Cloud environments: "What carries over from your setup". https://code.claude.com/docs/en/cloud-environments
- Claude Code changelog, for nested skill loading in `--plugin-dir` plugins (v2.1.325) and the releases since the docs were last updated. https://code.claude.com/docs/en/changelog
- Claude Code docs, Environment variables: `CLAUDE_CODE_SIMPLE`, `CLAUDE_CODE_SAFE_MODE`, `CLAUDE_CODE_DISABLE_POLICY_SKILLS`. https://code.claude.com/docs/en/env-vars
- Claude Platform docs, Agent Skills overview: "Where Skills work", "Limitations and constraints". https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
