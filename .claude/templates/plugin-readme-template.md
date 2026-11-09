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
💻 **Claude Code only** — <Why it needs Claude Code: for example "it ships an LSP server">. <What Claude does with it: "Claude can't install it." for a plugin with a top-level bin/, otherwise "Claude can install it, but" and what doesn't work there>.
</code-only>

> [!TIP]
> **TL;DR** — <One sentence on the outcome a user gets, for example "Type `/<plugin>:run` and get X without doing Y.">

<Plugin overview for readers: two to four sentences on what the plugin is, the problem it solves and why it is worth installing, at more length than the one-line description above.>

## ✨ Why use it

- **<Benefit title>** — <What pain disappears>.
- **<Benefit title>** — <What becomes faster or safer>.
- **<Benefit title>** — <What you no longer have to remember>.

## 🧩 What's inside

| Component      | Name                    | What it does        | How it runs                                                |
| :------------- | :---------------------- | :------------------ | :--------------------------------------------------------- |
| 🎯 Skill       | `<plugin>:<Skill name>` | <Short description> | `/<plugin>:<Skill name>` or automatically when relevant    |
| ⌨️ Command     | `/<plugin>:<Command name>` | <Short description> | You type it                                             |
| 🤖 Agent       | `<plugin>:<Agent name>` | <Short description> | Delegated by Claude, or "use the <Agent name> agent"       |
| 🪝 Hook        | `<Hook event>`          | <Short description> | Automatically on matching tool calls                       |
| 🧩 Mod         | `<Mod name>`            | <Short description> | Inside Claude Code, on the events it hooks                 |
| 🔌 MCP server  | `<Server name>`         | <Short description> | Tools appear as `mcp__plugin_<plugin>_<Server name>__*`    |
| 🧠 LSP server  | `<Language server>`     | <Short description> | Automatically for matching file types                      |
| 📡 Monitor     | `<Monitor name>`        | <Short description> | In the background while the session runs                   |
| 🔁 Workflow    | `/<plugin>:<Workflow name>` | <Short description> | You type it                                            |
| ⚙️ Executable  | `<Executable name>`     | <Short description> | On the Bash tool's `PATH` while the plugin is enabled      |

<Keep one row per component the plugin ships, and in Compatibility one row per component type; delete the other rows and this line.>

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | <Minimum Claude Code version> | `claude --version` |
| <Tool name> | <Tool minimum version> | `<Tool check command>` |

<Base tools line: "The plugin also uses" and the POSIX base tools its hooks or scripts run, such as `sed`, `awk` and `grep`, "which come with macOS and Linux"; delete this line when it runs none.>

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

<One details block per install method the tool's official docs give, then its check command in a fenced block; one tool section per row of the table after Claude Code. With no tool beyond Claude Code, delete this line, the tool's row and the tool's section.>

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
### 🖥️ Claude (web and desktop)

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `<owner>/<repo>`.
3. Find **<Display Name>** in **Discover** and select **Add**.
</app>

## 🚀 Usage

### <Task name>

```text
/<plugin>:<Skill name> <Skill arguments>
```

**Result:** <What Claude does or produces. Two to four realistic examples, each under its own ### heading with its prompt or command in a fenced block.>

## ⚙️ Configuration

| Option         | Type          | Default         | Description        |
| :------------- | :------------ | :-------------- | :----------------- |
| `<Option key>` | <Option type> | <Default value> | <What it controls> |

Set an option when you install:

```bash
claude plugin install <plugin>@<marketplace-name> --config <Option key>=<Option value>
```

Change it later:

```text
/plugin configure <plugin>@<marketplace-name>
```

Or open `/plugin` → **Installed** → **<Display Name>** → **Configure options**.

<Configuration variants: with no options but behavior the user's project decides, replace the table and the commands above with a table of what the plugin reads in the project and what it does then; with neither, delete this section and its link in the header.>

## 🔍 What this plugin runs and sends

- **Hooks:** <One line per hook: `<Hook event>` on `<Tool matcher>` runs `<Hook command>`, which does what. Then once: "Hooks run on their own, with your access and without a permission prompt." Or "none".>
- **Mod:** <For a mod: the events it hooks, every file it reads, every environment variable, process and network call it uses, and what it never does (writes, network, model calls), then "It runs inside Claude Code with your access and no sandbox." Otherwise delete this bullet.>
- **MCP servers:** <`<Server name>` — its command or URL, and what it's used for; or "none">.
- **Network:** <Every destination and the data sent there, or "none">.
- **Files written:** <Paths, including anything under the plugin data directory, or "none">.
- **Privacy:** the author collects no data. The marketplace's [privacy policy](https://github.com/<owner>/<repo>/blob/main/PRIVACY.md) covers this plugin and the outside services it can reach.
- **Before you install:** <For a plugin with a mod, keep this bullet and delete this placeholder; otherwise delete the bullet.> a mod runs with your permissions and no sandbox. Install it only if you trust this marketplace; the Mod line above lists everything it reaches.

## 🔄 Updating

```bash
claude plugin update <plugin>@<marketplace-name>
```

Then, in an open session:

```text
/reload-plugins
```

<app>Installed from Claude? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `<plugin>@synced`: update and uninstall it in Claude (**Customize** → **Plugins**).</app>

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **<marketplace-name>** → **Enable auto-update**.

<Update each tool of Prerequisites the way you installed it, with the command in a fenced block, for example `brew upgrade <Homebrew formula>`; delete this line when the plugin needs no tool beyond Claude Code.>

## 🗑️ Uninstalling

```bash
claude plugin uninstall <plugin>@<marketplace-name>
```

Installed with `--scope project`:

```bash
claude plugin uninstall <plugin>@<marketplace-name> --scope project
```

<app>In Claude: **Customize** → **Plugins** → **<Display Name>** → its menu → **Remove**.</app>

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. <What the data directory holds, or "The plugin keeps nothing in its data directory.", then what stays behind: files in your project and tools you installed for it.>

## 🧭 Compatibility

**Works in:** <surfaces-text>

| Component | Claude Code | Claude |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |
| ⌨️ Commands | ✅ | ✅ you run them by typing their name; where Claude can't run tasks, it applies them as skills |
| 🤖 Agents | ✅ | ⚠️ only in conversations where Claude can run tasks |
| 🪝 Hooks | ✅ | ⚠️ only in conversations where Claude can run tasks |
| 🧩 Mods | ✅ v2.1.287+ (Desktop v2.1.286+); hooks run in every session except Desktop on WSL; ⚠️ drawing depends on where: panes in the terminal, Desktop and VS Code (extension v2.1.299+, v2.1.304+ without feature flags), the band above the prompt only in the terminal and Desktop | ⚠️ the plugin directory lists a mod for Claude Code only |
| 🔌 Remote MCP server | ✅ | 🔗 add or connect it on the plugin's **Connectors** tab |
| 🖥️ Local MCP server | ✅ | ⚠️ only in conversations that run tasks on your computer, with Claude Desktop open |
| 🔐 MCP server using `${user_config.*}` | ✅ prompts you for values | 🔗 Claude doesn't prompt for the values: it skips the server when an option it references has no default, or, where Claude can't run tasks, when its URL holds the reference; with the values in headers, the **Connectors** tab lists the server as not added until you connect it there and enter them yourself |
| 🧠 LSP servers | ✅ | ➖ |
| 🎨 Output styles | ✅ | ➖ |
| 🌈 Themes | ✅ | ➖ |
| 🛠️ Default `settings` | ✅ | ➖ |
| 📡 Monitors | ✅ | ➖ not documented for Claude |
| 🔁 Workflows | ✅ | ➖ not documented for Claude |
| ⚙️ Executables (`bin/`) | ✅ | ❌ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

<Compatibility note: what differs for this plugin on a surface, such as a skill that needs a program Claude can't run, and for a mod where it runs and draws; delete this line when nothing differs.>

**Platforms:** macOS and Linux<Windows clause: ", and Windows through Git Bash" when every script and tool the plugin runs works there; otherwise delete this placeholder>.

## 🚧 Limitations

- <Limit the user should know, one per bullet.>
- <For a mod, keep these and fill them from building-mods section 5: what turns it off (`disableAllHooks` in your settings or managed settings, an organization's `allowManagedModsOnly`, `--safe-mode` and `--bare`); that with managed settings or a Team or Enterprise login the built-in guard `cc-plugin-sec-default` loads ahead of user mods and can refuse the mod or keep a deny it tried to lift; that `allowManagedModsOnly` refuses any mod installed from a GitHub source, even one the organization enables; that the mod can't restyle the permission prompt or change what it shows; and that `/plugin` names the mods the session loaded while only `claude --debug` shows why one was refused. With no limits, delete this section.>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/<plugin>:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<Plugin-specific questions, each in its own closed details block with any command in a fenced block, or delete this line.>

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

## 🙏 Credits

<Third-party work the plugin builds on, with its license and a link, or delete this section.>

## 📄 License

[MIT](./LICENSE) © Nery Murillo.<License notes: when the plugin derives from third-party material, add " Parts are derived from <Source work> (<Source license>); see [NOTICE.txt](./NOTICE.txt)."; when it names another third-party product, add " Not affiliated with or endorsed by <Trademark owner>. _<Product name>_ is a trademark of <Trademark owner>."; otherwise delete this placeholder.> Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
