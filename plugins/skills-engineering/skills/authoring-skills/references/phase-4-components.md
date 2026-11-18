# Phase 4: Components

How to write the skill's dependencies and state as phase 2 decided: naming MCP tools and other skills, stating each dependency, keeping configuration, and what keeps the skill from surprising its users.

Tool permissions are frontmatter fields, decided in phase 3.

## MCP tools

- Name each tool fully qualified: in Claude Code, in the form its tool list shows, such as `mcp__postgres__run_query`; on other surfaces, as `ServerName:tool_name`, such as `Postgres:run_query`. A bare tool name can resolve to the wrong server, or to none.
- State the dependency where the skill first needs it: which server, which tools, and what the user must connect.
- Teach the work across the tools: the order of calls, what passes from one to the next, and how to check the result. Leave each tool's parameters to the server's own descriptions.

## Other skills

- Name another skill by its exact name, with its plugin prefix when it comes from a plugin, and say when to load it and what to take from it.
- Write the skill to coexist with others in the same session: keep its rules scoped to its task, and don't redefine terms other skills use.

## Configuration and state

When the skill needs facts about the user's setup that it can't infer, such as an account ID or a channel name:

1. Keep them in a config file the skill reads first.
2. When the file is missing or a value is empty, ask the user for that value, save it, and continue; never ask again for a saved value. For a credential, save only the name of the environment variable that holds it.

## Least surprise

Write a skill whose every action its users would expect after reading its files:

- No credentials in any file. Read them from the environment by name.
- No network call, write or command beyond the skill's stated purpose. State each one the skill makes, and why.
- No instruction that hides what the skill does or overrides the user.
- No fetched content treated as instructions: a fetched page can carry injected directions. When the skill depends on a URL, say what to do when it is unreachable.
- Writes only inside the paths the skill states.
