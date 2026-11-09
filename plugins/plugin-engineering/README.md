<div align="center">

# 🔧 Plugin Engineering

<p><strong>Builds and maintains a public Claude Code plugin marketplace on GitHub from the official docs, distilled for plugins that third parties install: marketplaces, manifests, skills, agents, hooks, mods, MCP servers, settings, validation and releases, checked against the latest release notes. Includes the complete plugin CLI reference: every claude plugin and claude plugin marketplace subcommand, /plugin form and session flag, with exact flags, messages, JSON fields, exit codes and minimum versions.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fplugin-engineering%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Development-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.295-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — Ask Claude to design, build, fix or release a plugin for your public GitHub marketplace, and it works from the official docs instead of memory, checks what changed in newer Claude Code releases, and validates the result. Ask it to install, update, validate, tag or remove a plugin or marketplace, and it runs the right command with the right flags and reads the exact message and exit code.

## ✨ Why use it

- **Built from the official docs, not from memory** — the Claude Code, plugin, platform and Help Center pages on marketplaces, manifests, skills, agents, hooks, mods, MCP servers, settings and releases, kept to what a public marketplace and the people who install its plugins need, so Claude follows the documented behavior.
- **Checked against new releases** — before it relies on a version-sensitive fact, Claude reads the Claude Code release notes published after the references were checked and the live page, and tells you what differs.
- **Validated before you publish** — after Claude changes plugin or marketplace files, it runs `claude plugin validate --strict` and fixes what the validator reports.
- **No more guessing flags** — every `claude plugin` and `claude plugin marketplace` subcommand, every `/plugin` form, `/reload-plugins`, `--plugin-dir` and `--plugin-url`, with their flags, defaults and aliases, is at hand in every session.
- **Scripts that read results correctly** — exact output and error messages, `--json` fields and exit codes, so a CI job or setup script acts on what the command really reported.
- **Fewer destructive surprises** — Claude knows that removing a marketplace uninstalls its plugins, that uninstalling deletes saved data, and that `/plugin install` with a path installs nothing, and it warns you before it acts.
- **Version-aware** — each version-gated flag carries its minimum Claude Code version, and Claude checks `--help` on your version before relying on one.

## 🧩 What's inside

| Component     | Name                    | What it does        | How it runs                                             |
| :------------ | :---------------------- | :------------------ | :------------------------------------------------------ |
| 🎯 Skill      | `plugin-engineering:public-marketplace-dev` | The official docs for building and maintaining plugins in a public GitHub marketplace: 65 references, with the official images and example manifests, and a procedure for checking facts against the latest release notes | Automatically when you design, build, release or maintain plugins in a public GitHub marketplace, or `/plugin-engineering:public-marketplace-dev` |
| 🎯 Skill      | `plugin-engineering:cli-commands-guide` | The complete Claude Code plugin CLI reference: plugin commands, marketplace commands, `/plugin` and `/reload-plugins`, and the session-only flags | Automatically when you work with plugins or marketplaces, or `/plugin-engineering:cli-commands-guide` |

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | 2.1.295 | `claude --version` |

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
claude plugin install plugin-engineering@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install plugin-engineering --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install plugin-engineering@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install plugin-engineering@the-claude-factory
```

### 🖥️ Claude app (web and desktop)

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Plugin Engineering** in **Discover** and select **Add**.

## 🚀 Usage

You don't need to call the skills: Claude loads them when a task involves plugins or marketplaces. To load one yourself:

```text
/plugin-engineering:public-marketplace-dev
/plugin-engineering:cli-commands-guide
```

### Add a hook to a plugin you publish

```text
Add a PreToolUse hook to my formatter plugin that blocks edits to generated files.
```

**Result:** Claude reads the plugin hook rules and the hooks reference, writes `hooks/hooks.json` with `${CLAUDE_PLUGIN_ROOT}` paths and the script it calls, checks the hook behavior against the Claude Code releases newer than the references, and runs `claude plugin validate --strict` on the plugin and the marketplace.

### Audit a plugin before a release

```text
Audit my plugin against the current docs before I release it.
```

**Result:** Claude compares the plugin's manifest and components with the references and the live pages, reads the release notes since the references were checked, and reports each finding with its source, without changing a file until you decide.

### Install a plugin for the whole team

```text
Install formatter from my-marketplace for everyone who clones this repository.
```

**Result:** Claude runs `claude plugin install` with the plugin's `name@marketplace` and `--scope project`, reads the `Successfully installed plugin` line, and reminds you that each collaborator still runs the install once, because committing the setting doesn't download the plugin.

### Check a plugin before you publish it

```text
Validate my plugin and marketplace strictly and tell me what to fix.
```

**Result:** Claude runs `claude plugin validate <plugin-dir> --strict` and `claude plugin validate . --strict`, explains each error, warning and README advice, and reminds you that a marketplace run doesn't read each plugin's component files.

### Script plugin updates in CI

```text
Write a CI step that updates our plugin and fails only on a real error.
```

**Result:** Claude runs `claude plugin update` with the plugin's `name@marketplace` and `--json`, parses only the last stdout line, checks `outcome` and the exit code, and, for a plugin whose marketplace declares an install command, passes `--accept-command` with the `sha256` a person reviewed instead of a blanket `-y`.

### Find out why a command did nothing

```text
I ran /plugin install ./my-plugin and nothing happened.
```

**Result:** Claude explains that `/plugin install` with a path reports `Marketplace "./my-plugin" not found` and installs nothing, then gives you the commands that add the marketplace and install the plugin, or `claude --plugin-dir ./my-plugin` to try it for one session.

## 🔍 What this plugin runs and sends

- **Hooks:** none.
- **MCP servers:** none.
- **Scripts:** none. The plugin ships only skills and their reference files.
- **Network:** none from the plugin itself. When Claude checks whether something changed in a newer Claude Code release, the skill tells it to download the public Claude Code changelog (`raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md`) with `curl` to a temporary file, read only the releases it needs, and delete the file; or to read the live Claude Code docs (`code.claude.com`) and release notes with Claude's own web tools. Nothing about you is sent there.
- **Commands run:** only the `claude plugin` commands your task needs, such as `claude plugin validate --strict` after Claude changes plugin files, through Claude's Bash tool and its usual permission prompts. The skill tells Claude to confirm before a command that deletes data, such as `claude plugin marketplace remove` or `claude plugin uninstall`.
- **Files written:** none by the plugin itself. Claude creates or changes plugin and marketplace files only when your task asks for it, through its usual edit permission prompts.

## 🔄 Updating

```bash
claude plugin update plugin-engineering@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `plugin-engineering@synced`: update and uninstall it in the app (**Customize** → **Plugins**).

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall plugin-engineering@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall plugin-engineering@the-claude-factory --scope project
```

In the Claude app: **Customize** → **Plugins** → **Plugin Engineering** → its menu → **Remove**.

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps no data and writes no files of its own, so nothing is left behind.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component                              |                         Claude Code                          |                                                                                                                                          Claude app                                                                                                                                           |
| :------------------------------------- | :----------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| 🎯 Skills                              |                              ✅                              |                                                                                                                                              ✅                                                                                                                                               |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/plugin-engineering:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>My Claude Code version is older or newer than the one the references were checked on.</b></summary>

Each version-gated flag lists its minimum version. Claude checks `claude plugin <subcommand> --help` on your machine and the live docs before relying on one, and tells you when your version behaves differently.

</details>

<details>
<summary><b>I use the Claude app. Can Claude run these commands there?</b></summary>

Plugins you add in the Claude app live on your claude.ai account and are managed in **Customize** → **Plugins**. `claude plugin` commands change the machine Claude Code runs on, so the skill gives you the exact command or app path when the current shell isn't the installation you want to change.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Plugin commands reference](https://code.claude.com/docs/en/plugins/cli-reference)
- 📖 [Skills](https://code.claude.com/docs/en/skills)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=plugin-engineering) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=plugin-engineering) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=plugin-engineering)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
