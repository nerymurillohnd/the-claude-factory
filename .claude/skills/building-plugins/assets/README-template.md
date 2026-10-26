<!-- TEMPLATE: every double-brace placeholder and every TODO comment must be resolved before release. check-repo.mjs fails on leftovers. Keep every section; delete only rows, blocks and links a TODO says to delete. -->
<div align="center">

# {{emoji}} {{displayName}}

<p><strong>{{description}}</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2F{{name}}%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-{{surfacesBadge}}-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-{{categoryBadge}}-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%20{{minClaudeCode}}-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Install](#-installation) •
[Usage](#-usage) •
[Configuration](#%EF%B8%8F-configuration) • <!-- TODO: delete this link together with the Configuration section when there is nothing to configure. -->
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

{{surfacesNote}}> [!TIP]
> **TL;DR** — <!-- TODO: one sentence on the outcome a user gets, e.g. "Type `/{{name}}:run` and get X without doing Y." -->

## ✨ Why use it

<!-- TODO: sell the outcome, not the mechanics. 3–5 bullets, each starting with a bold benefit. -->

- **Benefit one** — what pain disappears.
- **Benefit two** — what becomes faster or safer.
- **Benefit three** — what you no longer have to remember.

## 🧩 What's inside

<!-- TODO: one row per component. Delete rows you don't ship. The last column shows exactly what users type or what triggers it. -->

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `{{name}}:example` | Short description | `/{{name}}:example` or automatically when relevant |
| 🤖 Agent | `{{name}}:example-agent` | Short description | Delegated by Claude, or "use the example-agent agent" |
| 🪝 Hook | `PreToolUse` | Short description | Automatically on matching tool calls |
| 🔌 MCP server | `example` | Short description | Tools appear as `mcp__plugin_{{name}}_example__*` |
| 🧠 LSP server | `example-lsp` | Short description | Automatically for matching file types |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v{{minClaudeCode}} or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | <!-- TODO: each tool on PATH with its version constraint, e.g. "`node` 22+ and `gh`, signed in — see below", or "None" --> |
| **Accounts / API keys** | <!-- TODO: e.g. "A GitHub token (asked for when you enable the plugin)", or "None" --> |
| **Network** | <!-- TODO: every network call: what, to where and when, e.g. "The MCP server calls api.github.com", or "None" --> |

<!-- TODO: list how to install each external tool, with the minimum version of any single feature that needs one; delete this block when there are none. -->
**Install the tools:**

- <!-- TODO: **`tool`** — why the plugin needs it. macOS: `command` · Linux: `command`. Alternatives. -->

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install {{name}} --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install {{name}}@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install {{name}} --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install {{name}}@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **{{displayName}}** in **Discover** and select **Add**.

</details>

<!-- TODO: for a Claude Code-only plugin, delete the Claude app block above and keep the Code-tab block below; otherwise keep both. -->
<details>
<summary><b>🖥️ Claude desktop app — Code tab</b></summary>

With the marketplace added, click **+** next to the prompt box and select **Add plugins**; if the menu shows **Plugins** instead, select it, then **Browse plugins**. Then select **{{displayName}}** and choose a scope.

</details>

> [!NOTE]
> No GitHub SSH key? Claude Code checks whether one works with `github.com` before it clones. Set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` in your shell to skip that check and always clone over HTTPS. New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

<!-- TODO: keep the next paragraph only when the plugin ships a mod; otherwise delete it. -->
A mod runs with your permissions and no sandbox. Before you install it, you can see everything it hooks and calls with `claude plugin validate <path to the plugin folder>`.

## 🚀 Usage

<!-- TODO: 2–4 realistic examples. Show what the user types and what they get back. -->

### Example: <!-- TODO: task name -->

```text
/{{name}}:example <argument>
```

**Result:** <!-- TODO: what Claude does or produces. -->

## ⚙️ Configuration

<!-- TODO: document every userConfig option, env var and setting. Delete this section, and its link at the top, when there is nothing to configure. -->

| Option | Type | Default | Description |
| :-- | :-- | :-- | :-- |
| `example_option` | string | — | What it controls. |

Set the options when Claude Code asks for them as you install or enable the plugin, or at any time:

- In a session: `/plugin` → **Installed** → **{{displayName}}** → **Configure options**, or `/plugin configure {{name}}@the-claude-factory`.
- From your shell, at install time: `claude plugin install {{name}}@the-claude-factory --config <option>=<value>`. The shell install never asks for values on its own.

<!-- TODO: say which options are stored in your system's secure credential store (the ones marked sensitive), or delete this comment. -->

## 🔍 What this plugin runs and sends

<!-- TODO: state everything the plugin does on the user's machine. Write "None" for a line that does not apply; never delete a line. -->

- **Hooks:** <!-- TODO: each `<Event>` on `<matcher>`, the script it runs and what that script does, or "None" -->
- **MCP servers:** <!-- TODO: each server, its command or URL, and what it is used for, or "None" -->
- **Monitors:** <!-- TODO: each background command and what it watches, or "None" -->
- **Network:** <!-- TODO: every destination and the data sent there, or "None" -->
- **Files written:** <!-- TODO: every path, including anything under the plugin's data directory, or "None" -->

## 🔄 Updating

Auto-update is off by default for this marketplace, as for every third-party marketplace. To update now:

```bash
claude plugin update {{name}}@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **{{displayName}}** → **Update now**. Then run `/reload-plugins`. <!-- TODO: name each external tool the user updates on their own, e.g. "Update `gopls` yourself, the way you installed it.", or delete this comment. -->

<!-- TODO: delete the next paragraph for a Claude Code-only plugin. -->
Added from the Claude app? Claude Code loads it as `{{name}}@synced` and picks up its updates at each session start; update and remove it in the app (**Customize** → **Plugins**). In `/plugin` you can only turn it off, unless your organization requires it.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall {{name}}@the-claude-factory
```

Installed with `--scope project`? Add `--scope project` here too. Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`.

In a session: `/plugin` → **Installed** → **{{displayName}}** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **{{displayName}}** → its menu → **Remove**. <!-- TODO: drop the Claude app sentence for a Claude Code-only plugin. -->

<!-- TODO: say what stays behind: data the plugin wrote, files in the user's project, tools the user installed for it; or "The plugin keeps no data and writes no files, so nothing is left behind." -->

## 🧭 Compatibility

<!-- TODO: keep one row per component type this plugin ships (check-repo.mjs enforces it) and delete the rest. Each cell is the docs/compatibility.md cell for that type. -->

**Works in:** {{surfacesText}}

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |
| ⌨️ Commands | ✅ | ✅ run as `/plugin:command`; loaded as a skill in a chat conversation |
| 🤖 Agents | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |
| 🪝 Hooks | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |
| 🧩 Mods | ✅ every Claude Code session except a Desktop session on WSL | ⚠️ the plugin directory lists a mod for Claude Code only |
| 🔌 Remote MCP server | ✅ | 🔗 add or connect it on the plugin's **Connectors** tab |
| 🖥️ Local MCP server | ✅ | ⚠️ only in Cowork sessions on your computer |
| 🔐 MCP server using `${user_config.*}` | ✅ prompts you for values | 🔗 the app can't fill the values: when they sit in headers, the plugin's **Connectors** tab lists the server as not added, and it works once you connect it there and enter them yourself, such as a token as a request header; a chat conversation skips it when its URL holds the reference |
| 🧠 LSP servers | ✅ | ➖ |
| 🎨 Output styles | ✅ | ➖ |
| 🌈 Themes | ✅ | ➖ |
| 📡 Monitors | ✅ | ➖ |
| 🔁 Workflows | ✅ | ➖ |
| ⚙️ Executables in a top-level `bin/` | ✅ | ❌ |

<sub>✅ loads · ⚠️ partial · 🔗 needs a manual step · ➖ ignored on that surface · ❌ the whole plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise. See [Compatibility](../../docs/compatibility.md).</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/{{name}}:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<!-- TODO: add plugin-specific questions, the most common one first. -->

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
<!-- TODO: link sibling plugins that pair well with this one, and the official docs of each component type the plugin ships (a mod: https://code.claude.com/docs/en/plugins/mods/overview). -->

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin={{name}}) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin={{name}}) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin={{name}})

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo <!-- TODO: when the plugin derives from third-party material, add "Parts are derived from <source> (<license>); see [NOTICE.txt](./NOTICE.txt)."; when it names a third-party product, add "Not affiliated with or endorsed by <owner>. *<product>* is a trademark of <owner>."; otherwise delete this comment. -->
