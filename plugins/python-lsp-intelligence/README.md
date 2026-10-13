<div align="center">

# 🐍 Python LSP Intelligence

<p><strong>Gives Claude Code the basedpyright language server for Python, plus a skill that teaches Claude to resolve symbols, aliases and imports semantically, fix basedpyright and Ruff findings without suppressing them, and verify every change with evidence.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fpython-lsp-intelligence%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
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

💻 **Claude Code only** — it connects a language server, and only Claude Code runs language servers. Install it where you write Python, in Claude Code.

> [!TIP]
> **TL;DR** — Install basedpyright, add this plugin, and Claude sees the type errors its own edits introduce, finds every caller of a function by symbol instead of by text, and tells you exactly which checks passed.

## ✨ Why use it

- **Type errors caught as Claude edits** — after each edit to a `.py`, `.pyi` or `.pyw` file, basedpyright's errors and warnings reach Claude, so it fixes what it broke before you run anything.
- **Renames that don't miss callers** — Claude finds references by symbol, then checks `import … as` aliases, re-exports, `__all__`, entry points, pytest fixtures and string-based lookups that a reference search can't see.
- **Fixes, not silencing** — untyped data is validated at the boundary and narrowed to the real type; no `cast`, `# type: ignore`, invented defaults or weaker rules just to make a finding disappear.
- **Honest verification** — Ruff, the formatter, basedpyright and your tests are reported separately, with the files each one covered and what stayed unverified.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧠 LSP server | `basedpyright` | Connects `basedpyright-langserver` for `.py`, `.pyi` and `.pyw` files | Automatically when Claude opens or edits a Python file |
| 🎯 Skill | `python-lsp-intelligence:python-lsp-intelligence` | Teaches Claude to navigate, diagnose, repair and verify Python code with the language server, basedpyright and Ruff | Automatically when you work on Python code, or `/python-lsp-intelligence:python-lsp-intelligence` |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.292 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | `basedpyright-langserver` on the `PATH` of the shell you start `claude` from: `uv tool install basedpyright` (or `pip install basedpyright`, `brew install basedpyright`). Recommended: `ruff` for linting and formatting. For the optional control tests only: `bash` (Git Bash on Windows) and `jq` 1.6 or later |
| **Accounts / API keys** | None |

The plugin doesn't install the language server; Claude Code starts `basedpyright-langserver` by name from your `PATH`.

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install python-lsp-intelligence --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install python-lsp-intelligence@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install python-lsp-intelligence --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install python-lsp-intelligence@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

To confirm the server starts, ask Claude to introduce a type error in a Python file and fix it. A line like `Found 1 new diagnostic issue in 1 file` under the edit means it's working.

## 🚀 Usage

You don't need to call anything: the language server starts with the first Python file Claude edits, and the skill loads when you work on Python code.

### Example: rename a public function

```text
Rename load_settings to read_settings across the project.
```

**Result:** Claude finds the definition and its references through the language server, also checks aliased imports, `__all__`, entry points and string references, edits only the confirmed uses, and reports the checks it ran and any consumer it couldn't confirm.

### Example: fix a type error without hiding it

```text
basedpyright says reportReturnType in parse_config. Fix it.
```

**Result:** Claude reads the rule, the intended contract and the callers, fixes the implementation or validates the untyped value, and re-runs basedpyright on the file and its callers — no `cast` or `# type: ignore`.

### Example: invoke the skill directly

```text
/python-lsp-intelligence:python-lsp-intelligence why does this import fail only in the editor?
```

**Result:** Claude compares the interpreter, configuration and source the editor and the command line use, and names the difference instead of editing the import.

## 🔄 Updating

```bash
claude plugin update python-lsp-intelligence@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Python LSP Intelligence** → **Update now**. Then run `/reload-plugins`.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall python-lsp-intelligence@the-claude-factory
```

In a session: `/plugin` → **Installed** → **Python LSP Intelligence** → **Uninstall**. basedpyright stays installed; remove it with the tool you installed it with.

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

Run `/reload-plugins`, then type `/python-lsp-intelligence:` to list its skill. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Claude never reports diagnostics for Python files.</b></summary>

Open `/plugin` → **Errors**. `Executable not found in $PATH: "basedpyright-langserver"` means the server isn't installed or isn't on the `PATH` of the shell you started `claude` from. Install it, check with `which basedpyright-langserver`, and restart Claude Code.

</details>

<details>
<summary><b>basedpyright reports a missing import that runs fine.</b></summary>

The language server may be using a different interpreter than the one that has your packages, for example a script with inline dependencies or a project without a `.venv`. Claude explains the mismatch instead of changing the import; point basedpyright at the right environment in your project's configuration.

</details>

<details>
<summary><b>Does it change my project's lint or type-checking settings?</b></summary>

No. Claude uses your configuration as it is and reports when a disabled rule or an excluded file limits what was checked. The optional control tests run in a temporary folder with their own settings.

</details>

<details>
<summary><b>I already use another Python language server plugin.</b></summary>

Each file extension gets one server. When two enabled plugins claim `.py`, the first registered handles it and `/plugin` → **Errors** shows that the other isn't used. Keep one of them enabled.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🐚 [Bash LSP Intelligence](../bash-lsp-intelligence/README.md) · 🟦 [TypeScript 7 LSP Intelligence](../typescript7-lsp-intelligence/README.md)
- 📖 [Claude Code code intelligence docs](https://code.claude.com/docs/en/plugins/code-intelligence)
- 📖 [basedpyright docs](https://docs.basedpyright.com/latest/)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=python-lsp-intelligence) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=python-lsp-intelligence) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=python-lsp-intelligence)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
