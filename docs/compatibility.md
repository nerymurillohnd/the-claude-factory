# 🧭 Compatibility

> Which parts of a plugin load in **Claude Code**, **Cowork** and **Claude chat** — so you know what you'll get before you install.

Claude Code, Cowork and Claude chat can all install the same plugin, but each one loads a different subset of what it contains. A surface silently skips components it doesn't support, so a plugin can feel complete in one place and partial in another. **Every plugin README has a Compatibility table** that applies these rules to that plugin.

---

## 🧩 Components by surface

| Component | Claude Code | Cowork | Claude chat |
| :-- | :--: | :--: | :--: |
| 🎯 **Skills** (`skills/<name>/SKILL.md`) | ✅ | ✅ | ✅ |
| ⌨️ **Commands** (`commands/*.md`) | ✅ | ✅ run as `/plugin:command` | ⚠️ loaded as a skill |
| 🤖 **Agents** (`agents/*.md`) | ✅ | ✅ | ➖ |
| 🪝 **Hooks** (`hooks/hooks.json`) | ✅ | ✅ | ➖ |
| 🔌 **Remote MCP server** (`http`/`sse`, fixed URL) | ✅ | ✅ connect from the plugin's **Connectors** tab | 🔗 add or connect it on the **Connectors** tab |
| 🖥️ **Local MCP server** (a command, incl. `.mcpb`) | ✅ | ✅ when the session runs on your computer | ➖ |
| 🔐 **MCP server using `${user_config.*}`** | ✅ prompts you for values | ⚠️ only options with defaults | ➖ when the URL uses them |
| 🧠 **LSP servers** | ✅ | ➖ | ➖ |
| 🎨 **Output styles** · 🌈 **Themes** · ⚙️ **`settings`** | ✅ | ➖ | ➖ |
| ⚙️ **Executables** in a top-level `bin/` | ✅ | ❌ | ❌ |

**Legend:** ✅ loads · ⚠️ partial · 🔗 needs a manual step · ➖ ignored on that surface · ❌ the whole plugin can't be installed there

<sub>Source: Anthropic, [Plugin feature support across platforms](https://claude.com/docs/plugins/platform-support).</sub>

## 🗺️ Where you add plugins

| | Cowork & Claude chat | Claude Code |
| :-- | :-- | :-- |
| **Where** | **Customize** → **Plugins** | `/plugin` in a session, or `claude plugin install` |
| **Install attaches to** | Your claude.ai account | The machine (user, project or local scope) |
| **Sync** | Installs also appear in Claude Code as `<plugin>@synced` | Shell installs stay on that machine |
| **Limits** | Up to 25 added marketplaces; 5,000 files / 200 MB per plugin | None per account |

## 💡 What this means for you

- 🧑‍💻 **Using Claude Code?** Everything in a plugin works.
- 🤝 **Using Cowork?** Skills, agents, hooks and MCP servers work. LSP servers, output styles and themes are skipped. Plugins with a `bin/` folder can't be installed — their README says so up front.
- 💬 **Using Claude chat?** Skills work. Agents and hooks are skipped; remote MCP servers need to be connected by hand.

---

<sub>⬅️ [Managing plugins](./managing-plugins.md) · Next: [Troubleshooting](./troubleshooting.md) ➡️</sub>
