<!--
  Procedure: .claude/references/plugin-readme.md
  Values to replace are {{camelCase}}. Instructions are HTML comments: follow each one, then delete it.
  Surface blocks: keep the content between <!- - app:start - -> and <!- - app:end - -> only when the plugin works in Claude,
  and the content between <!- - code-only:start - -> and <!- - code-only:end - -> only when it works in Claude Code alone;
  delete the markers themselves in both cases. Delete this comment.
-->
<div align="center">

# {{pluginEmoji}} {{displayName}}

<p><strong>{{description}}</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2F{{owner}}%2F{{repo}}%2Fmain%2Fplugins%2F{{name}}%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-{{surfacesBadge}}-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-{{categoryBadge}}-6B7280)]({{marketplaceCatalogUrl}})
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%20{{minClaudeCodeVersion}}-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: {{license}}](https://img.shields.io/badge/license-{{license}}-22C55E)](./LICENSE)

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

<!-- code-only:start -->
💻 **Claude Code only** — {{codeOnlyReason}}. {{codeOnlyEffect}}
<!-- code-only:end -->
<!-- codeOnlyReason: why it needs Claude Code, for example "it ships an LSP server". codeOnlyEffect: "Claude can't install it." for a plugin with a top-level bin/; otherwise "Claude can install it, but" and what doesn't work there. -->

> [!TIP]
> **TL;DR** — {{tldr}}

<!-- tldr: one sentence on the outcome a user gets, for example "Type `/{{name}}:run` and get X without doing Y." -->

{{overview}}

<!-- overview: two to four sentences on what the plugin is, the problem it solves and why it is worth installing, at more length than the description above. -->

## ✨ Why use it

- **{{benefitTitle}}** — {{benefit}}

<!-- Three benefits, one per bullet: what pain disappears, what becomes faster or safer, what the user no longer has to remember. -->

## 🧩 What's inside

| Component      | Name                    | What it does        | How it runs                                                |
| :------------- | :---------------------- | :------------------ | :--------------------------------------------------------- |
| 🎯 Skill       | `{{name}}:{{skillName}}` | {{componentSummary}} | `/{{name}}:{{skillName}}` or automatically when relevant |
| ⌨️ Command     | `/{{name}}:{{commandName}}` | {{componentSummary}} | You type it                                           |
| 🤖 Agent       | `{{name}}:{{agentName}}` | {{componentSummary}} | Delegated by Claude, or "use the {{agentName}} agent"    |
| 🪝 Hook        | `{{hookEvent}}`          | {{componentSummary}} | Automatically on matching tool calls                     |
| 🧩 Mod         | `{{modName}}`            | {{componentSummary}} | Inside Claude Code, on the events it hooks               |
| 🔌 MCP server  | `{{serverName}}`         | {{componentSummary}} | Tools appear as `mcp__plugin_{{name}}_{{serverName}}__*` |
| 📨 Channel     | `{{channelServer}}`      | {{componentSummary}} | When you start Claude Code with `--channels plugin:{{name}}@{{marketplaceName}}` |
| 🧠 LSP server  | `{{languageServer}}`     | {{componentSummary}} | Automatically for matching file types                    |
| 📡 Monitor     | `{{monitorName}}`        | {{componentSummary}} | In the background while the session runs                 |
| 🔁 Workflow    | `/{{name}}:{{workflowName}}` | {{componentSummary}} | You type it                                          |
| ⚙️ Executable  | `{{executableName}}`     | {{componentSummary}} | On the Bash tool's `PATH` while the plugin is enabled    |

<!-- Keep one row per component the plugin ships, and in Compatibility one row per component type; delete the other rows. -->

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | {{minClaudeCodeVersion}} | `claude --version` |
| {{toolName}} | {{toolMinVersion}} | `{{toolCheckCommand}}` |

The plugin also uses {{baseTools}}, which come with macOS and Linux.

<!-- baseTools: the POSIX base tools its hooks or scripts run, such as `sed`, `awk` and `grep`. Delete that sentence when it runs none. -->

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

### {{toolEmoji}} {{toolName}}

<details>
<summary>{{methodEmoji}} <b>{{installMethod}}</b> — {{installPlatforms}}</summary>

```bash
{{installCommand}}
```

</details>

<!-- One details block per install method the tool's official docs give, then its check command in a fenced block; one tool section per row of the table after Claude Code. With no tool beyond Claude Code, delete the tool's row and the tool's section. -->

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add {{owner}}/{{repo}}
claude plugin install {{name}}@{{marketplaceName}}
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install {{name}} --marketplace {{owner}}/{{repo}}
```

For everyone working in the current repository:

```bash
claude plugin install {{name}}@{{marketplaceName}} --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add {{owner}}/{{repo}}
/plugin install {{name}}@{{marketplaceName}}
```

<!-- app:start -->
### 🖥️ Claude (web and desktop)

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `{{owner}}/{{repo}}`.
3. Find **{{displayName}}** in **Discover** and select **Add**.
<!-- app:end -->

## 🚀 Usage

### {{taskName}}

```text
/{{name}}:{{skillName}} {{skillArguments}}
```

**Result:** {{result}}

<!-- Two to four realistic examples, each under its own ### heading with its prompt or command in a fenced block and what Claude does or produces. -->

## ⚙️ Configuration

| Option         | Type          | Default         | Description        |
| :------------- | :------------ | :-------------- | :----------------- |
| `{{optionKey}}` | {{optionType}} | {{optionDefault}} | {{optionSummary}} |

Set an option when you install:

```bash
claude plugin install {{name}}@{{marketplaceName}} --config {{optionKey}}={{optionValue}}
```

Change it later:

```text
/plugin configure {{name}}@{{marketplaceName}}
```

Or open `/plugin` → **Installed** → **{{displayName}}** → **Configure options**.

<!-- With no options but behavior the user's project decides, replace the table and the commands above with a table of what the plugin reads in the project and what it does then. With neither, delete this section and its link in the header. -->

## 🔍 What this plugin runs and sends

- **Hooks:** {{hooksRun}}
- **Mod:** {{modRuns}}
- **MCP servers:** {{mcpServersRun}}
- **Network:** {{networkDestinations}}
- **Files written:** {{filesWritten}}
- **Privacy:** the author collects no data. The marketplace's [privacy policy]({{privacyPolicyUrl}}) covers this plugin and the outside services it can reach.
- **Before you install:** a mod runs with your permissions and no sandbox. Install it only if you trust this marketplace; the Mod line above lists everything it reaches.

<!--
  hooksRun: one line per hook: `{{hookEvent}}` on `{{toolMatcher}}` runs `{{hookCommand}}`, which does what; then once: "Hooks run on their own, with your access and without a permission prompt." Or "none".
  modRuns: for a mod, the events it hooks, every file it reads, every environment variable, process and network call it uses, and what it never does (writes, network, model calls), then "It runs inside Claude Code with your access and no sandbox." Without a mod, delete the Mod bullet and the Before you install bullet.
  mcpServersRun: each server name, its command or URL and what it is used for; or "none".
  networkDestinations: every destination and the data sent there, or "none".
  filesWritten: paths, including anything under the plugin data directory, or "none".
-->

## 🔄 Updating

```bash
claude plugin update {{name}}@{{marketplaceName}}
```

Then, in an open session:

```text
/reload-plugins
```

<!-- app:start -->
Installed from Claude? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `{{name}}@synced`: update and uninstall it in Claude (**Customize** → **Plugins**).
<!-- app:end -->

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **{{marketplaceName}}** → **Enable auto-update**.

<!-- Update each tool of Prerequisites the way you installed it, with the command in a fenced block, for example `brew upgrade {{homebrewFormula}}`. Delete this comment when the plugin needs no tool beyond Claude Code. -->

## 🗑️ Uninstalling

```bash
claude plugin uninstall {{name}}@{{marketplaceName}}
```

Installed with `--scope project`:

```bash
claude plugin uninstall {{name}}@{{marketplaceName}} --scope project
```

<!-- app:start -->
In Claude: **Customize** → **Plugins** → **{{displayName}}** → its menu → **Remove**.
<!-- app:end -->

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. {{dataLeftBehind}}

<!-- dataLeftBehind: what the data directory holds, or "The plugin keeps nothing in its data directory.", then what stays behind: files in your project and tools you installed for it. -->

## 🧭 Compatibility

**Works in:** {{surfacesText}}

<!-- Copy the rows below from the marketplace's component × surface matrix, one row per component type the plugin ships, and keep them identical to it. -->

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
| 📨 Channels | ⚠️ research preview; you turn a channel on for each session with `--channels`, and the plugin must be on Anthropic's channel allowlist or on your organization's | ➖ not documented for Claude |
| 📡 Monitors | ✅ | ➖ not documented for Claude |
| 🔁 Workflows | ✅ | ➖ not documented for Claude |
| ⚙️ Executables (`bin/`) | ✅ | ❌ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

{{compatibilityNote}}

<!-- compatibilityNote: what differs for this plugin on a surface, such as a skill that needs a program Claude can't run, and for a mod where it runs and draws. Delete it when nothing differs. -->

**Platforms:** macOS and Linux{{windowsClause}}.

<!-- windowsClause: ", and Windows through Git Bash" when every script and tool the plugin runs works there; otherwise delete it. -->

## 🚧 Limitations

- {{limitation}}

<!--
  One limit the user should know per bullet. With no limits, delete this section.
  For a mod, keep these limits: what turns it off (`disableAllHooks` in your settings or managed settings, an organization's `allowManagedModsOnly`, `--safe-mode` and `--bare`); that with managed settings or a Team or Enterprise login the built-in guard `cc-plugin-sec-default` loads ahead of user mods and can refuse the mod or keep a deny it tried to lift; that `allowManagedModsOnly` refuses any mod installed from a GitHub source, even one the organization enables; that the mod can't restyle the permission prompt or change what it shows; and that `/plugin` names the mods the session loaded while only `claude --debug` shows why one was refused.
-->

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/{{name}}:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide]({{troubleshootingUrl}}).

</details>

<!-- Plugin-specific questions, each in its own closed details block with any command in a fenced block. -->

## 🔗 Related

- 📦 [All plugins in {{marketplaceDisplayName}}]({{marketplaceCatalogUrl}})
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- {{relatedLink}}

<!-- relatedLink: sibling plugins that pair well with this one, and the official docs of each component type the plugin ships; for a mod, https://code.claude.com/docs/en/plugins/mods/overview. -->

## 🐞 Found a problem?

[Report a bug](https://github.com/{{owner}}/{{repo}}/issues/new?template=bug_report.yml&plugin={{name}}) •
[Request a feature](https://github.com/{{owner}}/{{repo}}/issues/new?template=feature_request.yml&plugin={{name}}) •
[Ask a question](https://github.com/{{owner}}/{{repo}}/issues/new?template=question.yml&plugin={{name}})

<!-- The template file names and the `plugin` field must match the repository's issue forms. -->

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 🙏 Credits

{{credits}}

<!-- credits: third-party work the plugin builds on, with its license and a link. Without any, delete this section. -->

## 📄 License

[{{license}}](./LICENSE) © {{copyrightHolders}}.{{licenseNotes}} Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.

<!-- licenseNotes: when the plugin derives from third-party material, " Parts are derived from {{sourceWork}} ({{sourceLicense}}); see [NOTICE.txt](./NOTICE.txt)."; when it names another third-party product, " Not affiliated with or endorsed by {{trademarkOwner}}. _{{productName}}_ is a trademark of {{trademarkOwner}}."; otherwise delete it. -->
