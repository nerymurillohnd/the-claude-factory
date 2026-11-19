# Phase 2: Skill location

Where a skill can live, which sessions load it from there, and when it loads.

## Gotchas

- At startup, Claude Code loads `.claude/skills/` from the folder the session starts in and from every parent up to the repository root, plus `~/.claude/skills/`. A `.claude/skills/` in a subfolder below the start folder loads only the first time Claude reads or edits a file there, and until then it can't be invoked by name.
- Cowork, cloud sessions and cloud scheduled tasks don't read `~/.claude/skills/`. A cloud scheduled task that invokes a skill found only there reports that the skill was not found.
- A cloud thread in a Claude project doesn't load the skills committed to a repository's `.claude/skills/`, and a cloud session doesn't load the plugins declared in the repository's `.claude/settings.json` or enabled only in the user's settings.
- A `SKILL.md` at a plugin's root loads only when the plugin has no `skills/` folder and no `skills` key in its manifest.
- A skill folder can be a symlink to a folder elsewhere on disk: Claude Code reads `SKILL.md` from the target, and loads the skill once even when several locations point at it.

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
- The user in Cowork, cloud sessions or cloud scheduled tasks: the claude.ai account. Write and edit it on claude.ai, never in the local copy.
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
- Read [Provision and manage skills for your organization](https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization) when the skill goes to an organization on claude.ai. It gives how an owner provisions skills.
