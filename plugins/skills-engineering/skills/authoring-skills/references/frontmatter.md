# Frontmatter

Each frontmatter field: what it is for, when to set it, and when to leave it out. Leave a field out unless the plan gives it a reason: its default is right for most skills. For any detail beyond this decision, consult https://code.claude.com/docs/en/skills.

Claude Code reads frontmatter only when `---` is the file's first line. It ignores a misspelled field without an error, and it loads a skill whose YAML doesn't parse with no fields set. So spell every field exactly, and quote a value that contains a colon followed by a space.

## Fields every surface accepts

- **`name`**: the skill's identifier and, in Claude Code, its command. Set it on every skill. Its rules are in phase-3-design-and-plan.md.
- **`description`**: what the skill does and when to use it. Set it on every skill. How to write it is in phase-3-design-and-plan.md.
- **`license`**: the license name, or the name of a license file in the folder. Set it on a skill distributed on its own; leave it out when a plugin or repository already states the license.
- **`compatibility`**: what the skill needs from its environment, in up to 500 characters, such as `Requires git and network access`. Set it only when the skill fails without something a surface may lack.
- **`metadata`**: a map of string keys to string values for your own tooling, such as `version`. Set it only when a tool of yours reads it, and never reuse a field name as a key.
- **`allowed-tools`**: tools the model may use without asking, during the turn that invokes the skill; the grant clears at the user's next message. It grants and never removes a tool.
  - Set it only when the body tells the model to run specific commands on every run, and asking each time would interrupt a flow the user already chose by invoking the skill.
  - Write the narrowest rule that matches the exact command in the body, such as `Bash(git add *) Bash(git commit *)`. Never grant a bare `Bash` or `Bash(*)`: a skill shared in a repository grants itself that access on every machine that runs it.
  - A scheduled task or `/loop` asks before running a skill that declares `allowed-tools` or `hooks`. For a skill meant to run unattended, tell its users to add `Skill([name])` to `permissions.allow`, where `[name]` is the skill's name.

## Fields only Claude Code accepts

An upload to claude.ai or the Skills API fails on any of these, so leave them out of a skill phase 2 placed outside Claude Code.

- **`when_to_use`**: extra trigger phrases appended to the description in the skill listing. Set it when a Claude Code skill has more triggers than the description can carry; it counts toward the same listing cut.
- **`argument-hint`**: the hint shown when the user types the command, such as `[issue-number]`. Set it when the skill takes arguments.
- **`arguments`**: names for the positional arguments, so the body can refer to each by name. Set it when the skill takes two or more arguments.
- **`disable-model-invocation`** and **`user-invocable`**: `disable-model-invocation: true` lets only users invoke the skill; `user-invocable: false` lets only the model. Set either only as phase 2 decided who invokes the skill.
- **`disallowed-tools`**: tools removed while the skill is active, until the user's next message. Set it, not `allowed-tools`, when the skill must never call a tool, such as asking the user during an unattended run.
- **`model`** and **`effort`**: the model and reasoning effort for the rest of the turn, or for the fork with `context: fork`. Set them only when the task needs a different capability or depth than the session's.
- **`context`**: `fork` runs the skill in a new subagent, with the body as its task. Set it only as phase 2 decided for a skill run by a subagent.
- **`agent`** and **`background`**: with `context: fork`, the subagent type to use, and whether to wait for its result (`background: false`).
- **`hooks`**: hooks registered when the skill is invoked, for the rest of the session. Build them as scripts-and-hooks.md describes.
- **`paths`**: file patterns that limit automatic loading to work on matching files, such as `src/api/**`. Set it when the skill applies only to certain files.
- **`shell`**: `powershell` runs the skill's injected commands in PowerShell. Set it only for a Windows-only skill.
