# Live checks of a plugin's MCP servers

Checked 2026-10-25 against `/en/mcp`, `/en/plugins/manifest-reference` ("User configuration"), `/en/hooks` and `/en/plugins/cli-reference` (`reload-plugins`), Claude Code v2.1.310.

Run these only when Nery says a plugin with an MCP server, or with a hook that matches or calls MCP tools, is ready. They load the plugin, start its servers and call real tools, which the static checks of the plugin build never do. While the plugin is still being shaped, run none of them.

## Before you start

- The static checks of the build have passed: the manifest and MCP schema checks and `claude plugin validate --strict` on the plugin directory.
- Load the plugin from its folder with `claude --plugin-dir plugins/<name>`, in a session that is not your daily one.
- A server that needs a credential needs one the user would type. Use a test account or token through the option itself, never a value pasted into a file, and never print it.

## Load and connect

1. Load the plugin with the option unset. A server whose `url` uses the unset option must not connect: the `/plugin` **Errors** tab shows `Invalid MCP server config for "<server>": URL is unset or invalid`. A packaged `.mcpb` server with a required setting unset shows `Bundled MCP server "<name>" was not started: it needs configuration`. Compare what you see with the README's setup text: they must agree.
2. Set the option (`/plugin` → **Installed** → **Configure**, or `/plugin configure <plugin>@<marketplace>`), run `/reload-plugins`, and confirm `/mcp` shows the server as `plugin:<plugin>:<server>`, connected.
3. Call a tool from the main conversation, and from an agent that lists it in `tools` by its scoped name (`mcp__plugin_<plugin>_<server>__<tool>`). A bare-key name in `tools` must not reach it.

## The Claude app

For a remote server with `${user_config.*}` in headers, take the Claude app steps (the plugin's **Connectors** tab, **No sign in**, and an `authorization` header) from the official claude.com and support.claude.com pages. Nery runs no per-plugin Claude app check: state in the README or the report what was not observed live as unverified, and never log it as debt or a blocker.

## Hooks that match or call MCP tools

Check each case separately; use mocks or fixtures for states you cannot reach, and label live behavior you did not test:

- Correct and incorrect plugin-scoped server identifiers in an `mcp_tool` handler's `server`.
- Full tool-name matching, and rejection of a bare-server matcher.
- Valid arguments, and missing or invalid event input paths in `input`.
- Successful text output, event-supported JSON decisions, and `isError: true`.
- Connected, connecting, cached, unavailable and unauthenticated servers.
- Launch-time `SessionStart`, a later `SessionStart`, and `Setup`.
- A hook timeout against the startup and execution timeouts.

Read the debug log (`claude --debug-file <path>`) before changing configuration for a skipped hook, and redact secrets before quoting it.

## Report

What you ran, what each step showed, the cases you could not reach, and what stays unverified.
