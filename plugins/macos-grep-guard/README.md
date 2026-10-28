<div align="center">

# 🔎 macOS Grep Guard

<p><strong>Stops recursive grep from silently skipping gitignored and binary files on macOS, blocks BSD awk's ignored IGNORECASE, and adds the macOS form when a BSD or zsh command fails.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fmacos-grep-guard%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Development-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.287-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Install](#-installation) •
[Usage](#-usage) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it ships a mod, which runs inside Claude Code. It doesn't install in the Claude app (chat or Cowork). It acts only on macOS and does nothing on Linux or Windows.

> [!TIP]
> **TL;DR** — On a Mac, a recursive `grep` never returns a quietly incomplete answer: Claude states in the command whether gitignored and binary files count, and BSD or zsh errors come back with the macOS fix.

## ✨ Why use it

- **Complete searches** — in Claude's shell on macOS, `grep` is ugrep with `--ignore-files` and `-I`, so a recursive search skips gitignored and binary files and an empty result looks like proof that something does not exist. The guard stops the command until it says which files it covers.
- **No silent awk mismatch** — macOS awk is BSD awk and ignores `IGNORECASE`. The guard stops the program and suggests `tolower($0) ~ /pattern/`.
- **Fixes in the same turn** — when a command fails with a known BSD or zsh error (`uniq -w`, `stat -c`, GNU-style `sed -i`, `timeout`, an unmatched glob), Claude reads the macOS form next to the error and retries.

## 🧩 What's inside

| Component | Name                                  | What it does                                                                                                                                     | How it runs                                                       |
| :-------- | :------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------- |
| 🧩 Mod    | [`hooks/register.ts`](hooks/register.ts) | Stops a recursive `grep` that would skip files and an `awk` program that relies on `IGNORECASE`; adds the macOS form after a BSD or zsh error | Automatically on every Bash call, in the main session and in subagents |

## ✅ Requirements

| Requirement             | Details                                                                                     |
| :---------------------- | :------------------------------------------------------------------------------------------ |
| **Claude Code**         | v2.1.287 or later (v2.1.286 in the Desktop app) — check with `claude --version`             |
| **Surfaces**            | See [Compatibility](#-compatibility)                                                        |
| **macOS**               | 13.0 or later, Apple Silicon or Intel. On any other system the guard does nothing           |
| **External tools**      | `git` on your `PATH`, to list the gitignored files under a search folder. Install it with `xcode-select --install` |
| **Accounts / API keys** | None                                                                                        |
| **Network**             | None. See [What this plugin runs and sends](#-what-this-plugin-runs-and-sends)              |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install macos-grep-guard --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install macos-grep-guard@the-claude-factory
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
/plugin install macos-grep-guard --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install macos-grep-guard@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude desktop app — Code tab</b></summary>

With the marketplace added, click **+** next to the prompt box → **Add plugins** (or **Plugins** → **Browse plugins**), or open **Settings** → **Plugins** → **Discover**; then select **macOS Grep Guard** and choose a scope.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

A mod runs with your permissions and no sandbox. Before you install it, you can see everything it hooks and calls with `claude plugin validate <path to the plugin folder>`.

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

- **Mod:** one `tool.call` hook on `Bash`, [`hooks/register.ts`](hooks/register.ts), with its rules in [`hooks/rules.ts`](hooks/rules.ts). It runs with your permissions and no sandbox. See Where it runs and what turns it off, below.
- **Reads:** the Bash command and its result, which Claude Code passes to the mod. For a recursive `grep` without explicit choices, the names of files and folders under the search folder (to find `.gitignore` files and nested `.git` folders) and, through `git`, the `.gitignore` files and the repository index there. No file contents.
- **Processes it starts**, each without a shell and each stopped after 5 seconds: `uname -s` once per session; `awk` once, to check whether `IGNORECASE` works; and, for a recursive `grep` without explicit choices, `/usr/bin/find <folder> -name .gitignore -print -quit`, `/usr/bin/find <folder> -mindepth 2 -name .git -print -quit`, `git -C <folder> rev-parse --is-inside-work-tree` and `git -C <folder> ls-files`. Every `git` call runs with `-c core.fsmonitor=false`, so a program that a cloned repository names in its own config never runs.
- **MCP servers:** none.
- **Network:** none.
- **Files written:** none.
- **Never does:** rewrite a command, write a file, call a model or reach the network.

Run `claude plugin validate <path to the plugin folder>` before you install it to see everything it hooks and calls.

## 🔄 Updating

```bash
claude plugin update macos-grep-guard@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **macOS Grep Guard** → **Update now**. Then run `/reload-plugins`.

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall macos-grep-guard@the-claude-factory
```

Installed with `--scope project`? Add `--scope project` here too.

In a session: `/plugin` → **Installed** → **macOS Grep Guard** → **Uninstall**.

The plugin keeps no data and writes no files, so nothing is left behind.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component                              |                         Claude Code                          |                                                                                                                                          Claude app                                                                                                                                           |
| :------------------------------------- | :----------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| 🧩 Mods                                | ✅ every Claude Code session except a Desktop session on WSL |                                                                                                                   ⚠️ the plugin directory lists a mod for Claude Code only                                                                                                                    |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

**Tested with** Claude Code v2.1.312 on macOS 27 (Apple Silicon).

## 🛡️ Where it runs and what turns it off

- **Where it runs:** every Claude Code session on macOS, in the terminal and in the Desktop app, except a Desktop session on WSL. On Linux and Windows it checks `uname` once and does nothing.
- **What turns it off:** `disableAllHooks`, and an organization's `allowManagedModsOnly`, which refuses any mod installed from a GitHub source. `--safe-mode` and `--bare` start Claude Code without the plugin's mod.
- **Organizations:** with managed settings or a Team or Enterprise login, Claude Code's built-in guard loads ahead of user mods and can keep a deny the mod tried to lift.
- **The permission prompt:** the mod cannot restyle it or change what it shows. It only allows a command or stops it with a message for Claude.
- **Diagnosis:** `/plugin` shows `1 mod active · macos-grep-guard` under the tabs when the mod loaded. Only `claude --debug` shows why a mod was refused or a hook skipped.

## 🚧 Limitations

| Limitation | What you see | Safe recovery |
| :--------- | :----------- | :------------ |
| Every recursive `grep` without a binary choice is stopped, whether or not the folder holds a binary file: no cheap check tells | Claude retries with the flags | None needed: the retry costs one step and never returns incomplete data |
| A search started below a `.gitignore` that also has patterns in a parent folder can be stopped when nothing would be skipped | Same as above | Same as above |
| A search folder that holds a nested repository or submodule is stopped whenever it has a `.gitignore` | Same as above | Same as above |
| In a subagent, a recursive `grep` on a relative path is stopped, because a subagent's Bash folder does not follow the session's | Claude retries with the flags or an absolute path | Same as above |
| A command run in the background returns no error output | No hint after a background command fails | Read the background task's output |
| Calls to the Grep and Glob tools, `Monitor` commands, and `length()` on accented text are not checked | Nothing from this plugin | Use Bash for searches; use perl for multibyte text |
| The mods API can change between Claude Code releases | The guard may stop working after an update; a failed hook lets the command run, except a recursive `grep`, which is stopped | Run `claude plugin update macos-grep-guard@the-claude-factory` |

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/macos-grep-guard:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

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

[MIT](./LICENSE) © Nery Murillo The approach to shell parsing is credited in [NOTICE.txt](./NOTICE.txt).
