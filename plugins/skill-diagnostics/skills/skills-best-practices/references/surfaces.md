# Surfaces

How a skill loads, where it runs, and what each surface loads, copies, replaces or skips.

## Contents

- [How skills load](#how-skills-load)
- [After compaction](#after-compaction)
- [Preloading into subagents](#preloading-into-subagents)
- [Origins and the surfaces they reach](#origins-and-the-surfaces-they-reach)
- [Where skills load](#where-skills-load)
- [Names and folders](#names-and-folders)
- [Repository skills in cloud sessions](#repository-skills-in-cloud-sessions)
- [Plugin components by surface](#plugin-components-by-surface)
- [Plugin skills in chat](#plugin-skills-in-chat)
- [How the body behaves by surface](#how-the-body-behaves-by-surface)
- [Runtime limits by surface](#runtime-limits-by-surface)

## How skills load

A skill is a folder with a `SKILL.md` file (frontmatter + Markdown instructions) and optional `scripts/`, `references/` and `assets/` \[AS\]\[PL\]. It loads in three stages, so a skill costs almost nothing until a task needs it \[AS\]\[PL\]\[CC\].

| Level | When it loads | Approximate cost | What loads |
| --- | --- | --- | --- |
| 1. Metadata | Always, at startup | About 100 tokens per skill | `name` and `description` |
| 2. Instructions | When the skill triggers | Under 5,000 tokens recommended | The `SKILL.md` body |
| 3. Resources | Only when read or run | None until accessed | Reference files are read into context; scripts run and only their output enters context |

- **The description triggers the skill.** The description carries the whole burden of triggering: the agent sees only it before deciding \[AS\].
- **Simple requests may not trigger.** Agents usually consult a skill only for tasks beyond what they can do alone; a one-step request such as "read this PDF" may not trigger a PDF skill \[AS\].
- **A loaded skill stays loaded.** In Claude Code, once a skill loads its content stays in the conversation across turns and is not re-read, so every line is a recurring cost \[CC\].

## After compaction

- **First 5,000 tokens re-attached.** After auto-compaction, Claude Code re-attaches each invoked skill's first 5,000 tokens, within a 25,000-token budget shared by all skills, newest first \[CC\]. Put the most important instructions near the top.
- **References are not re-attached.** Only the skill's invocation is re-attached. The page names nothing else, so a reference file Claude read during the task can't be counted on after compaction; a rule that must survive it belongs in the first 5,000 tokens of `SKILL.md`, or the step that needs a reference says to read it again `default`.
- **The skill list is sent again.** After compaction, Claude Code sends Claude the skill list again; `/reload-skills` sends only new or changed skills \[CL\] (2.1.304) `req`.

## Preloading into subagents

- **Full content at startup.** A subagent that preloads a skill through its `skills` field gets the full skill content at startup, not only the description, for up to the first 32 distinct names listed. A skill with `disable-model-invocation: true` can't be preloaded \[CC\].
- **Name reference files instead of preloading an orchestrator.** Preloading an orchestrator skill into a reviewer agent puts the whole orchestrator in the reviewer's context. A plugin agent that needs only some rules names the reference files to read instead `default`.

## Origins and the surfaces they reach

A skill is checked for every surface, but its origin decides which surfaces it reaches and where its fixes belong \[SD\]\[CC\].

| Origin | How to tell | Reaches | Fix it in |
| --- | --- | --- | --- |
| claude.ai account skill | Enabled in claude.ai skills settings; on disk under `~/.claude/skills/synced/` | Chat, Cowork, cloud sessions, project cloud threads, and terminal sessions signed in with that account \[CC\] | claude.ai: a sync overwrites local edits \[CC\] |
| Plugin skill | An ancestor folder holds `.claude-plugin/plugin.json` | Claude Code; chat and Cowork when the plugin is on the account (synced as `<name>@synced`) \[CP\]\[CC\] | The plugin's source |
| Personal | `~/.claude/skills/` | Claude Code on that machine, and desktop scheduled tasks; not Cowork, cloud sessions or cloud scheduled tasks \[CC\] | Locally |
| Project | A repository's `.claude/skills/` | Claude Code in that repository and standalone cloud sessions, which clone it; not a project's cloud threads \[CC\] | The repository |
| Loose folder | Anywhere else | Claude Code once installed or loaded | Locally |

## Where skills load

- **Locations** \[CC\]: personal `~/.claude/skills/`, project `.claude/skills/`, nested, `--add-dir`, plugin `skills/` (as `/plugin:skill`), enterprise, and claude.ai-synced skills. Project skills don't load in Claude Code project cloud threads; personal skills don't load in Cowork or cloud sessions.
- **Bash sandbox and nested folders.** With the Bash sandbox on, skills in `.claude/skills` folders below the starting folder load only if Claude Code starts there or `/cd` moves there \[CL\] (2.1.319; not on the skills page) `req`.

## Names and folders

Owned by `SU-3` and `SU-4` in [checklist.md](checklist.md) \[CC\].

- **Same name, which one runs.** Enterprise wins over personal, and personal over project: with `deploy` in both `~/.claude/skills/` and the project, `/deploy` runs the personal one. A skill and a `.claude/commands/` file with one name: the skill. Plugin skills never clash, being namespaced `/plugin-name:skill-name`.
- **Shadowing a bundled skill or a command.** A personal or project skill named like a bundled skill or a built-in command replaces it, but not its aliases: "A project `code-review` skill replaces `/code-review`, and the bundled alias `/review` never runs your skill". A collision that isn't the point of the skill is a defect.
- **`verify` and `simplify`.** When a session starts with a skill named `verify` or `simplify` that Claude can invoke, from the enterprise, personal, project or added-directory location or a `.claude/commands/` file, Claude's commit instructions tell it to run that skill "right before each commit, except for changes to docs or tests" (v2.1.286+). Plugin skills, synced skills and the bundled ones don't count; `disable-model-invocation: true` turns it off. A skill with one of these names must mean to run before every commit.
- **Symlinked folders.** In the enterprise, personal and project locations a skill folder can be a symlink; Claude Code reads the target and loads it once even when several locations point at it. Plugin skills handle symlinks differently.
- **A skill folder that is a plugin.** A personal or project skill folder that holds `.claude-plugin/plugin.json` can load as a plugin named `<name>@skills-dir`, "with its own agents, hooks, and MCP servers"; in a project this needs the workspace trust dialog, and administrators can block it. What it runs beyond the skill must be announced like any other action.

## Repository skills in cloud sessions

Two cloud cases differ, and both hold \[CC\]:

- **Standalone cloud session.** A standalone cloud session clones the repository and loads the skills committed to its `.claude/skills/` from that clone (cloud environments page).
- **Project cloud thread.** "In a project's cloud thread, skills committed to a repository's `.claude/skills/` aren't available" (skills page).

## Plugin components by surface

A surface skips what it doesn't load, so a plugin can look complete in one place and partial in another \[CP\].

| Component | Chat | Cowork | Claude Code |
| --- | --- | --- | --- |
| Skills | Loads | Loads | Loads |
| Agents | Ignored | Loads | Loads |
| Hooks (`hooks/hooks.json`) | Ignored | Loads | Loads |
| Local MCP server | Ignored | Loads when the session runs on your computer | Loads |
| Executables in `bin/` | Can't be installed | Can't be installed | Loads |

- **State what the skill does without its agents and hooks.** A plugin skill that relies on its agents or hooks states what it does without them, because chat ignores both \[CP\]\[SD\] `rec`.

## Plugin skills in chat

- **In chat only the skill's own folder reaches Claude.** "In chat on claude.ai, the skill's whole folder, scripts included, is copied into the code execution sandbox" \[CP\]. The page names only the skill's folder, so a file at the plugin root or in `agents/` can't be counted on in chat, and a plugin skill that must work there keeps every file it reads or runs inside its own folder `default`.
- **`${CLAUDE_SKILL_DIR}` isn't replaced in chat.** "Claude Code and Cowork replace `${CLAUDE_SKILL_DIR}` with the skill's folder"; in chat the path must also read correctly relative to `SKILL.md`, such as `scripts/render.py` \[CP\] `req`.
- **Upload a plugin from a file.** A plugin can be added to the account from a file: **Customize > Plugins > Add > Upload plugin** with a zip of the folder, up to 5,000 files and 200 MB \[CP\]. It then also reaches Claude Code as a synced plugin \[CP\].

## How the body behaves by surface

- **Cloud session.** In a cloud session, a synced skill's body behaves like a local skill \[CC\].
- **Cowork on the desktop.** In a Cowork session on the desktop, Claude Code replaces every `!` command line with the `disableSkillShellExecution` placeholder, for every skill \[CC\].
- **Synced skill on your machine.** In any other session on your machine, a synced skill doesn't run `!` commands, doesn't attach the files `@` references name, and leaves `${CLAUDE_PROJECT_DIR}` and `${CLAUDE_SESSION_ID}` as literal text \[CC\].
- **Chat and the API.** Claude Code-only body features, such as dynamic context injection, don't function in claude.ai chat or through the API \[CC\].
- **Depending on a skipped feature is a defect.** An instruction that depends on a feature a reached surface skips is a defect `req`; the same feature with nothing depending on it is harmless \[SD\].

## Runtime limits by surface

Runtime limits differ by surface \[PL\]: on the Claude API there is no network and no package installation; on claude.ai network access varies by settings; in Claude Code skills have full network access and should install packages only locally, never globally. How a skill declares and installs its dependencies is in [scripts.md](scripts.md#self-contained-dependencies).
