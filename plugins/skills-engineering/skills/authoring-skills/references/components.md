# Components

How to write a skill that relies on more than its own files and scripts: tool permissions, MCP tools, other skills, configuration and state, and what keeps it from surprising its users.

## Tool permissions

- **`allowed-tools`** lets the model use the listed tools without asking, during the turn that invokes the skill. It grants; it never removes a tool. Set it only when the body tells the model to run specific commands on every run, and asking each time would interrupt a flow the user already chose by invoking the skill.
- Write the narrowest rule that matches the exact command in the body, such as `Bash(git add *) Bash(git commit *)`. Never grant a bare `Bash` or `Bash(*)`: a skill shared in a repository grants itself that access on every machine that runs it.
- **`disallowed-tools`** removes tools while the skill is active. Use it, not `allowed-tools`, to keep the model away from a tool.

## MCP tools

- Name each tool by its server and tool name, in the form the tool list shows, such as `mcp__postgres__run_query`. A bare tool name can resolve to the wrong server, or to none.
- State the dependency where the skill first needs it: which server, which tools, and what the user must connect.
- Say what to do when the server isn't connected: tell the user what to connect and stop, or fall back to a stated alternative.
- Teach the work across the tools: the order of calls, what passes from one to the next, and how to check the result. Leave each tool's parameters to the server's own descriptions.

## Other skills

- Name another skill by its exact name, with its plugin prefix when it comes from a plugin, and say when to load it and what to take from it.
- The other skill must not be restricted to its users; read `special-placements.md` for why.
- When the other skill may be missing, say what to do without it. A skill for third parties works on its own, with other skills as optional help.
- Write the skill to coexist with others in the same session: keep its rules scoped to its task, and don't redefine terms other skills use.

## Configuration and state

When the skill needs facts about the user's setup that it can't infer, such as an account ID or a channel name:

1. Keep them in a config file the skill reads first.
2. When the file is missing or a value is empty, ask the user for that value once, save it, and continue.
3. Never ask again for a value that is saved.

Keep the config and any state where updates don't erase them:

- **Plugin skill**: the plugin's data folder, `CLAUDE_PLUGIN_DATA` written with a dollar sign and braces. The plugin's install folder is replaced on every update.
- **Personal or project skill**: the skill's folder, or the project when the state belongs to it, kept out of version control if private.
- **claude.ai or the API**: don't rely on files from an earlier conversation; design the skill to work without saved state.

For a history the skill learns from, such as earlier reports, append to a log in the same place and say when the model reads it.

## Least surprise

Write a skill whose every action its users would expect after reading its files:

- No credentials in any file. Read them from the environment by name.
- No network call, write or command beyond the skill's stated purpose. State each one the skill makes, and why.
- No instruction that hides what the skill does or overrides the user.
- No fetched content treated as instructions: a fetched page can carry injected directions. When the skill depends on a URL, say what to do when it is unreachable.
- Writes only inside the paths the skill states.
