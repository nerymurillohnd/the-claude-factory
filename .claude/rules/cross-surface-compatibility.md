# Cross-surface compatibility (Claude Code ↔ Cowork)

House standard: every plugin works in **Claude Code and Cowork**, unless its nature makes it Claude Code-only — then its README says so up front.

Verified 2026-10-11 against <https://claude.com/docs/plugins/platform-support>, <https://claude.com/docs/plugins/build> and <https://claude.com/docs/cowork/guide/plugins>. Treat this file as the source of truth; `/docs-drift-check` re-verifies it.

## How it works

- One plugin folder, one marketplace, installs on both. Each app loads the components it supports and silently skips the rest.
- Exception: a top-level `bin/` makes Cowork and Claude chat **refuse the whole plugin**.
- Cowork/chat installs attach to the claude.ai account and also reach Claude Code as `<plugin>@synced`; Claude Code shell installs stay on that machine.
- Cowork limits: 200 MB and 5,000 files per plugin, 500 plugins per marketplace, 25 added marketplaces per account.

## Component matrix

| Component | Claude Code | Cowork | Claude chat | Use it as |
| :-- | :--: | :--: | :--: | :-- |
| Skills `skills/<name>/SKILL.md` | ✅ | ✅ | ✅ | **Core — shared** |
| Skill files `references/`, `assets/`, `scripts/` | ✅ | ✅ | ✅ | **Shared**; call scripts via `${CLAUDE_SKILL_DIR}/scripts/...` |
| Commands `commands/*.md` | ✅ | ✅ `/plugin:command` | ⚠️ loads as a skill | Shared; prefer skills for new work |
| Agents `agents/*.md` | ✅ | ✅ | ➖ | **Shared** with Cowork |
| Hooks `hooks/hooks.json` | ✅ | ✅ | ➖ | **Shared** with Cowork |
| Remote MCP (`http`/`sse`, fixed URL, `.mcp.json`) | ✅ connects directly | ✅ user connects it on the plugin's **Connectors** tab | 🔗 user adds/connects it | **Preferred integration** |
| Local MCP (command, `.mcpb`/`.dxt`) | ✅ | ⚠️ only when the Cowork session runs on the user's computer | ➖ | Shared with conditions |
| `userConfig` / `${user_config.*}` | ✅ prompts | ⚠️ never prompts; only options with defaults work | ➖ when the URL uses it | Always give defaults |
| LSP servers | ✅ | ➖ | ➖ | Claude Code-only extra |
| Output styles · themes · `settings` | ✅ | ➖ | ➖ | Claude Code-only extra |
| Monitors · workflows · mods | ✅ | ➖ | ➖ | Claude Code-only extra |
| Plugin `dependencies` | ✅ | ➖ | ➖ | Claude Code-only |
| Executables in top-level `bin/` | ✅ | ❌ | ❌ | **Blocks install** on Cowork/chat |

✅ loads · ⚠️ conditional · 🔗 manual step · ➖ ignored · ❌ can't be installed

## Design rules

1. Build the core from skills (+ references/assets/scripts), agents and hooks.
2. No top-level `bin/`. Put code in a skill's `scripts/` or call it from hooks. Use `bin/` only for a Claude Code-only plugin, declared in the README.
3. Integrate services through remote MCP servers; local MCP only when unavoidable, documented as "Cowork: only on your computer".
4. Every `userConfig` option has a default, so the plugin works in Cowork without prompts. Secrets: `sensitive: true`.
5. LSP, output styles, themes, monitors, workflows, mods and `dependencies` are enhancements; the plugin must still deliver its core value in Cowork without them.
6. Scripts and hooks use only common system tools (`bash`, `python3`, `node`), install nothing, and fail safe with a clear message — the Cowork runtime's available interpreters are **not documented** (unverified), so never assume more.
7. Test on both before every release:
   - Claude Code: `claude --plugin-dir plugins/<name>` (or local marketplace install).
   - Cowork: add the marketplace (or **Customize → Plugins → Add → Upload plugin** with a zip), start a task, confirm skills/agents/hooks load and connectors connect.

## Declaring surfaces

- Every plugin declares its surfaces in `plugin.json` → `"metadata": { "surfaces": [...] }`: `["claude-code", "cowork"]` (default) or `["claude-code"]`. Claude Code ignores `metadata`; our tooling reads it.
- Scaffold a Claude Code-only plugin with `new-plugin.mjs --claude-code-only`.
- From that one field: the README **works in** badge, the catalog **Works in** column, and `check-repo.mjs` checks.
- `check-repo.mjs` fails when: `metadata.surfaces` is missing/invalid; a plugin ships `bin/` but isn't `["claude-code"]`; the badge doesn't match; a Claude Code-only README lacks "**Claude Code only**"; the Compatibility table misses a row for a shipped component or lists one it doesn't ship.

## README obligations

- The **Compatibility** table reflects exactly the components the plugin ships, per the matrix above.
- A Claude Code-only plugin states it in the hero/TL;DR, and the reason (e.g. "ships an LSP server", "needs `bin/` executables").
- Conditional features (local MCP, `userConfig`) are explained in Requirements/Configuration for Cowork users.
