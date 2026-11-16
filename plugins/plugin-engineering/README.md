<div align="center">

# 🔧 Plugin Engineering

<p><strong>Builds and maintains a public Claude Code plugin marketplace on GitHub from the official docs, with the complete plugin CLI reference, plugin testing, debugging and evals, and guided renames, merges, splits, updates and removals that ask before they delete anything.</strong></p>

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
[Configuration](#%EF%B8%8F-configuration) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

> [!TIP]
> **TL;DR** — Ask Claude to build, test, debug, release, rename or remove a Claude Code plugin or marketplace, and it works from the current official docs and the exact plugin commands instead of from memory.

Plugin Engineering gives Claude four skills for the whole life of a plugin that other people install from a public GitHub marketplace. One holds the official docs, pruned to what such a marketplace needs. One holds the complete reference of the `claude plugin` command line. One tests and debugs plugins and their evals. One plans and carries out renames, merges, splits, updates and removals, and asks you before any step that deletes a plugin, its data or a marketplace.

## ✨ Why use it

- **The right command on the first try** — Claude reads every `claude plugin` and `claude plugin marketplace` subcommand, `/plugin` form and session flag, with its exact flags, messages, exit codes and minimum version, so it stops guessing a flag that doesn't exist.
- **Failures traced to a documented cause** — when a plugin won't install, load or run, Claude finds the stage that produced the message, names the cause the docs give, checks every other place that cause reaches, and verifies the fix before it calls it done.
- **Changes that don't strand your users** — a rename, merge or removal gets a plan with an owner and a "done when" check for each stage, and the plugin asks you before an action that deletes data or reaches every user.

## 🧩 What's inside

| Component | Name                                              | What it does                                                                                                                                                                                                                                              | How it runs                                                                       |
| :-------- | :------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------- |
| 🎯 Skill  | `plugin-engineering:public-marketplace-dev`       | Teaches Claude to design, build, version, release and maintain a public GitHub plugin marketplace from the official docs, and to check version-sensitive facts against the latest release notes and run `claude plugin validate --strict` after a change. | `/plugin-engineering:public-marketplace-dev` or automatically when relevant       |
| 🎯 Skill  | `plugin-engineering:cli-commands-guide`           | Gives Claude the complete plugin command reference, with flags, defaults, aliases, messages, JSON fields, exit codes, scopes and minimum versions.                                                                                                        | `/plugin-engineering:cli-commands-guide` or automatically when relevant           |
| 🎯 Skill  | `plugin-engineering:plugin-testing-and-debugging` | Tests, troubleshoots and debugs plugins, reviews them before you publish, and writes, runs and gates plugin evals.                                                                                                                                        | `/plugin-engineering:plugin-testing-and-debugging` or automatically when relevant |
| 🎯 Skill  | `plugin-engineering:migrating-plugins`            | Plans and carries out renames, merges, splits, updates, retirements, delistings and removals of plugins and marketplaces, and writes the notes for the users who have them.                                                                               | `/plugin-engineering:migrating-plugins` or automatically when relevant            |
| 🪝 Hook   | `PreToolUse` on `Bash` and `Edit\|Write`          | Asks you before a plugin removal, a deletion of plugin or marketplace files, or a `marketplace.json` edit that uninstalls plugins for your users.                                                                                                         | Automatically on matching tool calls, once `migrating-plugins` is invoked         |

## 📋 Prerequisites

| Tool                                                | Minimum version | Check                             |
| :-------------------------------------------------- | :-------------- | :-------------------------------- |
| Claude Code                                         | 2.1.295         | `claude --version`                |
| Bash                                                | 3.2             | `bash --version`                  |
| git (optional)                                      | 2.31            | `git --version`                   |
| jq (optional)                                       | —               | `jq --version`                    |
| GitHub CLI, `gh` (optional)                         | —               | `gh --version`                    |
| bubblewrap and socat (optional, Linux)              | —               | `command -v bwrap socat`          |
| Claude Code docs MCP server (optional, recommended) | —               | `claude mcp get claude-code-docs` |

The plugin also uses `awk`, `cat`, `curl`, `grep`, `mktemp`, `printf`, `rm` and `sh`, which come with macOS and most Linux distributions.

The optional tools matter only for the work that uses them. git runs your release tags and the evals (`claude plugin eval` stops before it runs a case when git is older than 2.31). jq reads `plugin.json` and `marketplace.json` in the checks `migrating-plugins` gives. `gh` signs in to a private marketplace. bubblewrap and socat sandbox the eval runs that grant Claude Bash on Linux. The docs server lets Claude search the Claude Code docs.

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
brew upgrade claude-code  # claude-code@latest if you installed that cask
```

</details>
<details>
<summary>📦 <b>npm</b> — any platform</summary>

```bash
npm install -g @anthropic-ai/claude-code@latest
```

</details>

### 🐚 Bash

Bash comes with macOS (version 3.2) and with Linux, and the plugin's hook runs on it. Check it:

```bash
bash --version
```

### 🌿 git

<details>
<summary>🍎 <b>Xcode Command Line Tools</b> — macOS</summary>

```bash
git --version  # offers to install the tools when git is missing
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt install git-all
```

</details>
<details>
<summary>🎩 <b>dnf</b> — Fedora, RHEL</summary>

```bash
sudo dnf install git-all
```

</details>

Then check it:

```bash
git --version
```

### 🔎 jq

<details>
<summary>🍺 <b>Homebrew</b> — macOS</summary>

```bash
brew install jq
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian, Ubuntu</summary>

```bash
sudo apt-get install jq
```

</details>
<details>
<summary>🎩 <b>dnf</b> — Fedora</summary>

```bash
sudo dnf install jq
```

</details>

Then check it:

```bash
jq --version
```

### 🐙 GitHub CLI

<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install gh
```

</details>
<details>
<summary>🐧 <b>apt</b> — Debian, Raspberry Pi, Ubuntu</summary>

```bash
(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
	&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
	&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
	&& sudo mkdir -p -m 755 /etc/apt/sources.list.d \
	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
	&& sudo apt update \
	&& sudo apt install gh -y
```

</details>
<details>
<summary>🎩 <b>dnf5</b> — Fedora, RHEL, CentOS, Amazon Linux</summary>

```bash
sudo dnf install dnf5-plugins
sudo dnf config-manager addrepo --from-repofile=https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh
```

</details>
<details>
<summary>🎩 <b>dnf4</b> — Fedora, RHEL, CentOS, Amazon Linux</summary>

```bash
sudo dnf install 'dnf-command(config-manager)'
sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh
```

</details>

Then check it:

```bash
gh --version
```

### 🧱 bubblewrap and socat

You need them only on Linux, and only for evals whose cases grant Claude Bash. macOS has its own sandbox.

<details>
<summary>🐧 <b>apt</b> — Ubuntu, Debian</summary>

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

Then check them:

```bash
command -v bwrap socat
```

### 📚 Claude Code docs MCP server

The docs server lets Claude search the official Claude Code docs while it works on your plugins. The `migrating-plugins` skill searches it whenever it is in the session. Add it at user scope, so Claude has it in every project on your computer.

<details>
<summary>💻 <b>User scope (recommended)</b> — every project on your computer</summary>

```bash
claude mcp add --scope user --transport http claude-code-docs https://code.claude.com/docs/mcp
```

</details>

<details>
<summary>💻 <b>Project scope</b> — shared with your team through the repository</summary>

Run it at the project's root. It writes the server to `.mcp.json`, which you commit, and each teammate approves the server the first time Claude Code loads it.

```bash
claude mcp add --scope project --transport http claude-code-docs https://code.claude.com/docs/mcp
```

</details>

<details>
<summary>💻 <b>Local scope</b> — only you, only the current project</summary>

Local is the default when you leave out `--scope`.

```bash
claude mcp add --scope local --transport http claude-code-docs https://code.claude.com/docs/mcp
```

</details>

Then check it, and see which scope it was added at:

```bash
claude mcp get claude-code-docs
```

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

The four skills load on their own when your request matches them, and you can call each one by name. The hook needs no command: it acts by itself once `migrating-plugins` is invoked.

### Rename a plugin without breaking its users

```text
/plugin-engineering:migrating-plugins rename my-plugin to my-new-plugin in my GitHub marketplace
```

**Result:** Claude reads your marketplace and manifests, asks where the plugin lives (your machine, a Claude account, an organization, Anthropic's directory), checks whether relabeling with `displayName` would do instead, and plans each stage with its owner and a "done when" check. It stops for your yes before any step that deletes data or reaches every user, then writes the notes for the people who have the plugin.

### Debug a plugin that won't load

```text
/plugin-engineering:plugin-testing-and-debugging my plugin installs but its skills never show up
```

**Result:** Claude reads the state on disk (`claude plugin list --json`, `claude plugin details`, the `/plugin` Errors tab), places the problem at the stage that produced it, names the documented cause, applies the fixes in one pass, and verifies with the output the docs say a working install shows.

### Look up an exact command

```text
/plugin-engineering:cli-commands-guide how do I install a plugin for everyone in my repository, and what does uninstall delete?
```

**Result:** Claude answers from the command reference: the `--scope project` form, the minimum version each flag needs, and that uninstalling from the last scope deletes the plugin's options and data unless you pass `--keep-data`.

### Add a component to your plugin

```text
/plugin-engineering:public-marketplace-dev add a PreToolUse hook to my plugin that blocks edits to .env files
```

**Result:** Claude reads the hooks and manifest references, writes the hook, checks every version-sensitive fact against the release notes, runs `claude plugin validate --strict` on the plugin, and fixes what the validator reports.

## ⚙️ Configuration

This plugin has no options to set. What it does depends on your project, which it reads only when you ask for plugin work:

| What it reads                                                                    | What it does then                                                                                                                                                                    |
| :------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.claude-plugin/marketplace.json` and each plugin's `.claude-plugin/plugin.json` | Learns the marketplace and plugin names, versions and sources. Before a `marketplace.json` edit that sets `forceRemoveDeletedPlugins` or maps a plugin to `null`, the hook asks you. |
| Your README, `CLAUDE.md` and git remotes                                         | Learns how the project is hosted, released and versioned.                                                                                                                            |
| A plugin's `evals/` folder                                                       | Reads and writes eval cases and graders there when you ask for evals.                                                                                                                |
| The command Claude is about to run, when `migrating-plugins` is active           | Asks you before a plugin removal, or an `rm`, `rmdir`, `unlink`, `git rm` or `find -delete` on plugin, marketplace or `~/.claude/plugins/` paths.                                    |

## 🔍 What this plugin runs and sends

- **Hooks:** `migrating-plugins` declares its hooks in its own frontmatter. Claude Code registers them when you invoke that skill and keeps them for the rest of the session. Each entry is a `PreToolUse` hook that runs `bash "${CLAUDE_PLUGIN_ROOT}/skills/migrating-plugins/scripts/ask-before-destructive.sh"` with `onFailure: block`:
  - on `Bash`, when the command matches `claude plugin *`;
  - on `Bash`, when it matches `claude plugins *`;
  - on `Bash`, when it matches `rm *`;
  - on `Bash`, when it matches `rmdir *`;
  - on `Bash`, when it matches `unlink *`;
  - on `Bash`, when it matches `git rm *`;
  - on `Bash`, when it matches `find *`;
  - on `Edit`, when the file matches `**/marketplace.json`;
  - on `Write`, when the file matches `**/marketplace.json`.

  The script reads the hook input from standard input, matches it as text with `grep`, and prints fixed JSON that asks you to confirm. It asks before `claude plugin uninstall`, `remove` or `rm`, `claude plugin marketplace remove`, `claude plugin prune` without `--dry-run`, `claude plugin restore-set-aside --discard`, a deletion on plugin, marketplace or `~/.claude/plugins/` paths, and a `marketplace.json` edit that touches `forceRemoveDeletedPlugins` or sets a value to `null`. It never denies a command on its own, calls no program but `bash`, `cat`, `grep` and `printf`, reads no file, uses no network and writes nothing. If the script itself fails, `onFailure: block` stops that one action. Hooks run on their own, with your access and without a permission prompt.
- **MCP servers:** none.
- **Network:** the plugin ships no program that connects to a network. The skills tell Claude to check the live official docs, so when you ask for plugin work Claude can download pages with `curl`, or read them through WebFetch or the docs MCP server you added, from `code.claude.com`, `claude.com`, `support.claude.com` and the Claude Code changelog on GitHub. Those requests carry only the page address. The plugin commands Claude runs for you contact the marketplace's git host, for example GitHub, as they would if you ran them. `claude plugin eval` makes real model calls on your Claude account, and the skill agrees the scope and cost with you before the first run.
- **Files written:** none by the plugin itself, and nothing under `${CLAUDE_PLUGIN_DATA}`. While Claude reads the docs, it saves pages in a temporary folder from `mktemp -d` and deletes it at the end. Files Claude creates or changes because you asked, such as plugin manifests, `marketplace.json`, eval cases under a plugin's `evals/` folder and release notes, go where you tell it.
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

Update the GitHub CLI the way you installed it:

```bash
brew upgrade gh
```

```bash
sudo apt update
sudo apt install gh
```

```bash
sudo dnf update gh
```

Update git, jq, bubblewrap and socat with the package manager that installed them.

## 🗑️ Uninstalling

```bash
claude plugin uninstall plugin-engineering@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall plugin-engineering@the-claude-factory --scope project
```

In Claude: **Customize** → **Plugins** → **Plugin Engineering** → its menu → **Remove**.

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps nothing in its data directory. Files Claude wrote into your projects while you worked stay where they are, and so do the tools you installed for it (Bash, git, jq, `gh`, bubblewrap, socat). Remove the docs server, if you added it, with this command:

```bash
claude mcp remove claude-code-docs --scope user
```

Use the scope you added it at; without `--scope`, the command removes it from whichever scope holds it.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude

| Component | Claude Code |                       Claude                        |
| :-------- | :---------: | :-------------------------------------------------: |
| 🎯 Skills |     ✅      |                         ✅                          |
| 🪝 Hooks  |     ✅      | ⚠️ only in conversations where Claude can run tasks |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

In Claude, the skills teach Claude the docs and the command reference in every conversation. The `claude` commands they describe run only where Claude can run tasks on a computer that has Claude Code installed. Elsewhere Claude gives you the exact command to run yourself. The hook calls `bash`, `cat`, `grep` and `printf`, so it works only where those exist.

**Platforms:** macOS and Linux.

## 🚧 Limitations

- The hook is a safety net, not the rule: it exists only after `migrating-plugins` is invoked, and `disableAllHooks` in your settings turns it off. Claude still asks you first.
- The hook can't see `/plugin`, Claude, claude.ai or the developer portal, a `marketplace.json` edit made through `Bash`, or a push, so it never asks about those. The skill asks you before them anyway.
- Claude can't run `/plugin` or `/reload-plugins` from the shell. It tells you to run them in the open session, and a running session keeps the version it loaded until you do.
- The bundled docs are pruned copies. They leave out Anthropic's directory submission flow, private repositories and their credentials, hosts other than GitHub, GitHub Enterprise Server, and the `url`, `npm`, `archive` and `command` plugin sources, so for those topics Claude reads the live page.
- `public-marketplace-dev` is for plugins in a public GitHub marketplace. `migrating-plugins` doesn't create a plugin from nothing: it works on an existing one, or on the target of a merge or a split.
- When a bundled page and the live docs or the release notes disagree, Claude follows the live source and tells you which part is out of date.
- Evals run real model calls on your account. A suite that grants Claude Bash on Linux needs bubblewrap and socat, and native Windows has no sandbox backend for it.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/plugin-engineering:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Which skill do I call?</b></summary>

You rarely need to choose. Describe the job and Claude loads the skill that fits: building and releasing (`public-marketplace-dev`), command syntax (`cli-commands-guide`), errors, checks and evals (`plugin-testing-and-debugging`), or renames, updates and removals (`migrating-plugins`). To force one, type its name after `/plugin-engineering:`.

</details>

<details>
<summary><b>Claude asked me to confirm a command I didn't expect.</b></summary>

The `migrating-plugins` hook asks before an action that deletes a plugin, its options, its data or a marketplace. Approve it only when that is what you want, and read the reason it shows. The hook asks and never denies, so declining stops that one action.

</details>

<details>
<summary><b>An action was blocked and I wasn't asked.</b></summary>

When the hook script can't run, `onFailure: block` stops that action. Check that Bash and `grep` are on your `PATH`:

```bash
bash --version
command -v grep
```

</details>

<details>
<summary><b>Does the plugin change anything on its own?</b></summary>

No. The skills only change your plugin or marketplace files when you ask, and `claude plugin eval` spends usage only after you agree the scope and cost.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 🧪 [Plugin Evals](../plugin-evals/README.md) and [Plugin Test Bench](../plugin-test-bench/README.md): deeper work on plugin evals and on testing a plugin before release
- 🪝 [Hook Engineering](../hook-engineering/README.md) and 🧩 [Mods Engineering](../mods-engineering/README.md): hooks and mods for your plugins
- 📖 [Skills docs](https://code.claude.com/docs/en/skills) and [Hooks docs](https://code.claude.com/docs/en/hooks)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=plugin-engineering) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=plugin-engineering) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=plugin-engineering)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 🙏 Credits

The reference files of `public-marketplace-dev` are pruned copies of Anthropic's official documentation: the [Claude Code docs](https://code.claude.com/docs/en/overview), the [Claude plugin docs](https://claude.com/docs/plugins/overview), the [Claude Platform docs](https://platform.claude.com/docs) and the [Claude Help Center](https://support.claude.com). The `cli-commands-guide`, `plugin-testing-and-debugging` and `migrating-plugins` references are written from those same pages and from the `claude` command's own help.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by GitHub, Inc. or Anthropic. _GitHub_ is a trademark of GitHub, Inc.; _Claude_ and _Claude Code_ are trademarks of Anthropic.
