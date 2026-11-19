# Phase 2: Skill location

Where a skill can live, which sessions load it from there, and when it loads.

## Gotchas

- A project's cloud thread doesn't load the repository's skills, and a cloud session doesn't load plugins declared in the repository's or the user's settings: tell the user to add the skill to their claude.ai account for those sessions, since only they can.
- A `SKILL.md` at a plugin's root loads only when the plugin has no `skills/` folder and no `skills` key: use one layout or the other.

## The locations

| Location | Path | Loads in |
| :-- | :-- | :-- |
| User scope | `~/.claude/skills/<name>/` | Every Claude Code session of that user on that machine |
| Project scope | `.claude/skills/<name>/` in a repository | Every Claude Code session in the repository, local or cloud, except a project's cloud threads |
| Nested in a project | `<subdir>/.claude/skills/<name>/` | The same sessions, once Claude touches a file in `<subdir>` or the session starts there |
| Added directory | `<dir>/.claude/skills/<name>/` | Only the sessions started with `--add-dir <dir>` or that run `/add-dir` |
| Plugin | `<plugin>/skills/<name>/`, or `<plugin>/SKILL.md` | Sessions where the plugin is installed and enabled |
| claude.ai account | Created or enabled on claude.ai, alone or in a plugin | claude.ai, Cowork, cloud sessions, project threads, and Claude Code signed in with that account, as a download to `~/.claude/skills/synced/`, unless `syncClaudeAiSkills` is `false` on that machine |
| Enterprise | `.claude/skills/<name>/` in the managed settings directory | All users on the machines where the organization deploys it |
| Claude API | A zip uploaded through the Skills API | API requests in that workspace; no other surface |

## Choose the location

Choose by who must get the skill and in which sessions:

- Only the user, in their local sessions: user scope. Write it for that user alone: it can rely on their own tools, paths and conventions.
- Everyone who works in a repository: project scope. Write it for any of them, with no paths, names or settings of one person's machine.
- One package of a monorepo: nested, so it loads with work on that package. A skill that must run before Claude touches the package belongs at the repository root.
- Third parties, on their machines: a plugin in a marketplace.
- The user in Claude, cloud sessions or cloud scheduled tasks: the claude.ai account.
  - In a Claude conversation, deliver the skill file: the user saves it to their account from the conversation, and asks you there for each later change.
  - In Claude Code, package the skill folder as a ZIP, laid out as the architecture file of Phase 2 shows, and tell the user to upload it on claude.ai; for a later change, package it again.
- Every machine of an organization: enterprise. Deliver the skill folder, and tell the user their administrator installs it.

Example: the user works on their laptop and in cloud scheduled tasks. The account skill reaches both; a skill in user scope fails in the cloud with "not found".

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Choose where skills load](https://code.claude.com/docs/en/skills#where-skills-live) when a location's path or loading rule is in doubt. It holds the locations table and the rules for skill folders.
- Read [Load skills in monorepos and subdirectories](https://code.claude.com/docs/en/skills#discovery-from-parent-and-nested-directories) when the skill lives below the repository root or the session runs in a worktree. It covers parent and nested loading.
- Read [Load skills from a directory outside the project](https://code.claude.com/docs/en/skills#skills-from-additional-directories) when the skill lives in an added directory. It says what an added directory loads.
- Read [Use skills in Cowork and cloud sessions](https://code.claude.com/docs/en/skills#skills-in-cowork-and-cloud-sessions) when the skill must reach Cowork, cloud sessions or scheduled tasks. It says which locations those sessions read.
- Read [Skills synced from claude.ai](https://code.claude.com/docs/en/skills#how-synced-skills-behave) when the skill lives on the claude.ai account. It covers how the sync works in each kind of session.
- Read [Plugins synced from claude.ai](https://code.claude.com/docs/en/plugins/loading#synced-plugins) when the skill ships in a plugin that the account or the organization turns on. It says which sessions load synced plugins.
- Read [How to create a skill with Claude through conversation](https://academy.claude.com/tutorials/how-to-create-a-skill-with-claude-through-conversation) when you build the skill in a Claude conversation. It shows how the user saves the skill file Claude creates and asks for changes.
- Read [Package your skill](https://claude.com/docs/skills/how-to#package-your-skill) when you deliver a ZIP for the user to upload. It gives the layout the upload requires and how to check the ZIP first.
- Read [Provision and manage skills for your organization](https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization) when the skill goes to an organization on claude.ai. It gives how an owner provisions skills.

## Exit

You can name where the skill lives, which sessions load it from there, and how it reaches its users. Then return to the step list in `SKILL.md`, and go on with the next file or step.
