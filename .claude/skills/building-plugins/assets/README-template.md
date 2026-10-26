<div align="center">

# <Emoji> <Display Name>

<p><strong><description></strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2F<owner>%2F<repo>%2Fmain%2Fplugins%2F<plugin>%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-<surfaces-badge>-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-<category-badge>-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%20<Minimum Claude Code version>-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
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

- **<Benefit>** — <what pain disappears>.
- **<Benefit>** — <what becomes faster or safer>.
- **<Benefit>** — <what you no longer have to remember>.

## 🧩 What's inside

| Component     | Name                | What it does        | How it runs                                        |
| :------------ | :------------------ | :------------------ | :------------------------------------------------- |
| 🎯 Skill      | `<plugin>:<Skill>`  | <Short description> | `/<plugin>:<Skill>` or automatically when relevant |
| 🤖 Agent      | `<plugin>:<Agent>`  | <Short description> | Delegated by Claude, or "use the <Agent> agent"    |
| 🪝 Hook       | `<Event>`           | <Short description> | Automatically on matching tool calls               |
| 🔌 MCP server | `<Server>`          | <Short description> | Tools appear as `mcp__plugin_<plugin>_<Server>__*` |
| 🧠 LSP server | `<Language server>` | <Short description> | Automatically for matching file types              |

## ✅ Requirements

| Requirement             | Details                                                                   |
| :---------------------- | :------------------------------------------------------------------------ |
| **Claude Code**         | v<Minimum Claude Code version> or later — check with `claude --version`   |
| **Surfaces**            | See [Compatibility](#-compatibility)                                      |
| **External tools**      | <Each tool on PATH, its minimum version and how to install it, or "None"> |
| **Accounts / API keys** | <For example "A GitHub token (prompted on enable)", or "None">            |
| **Network**             | See [What this plugin runs and sends](#-what-this-plugin-runs-and-sends)  |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install <plugin> --marketplace <owner>/<repo>

# Or, with the marketplace already added
claude plugin install <plugin>@<marketplace-name>
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

No GitHub SSH key? Set this first, so installs from `/plugin` and updates use HTTPS:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install <plugin> --marketplace <owner>/<repo>
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install <plugin>@<marketplace-name>` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<app>
<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `<owner>/<repo>`.
3. Find **<Display Name>** in **Discover** and select **Add**.

In the desktop app's **Code** tab you can also click **+** next to the prompt box → **Add plugins** (or **Plugins** → **Browse plugins**), or open **Settings** → **Plugins** → **Discover**.

</details>
</app>

<code-only>
<details>
<summary><b>🖥️ Claude desktop app — Code tab</b></summary>

With the marketplace added, click **+** next to the prompt box → **Add plugins** (or **Plugins** → **Browse plugins**), or open **Settings** → **Plugins** → **Discover**; then select **<Display Name>** and choose a scope.

</details>
</code-only>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

<For a plugin with a mod, keep this paragraph and delete this line; otherwise delete both.> A mod runs with your permissions and no sandbox. Before you install it, you can see everything it hooks and calls with `claude plugin validate <path to the plugin folder>`.

## 🚀 Usage

### <Task name>

```text
/<plugin>:<Skill> <Arguments>
```

**Result:** <What Claude does or produces. Two to four realistic examples, each under its own ### heading.>

## ⚙️ Configuration

| Option     | Type   | Default   | Description        |
| :--------- | :----- | :-------- | :----------------- |
| `<Option>` | <Type> | <Default> | <What it controls> |

Set options when installing (`claude plugin install <plugin>@<marketplace-name> --config <Option>=<Value>`), later with `/plugin configure <plugin>@<marketplace-name>`, or in `/plugin` → **Installed** → **<Display Name>** → **Configure options**. <Delete this section, and its link in the header, when there is nothing to configure.>

## 🔍 What this plugin runs and sends

- **Hooks:** <`<Event>` on `<Matcher>` runs `scripts/<File>`, which does what; or "none">.
- **MCP servers:** <`<Server>` — its command or URL, and what it's used for; or "none">.
- **Network:** <Every destination and the data sent there, or "none">.
- **Files written:** <Paths, including anything under the plugin data directory, or "none">.

## 🔄 Updating

```bash
claude plugin update <plugin>@<marketplace-name>
```

Or in a session: `/plugin` → **Installed** → **<Display Name>** → **Update now**. Then run `/reload-plugins`. <Name each external tool the user updates on their own, for example "Update `gopls` yourself, the way you installed it.", or delete this sentence.>

<app>Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `<plugin>@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.</app>

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **<marketplace-name>** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall <plugin>@<marketplace-name>
```

Installed with `--scope project`? Add `--scope project` here too. Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you pass `--keep-data`.

In a session: `/plugin` → **Installed** → **<Display Name>** → **Uninstall**. <app>In the Claude app: **Customize** → **Plugins** → **<Display Name>** → its menu → **Remove**.</app>

<What stays behind: data the plugin wrote, files in the user's project, tools the user installed for it; or "The plugin keeps no data and writes no files, so nothing is left behind.">

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

[MIT](./LICENSE) © Nery Murillo <When the plugin derives from third-party material, add "Parts are derived from <Source> (<License>); see [NOTICE.txt](./NOTICE.txt)."; when it names a third-party product, add "Not affiliated with or endorsed by <Owner>. _<Product>_ is a trademark of <Owner>."; otherwise delete this placeholder.>
