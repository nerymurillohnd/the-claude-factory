# 🧭 Compatibility

> Which parts of a plugin load in **Claude Code** and in the **Claude app** — so you know what you'll get before you install.

Claude Code and the Claude app (web, desktop and mobile) can both install the same plugin, but each one loads a different subset of what it contains. A surface silently skips components it doesn't support, so a plugin can feel complete in one place and partial in another. **Every plugin README has a Compatibility table** that applies these rules to that plugin.

---

## 🧩 Components by surface

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 **Skills** (`skills/<name>/SKILL.md`) | ✅ | ✅ |
| ⌨️ **Commands** (`commands/*.md`) | ✅ | ✅ run as `/plugin:command`; loaded as a skill in a chat conversation |
| 🤖 **Agents** (`agents/*.md`) | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |
| 🪝 **Hooks** (`hooks/hooks.json`) | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |
| 🧩 **Mods** (a hooks module under `modules` in `hooks/hooks.json`) | ✅ every Claude Code session except a Desktop session on WSL | ⚠️ the plugin directory lists a mod for Claude Code only |
| 🔌 **Remote MCP server** (`http`/`sse`, fixed URL) | ✅ | 🔗 add or connect it on the plugin's **Connectors** tab |
| 🖥️ **Local MCP server** (a command, incl. `.mcpb`) | ✅ | ⚠️ only in Cowork sessions on your computer |
| 🔐 **MCP server using `${user_config.*}`** | ✅ prompts you for values | 🔗 the app can't fill the values: when they sit in headers, the plugin's **Connectors** tab lists the server as not added, and it works once you connect it there and enter them yourself, such as a token as a request header; a chat conversation skips it when its URL holds the reference |
| 🧠 **LSP servers** | ✅ | ➖ |
| 🎨 **Output styles** · 🌈 **Themes** · ⚙️ **`settings`** | ✅ | ➖ |
| ⚙️ **Executables** in a top-level `bin/` | ✅ | ❌ |

**Legend:** ✅ loads · ⚠️ partial · 🔗 needs a manual step · ➖ ignored on that surface · ❌ the whole plugin can't be installed there

## 💬 Cowork sessions and chat conversations

Chat and Cowork are now one Claude app. When you send a message, the app runs it as a **Cowork session** when it can, with the full set of plugin components above, and as a **chat conversation** otherwise: for example on a device that can't run Cowork, or in the separate **Chat** mode that Team and Enterprise plans keep for now. In a chat conversation, a plugin's skills, commands and remote connectors work, but its agents, hooks and local MCP servers don't run.

<sub>Sources: Anthropic, [Use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude), [Claude Cowork and chat are one Claude](https://support.claude.com/en/articles/16761823), [Plugin feature support across platforms](https://claude.com/docs/plugins/platform-support).</sub>

## 🗺️ Where you add plugins

| | Claude app | Claude Code |
| :-- | :-- | :-- |
| **Where** | **Customize** → **Plugins** | `/plugin` in a session, or `claude plugin install` |
| **Install attaches to** | Your claude.ai account | The machine (user, project or local scope) |
| **Sync** | Installs also appear in Claude Code as `<plugin>@synced` | Shell installs stay on that machine |
| **Limits** | Up to 25 added marketplaces; 5,000 files / 200 MB per plugin | None per account |

## 💡 What this means for you

- 🧑‍💻 **Using Claude Code?** Everything in a plugin works.
- 🖥️ **Using the Claude app?** Skills, commands and remote MCP servers work everywhere. Agents, hooks and local MCP servers work in Cowork sessions, not in a chat conversation. LSP servers, output styles and themes are skipped. Plugins with a `bin/` folder can't be installed — their README says so up front.

---

<sub>⬅️ [Managing plugins](./managing-plugins.md) · Next: [Troubleshooting](./troubleshooting.md) ➡️</sub>
