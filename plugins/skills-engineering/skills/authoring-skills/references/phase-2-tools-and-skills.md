# Phase 2: Tools and other skills

What the skill relies on outside itself, its MCP tools, other skills and plugin dependencies, and what it does when one is missing.

## Gotchas

- A bare MCP tool name can resolve to the wrong server, or to none: name each tool fully qualified, as the MCP tools section shows.
- A plugin's local stdio server runs only on the user's machine, never on claude.ai: to reach claude.ai too, reference a remote server by its `https://` URL.
- Neither the model nor another skill can load a skill that sets `disable-model-invocation: true`: rely only on skills that don't set it.
- A dependency with no version constraint takes each new release on your users' next update, and a renamed tool then breaks your plugin: give each dependency you don't control a version constraint.

## MCP tools

- Name each tool fully qualified. In Claude Code, use the form its tool list shows, such as `mcp__postgres__run_query`. On other surfaces, use `ServerName:tool_name`, such as `Postgres:run_query`.
- State the dependency where the skill first needs it: which server, which tools, and what the user must connect.
- Say what to do when the server isn't connected: tell the user what to connect and stop, or fall back to a stated alternative.
- Teach the work across the tools: the order of calls, what passes from one to the next, and how to check the result. Leave each tool's parameters to the server's own descriptions.

## Other skills

- Name another skill by its exact name, with its plugin prefix when it comes from a plugin, and say when to load it and what to take from it.
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

When users load your plugin from claude.ai, tell them to turn the dependency on there too, or to install it from its marketplace.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [MCP tool references](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#mcp-tool-references) when the skill calls MCP tools. It gives the fully qualified form and why a bare name fails.
- Read [MCP servers](https://code.claude.com/docs/en/plugins/components#mcp-servers) when a plugin ships the server. It shows how to declare a local or a remote server in the plugin.
- Read [Plugin dependencies](https://code.claude.com/docs/en/plugins/dependencies) when the plugin declares one. It gives the entry forms, the version constraints and how users receive a dependency.

## Exit

Each MCP tool and other skill the skill relies on is named in full, with what to do when it is missing, and each plugin dependency is declared. Then return to the step list in `SKILL.md`, and go on with the next file or step.
