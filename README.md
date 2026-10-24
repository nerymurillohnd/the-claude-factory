<div align="center">

<img src="./docs/assets/banner.svg" alt="The Claude Factory — plugins for Claude Code and the Claude app" width="100%">

<br>

**Production-grade plugins that automate, accelerate and harden the way you work with Claude.**

*Skills · Agents · Hooks · MCP servers · LSP servers · Output styles — packaged, versioned and ready to install.*

<br>

<!-- plugin-count:start -->
[![Plugins](https://img.shields.io/badge/plugins-16-D97757?style=for-the-badge)](#-catalog)
<!-- plugin-count:end -->
[![Validate](https://img.shields.io/github/actions/workflow/status/nerymurillohnd/the-claude-factory/validate.yml?branch=main&label=validate&style=for-the-badge)](https://github.com/nerymurillohnd/the-claude-factory/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E?style=for-the-badge)](./LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugins-D97757?style=for-the-badge&logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/overview)

[**Quick start**](#-quick-start) •
[**Catalog**](#-catalog) •
[**Manage plugins**](#-manage-your-plugins) •
[**Compatibility**](#-where-plugins-work) •
[**Docs**](#-documentation) •
[**Support**](#-support)

</div>

---

## 🏭 What is The Claude Factory?

**The Claude Factory** is a public [plugin marketplace](https://code.claude.com/docs/en/plugins/overview) for **Claude Code** and the **Claude app**. Each plugin solves one real problem end to end — a workflow you repeat, a check you forget, a tool you wish Claude already knew — and installs with a single command.

| | |
| :-- | :-- |
| 🎯 **Focused** | One plugin, one job, done well. No kitchen-sink bundles. |
| 🧪 **Validated** | Every release passes the official `claude plugin validate --strict` plus our own quality gates. |
| 🔖 **Versioned** | Semantic versioning and a changelog for every plugin, so you always know what changed. |
| 📖 **Documented** | Every plugin ships a README with requirements, usage, configuration and compatibility. |
| 🔓 **Open** | MIT-licensed. Read the source of anything before you install it. |

## ⚡ Quick start

> [!IMPORTANT]
> You need **[Claude Code](https://code.claude.com/docs/en/overview)** (terminal, desktop app, VS Code or JetBrains) or the **Claude app** (web, desktop or mobile). Keep Claude Code current — check with `claude --version`.

### 1️⃣ Add the marketplace (once)

<details open>
<summary><b>💻 Terminal</b></summary>

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
```

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
```

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace**.
3. Enter `nerymurillohnd/the-claude-factory` (or `https://github.com/nerymurillohnd/the-claude-factory`).

</details>

### 2️⃣ Install a plugin

Pick one from the [catalog](#-catalog), then:

| Where | Command / action |
| :-- | :-- |
| 💻 Terminal | `claude plugin install <plugin>@the-claude-factory` |
| 💬 Claude Code session | `/plugin install <plugin>@the-claude-factory` — or browse `/plugin` → **Discover** |
| 🖥️ Desktop app | Any of three ways: **+** next to the prompt box → **Add plugins** (or **Plugins** → **Browse plugins**) · **Settings** → **Plugins** → **Discover** · **Customize** in the sidebar → **Plugins** → **Discover** |
| 🧩 VS Code | Type `/plugins` → **Plugins** tab → **Install** |
| 🖥️ Claude app | **Customize** → **Plugins** → **Discover** → select the plugin → **Add** |

> [!TIP]
> **Skip step 1.** Add the marketplace and install in one go:
>
> ```bash
> claude plugin install <plugin> --marketplace nerymurillohnd/the-claude-factory   # Claude Code v2.1.292+
> ```
>
> Inside a session: `/plugin install <plugin> --marketplace nerymurillohnd/the-claude-factory` (v2.1.275+).

### 3️⃣ Use it

Plugin skills are namespaced, so they never collide with yours: type `/<plugin>:` to see what a plugin adds. Run `/reload-plugins` if you installed into an open session.

## 📦 Catalog

<!-- catalog:start -->
| Category | Plugins |
| :-- | :--: |
| [🛠️ Development](#️-development) | 3 |
| [⚡ Productivity](#-productivity) | 1 |
| [🤖 Automation](#-automation) | 1 |
| [🧩 Mods](#-mods) | 2 |
| [🧪 Testing & Quality](#-testing--quality) | 3 |
| [🛡️ Security](#️-security) | 1 |
| [📚 Documentation & Writing](#-documentation--writing) | 1 |
| [🧠 Language Support](#-language-support) | 4 |

### 🛠️ Development

*Write, refactor, review and ship code faster.*

| Plugin | What it does | Works in | Version | Includes |
| :-- | :-- | :-- | :--: | :-- |
| [**GitHub Operations**](./plugins/github-operations#readme)<br>`github-operations@the-claude-factory` | Carries a GitHub pull request from open to merge, cleans up a Git repository without losing work, and brings the GitHub MCP server with it. | 💻 Code only | `0.4.0` | 🎯 Skills · 🤖 Agents · 🔌 MCP |
| [**Mods Engineering**](./plugins/mods-engineering#readme)<br>`mods-engineering@the-claude-factory` | Designs, builds, reviews, tests and debugs Claude Code mods, checking every interface against the current mod docs and the type declarations your own Claude Code build writes. | 💻 Code · 🖥️ Claude app | `0.1.0` | 🎯 Skills |
| [**Svelte Development**](./plugins/svelte-development#readme)<br>`svelte-development@the-claude-factory` | Writes, reviews and migrates Svelte 5 and SvelteKit 3 code by current practice, checking every change against the official Svelte docs and autofixer, the Svelte language server and your project's own check. | 💻 Code · 🖥️ Claude app | `0.1.0` | 🎯 Skills · 🤖 Agents · 🔌 MCP · 🧠 LSP |

### ⚡ Productivity

*Everyday workflows, planning and knowledge work.*

| Plugin | What it does | Works in | Version | Includes |
| :-- | :-- | :-- | :--: | :-- |
| [**Prompt Writer**](./plugins/prompt-writer#readme)<br>`prompt-writer@the-claude-factory` | Turns a goal, idea or draft into one copy-ready prompt tuned to the target Claude model and effort: it clarifies intent, checks current official facts and recommends the setup to run it with. | 💻 Code · 🖥️ Claude app | `0.2.0` | 🎯 Skills |

### 🤖 Automation

*Hooks, agents and pipelines that run work for you.*

| Plugin | What it does | Works in | Version | Includes |
| :-- | :-- | :-- | :--: | :-- |
| [**Hook Engineering**](./plugins/hook-engineering#readme)<br>`hook-engineering@the-claude-factory` | Designs, writes, audits and debugs Claude Code hooks end to end: the event and configuration that decide when a hook runs, the input and output contract that decides what it does, prompt, agent and background hooks, workspace trust and security, and how mods interact with hooks, checked against the current docs and changelog. | 💻 Code · 🖥️ Claude app | `0.2.0` | 🎯 Skills · 🤖 Agents |

### 🧩 Mods

*Panels, bands and status views that change Claude Code's own interface.*

| Plugin | What it does | Works in | Version | Includes |
| :-- | :-- | :-- | :--: | :-- |
| [**Tool Ledger**](./plugins/tool-ledger#readme)<br>`tool-ledger@the-claude-factory` | Lists every tool call of the session in a live panel: what ran, on what, whether Claude or a subagent made it, and whether it finished, failed or was denied. | 💻 Code only | `0.1.0` | 🧩 Mods |
| [**Turn Meter**](./plugins/turn-meter#readme)<br>`turn-meter@the-claude-factory` | Shows how long each turn took, how many tools it used in the main thread and in subagents, and the tokens it spent, in a band above the prompt, and alerts you when a long turn ends. | 💻 Code only | `0.1.0` | 🧩 Mods |

### 🧪 Testing & Quality

*Tests, audits, linting and quality gates.*

| Plugin | What it does | Works in | Version | Includes |
| :-- | :-- | :-- | :--: | :-- |
| [**Plugin Evals**](./plugins/plugin-evals#readme)<br>`plugin-evals@the-claude-factory` | Makes Claude an expert in Claude Code plugin evals: designs suites that prove what a plugin adds, writes cases, graders and mocks, runs and gates them in CI, and reads the results, always checked against the CLI and docs you have today. | 💻 Code · 🖥️ Claude app | `0.1.1` | 🎯 Skills |
| [**Plugin Test Bench**](./plugins/plugin-test-bench#readme)<br>`plugin-test-bench@the-claude-factory` | Proves your Claude Code plugin works the way your users receive it: installs a copy in a throwaway config, checks it loads, runs your eval suite against that copy, and reviews your eval cases so they measure what the plugin adds. | 💻 Code only | `0.1.0` | 🎯 Skills |
| [**Skill Diagnostics**](./plugins/skill-diagnostics#readme)<br>`skill-diagnostics@the-claude-factory` | Audits Claude skills for best-practice conformance, portability and whether a model can run them without guessing, with file-and-line evidence and one verdict. | 💻 Code · 🖥️ Claude app | `0.1.2` | 🎯 Skills · 🤖 Agents · 🪝 Hooks |

### 🛡️ Security

*Guardrails, secret hygiene and security reviews.*

| Plugin | What it does | Works in | Version | Includes |
| :-- | :-- | :-- | :--: | :-- |
| [**Block No Verify**](./plugins/block-no-verify#readme)<br>`block-no-verify@the-claude-factory` | Blocks Claude's git commands that skip commit hooks or signing (--no-verify, --no-gpg-sign, commit.gpgsign=false), so your quality gates always run. | 💻 Code · 🖥️ Claude app | `0.1.1` | 🪝 Hooks |

### 📚 Documentation & Writing

*Docs, changelogs, records and written content.*

| Plugin | What it does | Works in | Version | Includes |
| :-- | :-- | :-- | :--: | :-- |
| [**Project Maintainer**](./plugins/project-maintainer#readme)<br>`project-maintainer@the-claude-factory` | Keeps a project's memory in its .claude folder: decisions recorded as ADRs, technical debt tracked in a ledger, and a handoff that carries each session's state to the next one. | 💻 Code · 🖥️ Claude app | `0.2.0` | 🎯 Skills · 🪝 Hooks · 🧩 Mods |

### 🧠 Language Support

*LSP servers and code intelligence for specific languages.*

| Plugin | What it does | Works in | Version | Includes |
| :-- | :-- | :-- | :--: | :-- |
| [**Bash LSP Intelligence**](./plugins/bash-lsp-intelligence#readme)<br>`bash-lsp-intelligence@the-claude-factory` | Gives Claude Code bash-language-server for Bash and POSIX shell scripts, formats and checks every script Claude edits with shfmt and ShellCheck using your own configuration, and teaches Claude to trace sourced files and same-named functions before a rename. | 💻 Code only | `0.2.3` | 🎯 Skills · 🪝 Hooks · 🧠 LSP |
| [**Python LSP Intelligence**](./plugins/python-lsp-intelligence#readme)<br>`python-lsp-intelligence@the-claude-factory` | Gives Claude Code the basedpyright language server for Python, checks every Python file Claude edits with ruff and basedpyright using your own configuration, and teaches Claude to navigate by symbol, resolve aliases and imports, and fix findings without suppressing them. | 💻 Code only | `0.2.2` | 🎯 Skills · 🪝 Hooks · 🧠 LSP |
| [**TypeScript 6 LSP Intelligence**](./plugins/typescript6-lsp-intelligence#readme)<br>`typescript6-lsp-intelligence@the-claude-factory` | Connects your TypeScript 6 language server to Claude Code, type-checks every file Claude edits with your own TypeScript under a strictest policy, and teaches Claude to find the program that owns a file and fix compiler findings without unsafe assertions or suppressions. | 💻 Code only | `0.3.0` | 🎯 Skills · 🪝 Hooks · 🧠 LSP |
| [**TypeScript 7 LSP Intelligence**](./plugins/typescript7-lsp-intelligence#readme)<br>`typescript7-lsp-intelligence@the-claude-factory` | Connects the native TypeScript 7 language server to Claude Code, type-checks every file Claude edits with your own native TypeScript 7 compiler under a strictest policy, and teaches Claude to find the program that owns a file and fix compiler findings without unsafe assertions or suppressions. | 💻 Code only | `0.4.0` | 🎯 Skills · 🪝 Hooks · 🧠 LSP |

<sub>**Legend:** 🎯 Skills · ⌨️ Commands · 🤖 Agents · 🪝 Hooks · 🧩 Mods · 🔌 MCP · 🧠 LSP · 🎨 Output styles · 📡 Monitors · 🔁 Workflows · 🌈 Themes · ⚙️ Executables</sub>
<!-- catalog:end -->

## 🔧 Manage your plugins

| Task | 💻 Terminal | 💬 In a session |
| :-- | :-- | :-- |
| **List installed plugins** | `claude plugin list` | `/plugin` → **Installed** |
| **See what a plugin adds** | `claude plugin details <plugin>` | `/plugin` → **Installed** → select it |
| **Update one plugin** | `claude plugin update <plugin>@the-claude-factory` | `/plugin` → **Installed** → **Update now** |
| **Update everything from here** | — | `/plugin` → **Marketplaces** → **the-claude-factory** → **Update marketplace** |
| **Disable / enable** | `claude plugin disable <plugin>@the-claude-factory` | `/plugin` → **Installed** → **Space** |
| **Uninstall** | `claude plugin uninstall <plugin>@the-claude-factory` | `/plugin` → **Installed** → **Uninstall** |
| **Remove the marketplace** | `claude plugin marketplace remove the-claude-factory` | `/plugin marketplace remove the-claude-factory` |

> [!TIP]
> 🔄 **Get updates automatically.** Third-party marketplaces start with auto-update **off**. Turn it on once: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

In the **Claude app**, manage everything from **Customize** → **Plugins**: select **Check for updates** to pull new versions now, or open a plugin, open its menu and select **Remove**. Full details: [Managing plugins](./docs/managing-plugins.md).

> [!WARNING]
> Removing the marketplace **uninstalls every plugin** you installed from it.

## 🧭 Where plugins work

The same plugin installs in Claude Code and in the Claude app, but each loads a different subset of components. Every plugin README has its own **Compatibility** table.

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |
| 🤖 Agents | ✅ | ⚠️ in Cowork sessions |
| 🪝 Hooks | ✅ | ⚠️ in Cowork sessions |
| 🧩 Mods | ✅ except a Desktop session on WSL | ⚠️ listed for Claude Code only |
| 🔌 Remote MCP servers | ✅ | 🔗 connect on the plugin's **Connectors** tab |
| 🖥️ Local MCP servers | ✅ | ⚠️ in Cowork sessions on your computer |
| 🧠 LSP · 🎨 Output styles · 🌈 Themes | ✅ | ➖ |
| ⚙️ Executables in `bin/` | ✅ | ❌ |

<sub>✅ loads · ⚠️ conditional · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can and as a chat conversation otherwise; agents, hooks and local MCP servers don't run in a chat conversation. Sources: [Use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude), [Plugin feature support across platforms](https://claude.com/docs/plugins/platform-support). More in [Compatibility](./docs/compatibility.md).</sub>

## 🛡️ Trust & safety

Plugins can run hooks, scripts and MCP servers on your machine. Before installing **any** plugin — from here or anywhere else:

- 🔍 Read its README and source: everything here is in [`plugins/`](./plugins).
- 🧾 Review what it adds in the install panel (**Will install**) or with `claude plugin details <plugin>`.
- 🔐 Report vulnerabilities privately — see our [Security policy](./SECURITY.md).

## 📚 Documentation

| Guide | What you'll find |
| :-- | :-- |
| 📥 [Installation](./docs/installation.md) | Adding the marketplace and installing plugins on every surface, scopes, private setups |
| 🔧 [Managing plugins](./docs/managing-plugins.md) | Updates, auto-update, disabling, uninstalling, removing the marketplace |
| 🧭 [Compatibility](./docs/compatibility.md) | What loads in Claude Code and the Claude app |
| 🩺 [Troubleshooting](./docs/troubleshooting.md) | Fixes for the most common install and loading errors |
| ❓ [FAQ](./docs/faq.md) | Quick answers about the marketplace, versions and support |
| 📖 [Official plugin docs](https://code.claude.com/docs/en/plugins/overview) | Anthropic's reference for plugins and marketplaces |

## 💬 Support

| I want to… | Go here |
| :-- | :-- |
| 🐞 Report a bug in a plugin | [Open a bug report](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml) |
| ✨ Suggest an improvement | [Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml) |
| 💡 Propose a new plugin | [Share a plugin idea](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=plugin_idea.yml) |
| 📝 Fix the docs | [Report a docs issue](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=docs_issue.yml) |
| ❔ Ask a question | [Ask here](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml) |
| 🔐 Report a vulnerability | [Report privately](https://github.com/nerymurillohnd/the-claude-factory/security/advisories/new) |

> [!NOTE]
> This repository is maintained by its owners and **does not accept pull requests**. Issues are the way to contribute — every report is read and answered. See [Contributing](./CONTRIBUTING.md).

## 📝 Changelog

Marketplace-level changes (plugins added, updated or retired) are in [CHANGELOG.md](./CHANGELOG.md). Each plugin also keeps its own changelog in its folder.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by Anthropic. *Claude* and *Claude Code* are trademarks of Anthropic, PBC.

<div align="center">

<sub>Built with care for the Claude community · <a href="#top">Back to top ⬆️</a></sub>

</div>
