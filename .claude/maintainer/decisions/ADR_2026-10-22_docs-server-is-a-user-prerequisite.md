---
status: accepted
date: 2026-10-22
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The Claude Code docs server is a user prerequisite of hook-engineering, not a bundled component

## Scope

- In scope: how `plugins/hook-engineering` reaches the official Claude Code docs MCP server (`https://code.claude.com/docs/mcp`): its manifest components, the `hook-development` skill, `references/docs-map.md`, the `hook-engineer` agent and the README.
- Out of scope: the agent's tool grant (ADR_2026-10-22_hook-engineer-agent-inherits-session-tools) and how other plugins of the marketplace reach documentation.

## Context and problem statement

hook-engineering 0.1.0 bundled the docs server in `.mcp.json`, so its tools were named `mcp__plugin_hook-engineering_claude-code-docs__*`. On 2026-10-22, in a Claude Code session, Nery asked for the install command of the docs server and learned it was already loaded through the plugin. He was evaluating whether the plugin should instead state the server as a prerequisite, so Claude calls the tools by their native names, because he did not know to what extent a server tied to a hooks plugin could bias Claude into using it only for hooks questions (stated by Nery on 2026-10-22). In the same session Claude added that a general-purpose resource, the whole Claude Code documentation, was coupled to a specialized plugin: turning hook-engineering off removed the docs for everything else, and another plugin needing them would duplicate the server.

The 0.1.0 files also documented that Claude Code connects one server per URL, so the plugin's copy was suppressed when the user or another plugin already defined the same URL, and its scoped tool names could then not be called.

## Decision drivers

- Native tool names, `mcp__claude-code-docs__*`, as the [official MCP quickstart](https://code.claude.com/docs/en/mcp-quickstart) sets them up, instead of names prefixed with the plugin.
- The suspicion that the plugin-prefixed name biases the server's use toward hooks (Nery's concern; not verified: in that session Claude used the bundled server for a non-hooks question and it worked).
- A general resource should not depend on one specialized plugin, and should not be duplicated across plugins.
- No extra plugin to maintain.

## Considered options

- **A. Manual prerequisite**: the README tells the user to run `claude mcp add --transport http --scope user claude-code-docs https://code.claude.com/docs/mcp`, or to add a custom connector in the Claude app; the skill and the agent fall back to the raw docs pages when it is missing: chosen.
- **B. A separate `claude-code-docs` plugin declared in `dependencies`**: rejected, because its tools would still carry a plugin prefix (`mcp__plugin_claude-code-docs_claude-code-docs__*`) and it adds a plugin to maintain.
- **Keep the server bundled (0.1.0)**: rejected, for the drivers above.
- **A `SessionStart` hook that checks whether the server is registered and prints the command once**: not adopted; the skill and the agent already tell the user the command once when the tools are missing.

## Decision outcome

Chosen option: **A. Manual prerequisite**, because it gives the native tool names and the configuration the official docs teach, decouples the documentation from the plugin, and leaves no other plugin to maintain.

### Consequences

- Good, because the docs server serves every task in the session under its own name and survives disabling hook-engineering.
- Good, because a Claude app connector at the same URL also works: it reaches Claude Code as `mcp__claude_ai_<connector name>__*` ([permissions](https://code.claude.com/docs/en/permissions)), and a server added in Claude Code takes precedence over it ([MCP, scope hierarchy and precedence](https://code.claude.com/docs/en/mcp#scope-hierarchy-and-precedence)).
- Bad, because installing the plugin no longer installs the server: users must add it themselves, and 0.1.0 users lose it on update until they do. The release was marked breaking (0.2.0).
- Bad, because a user who never adds it gets the raw-page fallback, which costs more fetches.

## More information

- Implemented in [PR #42](https://github.com/nerymurillohnd/the-claude-factory/pull/42), merged on 2026-10-22 as `31ad541` and released as `hook-engineering--v0.2.0`.
- The decision was made on 2026-10-22, before the change was built.
- The Claude app connector steps come from the official help article; the tool names a connector carries inside a Cowork session were not observed.
