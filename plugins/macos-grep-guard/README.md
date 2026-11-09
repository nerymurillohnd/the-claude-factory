<div align="center">

# 🔎 macOS Grep Guard

<p><strong>Stops recursive grep from silently skipping gitignored and binary files on macOS, blocks BSD awk's ignored IGNORECASE, and adds the macOS form when a BSD or zsh command fails.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fmacos-grep-guard%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
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

💻 **Claude Code only** — it ships a mod, which runs inside Claude Code. Claude can install it, but the mod doesn't run there. It acts only on macOS and does nothing on Linux or Windows.

> [!TIP]
> **TL;DR** — On a Mac, a recursive `grep` never returns a quietly incomplete answer: Claude states in the command whether gitignored and binary files count, and BSD or zsh errors come back with the macOS fix.

On macOS, the `grep` in Claude's shell skips gitignored and binary files during a recursive search, BSD `awk` ignores `IGNORECASE`, and many GNU-style commands fail with errors Claude doesn't expect. macOS Grep Guard is a Claude Code mod that reviews every Bash call: it stops a search that would quietly miss files until the command says which files count, stops an `awk` program that relies on `IGNORECASE`, and adds the macOS form next to a known BSD or zsh error. Claude's answers stay complete, and its retries land on the first try.

## ✨ Why use it

- **Complete searches** — in Claude's shell on macOS, `grep` is ugrep with `--ignore-files` and `-I`, so a recursive search skips gitignored and binary files and an empty result looks like proof that something does not exist. The guard stops the command until it says which files it covers.
- **No silent awk mismatch** — macOS awk is BSD awk and ignores `IGNORECASE`. The guard stops the program and suggests `tolower($0) ~ /pattern/`.
- **Fixes in the same turn** — when a command fails with a known BSD or zsh error (`uniq -w`, `stat -c`, GNU-style `sed -i`, `timeout`, an unmatched glob), Claude reads the macOS form next to the error and retries.

## 🧩 What's inside

| Component | Name                                  | What it does                                                                                                                                     | How it runs                                                       |
| :-------- | :------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------- |
| 🧩 Mod    | [`hooks/register.ts`](hooks/register.ts) | Stops a recursive `grep` that would skip files and an `awk` program that relies on `IGNORECASE`; adds the macOS form after a BSD or zsh error | Automatically on every Bash call, in the main session and in subagents |

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | 2.1.292 | `claude --version` |
| macOS, Apple Silicon or Intel | 13.0 | `sw_vers -productVersion` |
| git, to list the gitignored files under a search folder | — | `git --version` |

The plugin also uses `uname`, `awk` and `find`, which come with macOS and Linux. On any system other than macOS the guard does nothing.

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

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install macos-grep-guard@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install macos-grep-guard --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install macos-grep-guard@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install macos-grep-guard@the-claude-factory
```

## 🚀 Usage

There is nothing to invoke: the guard reviews every Bash call. Ask Claude to search as usual.

### Search a repository

```text
Find every place that reads API_KEY in this repository.
```

**Result:** if Claude runs a recursive `grep` without both choices written in the command, and gitignored files would be skipped or the binary choice is missing, the command is stopped and Claude reads which flags to add. It retries with `--no-ignore-files --binary-files=binary`, or with `--ignore-files` and `-I` when skipping `node_modules` or binaries is the intent. The retry keeps the start of the command unchanged, so permission rules such as `Bash(grep -r:*)` still match it.

### Recover from a BSD command

```text
Show the first 4 characters of each line of names.txt, deduplicated with uniq -w4.
```

**Result:** macOS `uniq` has no `-w`. When the command fails, Claude reads the awk form that compares the first N characters, and retries.

## 🔍 What this plugin runs and sends

- **Hooks:** none; the plugin has no command hooks, only the mod below.
- **Mod:** one `tool.call` hook on `Bash`, [`hooks/register.ts`](hooks/register.ts), with its rules in [`hooks/rules.ts`](hooks/rules.ts). What turns it off and how organizations affect it are under [Limitations](#-limitations).
  - **Reads:** the Bash command and its result, which Claude Code passes to the mod. For a recursive `grep` without explicit choices, the names of files and folders under the search folder (to find `.gitignore` files and nested `.git` folders) and, through `git`, the `.gitignore` files and the repository index there. No file contents.
  - **Processes it starts**, each without a shell and each stopped after 5 seconds: `uname -s` on the first Bash call, and again on each later call while `uname` can't start; `awk` once, the first time a command uses `IGNORECASE`, to check whether it works; and, for a recursive `grep` without explicit choices, `/usr/bin/find <folder> -name .gitignore -print -quit`. When that finds a `.gitignore`, it runs `git -C <folder> rev-parse --is-inside-work-tree`, and inside a work tree `/usr/bin/find <folder> -mindepth 2 -name .git -print -quit`, then `git -C <folder> ls-files --others --ignored --exclude-per-directory=.gitignore --directory -- .` and `git -C <folder> ls-files --cached --ignored --exclude-per-directory=.gitignore -- .`. Every `git` call runs with `-c core.fsmonitor=false`, so a program that a cloned repository names in its own config never runs.
  - **Never does:** rewrite a command, write a file, call a model or reach the network.
  - It runs inside Claude Code with your access and no sandbox.
- **MCP servers:** none.
- **Network:** none.
- **Files written:** none.
- **Privacy:** the author collects no data. The marketplace's [privacy policy](https://github.com/nerymurillohnd/the-claude-factory/blob/main/PRIVACY.md) covers this plugin and the outside services it can reach.
- **Before you install:** a mod runs with your permissions and no sandbox. Install it only if you trust this marketplace; the Mod line above lists everything it reaches.

## 🔄 Updating

```bash
claude plugin update macos-grep-guard@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update `git` the way you installed it, for example with Homebrew:

```bash
brew upgrade git
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall macos-grep-guard@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall macos-grep-guard@the-claude-factory --scope project
```

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The plugin keeps nothing in its data directory. It writes no files, so nothing is left in your projects; `git` stays installed.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude |
| :-- | :--: | :--: |
| 🧩 Mods | ✅ v2.1.287+ (Desktop v2.1.286+); hooks run in every session except Desktop on WSL; ⚠️ drawing depends on where: panes in the terminal, Desktop and VS Code (extension v2.1.299+, v2.1.304+ without feature flags), the band above the prompt only in the terminal and Desktop | ⚠️ the plugin directory lists a mod for Claude Code only |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

The guard needs Claude Code 2.1.292 or later and draws nothing. It acts in every Claude Code session on macOS, in the terminal and in the Desktop app, except a Desktop session on WSL. On Linux and Windows it checks `uname` on the first Bash call and does nothing; where `uname` can't start, it checks again on each Bash call and still does nothing.

**Platforms:** macOS and Linux.

## 🚧 Limitations

- **What turns it off:** `disableAllHooks` in your settings or managed settings, and an organization's `allowManagedModsOnly`, which refuses any mod installed from a GitHub source, even one the organization enables. `--safe-mode` and `--bare` start Claude Code without the plugin's mod.
- **Organizations:** with managed settings or a Team or Enterprise login, Claude Code's built-in guard `cc-plugin-sec-default` loads ahead of user mods and can refuse the mod or keep a deny the mod tried to lift.
- **The permission prompt:** the mod cannot restyle it or change what it shows. It only allows a command or stops it with a message for Claude.
- **Diagnosis:** `/plugin` shows `1 mod active · macos-grep-guard` under the tabs when the mod loaded. Only Claude Code's debug log shows why a mod was refused or a hook skipped (see [FAQ](#-faq--troubleshooting)).

| Limitation | What you see | Safe recovery |
| :--------- | :----------- | :------------ |
| Every recursive `grep` without a binary choice is stopped, whether or not the folder holds a binary file: no cheap check tells | Claude retries with the flags | None needed: the retry costs one step and never returns incomplete data |
| A search started below a `.gitignore` that also has patterns in a parent folder can be stopped when nothing would be skipped | Same as above | Same as above |
| A search folder that holds a nested repository or submodule is stopped whenever it has a `.gitignore` | Same as above | Same as above |
| In a subagent, a recursive `grep` on a relative path is stopped, because a subagent's Bash folder does not follow the session's | Claude retries with the flags or an absolute path | Same as above |
| A command run in the background returns no error output | No hint after a background command fails | Read the background task's output |
| Calls to the Grep and Glob tools, `Monitor` commands, and `length()` on accented text are not checked | Nothing from this plugin | Use Bash for searches; use perl for multibyte text |
| The mods API can change between Claude Code releases | The guard may stop working after an update; a failed hook lets the command run, except a recursive `grep`, which is stopped | Update the plugin, as below |

```bash
claude plugin update macos-grep-guard@the-claude-factory
```

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The guard doesn't seem to run after installing.</b></summary>

The plugin has no skills or commands, so nothing appears when you type `/macos-grep-guard:`. Run `/reload-plugins`, then open `/plugin`: `1 mod active · macos-grep-guard` under the tabs means the mod loaded. If it's missing, open `/plugin` → **Errors**, then start Claude Code in debug mode to see why the mod was refused:

```bash
claude --debug
```

See also the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Does installing this plugin modify my project?</b></summary>

No. The plugin writes no files. It only allows or stops Bash commands and adds text for Claude after a failed command.

</details>

<details>
<summary><b>Why not add the flags automatically?</b></summary>

Claude Code checks permission rules against the command a hook passes on, so a rewritten command could stop matching rules you set, such as `Bash(grep -r:*)`. The guard leaves the command as Claude wrote it and asks for the flags at the end, where they keep the prefix intact.

</details>

<details>
<summary><b>I want to skip node_modules. Will the guard keep stopping me?</b></summary>

No. Append `--ignore-files` (and `-I` to skip binaries) and the command runs. The guard only requires that the choice is written in the command.

</details>

<details>
<summary><b>What happens if the guard itself fails?</b></summary>

A probe that cannot start, times out or is refused stops a recursive `grep`, because its result could be incomplete. Any other command runs as usual. If the guard cannot tell whether it runs on macOS, it stays out of the way.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Claude Code mods](https://code.claude.com/docs/en/plugins/mods/overview)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=macos-grep-guard) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=macos-grep-guard) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=macos-grep-guard)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. The approach to its shell parsing is credited in [NOTICE.txt](./NOTICE.txt). Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
