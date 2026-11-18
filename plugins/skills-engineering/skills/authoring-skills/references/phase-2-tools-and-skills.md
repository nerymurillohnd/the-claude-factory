# Phase 2: Tools and other skills

Decide what the skill relies on outside itself, and what it does when that is missing. This file covers:

- MCP tools
- other skills
- plugin dependencies

## MCP tools

- Name each tool fully qualified. In Claude Code, use the form its tool list shows, such as `mcp__postgres__run_query`. On other surfaces, use `ServerName:tool_name`, such as `Postgres:run_query`. A bare tool name can resolve to the wrong server, or to none.
- State the dependency where the skill first needs it: which server, which tools, and what the user must connect.
- Say what to do when the server isn't connected: tell the user what to connect and stop, or fall back to a stated alternative.
- Teach the work across the tools: the order of calls, what passes from one to the next, and how to check the result. Leave each tool's parameters to the server's own descriptions.
- A plugin's local stdio server runs in Claude Code and in Cowork on the user's machine, not on claude.ai. To reach claude.ai too, reference a remote server by its `https://` URL.

Read [MCP tool references](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#mcp-tool-references) when the skill calls MCP tools.

Read [MCP servers](https://code.claude.com/docs/en/plugins/components#mcp-servers) when a plugin ships the server.

## Other skills

- Name another skill by its exact name, with its plugin prefix when it comes from a plugin, and say when to load it and what to take from it.
- The other skill must not set `disable-model-invocation: true`: neither the model nor another skill can load a skill that sets it.
- A skill for third parties works on its own. Treat other skills as optional help, and say what to do without them.
- Keep the skill's rules scoped to its task, so it coexists with other skills in the same session.

## Plugin dependencies

When a skill can't work without another plugin, declare it in the `dependencies` array of `plugin.json`. An entry is the plugin's name, `name@marketplace` for another marketplace, or an object with a version constraint:

```json
{
  "name": "deploy-kit",
  "dependencies": [
    "audit-logger",
    { "name": "secrets-vault", "version": "~2.1.0" }
  ]
}
```

- Add a version constraint to a dependency you don't control. Without one, a new release of it reaches your users on their next update, and a renamed tool breaks your plugin.
- When users load your plugin from claude.ai, tell them to turn the dependency on there too, or to install it from its marketplace.

Read [Plugin dependencies](https://code.claude.com/docs/en/plugins/dependencies) when the plugin declares one.
