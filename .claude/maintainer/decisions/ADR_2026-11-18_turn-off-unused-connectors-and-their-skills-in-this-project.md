---
status: accepted
date: 2026-11-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Turn off eight claude.ai connectors and their skills in this project's settings

## Scope

`.claude/settings.json`: `deniedMcpServers`, the MCP rules in `permissions.deny` and `skillOverrides`. It covers the claude.ai connectors Gmail, Google Drive, Google Calendar, Google Sheets, Google Docs, Astro Docs, Cloudflare and Svelte, and the skills tied to them. It applies to sessions in this repository only. Out of scope: the owner's claude.ai account, other projects, and the Context7, GitHub, Claude Code Docs and Claude Academy connectors, which stay on.

## Context and problem statement

The owner asked to turn these eight connectors and their skills off for this repository. The reason was not stated by the user. The settings file already denied `claude.ai Gmail` and `claude.ai Google Calendar`, yet both connectors were active in this cloud session on 2026-11-18. The MCP page says connectors reach a cloud session from the cloud host, where the `deniedMcpServers` entries that reach the session filter them, and that `disableClaudeAiConnectors` acts only on the connectors a terminal session fetches itself (code.claude.com/docs/en/mcp, "How connectors reach Claude Code", read 2026-11-18). In the cloud the connectors' tools are named `mcp__Gmail__*`, `mcp__Google_Drive__*` and so on, while a terminal session names them `claude.ai Gmail`. The skills tied to these connectors are the synced `anthropic-skills:google-workspace` (Drive, Docs and Sheets) and `anthropic-skills:morning` (Gmail and Calendar briefs). The Cloudflare and Svelte skills come in the synced plugins `cloudflare` and `svelte-development`, which `enabledPlugins` already sets to `false`. Astro Docs ships no skill.

## Decision drivers

- Turn off exactly these eight connectors, and keep every other connector on.
- Work in cloud sessions and in terminal sessions, which name the connectors differently.
- Use only documented settings, and check each one where this session can.

## Considered options

- **`deniedMcpServers` with both name forms, `permissions.deny` globs on the connectors' tool names, and `skillOverrides` for the synced skills**: chosen.
- **`disableClaudeAiConnectors: true`**: rejected because it turns off every connector, Context7 and GitHub included, and doesn't reach the connectors a cloud host delivers.
- **The per-project `/mcp` toggle**: rejected because it writes to `~/.claude.json` on one machine, so it isn't shared through the repository.
- **`deniedMcpServers` alone**: rejected because the `claude.ai` names already listed didn't stop Gmail and Calendar in this cloud session, and the names a cloud host gives the connectors are not documented.
- **`skillOverrides` for the Cloudflare and Svelte skills**: rejected because the settings reference says overrides don't apply to plugin skills; their plugins stay off through `enabledPlugins` instead.

## Decision outcome

Chosen option: **both connector lists plus `skillOverrides`**, because the tool-name deny rules are documented to remove matching tools from Claude's context, and they match both the cloud form (`mcp__Gmail__*`) and the terminal form (`mcp__claude_ai_Gmail__*`). The `deniedMcpServers` entries also stop the connections where their names match.

### Consequences

- Good, because the eight connectors' tools left this cloud session as soon as the file changed, while Context7, GitHub, Claude Code Docs and Claude Academy stayed.
- Good, because `google-workspace` and `morning` no longer reach Claude's skill listing in this project.
- Bad, because the deny globs match by substring, so a future connector or plugin server whose name ends in one of these names, such as a plugin's `svelte` server, is blocked too.
- Bad, because the cloud server names in `deniedMcpServers` are inferred from the tool names, and the casing of the terminal names `claude.ai Cloudflare` and `claude.ai Svelte` is unverified; the deny rules cover both cases.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The eight connectors' tools leave the session | The cloud session's tool list after the settings change | All eight removed, the other connectors kept, 2026-11-18 | Next cloud session start |
| The two synced skills are hidden | `claude -p "/skill-doctor"` shows their listing cost as `-` | Both `-`, 2026-11-18; a control key that names no skill left `google-workspace` at ~330 | After a Claude Code upgrade |
| The connectors stay off in a terminal session | Open `/mcp` in a terminal session in this repository | pending | First terminal session on this repository |

## More information

- `skillOverrides` (since 2.1.129) and `deniedMcpServers` were checked against the settings reference and changelog on Claude Code 2.1.327.
- The keys `"anthropic-skills:google-workspace"` and `"google-workspace"` both hid the skill in a `/skill-doctor` test on 2026-11-18. The full name is used because it can't match a local skill with the same short name.
