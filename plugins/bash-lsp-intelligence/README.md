<div align="center">

# 🐚 Bash LSP Intelligence

<p><strong>Gives Claude Code bash-language-server for Bash and POSIX shell scripts, plus a skill that teaches Claude to trace sourced files and same-named functions, fix ShellCheck and shfmt findings without changing behavior, and verify every change with evidence.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fbash-lsp-intelligence%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Language%20Support-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.292-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Install](#-installation) •
[Usage](#-usage) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it connects a language server, and only Claude Code runs language servers. Install it where you write shell scripts, in Claude Code.

> [!TIP]
> **TL;DR** — Install bash-language-server and ShellCheck, add this plugin, and Claude sees the ShellCheck findings its own edits introduce, tells same-named functions apart by what each script sources, and fixes quoting without breaking globs or exit codes.

## ✨ Why use it

- **ShellCheck findings as Claude edits** — after each edit to a `.sh`, `.inc`, `.bash` or `.command` file, the language server's ShellCheck diagnostics reach Claude, so it fixes what it broke before you run the script.
- **Scripts in hidden folders count too** — the server indexes shell files under `.github/` and `.claude/` as well, where many CI and automation scripts live.
- **Renames that respect `source`** — two `render` functions in unrelated scripts aren't one rename target; Claude traces which definition each caller reaches through `source`/`.` chains, traps and dispatch before editing.
- **Fixes that keep behavior** — quoting, arrays, globbing and exit statuses are repaired for what the script means to do; no blanket quoting of intentional globs, no `|| true`, no `disable=` directives to hide a finding.
- **The real dialect, respected** — a Zsh script with a `.sh` name isn't converted to Bash; Claude reports what ShellCheck can't analyze instead of rewriting it.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧠 LSP server | `shellscript` | Connects `bash-language-server` for `.sh`, `.inc`, `.bash` and `.command` files, including those under `.github/` and `.claude/` | Automatically when Claude opens or edits a shell file |
| 🎯 Skill | `bash-lsp-intelligence:bash-lsp-intelligence` | Teaches Claude to navigate, diagnose, repair and verify shell scripts with the language server, ShellCheck and shfmt | Automatically when you work on shell scripts, or `/bash-lsp-intelligence:bash-lsp-intelligence` |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.292 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | `bash-language-server` on the `PATH` of the shell you start `claude` from: `npm i -g bash-language-server` (needs Node.js). Recommended: `shellcheck`, which the server runs for its diagnostics, and `shfmt` for formatting. For the optional control tests only: `bash` (Git Bash on Windows) and `jq` 1.6 or later |
| **Accounts / API keys** | None |

The plugin doesn't install the language server; Claude Code starts `bash-language-server` by name from your `PATH`. Without ShellCheck the server still navigates code but reports no ShellCheck findings.

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install bash-lsp-intelligence --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install bash-lsp-intelligence@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install bash-lsp-intelligence --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install bash-lsp-intelligence@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

To confirm the server starts, ask Claude to add an unquoted variable to a shell script and fix it. A line like `Found 1 new diagnostic issue in 1 file` under the edit means it's working.

## 🚀 Usage

You don't need to call anything: the language server starts with the first shell file Claude edits, and the skill loads when you work on shell scripts.

### Example: rename a function used across scripts

```text
Rename the cleanup function in scripts/lib/common.sh to remove_temp_files.
```

**Result:** Claude finds the definition and reference candidates through the language server, keeps only the callers that actually source that library, also checks `trap` strings, dispatch tables and CI files, and lists anything it couldn't confirm.

### Example: fix ShellCheck findings without changing behavior

```text
Fix the SC2086 warnings in deploy.sh.
```

**Result:** Claude quotes single values, turns argument lists into arrays, leaves intentional globs working, and reports ShellCheck and shfmt results separately, without running the deploy.

### Example: invoke the skill directly

```text
/bash-lsp-intelligence:bash-lsp-intelligence why does ShellCheck say this variable is never assigned?
```

**Result:** Claude follows the `source` chain the analyzer couldn't resolve and names the file that sets the variable, instead of adding a fake assignment.

## 🔄 Updating

```bash
claude plugin update bash-lsp-intelligence@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Bash LSP Intelligence** → **Update now**. Then run `/reload-plugins`.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall bash-lsp-intelligence@the-claude-factory
```

In a session: `/plugin` → **Installed** → **Bash LSP Intelligence** → **Uninstall**. bash-language-server, ShellCheck and shfmt stay installed; remove them with the tools you installed them with.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads, but it relies on the language server, which the Claude app doesn't run |
| 🧠 LSP server | ✅ | ➖ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

Claude Code on the web doesn't start plugin language servers either, so there Claude gets no diagnostics or code navigation from this plugin.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/bash-lsp-intelligence:` to list its skill. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Claude never reports diagnostics for shell files.</b></summary>

Open `/plugin` → **Errors**. `Executable not found in $PATH: "bash-language-server"` means the server isn't installed or isn't on the `PATH` of the shell you started `claude` from. If the server runs but no ShellCheck findings appear, install ShellCheck: the server runs it for those findings. Restart Claude Code after installing either.

</details>

<details>
<summary><b>My script has no extension. Is it covered?</b></summary>

The server handles `.sh`, `.inc`, `.bash` and `.command` files. Claude still reads and checks extensionless scripts with a shell shebang through ShellCheck and text search, and tells you when a result relied on that instead of the language server.

</details>

<details>
<summary><b>Will it convert my Zsh scripts to Bash?</b></summary>

No. Claude keeps each script's dialect. ShellCheck doesn't analyze Zsh, so Claude reports that limit instead of rewriting the script.

</details>

<details>
<summary><b>I already use another shell language server plugin.</b></summary>

Each file extension gets one server. When two enabled plugins claim `.sh`, the first registered handles it and `/plugin` → **Errors** shows that the other isn't used. Keep one of them enabled.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🐍 [Python LSP Intelligence](../python-lsp-intelligence/README.md) · 🟦 [TypeScript 7 LSP Intelligence](../typescript7-lsp-intelligence/README.md)
- 📖 [Claude Code code intelligence docs](https://code.claude.com/docs/en/plugins/code-intelligence)
- 📖 [bash-language-server](https://github.com/bash-lsp/bash-language-server)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=bash-lsp-intelligence) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=bash-lsp-intelligence) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=bash-lsp-intelligence)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
