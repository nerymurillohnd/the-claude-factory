# Phase 2: Frontmatter

The frontmatter fields the skill's type, location and components need: how Claude Code reads frontmatter, the fields every surface accepts, the fields only Claude Code accepts, the fields by type of skill, and the variables the body can use.

## How Claude Code reads it

- Frontmatter counts only when `---` is the file's first line.
- A field it doesn't recognize is ignored with no error, so spell every field exactly.
- If the YAML doesn't parse, the skill still loads with no fields set. Quote a value that contains a colon followed by a space.
- Booleans accept `true`, `false`, `yes`, `no`, `on`, `off`, `1` and `0`.
- Leave a field out unless the design gives it a reason: its default is right for most skills.

## Fields every surface accepts

An upload to claude.ai or the Skills API fails with a hard error on any other field.

- `name`: the skill's identifier and, in Claude Code, its command. Set it on every skill. Its rules are in the name and description file.
- `description`: what the skill does and when to use it. Set it on every skill.
- `license`: the license name, or the name of a bundled license file. Set it on a skill distributed on its own. Leave it out when a plugin or repository already states the license.
- `compatibility`: what the skill needs from its environment, in up to 500 characters. Set it only when the skill fails without something a surface may lack.
- `metadata`: a map for your own tooling. Set it only when a tool of yours reads it, and never reuse a field name as a key.
- `allowed-tools`: tools Claude can use without asking during the turn that invokes the skill. The grant clears at the user's next message, and it never removes a tool. It takes a space- or comma-separated string, or a YAML list.
  - Set it only when the body tells the model to run specific commands on every run, and asking each time would interrupt a flow the user chose by invoking the skill.
  - Write the narrowest rule that matches the exact command in the body, such as `Bash(git add *) Bash(git commit *)`. Never grant a bare `Bash` or `Bash(*)`: a skill shared in a repository grants itself that access on every machine that runs it.
  - A scheduled task or `/loop` asks before it runs a skill that declares `allowed-tools` or `hooks`. For a skill meant to run unattended, tell its users to add `Skill(<name>)` to `permissions.allow`.

## Fields only Claude Code accepts

Leave these out of a skill that must upload to claude.ai or the API.

- `when_to_use`: extra trigger phrases appended to the description in the listing. It counts toward the same 1,536-character cut. Set it when the skill has more triggers than the description can carry.
- `argument-hint`: the hint shown when the user types the command, such as `[issue-number]`. Set it when the skill takes arguments.
- `arguments`: names for the positional arguments, so the body refers to each by name. Set it when the skill takes two or more.
- `disable-model-invocation`: `true` lets only the user invoke the skill. Set it as decided in Phase 2: Skill types.
- `user-invocable`: `false` lets only the model invoke it. Set it as decided in Phase 2: Skill types.
- `disallowed-tools`: tools removed while the skill is active, until the user's next message. Set it, not `allowed-tools`, when the skill must never call a tool, such as asking the user during an unattended run.
- `model` and `effort`: the model and the reasoning effort for the rest of the turn, or for the fork with `context: fork`. Set them only when the task needs a different capability or depth than the session's.
- `context`: `fork` runs the skill in a new subagent with the body as its task. Set it only for a skill that is a complete task.
- `agent`: the subagent type to use with `context: fork`. It defaults to `general-purpose`.
- `background`: with `context: fork`, `false` waits for the subagent's result in the turn that invoked the skill. The default is `true`.
- `hooks`: hooks registered when the skill is invoked, for the rest of the session. Set it only for a check that must hold while the skill is active. The hooks file covers the rest.
- `paths`: glob patterns that limit automatic loading to work on matching files, such as `src/api/**`. Set it when the skill applies only to certain files.
- `shell`: `powershell` runs injected commands in PowerShell instead of bash. Set it only for a Windows-only skill.

## Fields by type of skill

- Reference skill that both invoke: `name` and `description`, plus `paths` when it applies to certain files.
- Task skill with side effects: add `disable-model-invocation: true`, `argument-hint` when it takes arguments, and `allowed-tools` when it runs fixed commands.
- Skill that is a subagent's task: add `context: fork`, and `agent`, `background`, `model` or `effort` when the task needs them.
- Background knowledge only the model loads: add `user-invocable: false`.
- Skill that must upload to claude.ai or the API: only the fields every surface accepts.

## Variables the body can use

- `$ARGUMENTS`, `$N` and `$ARGUMENTS[N]`: the arguments passed. `$name` for each name declared in `arguments`.
- `${CLAUDE_SESSION_ID}` and `${CLAUDE_EFFORT}`: the session and the effort level.
- `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`: the skill's folder and the project root.
- `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`: the plugin's install folder and data folder, in plugin skills only.

Claude Code replaces the path variables in the skill's content and in the Bash rules of `allowed-tools`.

Read [Frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference) when you need a field's exact behavior.

Read [Using skill frontmatter outside Claude Code](https://code.claude.com/docs/en/skills#using-skill-frontmatter-outside-claude-code) when the skill uploads.

Read [Available string substitutions](https://code.claude.com/docs/en/skills#available-string-substitutions) when the body uses variables.

## Exit

Each field the skill sets is chosen, with its value, in its order. Then return to the step list in `SKILL.md`, and go on with the next file or step.
