# Components

How to decide whether a skill is the right feature, and which components it needs beyond `SKILL.md`: files, tools, permissions, MCP servers, other skills, subagents, configuration and state.

## Contents

- Is a skill the right feature
- Component inventory
- Tool permissions
- MCP tools
- Other skills
- Setup and persistent state
- Security and least surprise

## Is a skill the right feature

Each Claude Code feature solves a different failure. Match the request to the failure before building:

- **Skill**: a procedure, playbook or body of knowledge the model needs for some tasks, not every session. The sign: the same instructions, checklist or steps get pasted into chat again and again, or a section of CLAUDE.md has grown from a fact into a procedure.
- **CLAUDE.md**: a fact or convention every session needs from the first turn, such as the build command or the repository layout. Short, always loaded.
- **Path-scoped rule** (`.claude/rules/` with `paths`): a convention for certain files, loaded when the model reads them.
- **Hook**: something that must happen every time an event occurs, whatever the model decides: blocking a command, formatting after each edit, logging. A skill is guidance the model can skip; a hook is enforcement.
- **Subagent**: a role that works in its own context with its own tools and returns a result, so its exploration doesn't fill the main conversation.
- **MCP server**: access to an external system or API the model can't otherwise reach. A skill teaches how to use those tools well; the server provides them.
- **Output style**: a change to how every response is written, for the whole session.

When the request mixes several, build each part as its own feature: a skill for the procedure, plus a hook for the step that must never be skipped. When it isn't a skill at all, tell the requester which feature fits and why, and stop.

## Component inventory

Add a component only when it answers a need of the skill's task. For each candidate, ask its question:

- **Reference file**: is there content only some runs need, or too long for the body?
- **Script**: is there an operation that must give the same result every run, that the model would otherwise rewrite each time, or that is easy to get wrong by hand?
- **Asset**: does the output start from a fixed file: a template, a boilerplate project, a font, an image?
- **Hook**: is there a check that must run on every event while the skill is active, even if the model forgets?
- **`allowed-tools`**: does every run need a command the user would otherwise approve again and again?
- **`disallowed-tools`**: must the skill never call some tool, such as asking the user during an unattended run?
- **MCP tools**: does the task act on an external system through a server the users have connected?
- **Another skill**: is part of the task already done well by an existing skill the model should load?
- **Subagent**: does part of the task need an isolated context: a broad search, a parallel review, an independent check?
- **Setup configuration**: does the skill need facts about the user's environment it can't infer, such as a channel name or an account ID?
- **Persistent state**: must something survive between runs: a log of past outputs, a cache, installed dependencies?

Record each component in the plan with the need it answers. A component without one is cost without value.

## Tool permissions

`allowed-tools` grants permission for listed tools during the turn that invokes the skill; it never limits which tools exist. Use it when:

- the body tells the model to run specific commands on every run, and
- prompting for each would interrupt a flow the user already chose by invoking the skill.

Write the narrowest rule that matches the exact command in the body:

```yaml
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
```

Never grant a bare `Bash` or a broad pattern such as `Bash(*)`: a skill checked into a repository grants itself that access on every machine that runs it. For a bundled script, use the same path variable in the rule and in the body so they match. Read [scripts-and-hooks.md](scripts-and-hooks.md) for that pattern.

To keep the model away from a tool, use `disallowed-tools` or the users' deny rules, not `allowed-tools`.

## MCP tools

- Name each tool by its full name, server and tool: `BigQuery:bigquery_schema`, or in Claude Code the form the tool list shows, such as `mcp__github__create_issue`. With several servers connected, a bare tool name can resolve to the wrong one or to none.
- State the dependency where the skill needs it: which server, which tools, and what the user must connect.
- Say what to do when the server isn't connected: tell the user what to connect and stop, or fall back to a stated alternative.
- Teach the workflow across tools, not each tool's parameters, which the server already describes: the order of calls, what to pass from one to the next, and how to check the result.

## Other skills

- Load another skill by its exact name as the model sees it, with its namespace for a plugin skill: `skills-engineering:auditing-skills`.
- The target must let the model invoke it: a skill with `disable-model-invocation: true` can't be loaded by the model or by another skill.
- Say when to load it and what to take from it, as you would for a reference file.
- When the other skill may not be installed, say what to do without it. A skill distributed to third parties should work alone, with other skills as optional improvements.
- Many skills can be loaded in one session. Write yours so it works alongside others: don't claim the whole session, don't redefine terms other skills use, and keep its rules scoped to its task.
- In a plugin, a skill can rely on a sibling skill in the same plugin; across plugins, state the dependency in the plugin's documentation.

## Setup and persistent state

When the skill needs facts about the user's setup:

1. Store them in a config file the skill reads first, such as `config.json`.
2. When the file is missing or a value is empty, ask the user for that value once, save it, and continue.
3. Never ask again for a value that is saved.

Where to keep the config and state:

- **Plugin skill**: under the plugin's persistent data folder, `CLAUDE_PLUGIN_DATA` written with a dollar sign and braces in the body. The plugin's install folder is replaced on every update, so anything saved next to the code is lost.
- **Personal or project skill**: in the skill folder, or in the project where the state belongs to the project, ignored by git when it is private.
- **claude.ai and the API**: no state survives between conversations; design the skill to work without it.

For a history the skill can learn from, such as previous reports, append to a log file or a small database in the same persistent location, and tell the model when to read it.

## Security and least surprise

A skill directs the model's tools. Write one whose behavior would not surprise its users if they read every file:

- No credentials in any file. Read them from the user's environment or a secrets manager, by name.
- No network call, file write or command outside the skill's stated purpose. State each one the skill makes, and why.
- No instruction that hides what the skill does, changes the model's behavior outside the task, or overrides the user.
- No content fetched from an external URL treated as instructions; fetched content can carry injected directions. If the skill depends on a URL, say what to do when it is unreachable, and never make it the only home of content the skill needs.
- Pin the versions of dependencies and tools the skill runs, so a later release doesn't change its behavior.
- Keep writes inside the paths the skill states: the project, its output folder, its data folder.
