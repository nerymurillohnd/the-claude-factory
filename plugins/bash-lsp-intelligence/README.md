<div align="center">

# 🐚 Bash LSP Intelligence

<p><strong>Gives Claude Code bash-language-server for Bash and POSIX shell scripts, formats and checks every script Claude edits with shfmt and ShellCheck using your own configuration, and teaches Claude to trace sourced files and same-named functions before a rename.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fbash-lsp-intelligence%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Language%20Support-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.292-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Install](#-installation) •
[Usage](#-usage) •
[Configuration](#%EF%B8%8F-configuration) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it connects a language server and a post-edit hook, and only Claude Code runs language servers. Install it where you write shell scripts, in Claude Code.

> [!TIP]
> **TL;DR** — Install bash-language-server, shfmt and ShellCheck, add this plugin, and every shell script Claude edits comes back formatted and checked with your own `.editorconfig` and `.shellcheckrc`, while Claude tells same-named functions apart by what each script sources.

## ✨ Why use it

- **Every edit is formatted and checked** — after each edit to a `.sh`, `.bash` or extensionless Bash script, the plugin runs `shfmt -w` and then `shellcheck` on that file. Findings go back to Claude as an error it must fix before moving on; a clean run shows you a one-line confirmation.
- **Your style and rules, not the plugin's** — shfmt reads your `.editorconfig` and ShellCheck your `.shellcheckrc` and `SHELLCHECK_OPTS`. A strict baseline (two-space indent, every optional check) applies only when you have none.
- **ShellCheck findings as Claude edits** — the language server also pushes ShellCheck diagnostics for `.sh`, `.inc`, `.bash` and `.command` files, including scripts under `.github/` and `.claude/`.
- **Renames that respect `source`** — two `render` functions in unrelated scripts aren't one rename target; Claude traces which definition each caller reaches through `source` chains, traps and dispatch before editing.
- **The real dialect, respected** — a Zsh script with a `.sh` name isn't converted to Bash; ShellCheck can't analyze it, and the plugin says so instead of calling it clean.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧠 LSP server | `shellscript` | Connects `bash-language-server` for `.sh`, `.inc`, `.bash` and `.command` files, indexing `.github/` and `.claude/` too | Automatically when Claude opens or edits a shell file |
| 🪝 Hook | `PostToolUse` · `PostToolUseFailure` | Runs `shfmt -w` and `shellcheck` on the shell scripts an Edit, Write or Bash call changed | Automatically after each of those tool calls |
| 🎯 Skill | `bash-lsp-intelligence:bash-lsp-intelligence` | Teaches Claude to navigate with the language server first, trust its results only after five checks, and work with shfmt and ShellCheck the way your project configures them | Automatically when you work on shell scripts, or `/bash-lsp-intelligence:bash-lsp-intelligence` |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.292 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | On the `PATH` of the shell you start `claude` from: `bash-language-server` (`npm install -g bash-language-server`), `shfmt` and `shellcheck` (macOS: `brew install shfmt shellcheck`; Debian/Ubuntu: `sudo apt install shellcheck` and shfmt from its [release binary](https://github.com/mvdan/sh/releases)), and Node.js 18 or later, which runs the hook. Windows: run Claude Code from Git Bash with the same tools on its `PATH` |
| **Accounts / API keys** | None |

The plugin doesn't install the tools; Claude Code starts `bash-language-server` by name and the hook starts `shfmt` and `shellcheck` by name from your `PATH`.

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

To confirm it works, ask Claude to write `echo $name` in a script and fix it. Under the edit you see `Found 1 new diagnostic issue in 1 file` from the language server and, once the file is clean, a line like `bash-lsp-intelligence: shfmt, shellcheck passed · scripts/deploy.sh` from the hook.

## 🚀 Usage

You don't need to call anything: the language server starts with the first shell file Claude edits, the hook runs after each edit, and the skill loads when you work on shell scripts.

### Example: what happens after an edit

```text
Add a --dry-run flag to scripts/deploy.sh.
```

**Result:** Claude edits the script. If shfmt or ShellCheck finds something, Claude sees it right away:

```text
shellcheck (scripts/deploy.sh):
In scripts/deploy.sh line 14:
  rsync $opts "$src" "$dest"
        ^-- SC2086 (info): Double quote to prevent globbing and word splitting.
Fix these findings in scripts/deploy.sh before continuing; do not suppress them.
```

Claude turns `opts` into an array, the hook runs again, and the turn ends with `bash-lsp-intelligence: shfmt, shellcheck passed · scripts/deploy.sh`.

### Example: rename a function used across scripts

```text
Rename render_report to build_report everywhere it's actually called.
```

**Result:** Claude takes the language server's reference list, keeps only the hits whose scripts reach this definition through `source`, greps traps, `bash -c` strings and hook commands for the rest, and edits only those.

### Example: format a script to the project's style

```text
Format scripts/backup.sh.
```

**Result:** Claude runs `shfmt -w`, which reads your `.editorconfig`, re-reads the file, and reports what changed.

## ⚙️ Configuration

The hook runs the tools the way you would from a terminal, so **your configuration wins**:

| Tool | What it reads | When you have none |
| :-- | :-- | :-- |
| shfmt | `.editorconfig`, searched from the script's folder upward (`[[shell]]` keys such as `indent_size`, `switch_case_indent`, `binary_next_line`) | `shfmt -i 2 -ci -bn`: two-space indent, indented `case` branches, binary operators at line start |
| ShellCheck | The first `.shellcheckrc` from the script's folder upward, then `~/.shellcheckrc` or `$XDG_CONFIG_HOME/shellcheckrc`, plus `SHELLCHECK_OPTS` | `shellcheck -o all -S style -x -a -P SCRIPTDIR`: every optional check, style severity, sourced files followed and checked |

An `.editorconfig`, a `.shellcheckrc` or `SHELLCHECK_OPTS` of your own replaces the corresponding default entirely; the plugin never creates or edits one.

**Optional, recommended:** let the hook see exactly which files a Bash command changed by adding this to your user settings (`~/.claude/settings.json`); without it the hook finds them by modification time:

```json
{
  "bashEditDiffEnabled": true
}
```

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

In a session: `/plugin` → **Installed** → **Bash LSP Intelligence** → **Uninstall**. bash-language-server, shfmt and ShellCheck stay installed; remove them with the tool you installed them with.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads, but it relies on the language server, which the Claude app doesn't run |
| 🪝 Hooks | ✅ | ➖ needs shfmt and ShellCheck on your machine and runs only where Claude Code runs language servers |
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

Open `/plugin` → **Errors**. `Executable not found in $PATH: "bash-language-server"` means the server isn't installed or isn't on the `PATH` of the shell you started `claude` from. Install it, check with `which bash-language-server`, and start a new session. ShellCheck must be on the same `PATH` for the server to report its findings.

</details>

<details>
<summary><b>The hook says a tool is not installed.</b></summary>

The message names the tool and where to get it, for example `shfmt is not installed, so no shell file was checked. Install it: brew install shfmt (macOS) or your distribution package`. Install it on the `PATH` of the shell that starts `claude`; the next edit is checked.

</details>

<details>
<summary><b>The hook reformatted a file I was editing.</b></summary>

That is `shfmt -w` applying your `.editorconfig` (or the default style). Claude is told to re-read the file before its next edit, so nothing is lost.

</details>

<details>
<summary><b>My scripts have hundreds of legacy findings. Will Claude chase them all?</b></summary>

No. The hook checks only the scripts Claude changes in the session, never the whole tree. Legacy scripts stay as they are until Claude edits them.

</details>

<details>
<summary><b>A Zsh script was "not checked".</b></summary>

ShellCheck supports sh, bash, dash and ksh only. The hook tells Claude the file was not checked instead of reporting it clean; use Bash, or a Zsh-aware linter, for that script.

</details>

<details>
<summary><b>I already use another shell language server plugin.</b></summary>

Each file extension gets one server. When two enabled plugins claim `.sh`, the first registered handles it and `/plugin` → **Errors** shows that the other isn't used. Keep one of them enabled.

</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

Through Git Bash: start Claude Code from a Git Bash shell that has `node`, `shfmt`, `shellcheck` and `bash-language-server` on its `PATH`.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🐍 [Python LSP Intelligence](../python-lsp-intelligence/README.md) · 🟦 [TypeScript 7 LSP Intelligence](../typescript7-lsp-intelligence/README.md) · 🟦 [TypeScript 6 LSP Intelligence](../typescript6-lsp-intelligence/README.md)
- 📖 [Claude Code code intelligence docs](https://code.claude.com/docs/en/plugins/code-intelligence)
- 📖 [ShellCheck wiki](https://www.shellcheck.net/wiki/) · [shfmt](https://github.com/mvdan/sh) · [bash-language-server](https://github.com/bash-lsp/bash-language-server)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=bash-lsp-intelligence) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=bash-lsp-intelligence) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=bash-lsp-intelligence)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
