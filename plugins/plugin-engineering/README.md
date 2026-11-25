<div align="center">

# 🔧 Plugin Engineering

<p><strong>Builds and maintains a public Claude Code plugin marketplace on GitHub from the official docs, distilled for plugins that third parties install: marketplaces, manifests, skills, agents, hooks, mods, MCP servers, settings, validation and releases, checked against the latest release notes. Includes the complete plugin CLI reference: every claude plugin and claude plugin marketplace subcommand, /plugin form and session flag, with exact flags, messages, JSON fields, exit codes and minimum versions. Tests plugins and runs their evals with CI gates, troubleshoots and debugs why one won't install, load or run, and ships a PostToolUse hook that runs claude plugin validate --strict, and a mod's tests, on a plugin after Claude edits or writes a file in it.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fplugin-engineering%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude-2563EB)](#-compatibility)
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
> **TL;DR** — Ask Claude to design, build, fix or release a plugin for your public GitHub marketplace, and it works from the official docs instead of memory, checks what changed in newer Claude Code releases, and validates the result. Ask it to install, update, validate, tag or remove a plugin or marketplace, and it runs the right command with the right flags and reads the exact message and exit code. Ask it why a plugin won't load, or to test one before you publish it, and it finds the documented cause and checks the fix. Every time Claude edits a file inside a plugin, the plugin's hook validates that plugin and hands Claude anything to fix.

Plugin Engineering gives Claude the official documentation for running a public Claude Code plugin marketplace on GitHub, distilled for plugins that other people install. It covers marketplaces, manifests, skills, agents, hooks, mods, MCP servers, settings, validation and releases, plus the complete plugin CLI reference. Claude works from these pages instead of memory and checks newer Claude Code release notes before it relies on a version-sensitive fact.

## ✨ Why use it

- **Built from the official docs, not from memory** — the Claude Code, plugin, platform and Help Center pages on marketplaces, manifests, skills, agents, hooks, mods, MCP servers, settings and releases, kept to what a public marketplace and the people who install its plugins need, so Claude follows the documented behavior.
- **Checked against new releases** — before it relies on a version-sensitive fact, Claude reads the Claude Code release notes published after the references were checked and the live page, and tells you what differs.
- **Validated after every edit** — a hook runs `claude plugin validate --strict` on the plugin each time Claude edits or writes a file inside it, and Claude fixes what the validator reports before it goes on.
- **No more guessing flags** — every `claude plugin` and `claude plugin marketplace` subcommand, every `/plugin` form, `/reload-plugins`, `--plugin-dir` and `--plugin-url`, with their flags, defaults and aliases, is at hand in every session.
- **Scripts that read results correctly** — exact output and error messages, `--json` fields and exit codes, so a CI job or setup script acts on what the command really reported.
- **Fewer destructive surprises** — Claude knows that removing a marketplace uninstalls its plugins, that uninstalling deletes saved data, and that `/plugin install` with a path installs nothing, and it warns you before it acts.
- **Debugging that finds the cause** — when a plugin won't install, load or run, Claude places the failure at its loading stage, matches the exact message to its documented cause, and checks every place the same cause reaches before it fixes anything.
- **Tested the way users receive it** — Claude checks what the validator never reads, loads the plugin from its folder, installs it from a git-hosted source into a throwaway configuration, and reviews it against Anthropic's directory and policy rules before you publish.
- **Evals that mean something** — when you want evals, Claude proposes and writes the cases with `claude plugin eval init`, tells you the cost before any run, compares the plugin against no plugin, and gates a CI job on whether the plugin still helps.
- **Version-aware** — each version-gated flag carries its minimum Claude Code version, and Claude checks `--help` on your version before relying on one.

## 🧩 What's inside

| Component | Name                                        | What it does                                                                                                                                                                                                                                                                                                                  | How it runs                                                                                                                                                      |
| :-------- | :------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🎯 Skill  | `plugin-engineering:public-marketplace-dev` | The official docs for building and maintaining plugins in a public GitHub marketplace: 65 references, with the official images and example manifests, and a procedure for checking facts against the latest release notes                                                                                                     | Only when you run `/plugin-engineering:public-marketplace-dev`                                                                                                   |
| 🎯 Skill  | `plugin-engineering:test-and-evals`         | Tests a plugin with the checks that cost nothing (strict validation, what the validator never reads, loading from the folder, every component, mod tests, an install the way users receive it, the directory and policy review), then builds and runs `claude plugin eval` suites and their CI gate once you approve the cost | Automatically right after you create a plugin and after every change to one, before you publish, when you ask for evals, or `/plugin-engineering:test-and-evals` |
| 🎯 Skill  | `plugin-engineering:troubleshoot-and-debug` | Diagnoses a plugin or marketplace that won't add, install, load or run: every documented message by the stage that produces it, the loading rules, components that load but misbehave, and what loads in cloud sessions, Claude, Cowork and the Agent SDK                                                                     | Automatically when a plugin fails or a change did nothing, or `/plugin-engineering:troubleshoot-and-debug`                                                       |
| 🎯 Skill  | `plugin-engineering:cli-commands-guide`     | The complete Claude Code plugin CLI reference: plugin commands, marketplace commands, `/plugin` and `/reload-plugins`, and the session-only flags                                                                                                                                                                             | Automatically when you work with plugins or marketplaces, or `/plugin-engineering:cli-commands-guide`                                                            |
| 🪝 Hook   | `PostToolUse` on `Edit` and `Write`         | Runs `claude plugin validate --strict` on the plugin that holds the edited file, or on the marketplace when the file is in its `.claude-plugin/` folder; when the file is code in a plugin with mod tests, also runs `claude plugin test`; shows Claude every error, warning and failed test, in full                         | Automatically after each edit or write; silent for files outside a plugin and when validation passes                                                             |

## 📋 Prerequisites

| Tool                                                      | Minimum version | Check              |
| :-------------------------------------------------------- | :-------------- | :----------------- |
| Claude Code                                               | 2.1.295         | `claude --version` |
| curl                                                      | any             | `curl --version`   |
| Bash (for the validation hook)                            | 3.2             | `bash --version`   |
| awk (for the validation hook)                             | any POSIX awk   | `awk -W version`   |
| find (for the validation hook)                            | any POSIX find  | `command -v find`  |
| git (optional; if installed, eval runs need this version) | 2.31            | `git --version`    |
| bubblewrap (Linux, for eval suites that grant Bash)       | —               | `bwrap --version`  |
| socat (Linux, for eval suites that grant Bash)            | —               | `socat -V`         |
| Claude Code docs MCP server (recommended)                 | —               | `claude mcp list`  |

The plugin also has Claude use `mktemp`, `awk`, `grep` and `rm` to read a range of Claude Code releases. Bash and `awk` come with macOS and Linux; the validation hook needs them, and the `claude` binary that runs your session, which it finds on its own.

git matters only when you run `claude plugin eval`: with a git older than 2.31 on your `PATH`, the command stops before running any case; without git, it runs normally. Eval suites that grant Bash run every command in Claude Code's OS sandbox: macOS has it built in, and Linux needs `bubblewrap` and `socat`. The docs server is Anthropic's official docs MCP server: the skills carry dated copies of the official pages and send Claude to the live page when a copy is missing a section or may be outdated, and the server lets Claude search and read that page instead of recalling it. You add it once; the plugin doesn't install it.

### 🤖 Claude Code

Already installed? Bring it to the latest version the way you installed it, as the official [Update Claude Code](https://code.claude.com/docs/en/setup#update-claude-code) guide shows for each installation method. New to Claude Code? Follow the [official setup](https://code.claude.com/docs/en/setup).

### 🌐 curl

macOS and most Linux distributions include curl.

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install curl
```

</details>
<details>
<summary>📦 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt install curl
```

</details>
<details>
<summary>📦 <b>dnf</b> — Fedora, RHEL</summary>

```bash
sudo dnf install curl
```

</details>

```bash
curl --version
```

### 🌿 git

<details>
<summary>🍏 <b>Xcode Command Line Tools</b> — macOS</summary>

```bash
xcode-select --install
```

</details>
<details>
<summary>🍺 <b>Homebrew</b> — macOS</summary>

```bash
brew install git
```

</details>
<details>
<summary>🚢 <b>MacPorts</b> — macOS</summary>

```bash
sudo port install git
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt-get install git
```

</details>
<details>
<summary>🐧 <b>Git PPA (latest stable)</b> — Ubuntu</summary>

```bash
sudo add-apt-repository ppa:git-core/ppa
sudo apt update
sudo apt install git
```

</details>
<details>
<summary>🎩 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install git
```

</details>
<details>
<summary>🏔️ <b>pacman</b> — Arch Linux</summary>

```bash
sudo pacman -S git
```

</details>
<details>
<summary>🦎 <b>zypper</b> — openSUSE</summary>

```bash
sudo zypper install git
```

</details>

```bash
git --version
```

### 📦 bubblewrap and socat

Needed on Linux only, and only for eval suites that grant Bash.

<details>
<summary>🐧 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt-get install bubblewrap socat
```

</details>
<details>
<summary>🎩 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install bubblewrap socat
```

</details>

### 📖 Claude Code docs server

Run this once in your terminal, not inside a session. `--scope user` makes it available in every project:

<details>
<summary>💻 <b>Claude Code</b> — any platform</summary>

```bash
claude mcp add --transport http --scope user claude-code-docs https://code.claude.com/docs/mcp
```

</details>

Check it; `claude-code-docs` should show `✔ Connected`. It needs no sign-in and no credentials.

```bash
claude mcp list
```

Use the name `claude-code-docs`, the one the [official MCP quickstart](https://code.claude.com/docs/en/mcp-quickstart) uses. Without the server, Claude reads the live pages with its own web tools instead.

In Claude, add it as a custom connector instead:

1. On a Pro or Max plan: **Customize** → **Connectors** → **+ Add** → **Add custom connector**.
2. Enter a name such as `Claude Code Docs` and the URL `https://code.claude.com/docs/mcp`, select **Continue**, check the detected settings and select **Continue** again.
3. Choose **No sign in** under **Authentication**, then select **Add**.

On a Team or Enterprise plan, an Owner adds it under **Organization settings** → **Connectors** → **Add** → **Custom** → **Web**, and you select **Connect** on it in **Customize** → **Connectors**. A Free plan allows one custom connector. Source: [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

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

### 🖥️ Claude (web and desktop)

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Plugin Engineering** in **Discover** and select **Add**.

## 🚀 Usage

Claude loads `cli-commands-guide`, `test-and-evals` and `troubleshoot-and-debug` on its own when a task involves plugins or marketplaces. `public-marketplace-dev` runs only when you call it, so Claude never loads it unasked. To load a skill yourself:

```text
/plugin-engineering:public-marketplace-dev
/plugin-engineering:cli-commands-guide
/plugin-engineering:test-and-evals
/plugin-engineering:troubleshoot-and-debug
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

### Fix a plugin that breaks only after you install it

```text
My formatter plugin works with --plugin-dir, but after I install it from our marketplace every edit shows a PostToolUse hook error.
```

**Result:** Claude reads `claude plugin list --json` and the plugin's details, places the failure in the installed copy, explains that an installed plugin is copied without the files outside its folder, and gives you the fix and the check that shows it worked.

### Gate a CI job on plugin evals

```text
Our eval job passes even when the plugin stopped helping. Make it fail then.
```

**Result:** Claude runs the suite with both arms, reads the mean delta (`aggregates.meanDelta`) from the JSON result, and sets the job to fail below the minimum you choose, and on a partial run.

## 🔍 What this plugin runs and sends

- **Hooks:** one `PostToolUse` hook on `Edit` and `Write`. When the edited file sits inside a plugin (a folder with `.claude-plugin/plugin.json`), or in a marketplace's `.claude-plugin/` folder, it runs `claude plugin validate --strict` on that folder with the `claude` binary of your session, and `claude plugin test` when the file is code in a plugin with mod tests; for every other file it exits without doing anything. It reads only the edited file's path and the plugin's file names, writes nothing, and makes no network call. When validation fails, Claude sees the validator's report; when the hook can't find a `claude` binary, Claude sees that instead.
- **MCP servers:** none.
- **Network:** none from the plugin itself. When Claude checks whether something changed in a newer Claude Code release, the skill tells it to download the public Claude Code changelog (`raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md`) with `curl` to a temporary file, read only the releases it needs, and delete the file; or to read the live Claude Code docs (`code.claude.com`) and release notes with Claude's own web tools, or through the Claude Code docs server when you added it. Nothing about you is sent there.
- **Commands run:** the hook's `claude plugin validate --strict`, which reads files only, and the `claude plugin` commands your task needs, through Claude's Bash tool and its usual permission prompts. The skill tells Claude to confirm before a command that deletes data, such as `claude plugin marketplace remove` or `claude plugin uninstall`.
- **Evals:** `claude plugin eval` makes real model calls on your account, billed to your plan or API usage. The skill tells Claude to agree the scope and the cost with you before the first run.
- **Files written:** none by the plugin itself. Claude creates or changes plugin and marketplace files only when your task asks for it, through its usual edit permission prompts.
- **Privacy:** the author collects no data. The marketplace's [privacy policy](https://github.com/nerymurillohnd/the-claude-factory/blob/main/PRIVACY.md) covers this plugin and the outside services it can reach.

## 🔄 Updating

```bash
claude plugin update plugin-engineering@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

Installed from Claude? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `plugin-engineering@synced`: update and uninstall it in Claude (**Customize** → **Plugins**).

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update curl the way you installed it, for example with Homebrew:

```bash
brew upgrade curl
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall plugin-engineering@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall plugin-engineering@the-claude-factory --scope project
```

In Claude: **Customize** → **Plugins** → **Plugin Engineering** → its menu → **Remove**.

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps nothing in its data directory and writes no files of its own, so nothing is left behind.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude

| Component | Claude Code | Claude |
| :-------- | :---------: | :----: |
| 🎯 Skills |     ✅      |   ✅   |
| 🪝 Hooks  |     ✅      |   ⚠️   |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

**Platforms:** macOS and Linux.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/plugin-engineering:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>My Claude Code version is older or newer than the one the references describe.</b></summary>

Each version-gated flag lists its minimum version. Claude checks `claude plugin <subcommand> --help` on your machine and the live docs before relying on one, and tells you when your version behaves differently.

</details>

<details>
<summary><b>I use Claude. Can Claude run these commands there?</b></summary>

Plugins you add in Claude live on your claude.ai account and are managed in **Customize** → **Plugins**. `claude plugin` commands change the machine Claude Code runs on, so the skill gives you the exact command or **Customize** path when the current shell isn't the installation you want to change.

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

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
