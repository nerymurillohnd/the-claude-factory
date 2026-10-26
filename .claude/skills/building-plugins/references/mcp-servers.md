# MCP servers in a plugin

Checked 2026-10-25 against `/en/mcp`, `/en/plugins/components`, `/en/plugins/manifest-reference`, `/en/plugins/troubleshooting`, `/en/sub-agents` and `/en/hooks` (Claude Code v2.1.310). Read this before you add or change a plugin's MCP server or its `userConfig`, an agent's MCP tools in `tools`, a skill's MCP `allowed-tools`, or MCP setup text in the README, and before you answer a question about MCP in plugins. For a hook that matches MCP tools or calls one (`mcp_tool`), a server's connection state, authentication or timeouts, also read `mcp-hooks-and-lifecycle.md`.

A plugin that bundles an MCP server puts its tools in front of every user's Claude, in the main conversation and in every agent, for as long as the plugin is enabled. The server needs credentials that only the user has, and each surface connects it differently. Work as an integration engineer who ships a server to strangers: assume the credential is missing, the Claude app cannot fill it, and the tool names are not what the docs' short examples show, and make each of those visible to the user instead of failing silently.

## Contents
- Rules
- Gotchas
- Order of work

## Rules

- Ship a server in the plugin's `.mcp.json` or manifest `mcpServers`. A plugin agent's own `mcpServers` is ignored for security, so never write it in a plugin agent file (Scope, below).
- A plugin server is connected for the whole conversation, so every tool description costs context there. Keep one server per user task that no other component serves, and drop a server you could replace with a skill.
- Never name a plugin tool by the bare server key. Use the scoped name everywhere a plugin refers to it: an agent's `tools`, permission rules, a skill's `allowed-tools`, a hook matcher.
- Secrets and per-user values go through `userConfig` and `${user_config.KEY}`. Never hardcode them, never read them from the user's shell environment. Put the value in a header, not in the URL: a chat conversation skips a server whose URL holds the reference.
- Disclose each server in the README: what it connects to, what it sends, and the prerequisites with how to install them. Keep exactly one Compatibility row per MCP type the plugin ships.
- Before relying on a `userConfig` option, read `/en/plugins/manifest-reference` → "User configuration"; before writing `${VAR}` in headers, read `/en/mcp` → "Environment variable expansion in `.mcp.json`". The Claude app rules are in the Gotchas below and in Test.
- Read `.claude/rules/plugins/mcp-component.md` for every MCP configuration change. It loads by itself only with a `.mcp.json`, so read it explicitly when the servers sit in the manifest's `mcpServers`, and say so if the file is missing.
- When the docs and the release notes disagree, the release notes win; read them raw from <https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md>.
- Never launch plugin code, connect a server or authenticate only to validate configuration: static checks first, live checks only when Test calls for them.

## Gotchas

- A tool of a plugin-bundled server is named `mcp__plugin_<plugin>_<server>__<tool>`, with any character outside letters, digits, `_` and `-` replaced by `_`. The server registers as `plugin:<plugin>:<server>`, which is the name an `mcp_tool` hook's `server` field takes.
- `${user_config.KEY}` is substituted in MCP server config (`url`, `headers`, `env`, `args`), but rejected in `headersHelper`, in shell-form hook commands and in monitor commands: the component fails with an error. In skill and agent content only non-sensitive values are substituted.
- `claude plugin install` from the shell never prompts for `userConfig`; it prints `N userConfig options not yet set` and the user runs `/plugin configure <plugin>@<marketplace>` or passes `--config KEY=VALUE`. A remote server whose `url` uses an unset option does not connect, and the `/plugin` **Errors** tab shows `Invalid MCP server config for "<server>": URL is unset or invalid`.
- A packaged `.mcpb` server whose own `user_config` has a required setting with no saved value does not start; the **Errors** tab shows `Bundled MCP server "<name>" was not started: it needs configuration`.
- The Claude app cannot fill `${user_config.*}` in headers: the plugin's **Connectors** tab lists the server as not added, and the user connects it there and types the value. Local (command) servers run only in Cowork sessions.
- A manifest server with the same name as one in `.mcp.json` replaces it. `claude plugin validate` reports an entry Claude Code would drop at load (Claude Code 2.1.281+).
- `claude mcp get` shows a plugin's stdio and WebSocket values as `[REDACTED]`; read `.mcp.json` or `plugin.json` on disk to see them.

## Order of work

Take these in order for each server, and for each agent that uses a server's tools.

### 1. Need

State the user task the server serves and why a skill or a script cannot serve it. Choose the transport: a remote server (`http` or `sse`, fixed URL) works in Claude Code and the Claude app; a local one (a command, or an `.mcpb` bundle) works in Claude Code and in Cowork sessions only. Check the choice against `docs/compatibility.md`, and get Nery's OK if a server forces a plugin to Claude Code-only.

### 2. Docs

Read `/en/mcp` and, in `/en/plugins/components`, the MCP servers section; read `/en/plugins/manifest-reference` for `userConfig` and the fields that reject it. For hooks, connection state and timeouts, the sources table at the end of `mcp-hooks-and-lifecycle.md` names the page for each topic. Open them through the Claude Code Docs MCP tools; when a heading is missing or exact wording decides, read the raw page at `https://code.claude.com/docs/en/<page>.md`.

### 3. Declare

- Write the server in `.mcp.json` at the plugin root, or in the manifest `mcpServers` key, which also takes a path or an `.mcpb` file. Path variables (the plugin root and data directories, wrapped as `${…}`) are substituted in `command`, `args` and `env` of a stdio server, and in `url`, `headers` and `headersHelper` of an `http`, `sse` or `ws` server (`/en/plugins/manifest-reference`).
- Put every credential or per-user value in `userConfig` and reference it as `${user_config.KEY}` in `headers`, `env` or `args`. Mark a token `sensitive`. Never use `headersHelper` with it.
- Run `claude plugin validate --strict plugins/<name>` and load the plugin with `claude --plugin-dir plugins/<name>`; `/mcp` must show the server as `plugin:<plugin>:<server>`.

### 4. Reach

Give an agent its tools through its `tools` allowlist, written with the scoped name: one entry per tool, or `mcp__plugin_<plugin>_<server>__*` for the whole server; never the bare-key form `mcp__<server>__*`, which matches no plugin tool. Confirm the real names in `/mcp` before you write the line. Leave `tools` unset to inherit everything. Use the same scoped name in a skill's `allowed-tools`, in any permission rule the README recommends, and in a hook matcher with `.*` for the whole server. Read `/en/sub-agents` before you write the agent, and its "Preload skills into subagents" section before you rely on `skills:` in its frontmatter.

### 5. Scope

A plugin cannot keep a server out of the main conversation or hand it to one agent only: that needs `mcpServers` in the agent's own frontmatter, and a plugin agent ignores it. Do not promise scoping in the README. When users need it, say that they can copy the agent file to `.claude/agents/` or `~/.claude/agents/` and declare the server inline there; a project agent loads an inline server only after the user trusts that folder, and `permissionMode` there is subject to the main conversation's mode. State that this is a manual step the plugin does not do.

### 6. Test

While Nery is still shaping the plugin, run only the cheap checks each edit needs and no live tests; run all of this once he says it is ready.

1. Load the plugin with the option unset: the server must not connect, and the README's setup text must match what the user sees.
2. Set the option, run `/reload-plugins`, and confirm the server and a tool call work.
3. Call a tool from an agent that lists it in `tools`, and from the main conversation.
4. For a remote server with `${user_config.*}` in headers, take the Claude app steps (the **Connectors** tab, **No sign in** and an `authorization` header) from the official claude.com and support.claude.com pages. Nery runs no per-plugin Claude app check: state in the README or the report what was not observed live as unverified, and never log it as debt or a blocker.

### 7. Document

In the README: the prerequisites (account, key, CLI) with how to install them and their alternatives; how to set each option (`/plugin` → **Installed** → **Configure**, `claude plugin install --config <key>=<value>` from the shell (for a bundled `.mcpb` server's own setting, `<server>.<key>=<value>`; Claude Code 2.1.285+), `/plugin configure <name>@synced` for a synced copy); every network call; the Claude app **Connectors** steps; and one Compatibility row per MCP type, matching `docs/compatibility.md`. An agent runs in the Claude app only in Cowork sessions, so say that an agent that depends on the server is unreachable from a chat conversation.
