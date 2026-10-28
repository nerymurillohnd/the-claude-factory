<div align="center">

# 🧩 Mods Engineering

<p><strong>Designs, builds, reviews, tests and debugs Claude Code mods, checking every interface against the current mod docs and the type declarations your own Claude Code build writes.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fmods-engineering%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Development-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.292-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Prerequisites](#-prerequisites) •
[Install](#-installation) •
[Usage](#-usage) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

> [!TIP]
> **TL;DR** — Ask Claude to build, review or fix a mod, and it works from the exact events, mods API methods and elements your Claude Code version supports, then proves the result with `claude plugin validate` and `claude plugin test`.

## ✨ Why use it

- **No invented APIs** — Claude checks each event, `$` method and element against the declarations your build writes into `.claude-plugin/types/` and the official mod pages, and labels anything it could not verify.
- **The right mechanism first** — before writing code, Claude checks whether a mod is the right tool, or whether a skill, a settings hook or an MCP server fits better, and explains the trade-off.
- **Mods that pass the engine's reader** — literal event names, explicit `$.namespace.method(...)` calls and no aliased namespaces, so `claude plugin validate` detects every hook and call you meant.
- **Tests that match the risk** — pass-through, rewrites, refusals, timers, drawings, reset, interruption and policy composition, with mocked tests reported apart from live runs.
- **Faster debugging** — Claude starts from the troubleshooting section that matches your symptom and keeps the exact diagnostic text instead of guessing.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `mods-engineering:cc-mods-guidance` | An engineering workflow for mods: scope, evidence, the right official page for each question, design, implementation within the engine's static-analysis rules, validation, tests, debugging and sharing | `/mods-engineering:cc-mods-guidance` or automatically when you work on a mod |

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | 2.1.292 | `claude --version` |

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

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install mods-engineering@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install mods-engineering --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install mods-engineering@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install mods-engineering@the-claude-factory
```

### 🖥️ Claude app (web and desktop)

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Mods Engineering** in **Discover** and select **Add**.

## 🚀 Usage

The skill loads on its own when you work on a mod. Call it by name to be sure it applies.

### Example: build a mod

```text
/mods-engineering:cc-mods-guidance Build a mod that shows the current Git branch in a band above the prompt
```

**Result:** Claude checks your Claude Code version and the generated declarations, records the outcome, events and failure behavior it will use, writes `.claude-plugin/plugin.json`, `hooks/hooks.json` and the hooks module, adds focused tests, then runs `claude plugin validate` and `claude plugin test` and reports their output.

### Example: review a mod before you share it

```text
Review the mod in ./my-mod before I publish it
```

**Result:** a report of the events and calls the validator detects, the file, process, network and model access the mod has, gaps in its tests, and any claim its README makes that the evidence does not support.

### Example: find out why a mod does nothing

```text
My mod installed fine but nothing shows up. Find out why.
```

**Result:** Claude checks whether mods can load, validates the source folder, reads the troubleshooting section that matches the symptom and the debug log, tests one hypothesis at a time and adds a regression test once the cause is confirmed.

### Example: choose the mechanism

```text
Should blocking `rm -rf` outside the project be a mod or a settings hook?
```

**Result:** a recommendation with the trade-off, drawn from the official comparison of mods, settings hooks, skills and MCP servers.

## 🔍 What this plugin runs and sends

- **Hooks:** none.
- **Commands:** to validate and test a mod, Claude runs the `claude` CLI (`claude plugin validate`, `claude plugin test`).
- **MCP servers:** none.
- **Network:** none of its own. The skill tells Claude to read the official mod pages on `code.claude.com`, which it does with your session's web fetch tool when that tool is available.
- **Files written:** none of its own.

## 🔄 Updating

```bash
claude plugin update mods-engineering@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `mods-engineering@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall mods-engineering@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall mods-engineering@the-claude-factory --scope project
```

In the Claude app: **Customize** → **Plugins** → **Mods Engineering** → its menu → **Remove**.

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps no data and writes no files of its own; the mods Claude built with it stay where they are.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

> [!IMPORTANT]
> Mods run in Claude Code, v2.1.287 or later. In the Claude app the skill helps you design, explain and review a mod, but loading, validating and testing one needs the `claude` CLI, so do those steps in Claude Code.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/mods-engineering:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>How is this different from Claude Code's built-in <code>plugin-authoring</code> skill?</b></summary>

The built-in skill makes a mod for you. This plugin adds the engineering around it: choosing the mechanism, verifying every interface against your build, the static-analysis rules, the tests a change needs, debugging by symptom, policy and sharing. When the built-in skill is available, this skill tells Claude to consult it too.

</details>

<details>
<summary><b>Will Claude load or install a mod without asking?</b></summary>

No. Loading a mod runs its code, so the skill asks for your approval before it loads a mod it has not reviewed, and it never installs, enables or publishes a mod, or changes a security policy, without your authorization.

</details>

<details>
<summary><b>Why does Claude trust my build's declarations over the docs?</b></summary>

Events and methods change between releases. The declarations Claude Code writes into `.claude-plugin/types/` when you load a mod from `--plugin-dir` in an interactive session, or when Claude writes the mod for you, describe the exact version you run, and the official docs say to trust them over any page when the two disagree. Without them, Claude follows the documented steps to generate them and labels what it could not verify.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code mods docs](https://code.claude.com/docs/en/plugins/mods/overview)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=mods-engineering) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=mods-engineering) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=mods-engineering)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
