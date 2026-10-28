<div align="center">

# <Plugin emoji> <Display Name>

<p><strong><description></strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2F<owner>%2F<repo>%2Fmain%2Fplugins%2F<plugin>%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-<surfaces-badge>-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-<category-badge>-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%20<Minimum Claude Code version>-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Prerequisites](#-prerequisites) •
[Install](#-installation) •
[Usage](#-usage) •
[Configuration](#%EF%B8%8F-configuration) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

<code-only>
💻 **Claude Code only** — <Why: for example "it ships an LSP server">. It doesn't install in the Claude app (chat or Cowork).
</code-only>

> [!TIP]
> **TL;DR** — <One sentence on the outcome a user gets, for example "Type `/<plugin>:run` and get X without doing Y.">

## ✨ Why use it

- **<Benefit title>** — <What pain disappears>.
- **<Benefit title>** — <What becomes faster or safer>.
- **<Benefit title>** — <What you no longer have to remember>.

## 🧩 What's inside

| Component     | Name                    | What it does        | How it runs                                             |
| :------------ | :---------------------- | :------------------ | :------------------------------------------------------ |
| 🎯 Skill      | `<plugin>:<Skill name>` | <Short description> | `/<plugin>:<Skill name>` or automatically when relevant |
| 🤖 Agent      | `<plugin>:<Agent name>` | <Short description> | Delegated by Claude, or "use the <Agent name> agent"    |
| 🪝 Hook       | `<Hook event>`          | <Short description> | Automatically on matching tool calls                    |
| 🔌 MCP server | `<Server name>`         | <Short description> | Tools appear as `mcp__plugin_<plugin>_<Server name>__*` |
| 🧠 LSP server | `<Language server>`     | <Short description> | Automatically for matching file types                   |

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | <Minimum Claude Code version> | `claude --version` |
| <Tool name> | <Tool minimum version> | `<Tool check command>` |

### 🤖 Claude Code

Already installed? Bring it to the latest version the way you installed it. New to Claude Code? Follow the [official setup](https://code.claude.com/docs/en/setup).

<details>
<summary>⬇️ <b>Native installer</b> — macOS, Linux, WSL</summary>

```bash
claude update
```

</details>
<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew upgrade claude-code
```

</details>
<details>
<summary>📦 <b>npm</b> — any platform</summary>

```bash
npm install -g @anthropic-ai/claude-code@latest
```

</details>

### <Tool emoji> <Tool name>

<details>
<summary><Method emoji> <b><Install method></b> — <Platforms it runs on></summary>

```bash
<Install command>
```

</details>

<One details block per install method the tool's official docs give; one tool section per row of the table after Claude Code. With no tool beyond Claude Code, delete this line, the tool's row and the tool's section.>

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add <owner>/<repo>
claude plugin install <plugin>@<marketplace-name>
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install <plugin> --marketplace <owner>/<repo>
```

For everyone working in the current repository:

```bash
claude plugin install <plugin>@<marketplace-name> --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add <owner>/<repo>
/plugin install <plugin>@<marketplace-name>
```

<app>
### 🖥️ Claude app (web and desktop)

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `<owner>/<repo>`.
3. Find **<Display Name>** in **Discover** and select **Add**.
</app>

## 🚀 Usage

### <Task name>

```text
/<plugin>:<Skill name> <Skill arguments>
```

**Result:** <What Claude does or produces. Two to four realistic examples, each under its own ### heading.>

## ⚙️ Configuration

| Option         | Type          | Default         | Description        |
| :------------- | :------------ | :-------------- | :----------------- |
| `<Option key>` | <Option type> | <Default value> | <What it controls> |

Set options when installing (`claude plugin install <plugin>@<marketplace-name> --config <Option key>=<Option value>`), later with `/plugin configure <plugin>@<marketplace-name>`, or in `/plugin` → **Installed** → **<Display Name>** → **Configure options**. <Delete this section, and its link in the header, when there is nothing to configure.>

## 🔍 What this plugin runs and sends

- **Hooks:** <`<Hook event>` on `<Tool matcher>` runs `scripts/<Hook script>`, which does what; or "none">.
- **MCP servers:** <`<Server name>` — its command or URL, and what it's used for; or "none">.
- **Network:** <Every destination and the data sent there, or "none">.
- **Files written:** <Paths, including anything under the plugin data directory, or "none">.
- **Before you install:** <For a plugin with a mod, keep this bullet and delete this placeholder; otherwise delete the bullet.> a mod runs with your permissions and no sandbox; `claude plugin validate <path to the plugin folder>` shows everything it hooks and calls.

## 🔄 Updating

```bash
claude plugin update <plugin>@<marketplace-name>
```

Then, in an open session:

```text
/reload-plugins
```

<app>Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `<plugin>@synced`: update and uninstall it in the app (**Customize** → **Plugins**).</app>

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **<marketplace-name>** → **Enable auto-update**.

<Update each tool of Prerequisites the way you installed it, for example with `brew upgrade <Homebrew formula>`; delete this line when the plugin needs no tool beyond Claude Code.>

## 🗑️ Uninstalling

```bash
claude plugin uninstall <plugin>@<marketplace-name>
```

Installed with `--scope project`:

```bash
claude plugin uninstall <plugin>@<marketplace-name> --scope project
```

<app>In the Claude app: **Customize** → **Plugins** → **<Display Name>** → its menu → **Remove**.</app>

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. <What stays behind: data the plugin wrote, files in the user's project, tools the user installed for it; or "The plugin keeps no data and writes no files, so nothing is left behind.">

## 🧭 Compatibility

**Works in:** <surfaces-text>

| Component                              |                         Claude Code                          |                                                                                                                                          Claude app                                                                                                                                           |
| :------------------------------------- | :----------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| 🎯 Skills                              |                              ✅                              |                                                                                                                                              ✅                                                                                                                                               |
| ⌨️ Commands                            |                              ✅                              |                                                                                                             ✅ run as `/plugin:command`; loaded as a skill in a chat conversation                                                                                                             |
| 🤖 Agents                              |                              ✅                              |                                                                                                                       ⚠️ in Cowork sessions, not in a chat conversation                                                                                                                       |
| 🪝 Hooks                               |                              ✅                              |                                                                                                                       ⚠️ in Cowork sessions, not in a chat conversation                                                                                                                       |
| 🧩 Mods                                | ✅ every Claude Code session except a Desktop session on WSL |                                                                                                                   ⚠️ the plugin directory lists a mod for Claude Code only                                                                                                                    |
| 🔌 MCP server (remote)                 |                              ✅                              |                                                                                                                    🔗 add or connect it on the plugin's **Connectors** tab                                                                                                                    |
| 🖥️ MCP server (local)                  |                              ✅                              |                                                                                                                          ⚠️ only in Cowork sessions on your computer                                                                                                                          |
| 🔐 MCP server using `${user_config.*}` |                  ✅ prompts you for values                   | 🔗 the app can't fill the values: when they sit in headers, the plugin's **Connectors** tab lists the server as not added, and it works once you connect it there and enter them yourself, such as a token as a request header; a chat conversation skips it when its URL holds the reference |
| 🧠 LSP server                          |                              ✅                              |                                                                                                                                              ➖                                                                                                                                               |
| 🎨 Output styles                       |                              ✅                              |                                                                                                                                              ➖                                                                                                                                               |
| 📡 Monitors                            |                              ✅                              |                                                                                                                                              ➖                                                                                                                                               |
| 🔁 Workflows                           |                              ✅                              |                                                                                                                                              ➖                                                                                                                                               |
| 🌈 Themes                              |                              ✅                              |                                                                                                                                              ➖                                                                                                                                               |
| ⚙️ Executables (`bin/`)                |                              ✅                              |                                                                                                                                              ❌                                                                                                                                               |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/<plugin>:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<Plugin-specific questions, each in its own details block, or delete this line.>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- <Sibling plugins that pair well with this one, and the official docs of each component type the plugin ships; a mod: https://code.claude.com/docs/en/plugins/mods/overview.>

## 🐞 Found a problem?

[Report a bug](https://github.com/<owner>/<repo>/issues/new?template=bug_report.yml&plugin=<plugin>) •
[Request a feature](https://github.com/<owner>/<repo>/issues/new?template=feature_request.yml&plugin=<plugin>) •
[Ask a question](https://github.com/<owner>/<repo>/issues/new?template=question.yml&plugin=<plugin>)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo <When the plugin derives from third-party material, add "Parts are derived from <Source work> (<Source license>); see [NOTICE.txt](./NOTICE.txt)."; when it names a third-party product, add "Not affiliated with or endorsed by <Trademark owner>. _<Product name>_ is a trademark of <Trademark owner>."; otherwise delete this placeholder.>
