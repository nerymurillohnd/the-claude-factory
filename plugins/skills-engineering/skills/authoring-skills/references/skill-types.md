# Skill types

What each kind of skill is, where it loads, which frontmatter fields it takes, and how its folder is laid out. Check any fact here against https://code.claude.com/docs/en/skills and https://agentskills.io/specification before you rely on it: these change between Claude Code versions.

## Contents

- Identify the type
- Locations and where each loads
- Surfaces and what each allows
- Frontmatter fields
- Invocation
- Skills run by subagents
- Arguments and substitutions
- Body features by surface
- Layout per type

## Identify the type

A skill's type is its location plus every surface it must run on. One skill can be several types at once, such as a plugin skill that is also uploaded to claude.ai. Settle both before choosing fields, because a field valid in one place breaks the upload in another.

Ask, in this order:

1. Where will the files live: managed settings, `~/.claude/skills/`, a repository's `.claude/skills/`, a subfolder's `.claude/skills/`, a plugin, or an upload to claude.ai or the Skills API?
2. Who triggers it: its users by `/name`, the model on its own, both, or a subagent?
3. Which surfaces must run it: Claude Code in a terminal, IDE or desktop app; Claude Code cloud sessions and project threads; Cowork; claude.ai; the Claude API; Managed Agents; another Agent Skills client?
4. Does it run in the main conversation, in a forked subagent, or preloaded into a custom subagent?

## Locations and where each loads

- **Enterprise**: `.claude/skills/<name>/SKILL.md` in the managed settings directory. Loads for every user on machines where the organization deploys it. Wins over personal and project skills of the same name.
- **Personal**: `~/.claude/skills/<name>/SKILL.md`. Loads in every project on that machine, but not in Cowork or cloud sessions, which never read the local home folder. Wins over a project skill of the same name.
- **Project**: `.claude/skills/<name>/SKILL.md`, committed to the repository. Loads in sessions in that repository, including cloud sessions, but not in cloud threads of a Claude project. Claude Code also loads `.claude/skills/` from every parent folder up to the repository root.
- **Nested**: `<subdir>/.claude/skills/<name>/SKILL.md`. Loads for sessions started in or below `<subdir>`, and for a session started higher up only once Claude reads or edits a file in that subfolder. A nested skill that shares a name with a root skill stays available as `/<subdir>:<name>`.
- **Additional directory**: `.claude/skills/` inside a folder passed with `--add-dir` or `/add-dir`. Loads for that session. `permissions.additionalDirectories` grants file access only and loads no skills.
- **Plugin `skills/`**: `<plugin>/skills/<name>/SKILL.md`. Loads wherever the plugin is enabled, always namespaced as `/<plugin>:<name>`, so it never collides with skills in other locations.
- **Plugin root**: a `SKILL.md` at the plugin root, in a plugin with no `skills/` folder and no `skills` key in its manifest, loads as the plugin's single skill. Set `name`: without it the command falls back to the plugin folder name.
- **Skill folder as a plugin**: a personal or project skill folder with `.claude-plugin/plugin.json` loads as a plugin named `<name>@skills-dir`, with its own agents, hooks and MCP servers. In a project it needs the workspace trust dialog accepted, and administrators can block it.
- **Command file**: a Markdown file in `.claude/commands/` is the older format. It takes the same frontmatter except `name` and `paths`, and has no supporting files. A skill of the same name wins. Write a skill for new work.
- **claude.ai account**: skills uploaded to or enabled on claude.ai. Cowork, cloud sessions and terminal sessions signed in with that account download them into `~/.claude/skills/synced/`. Downloads only: an edit there never reaches claude.ai and the next sync overwrites it. Change the skill on claude.ai.
- **Skills API**: uploaded to `/v1/skills` and shared with the whole workspace. A new version is a full snapshot, not a delta, under the same `name`.
- **Managed Agents**: attached in the agent's `skills` array, or read from a GitHub repository mounted in the session at `.claude/skills/<name>/SKILL.md`.

Names Claude Code refuses or skips:

- A folder named `synced`, in any letter case, in the enterprise, personal or project location.
- A folder, frontmatter `name` or command file named `anthropic-skills` or starting with `anthropic-skills:`.
- A name with a zero-width space, a control or private-use character, a direction-changing character, a blank other than one plain space between words, or `<` or `>`. Outside a plugin, the skill does not load. Inside a plugin's `skills/`, the characters become hyphens in the command name; in a frontmatter `name`, the name is ignored.
- A skill named `verify` or `simplify` in an enterprise, personal, project or additional-directory location, that Claude can invoke, makes Claude run it before each commit (Claude Code v2.1.286 or later). A project `verify` also replaces the bundled `/verify`. Pick another name unless that is the intent.
- A skill whose name matches a bundled skill or built-in command replaces it in a local session, but not its aliases.

## Surfaces and what each allows

Custom skills do not sync between surfaces. A skill built in Claude Code is not on claude.ai or the API until someone uploads it there, and each upload is managed separately.

- **Claude Code**: every frontmatter field and body feature in this file. Full network access, like any program on the machine. Install packages locally to the skill or project, never globally.
- **Claude Code cloud sessions and Cowork**: account skills from claude.ai; project skills from the repository in cloud sessions other than project threads. Cowork replaces every injected command with a disabled placeholder.
- **claude.ai**: uploaded as a zip, on plans with code execution enabled. Network access depends on user and admin settings; it can install npm and PyPI packages. Accepts only the six spec fields.
- **Claude API and Skills API**: runs in the code execution container. No network, no package installs at runtime: only the preinstalled packages listed for the code execution tool. Upload under 30 MB, `SKILL.md` at the upload root or one enclosing folder, up to 20 skills per request. Accepts only the six spec fields. Claude Platform on AWS, Google Cloud and Microsoft Foundry (hosted on Anthropic) follow the API's rules.
- **Managed Agents**: the API runtime, up to 500 skills per session.
- **Other Agent Skills clients**: the specification only. Assume none of Claude Code's extensions.

For a skill that must run on more than one surface, write to the strictest one: the six spec fields, no injected commands, no `CLAUDE_` variables, scripts that need no network and only preinstalled packages. Put Claude Code extras in a separate Claude Code-only copy, or leave them out.

## Frontmatter fields

Every field is optional in Claude Code; only `description` is recommended. Claude Code reads frontmatter only when `---` is the file's first line, ignores a misspelled field without an error, and loads a skill whose YAML fails to parse with no fields set. Booleans accept `true`, `false`, `yes`, `no`, `on`, `off`, `1` and `0`.

### The six spec fields (every surface)

- **`name`**: 1-64 characters, lowercase letters, digits and hyphens, no leading, trailing or doubled hyphen, matching the folder name. The platform also refuses XML tags and the words `anthropic` and `claude`. Set it on every skill that leaves Claude Code. In Claude Code it sets the command name; in a plugin it sets the last segment after the plugin prefix.
- **`description`**: 1-1,024 characters, no XML tags. What the skill does and when to use it. Read [name-and-description.md](name-and-description.md) before writing it.
- **`license`**: a license name or the name of a bundled license file. Set it on a skill distributed to third parties outside a plugin that already states its license.
- **`compatibility`**: up to 500 characters on environment requirements: intended product, system packages, network access. Set it only when the skill fails without something the surface may lack, such as `Requires git, docker and network access`.
- **`metadata`**: a map of string keys to string values for your own tooling, such as `author` or `version`. No agent acts on it. Never reuse a frontmatter field name as a key.
- **`allowed-tools`**: pre-approved tools. Experimental in the spec, and support varies between clients. In Claude Code it grants, it never restricts; see below.

Any other key makes a claude.ai upload, a Skills API upload or `package_skill.py` fail with `Unexpected key(s) in SKILL.md frontmatter`.

### Claude Code fields

Set each only when the reason applies; an unset field keeps the default, which is right for most skills.

- **`when_to_use`**: extra trigger phrases or example requests, appended to `description` in the listing and counted in its 1,536-character cap. Use it only for a Claude Code-only skill whose triggers don't fit the description; it breaks uploads.
- **`argument-hint`**: autocomplete hint, such as `[issue-number]` or `[filename] [format]`. Set it when the skill takes arguments.
- **`arguments`**: names for positional arguments, as a space-separated string or a YAML list, so the body can say `$issue` instead of `$0`. Set it when the skill takes two or more arguments.
- **`disable-model-invocation: true`**: only users can invoke it by `/name`. The description leaves Claude's context. See Invocation.
- **`user-invocable: false`**: only Claude can invoke it; hidden from the `/` menu. See Invocation.
- **`allowed-tools`**: tools Claude may use without asking during the turn that invokes the skill; the grant clears at the user's next message. It doesn't remove other tools. Grant the narrowest rule that covers the commands the body tells Claude to run, such as `Bash(git add *) Bash(git commit *)`, never `Bash`. A project skill's grant applies even in a `-p` run in an untrusted folder, and organizations can ignore it with `allowManagedPermissionRulesOnly`.
- **`disallowed-tools`**: tools removed while the skill is active, until the next user message. Set it for autonomous skills that must never call a tool, such as `AskUserQuestion` in a background loop.
- **`model`**: the model for the rest of the current turn, or the forked subagent's model with `context: fork`. Set it only when the task needs a specific capability tier; an organization's allowlist or auto mode can refuse it.
- **`effort`**: `low`, `medium`, `high`, `xhigh` or `max` for the rest of the turn, or the fork's level. Set it when the task needs deeper reasoning than the session default, or less for a mechanical fork.
- **`context: fork`**: runs the skill in a new subagent with the body as its task. See Skills run by subagents.
- **`agent`**: the subagent type for `context: fork`: `Explore`, `Plan`, `general-purpose` (default) or a custom agent name.
- **`background`**: with `context: fork`, `false` waits for the result in the invoking turn and keeps the full tool set. Default `true`.
- **`hooks`**: hooks registered when the skill is invoked, kept for the rest of the session. Read [scripts-and-hooks.md](scripts-and-hooks.md) before adding them.
- **`paths`**: glob patterns, relative to Claude's working directory, that limit automatic loading to work on matching files. Set it when the skill only applies to certain files, such as `src/api/**`. Files outside the working directory never match.
- **`shell`**: `bash` (default) or `powershell` for injected commands. Set `powershell` only for a Windows-only skill.

## Invocation

- **Default**: users can type `/name`, and Claude loads it when the description matches. Use for most skills.
- **`disable-model-invocation: true`**: users only. Use for actions with side effects or timing the user must control, such as committing, deploying or sending messages. The description is not in Claude's context; Claude Code blocks Claude's call unless the user's message contains `/name` as its own word. Such a skill can't be preloaded into a subagent, can't be the prompt of a session-scoped scheduled task, and other skills can't load it.
- **`user-invocable: false`**: Claude only. Use for background knowledge that is not an action, such as how a legacy system works. It hides the skill from the menu, but Claude can still invoke it; to stop Claude, use `disable-model-invocation`.

Choose by consequence: if Claude running it unasked could change something the user didn't approve, require the user to invoke it.

## Skills run by subagents

Two opposite directions; pick by who writes the task.

- **`context: fork` on the skill**: the skill's body becomes the task of a new subagent of type `agent`. The subagent sees no conversation history, so the body must carry everything: the goal, the inputs (usually through `$ARGUMENTS` or injected commands), the steps and the output to return. It runs in the background by default with the narrower background tool set, and its edits fall outside checkpoints. `Explore` and `Plan` start without CLAUDE.md. A body of guidelines with no task returns nothing useful: use fork only for a skill that is a complete task.
- **Preloaded through a subagent's `skills` field**: the full body is injected into the subagent's context at startup as reference, beside the task Claude delegates. Up to 32 distinct names; a missing or disabled one is skipped with a debug-log warning; a skill with `disable-model-invocation: true` can't be preloaded. Write it as reference content the subagent applies to whatever it was asked, with no assumption about the conversation that spawned it.

What changes in the body for each:

- A forked skill opens with the task and ends with what to return to the main conversation.
- A preloaded skill opens with the knowledge or procedure and never refers to "the user's request", because the subagent's task comes from its delegation message.
- Neither can ask the user mid-task in a background run; state the default to take and what to report instead.

## Arguments and substitutions

Claude Code replaces these in the rendered `SKILL.md` before Claude reads it:

- `$ARGUMENTS`: the full argument string as typed. With no placeholder in the body, Claude Code appends `ARGUMENTS: <value>` at the end.
- `$ARGUMENTS[N]` or `$N`: the argument at 0-based position N, shell-quoted. An unmatched index stays as literal text.
- `$name`: a name declared in `arguments`; an unmatched one becomes empty.
- `${CLAUDE_SKILL_DIR}`: the folder holding `SKILL.md`, in a plugin the skill's own folder.
- `${CLAUDE_PROJECT_DIR}`: the project root.
- `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`: plugin skills only; the plugin's install folder and its persistent data folder.
- `${CLAUDE_SESSION_ID}` and `${CLAUDE_EFFORT}`: the session ID and the current effort level.

The path variables are also replaced inside `allowed-tools` Bash rules, so the same variable in the rule and in the body's command lets a bundled script run without a prompt. They are not set in the environment of the commands Claude runs: the text is replaced before Claude sees it.

These substitutions exist only in Claude Code. On claude.ai and the API the text reaches Claude unchanged; refer to bundled files by paths relative to the skill root there.

## Body features by surface

- **Injected commands**: a backtick command preceded by an exclamation mark, or a fenced block opened with three backticks and an exclamation mark, runs before Claude sees the body and is replaced by its output. Claude Code only, and not in Cowork or in skills synced to a terminal session. Read [scripts-and-hooks.md](scripts-and-hooks.md) before using one.
- **`@` file references**: not attached in synced skills in a terminal session. Link supporting files with Markdown instead; Claude reads them when it needs them.
- **`ultrathink`** anywhere in the body requests deeper reasoning in Claude Code.
- **Synced skills**: in a terminal or VS Code session, no injected commands, no `@` attachments and no `CLAUDE_PROJECT_DIR` or `CLAUDE_SESSION_ID` substitution; in a cloud session they behave like local skills.
- **claude.ai and the API**: plain Markdown, bundled files and scripts the model runs itself. Nothing is pre-processed.

## Layout per type

Every type shares the same core: a folder named like the skill, holding `SKILL.md` and only the supporting files the skill uses. Read [structure.md](structure.md) for what goes in each subfolder.

Personal, project or nested skill:

```text
.claude/skills/release-notes/
├── SKILL.md
├── references/changelog-format.md
└── scripts/collect_commits.py
```

Plugin skill, with a script shared by two skills at the plugin level:

```text
my-plugin/
├── .claude-plugin/plugin.json
├── scripts/common.sh          # reached through CLAUDE_PLUGIN_ROOT
└── skills/
    ├── build/SKILL.md
    └── deploy/SKILL.md
```

Single skill at a plugin root, no `skills/` folder:

```text
my-plugin/
├── .claude-plugin/plugin.json
├── SKILL.md                   # name: review → /my-plugin:review
└── references/checklist.md
```

Upload to claude.ai or the Skills API, zipped with the folder at its root:

```text
pdf-forms.zip
└── pdf-forms/
    ├── SKILL.md               # six spec fields only
    └── scripts/fill_form.py   # standard library or preinstalled packages
```

Incorrect, and why:

```text
my-plugin/skills/deploy/SKILL.md   → runs ../../../shared/deploy.sh
```

The plugin cache copies only the plugin folder, so a path above the plugin root does not exist on users' machines.

```text
.claude/skills/Deploy Tool/SKILL.md   with   name: deploy-tool
```

The folder must match `name`, in lowercase with hyphens, or the upload and spec validation fail.
