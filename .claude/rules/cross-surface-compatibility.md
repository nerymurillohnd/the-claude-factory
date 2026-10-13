# Cross-surface compatibility (Claude Code ↔ Claude app)

House standard: every plugin works in **Claude Code and the Claude app**, unless its nature makes it Claude Code-only — then its README says so up front.

Verified 2026-10-12 against <https://claude.com/docs/plugins/platform-support>, <https://claude.com/docs/plugins/build>, <https://claude.com/docs/cowork/guide/plugins>, <https://support.claude.com/en/articles/13837440-use-plugins-in-claude>, <https://support.claude.com/en/articles/16761823> ("Claude Cowork and chat are one Claude"), <https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview> and <https://claude.com/docs/third-party/claude-desktop/unified-claude>. Treat this file as the source of truth; `/docs-drift-check` re-verifies it.

## How it works

- Two surfaces: **Claude Code** (terminal, IDEs, desktop **Code** tab) and the **Claude app** (claude.ai web, desktop, mobile). Chat and Cowork became one Claude app (rolling out to Pro and Max since 2026-09-16; Team and Enterprise keep separate Chat and Cowork for now).
- In the Claude app a conversation runs as a **Cowork session** when it can, and as a **chat conversation** otherwise: a device that can't run Cowork, or the separate Chat mode Team and Enterprise keep. Agents, hooks and local MCP servers don't run in a chat conversation ("grayed out in chat", support 13837440).
- Official plugin docs still describe chat and Cowork separately and give no component table for the unified app; the matrix below combines them with the support articles. Re-check with `/docs-drift-check`.
- One plugin folder, one marketplace, installs on both. Each surface loads the components it supports and silently skips the rest.
- Exception: a top-level `bin/` makes the Claude app **refuse the whole plugin**.
- Claude app installs attach to the claude.ai account and also reach Claude Code as `<plugin>@synced`; Claude Code shell installs stay on that machine.
- Claude app limits: 200 MB and 5,000 files per plugin, 500 plugins per marketplace, 512 MB per marketplace repository archive, 25 added marketplaces per account in each organization (Cowork guide: plugins, Limits; platform-support).

## Component matrix

| Component | Claude Code | Claude app | Use it as |
| :-- | :--: | :--: | :-- |
| Skills `skills/<name>/SKILL.md` | ✅ | ✅ | **Core — shared** |
| Skill files `references/`, `assets/`, `scripts/` | ✅ | ✅ | **Shared**; call scripts via `${CLAUDE_SKILL_DIR}/scripts/...` |
| Commands `commands/*.md` | ✅ | ✅ `/plugin:command`; loads as a skill in a chat conversation | Shared; prefer skills for new work |
| Agents `agents/*.md` | ✅ | ⚠️ Cowork sessions only | **Shared**; the skill still delivers value without them |
| Hooks `hooks/hooks.json` | ✅ | ⚠️ Cowork sessions only | **Shared**; never the only way to get the core value |
| Remote MCP (`http`/`sse`, fixed URL, `.mcp.json`) | ✅ connects directly | 🔗 user connects it on the plugin's **Connectors** tab | **Preferred integration** |
| Local MCP (command, `.mcpb`/`.dxt`) | ✅ | ⚠️ only in Cowork sessions on the user's computer | Shared with conditions |
| `userConfig` / `${user_config.*}` | ✅ prompts | ⚠️ never prompts; only options with defaults work | Always give defaults |
| LSP servers | ✅ | ➖ | Claude Code-only extra |
| Output styles · themes · `settings` | ✅ | ➖ | Claude Code-only extra |
| Monitors · workflows · mods | ✅ | ➖ | Claude Code-only extra |
| Plugin `dependencies` | ✅ | ➖ | Claude Code-only |
| Executables in top-level `bin/` | ✅ | ❌ | **Blocks install** in the Claude app |

✅ loads · ⚠️ conditional · 🔗 manual step · ➖ ignored · ❌ can't be installed

## Design rules

1. Build the core from skills (+ references/assets/scripts), agents and hooks.
2. No top-level `bin/`. Put code in a skill's `scripts/` or call it from hooks. Use `bin/` only for a Claude Code-only plugin, declared in the README.
3. Integrate services through remote MCP servers; local MCP only when unavoidable, documented as "Claude app: only in Cowork sessions on your computer".
4. Every `userConfig` option has a default, so the plugin works in the Claude app without prompts. Secrets: `sensitive: true`.
5. LSP, output styles, themes, monitors, workflows, mods and `dependencies` are enhancements; the plugin must still deliver its core value in the Claude app without them. Agents and hooks must degrade gracefully in a chat conversation.
6. Scripts and hooks use only common system tools (`bash`, `python3`, `node`), install nothing, and fail safe with a clear message. Every runtime they need is declared in the README **Requirements** section — the Claude app runtime's available interpreters are **not documented** (unverified), so never assume more.
7. Test on both before every release:
   - Claude Code: `/test-installed-plugin <name>` (copied install from a git source, load check, eval suite).
   - Claude app: add the marketplace (or **Customize → Plugins → Add → Upload plugin** with a zip); confirm skills/agents/hooks load in a Cowork session and that the skill still works in a chat conversation; connect connectors.

## Declaring surfaces

- Every plugin declares its surfaces in `plugin.json` → `"metadata": { "surfaces": [...] }`: `["claude-code", "claude-app"]` (default) or `["claude-code"]`. Claude Code ignores `metadata`; our tooling reads it.
- Scaffold a Claude Code-only plugin with `new-plugin.mjs --claude-code-only`.
- From that one field: the README **works in** badge, the catalog **Works in** column, and `check-repo.mjs` checks.
- `check-repo.mjs` fails when: `metadata.surfaces` is missing/invalid; a plugin ships `bin/` but isn't `["claude-code"]`; the badge doesn't match; a Claude Code-only README lacks "**Claude Code only**"; the Compatibility table misses a row for a shipped component or lists one it doesn't ship.

## README obligations

- The **Compatibility** table has the columns `Component | Claude Code | Claude app` and reflects exactly the components the plugin ships, per the matrix above, with the chat-conversation note under it.
- A Claude Code-only plugin states it in the hero/TL;DR, and the reason (e.g. "ships an LSP server", "needs `bin/` executables").
- Conditional features (agents, hooks, local MCP, `userConfig`) are explained in Requirements/Configuration for Claude app users.
