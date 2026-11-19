# Phase 2: Skill location

The places a skill can live, the path of each, and what each one changes in the skill you write.

## Contents

- [Gotchas](#gotchas)
- [The locations](#the-locations)
- [Path variables by location](#path-variables-by-location)
- [Skill folder rules](#skill-folder-rules)
- [User scope](#user-scope)
- [Project scope](#project-scope)
- [Nested in a project](#nested-in-a-project)
- [Added directory](#added-directory)
- [Plugin](#plugin)
- [claude.ai account](#claudeai-account)
- [Enterprise](#enterprise)
- [Bundled](#bundled)
- [Uploads outside Claude Code](#uploads-outside-claude-code)
- [Official sources](#official-sources)

## Gotchas

- At startup, Claude Code loads `.claude/skills/` from the folder the session starts in and from every parent up to the repository root, plus `~/.claude/skills/`. A `.claude/skills/` in a subfolder below the start folder loads only the first time Claude reads or edits a file there.
- A skill synced from claude.ai is a download. An edit to its copy in `~/.claude/skills/synced/` never reaches the account, and the next sync can overwrite it.
- A `SKILL.md` at a plugin's root loads only when the plugin has no `skills/` folder and no `skills` key in its manifest.
- A plugin doesn't load a `CLAUDE.md` at its root. Instructions a plugin must give Claude go in a skill.
- Claude Code replaces the path variables in two places only: the body of `SKILL.md`, and the `Bash(...)` rules of `allowed-tools`. A reference file that Claude opens keeps them as literal text, and the commands Claude runs through the Bash tool don't have them in their environment. State each resolved path in `SKILL.md`: tell Claude the path when it opens a reference, and pass it to a script as an argument.
- In a plugin skill, `${CLAUDE_SKILL_DIR}` is the skill's own subfolder, not the plugin root. A file shared by several skills of the plugin needs `${CLAUDE_PLUGIN_ROOT}`.
- A plugin installed from a marketplace is copied into Claude Code's cache, and nothing outside the plugin folder is copied with it. A path above the plugin root, such as `../shared`, isn't there at run time. A symlink is kept when it points inside the plugin, replaced by its target's content when it points elsewhere in the same marketplace, and dropped when it points outside it.
- claude.ai rejects a plugin with a top-level `bin/` folder. Keep the plugin's executables in `scripts/`, and call them as `${CLAUDE_PLUGIN_ROOT}/scripts/<name>`.
- `paths` in the frontmatter matches files against Claude's working directory. A file outside it, such as one in a sibling worktree, never activates the skill.

## The locations

| Location | Path |
| :- | :- |
| User scope | `~/.claude/skills/<skill-name>/SKILL.md` |
| Project scope | `.claude/skills/<skill-name>/SKILL.md` |
| Nested in a project | `<subdir>/.claude/skills/<skill-name>/SKILL.md` |
| Added directory | `<dir>/.claude/skills/<skill-name>/SKILL.md`, with `--add-dir <dir>` |
| Plugin, `skills/` folder | `<plugin>/skills/<skill-name>/SKILL.md` |
| Plugin, root | `<plugin>/SKILL.md` |
| claude.ai account | Created or enabled on claude.ai, downloaded to `~/.claude/skills/synced/<skill-name>/` |
| Plugin synced from claude.ai | Turned on for the account or by the organization, loaded as `<plugin>@synced` |
| Enterprise | `.claude/skills/<skill-name>/SKILL.md` in the managed settings directory |
| Bundled | Ships with Claude Code, such as `/code-review`, `/loop` and `/claude-api` |

## Path variables by location

In Claude Code, reach the skill's files and the project's through these variables, not through a relative path. A relative path in an injected command resolves from the session's working directory, which moves when Claude runs `cd`. Outside Claude Code, where no variable is replaced, use paths relative to the skill root.

| Location | `${CLAUDE_SKILL_DIR}` | `${CLAUDE_PLUGIN_ROOT}` | `${CLAUDE_PROJECT_DIR}` |
| :- | :- | :- | :- |
| User, project, nested, added directory, enterprise | The skill's folder | Not replaced | The project root |
| Plugin, `skills/` folder | The skill's subfolder | The root of the installed plugin version | The project root |
| Plugin, root | The plugin root, same as `${CLAUDE_PLUGIN_ROOT}` | The root of the installed plugin version | The project root |
| claude.ai account, in a terminal or VS Code session | The skill's folder | Not replaced | Not replaced: stays as literal text |
| Upload outside Claude Code | Not replaced | Not replaced | Not replaced |

A plugin also has `${CLAUDE_PLUGIN_DATA}`, a folder that survives plugin updates. `${CLAUDE_PLUGIN_ROOT}` changes with every version, so the skill writes nothing there that must last.

```markdown
Incorrect, because the path resolves from wherever the session is:
!`python3 scripts/check.py`

Correct, for a script in the skill's own folder:
!`python3 ${CLAUDE_SKILL_DIR}/scripts/check.py`

Correct, for a script that several skills of a plugin share:
!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check.py`
```

## Skill folder rules

Rules for the skill folder in the enterprise, user and project locations:

- Write a skill folder, not a file in `.claude/commands/`. That older format still loads, but holds no supporting files, and takes neither `name` nor `paths`.
- The skill folder can be a symlink to a folder elsewhere on disk. Claude Code reads `SKILL.md` from the target, and loads the skill once even when several locations point at it. Plugins handle symlinks differently.
- A user or project skill folder that also holds `.claude-plugin/plugin.json` loads as a plugin named `<name>@skills-dir`, with its own agents, hooks and MCP servers. Use it when the skill needs those. In a project it loads only after the user accepts the workspace trust dialog, and in either location an administrator can block it.

## User scope

A skill for one user, in every project on their machine.

- Write it for that user alone: it can rely on their own tools, paths and conventions.

## Project scope

A skill committed to a repository, for everyone who works in it.

- Everyone who clones the repository gets it. Write it for any of them: no paths, names or settings of one person's machine.
- Refer to project files through `${CLAUDE_PROJECT_DIR}` in `SKILL.md`, so the path holds wherever the session starts.

## Nested in a project

A project skill that belongs to one package or folder of a repository.

- It loads only once Claude touches a file in its folder, so it fits work on that package. A skill that must run before Claude touches the package belongs at the repository root.
- When its folder name matches another skill's, it runs as `/<subdir>:<skill-name>`, such as `/apps/web:deploy`.

## Added directory

A skill in a directory outside the project that a session adds with `--add-dir` or `/add-dir`.

- It loads only in the sessions that add that directory.
- When its name matches another skill's, it runs under the added folder's name: with `--add-dir ../cli`, a `verify` skill there runs as `/cli:verify`.

## Plugin

A skill distributed inside a plugin, to every user who installs and enables it.

- It runs as `/<plugin>:<skill-name>`, so it never clashes with a skill elsewhere.
- Reach the skill's own files through `${CLAUDE_SKILL_DIR}`, files shared across the plugin through `${CLAUDE_PLUGIN_ROOT}`, and data that must outlive an update through `${CLAUDE_PLUGIN_DATA}`.
- A plugin can add skill folders beyond `skills/` with the `skills` key in `plugin.json`. They add to the `skills/` scan.
- A single skill at the plugin root needs `name` in its frontmatter. Without it, a marketplace install names the skill after its cache folder.

```text
billing/
├── .claude-plugin/plugin.json
└── skills/
    └── close-month/
        └── SKILL.md          → /billing:close-month
```

## claude.ai account

A skill the user creates or enables on claude.ai, which Claude Code downloads into `~/.claude/skills/synced/`.

- Write and edit it on claude.ai, never in the local copy.
- Enabling it uploads it, so its frontmatter holds only `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`.
- In a terminal or VS Code session, its `!` commands don't run, its `@` references don't attach files, and `${CLAUDE_PROJECT_DIR}` and `${CLAUDE_SESSION_ID}` stay as literal text. Write the body so it needs none of them:

  ```markdown
  Incorrect, because in a terminal session the line arrives as literal text:
  !`git diff HEAD`

  Correct:
  Run `git diff HEAD` and summarize the changes it shows.
  ```

- It runs as `/anthropic-skills:<skill-name>`, or as `/<skill-name>` while no other command uses that name.

## Enterprise

A skill the organization deploys to every machine it manages.

- An administrator places it in the managed settings directory, such as `/etc/claude-code/.claude/skills/<skill-name>/` on Linux. Deliver the skill folder, and tell the user it is their administrator who installs it.
- It wins over a user or project skill with the same name.

## Bundled

A skill that ships with Claude Code, such as `/code-review`, `/debug`, `/loop` or `/claude-api`.

- Before you write a skill, check that no bundled skill already does the job.
- A skill of yours with a bundled skill's name replaces it, but not its aliases.

## Uploads outside Claude Code

A skill uploaded to claude.ai or to the Claude API, or used by another Agent Skills client, runs without Claude Code's processing:

- Frontmatter: only the six fields above. Any other field fails the upload:

  ```text
  Unexpected key(s) in SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name
  ```

- Body: argument placeholders, `${CLAUDE_*}` variables and injected commands don't work. Refer to bundled files by paths relative to the skill root.
- Claude API: scripts run with no network and no package installs, only the preinstalled packages. A script that needs either fails there.
- A skill uploaded to one surface isn't on the others. Each surface gets its own upload.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read [Choose where skills load](https://code.claude.com/docs/en/skills#where-skills-live) when a location's path or loading rule is in doubt. It holds the locations table and every rule for skill folders: symlinks, reserved names, command files, and folders that load as plugins.
- Read [Load skills in monorepos and subdirectories](https://code.claude.com/docs/en/skills#discovery-from-parent-and-nested-directories) when the skill lives below the repository root or the session runs in a worktree. It covers parent and nested loading, how `/cd` and `/add-dir` change it, and the versions each behavior needs.
- Read [Load skills from a directory outside the project](https://code.claude.com/docs/en/skills#skills-from-additional-directories) when the skill lives in an added directory or reaches an Agent SDK session. It says what an added directory loads, and what restricts it.
- Read [Skills synced from claude.ai](https://code.claude.com/docs/en/skills#how-synced-skills-behave) when the skill lives on the claude.ai account. It covers how frontmatter and body are handled in each kind of session, and how a synced skill's name works.
- Read [Plugins synced from claude.ai](https://code.claude.com/docs/en/plugins/loading#synced-plugins) when the skill ships in a plugin that the account or the organization turns on. It says which sessions load synced plugins and what they load.
- Read [Skills in a plugin](https://code.claude.com/docs/en/plugins/components#skills) when the skill ships in a plugin. It shows the layout, the command name, extra skill folders, the single skill at the root, and why a plugin's instructions go in a skill.
- Read [Available string substitutions](https://code.claude.com/docs/en/skills#available-string-substitutions) when the body refers to files by a path variable. It defines each variable, where Claude Code replaces it, and how the same variable in the body and in `allowed-tools` runs a bundled script without a prompt.
- Read [Environment variables](https://code.claude.com/docs/en/plugins/manifest-reference#environment-variables) when a plugin skill, hook or server needs a path. It tables where each variable resolves in each kind of plugin component, and which processes receive it in their environment.
- Read [Find plugins on disk](https://code.claude.com/docs/en/plugins/loading#find-plugins-on-disk) when the skill reads or writes plugin files at run time. It shows where the installed version and the data folder live, which plugins load in place and which are copied, and why a path above the plugin root isn't found.
- Read [Share files within a marketplace with symlinks](https://code.claude.com/docs/en/plugins/host-marketplace#share-files-within-a-marketplace-with-symlinks) when a plugin skill links to files outside its folder. It says which symlinks are kept, copied or dropped when the plugin is installed, and why claude.ai rejects a top-level `bin/`.
- Read [How injected commands run](https://code.claude.com/docs/en/skills#how-injected-commands-run) when the skill injects a command that touches a file. It gives the working directory, the shell, the timeout and the output limits of each injected command.
- Read [Bundled skills](https://code.claude.com/docs/en/skills#bundled-skills) and [Commands](https://code.claude.com/docs/en/commands) when the skill's job may already be bundled. They list the skills and commands that ship with Claude Code.
- Read [Resolve skills that share a name](https://code.claude.com/docs/en/skills#resolve-skills-that-share-a-name) when the same name may exist at another location. It gives the full table of which skill runs.
- Read [Using skill frontmatter outside Claude Code](https://code.claude.com/docs/en/skills#using-skill-frontmatter-outside-claude-code) when the skill uploads to claude.ai or the API. It gives the fields each distribution path accepts, the exact upload error, and where the other validation rules live.
- Read [Limitations and constraints](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#limitations-and-constraints) and [Limits and constraints](https://platform.claude.com/docs/en/build-with-claude/skills-guide#limits-and-constraints) when the skill uploads to claude.ai or the API. They give each surface's runtime and network limits, the request and upload limits, and how far each upload is shared.
- Read [How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) and [Provision and manage skills for your organization](https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization) when the skill goes to claude.ai or to an organization. They give how to structure and upload a skill, and how an owner provisions skills to everyone or, on Enterprise, to one group through a plugin.
