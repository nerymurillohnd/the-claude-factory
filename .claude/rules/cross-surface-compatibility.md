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
2. Integrate services through remote MCP servers; local MCP only when unavoidable, documented as "Claude app: only in Cowork sessions on your computer".
3. Every `userConfig` option has a default, so the plugin works in the Claude app without prompts. Secrets: `sensitive: true`.
4. LSP, output styles, themes, monitors, workflows, mods and `dependencies` are enhancements; the plugin must still deliver its core value in the Claude app without them. Agents and hooks must degrade gracefully in a chat conversation.
5. Scripts and hooks use only common system tools (`bash`, `python3`, `node`), install nothing, and fail safe with a clear message. Every runtime they need is declared in the README **Requirements** section — the Claude app runtime's available interpreters are **not documented** (unverified), so never assume more.

## README obligations

- Conditional features (agents, hooks, local MCP, `userConfig`) are explained in Requirements/Configuration for Claude app users.
