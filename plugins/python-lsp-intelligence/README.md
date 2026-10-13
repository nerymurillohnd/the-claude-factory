<div align="center">

# 🐍 Python LSP Intelligence

<p><strong>Gives Claude Code the basedpyright language server for Python, checks every Python file Claude edits with ruff and basedpyright using your own configuration, and teaches Claude to navigate by symbol, resolve aliases and imports, and fix findings without suppressing them.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fpython-lsp-intelligence%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
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

💻 **Claude Code only** — it connects a language server and a post-edit hook, and only Claude Code runs language servers. Install it where you write Python, in Claude Code.

> [!TIP]
> **TL;DR** — Install ruff and basedpyright, add this plugin, and every Python file Claude edits comes back linted, formatted and type-checked with your own configuration, while Claude navigates your code by symbol instead of by text search.

## ✨ Why use it

- **Every edit is checked, not just reported** — after each edit to a `.py`, `.pyi`, `.pyw` or `.ipynb` file, the plugin runs `ruff check --fix`, `ruff format` and `basedpyright` on that file. Findings go back to Claude as an error it must fix before moving on; a clean run shows you a one-line confirmation.
- **Your configuration, not the plugin's** — the tools read the `ruff.toml`, `pyproject.toml` or `pyrightconfig.json` your project already has, including your user-level ruff config. A strict baseline applies only when you have none.
- **Type errors caught as Claude edits** — basedpyright's own diagnostics also reach Claude through the language server, so a missing import or a wrong return type is visible without running anything.
- **Renames that don't miss callers** — Claude finds references by symbol, then checks `import … as` aliases, `__all__`, entry points, pytest fixtures and string-based lookups that a reference search can't see.
- **Fixes, not silencing** — no `# noqa`, `# type: ignore`, `cast()` or weakened rules just to make a finding disappear.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧠 LSP server | `basedpyright` | Connects `basedpyright-langserver` for `.py`, `.pyi` and `.pyw` files | Automatically when Claude opens or edits a Python file |
| 🪝 Hook | `PostToolUse` · `PostToolUseFailure` | Runs `ruff check --fix`, `ruff format` and `basedpyright` on the Python files an Edit, Write, NotebookEdit or Bash call changed | Automatically after each of those tool calls |
| 🎯 Skill | `python-lsp-intelligence:python-lsp-intelligence` | Teaches Claude to navigate with the language server first, trust its results only after five checks, and work with ruff and basedpyright the way your project configures them | Automatically when you work on Python code, or `/python-lsp-intelligence:python-lsp-intelligence` |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.292 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | On the `PATH` of the shell you start `claude` from: `ruff` and `basedpyright` (`uv tool install ruff` and `uv tool install basedpyright`, or `pip install ruff basedpyright`; `basedpyright-langserver` comes with basedpyright), and `python3` 3.9 or later, which runs the hook. Windows: run Claude Code from Git Bash with the same tools on its `PATH` |
| **Accounts / API keys** | None |

The plugin doesn't install the tools; Claude Code starts `basedpyright-langserver` by name and the hook starts `ruff` and `basedpyright` by name from your `PATH`.

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

To confirm it works, ask Claude to add a type error to a Python file and fix it. Under the edit you see `Found 1 new diagnostic issue in 1 file` from the language server and a line like `python-lsp-intelligence: ruff check, ruff format, basedpyright passed · app/models.py` from the hook once the file is clean.

## 🚀 Usage

You don't need to call anything: the language server starts with the first Python file Claude edits, the hook runs after each edit, and the skill loads when you work on Python code.

### Example: what happens after an edit

```text
Add a parse_config(path) function to app/config.py that returns the settings dict.
```

**Result:** Claude writes the function. If ruff or basedpyright finds something, Claude sees it right away:

```text
basedpyright (app/config.py):
  app/config.py:12:12 - error: Return type "dict[str, Unknown]" is partially unknown (reportUnknownVariableType)
Fix these findings in app/config.py before continuing; do not suppress them.
```

Claude fixes the type, the hook runs again, and the turn ends with `python-lsp-intelligence: ruff check, ruff format, basedpyright passed · app/config.py`.

### Example: rename a public function

```text
Rename load_settings to read_settings across the project.
```

**Result:** Claude finds the definition and its references through the language server, also checks aliased imports, `__all__`, entry points and string references, edits only the confirmed uses, and runs the checks on every file it touched.

### Example: fix a finding without hiding it

```text
basedpyright says reportReturnType in parse_config. Fix it.
```

**Result:** Claude reads the rule, the intended contract and the callers, fixes the implementation or validates the untyped value, and re-runs basedpyright on the file and its callers. No `cast` or `# type: ignore`.

## ⚙️ Configuration

The hook runs the tools the way you would from a terminal, so **your configuration wins**:

| Tool | What it reads | When you have none |
| :-- | :-- | :-- |
| ruff | The closest `ruff.toml`, `.ruff.toml` or `pyproject.toml` with `[tool.ruff]` above the file, then your user-level `~/.config/ruff/ruff.toml` | The plugin's `hooks/defaults/ruff.toml`: `select = ["ALL"]` with the formatter- and basedpyright-owned rules ignored, 100-column lines |
| basedpyright | The nearest `pyrightconfig.json`, or `pyproject.toml` with `[tool.basedpyright]`, above the file (passed with `-p`, since basedpyright's own lookup only sees the current directory) | The plugin's `hooks/defaults/pyrightconfig.json`: `recommended` mode with `failOnWarnings`, strict inference and the `report*` rules that complement the ruff ignores |

Any configuration file of your own replaces the corresponding default entirely; the plugin never creates or edits one.

**Optional, recommended:** let the hook see exactly which files a Bash command changed by adding this to your user settings (`~/.claude/settings.json`); without it the hook finds them by modification time:

```json
{
  "bashEditDiffEnabled": true
}
```

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

In a session: `/plugin` → **Installed** → **Python LSP Intelligence** → **Uninstall**. ruff and basedpyright stay installed; remove them with the tool you installed them with.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads, but it relies on the language server, which the Claude app doesn't run |
| 🪝 Hooks | ✅ | ➖ needs ruff and basedpyright on your machine and runs only where Claude Code runs language servers |
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

Open `/plugin` → **Errors**. `Executable not found in $PATH: "basedpyright-langserver"` means basedpyright isn't installed or isn't on the `PATH` of the shell you started `claude` from. Install it, check with `which basedpyright-langserver`, and start a new session.

</details>

<details>
<summary><b>The hook says a tool is not installed.</b></summary>

The message names the tool and its install command, for example `ruff is not installed, so no Python file was checked. Install it: uv tool install ruff`. Install it on the `PATH` of the shell that starts `claude`; the next edit is checked.

</details>

<details>
<summary><b>The hook reformatted a file I was editing.</b></summary>

That is `ruff format` applying your (or the default) style. Claude is told to re-read the file before its next edit, so nothing is lost.

</details>

<details>
<summary><b>My project has hundreds of legacy findings. Will Claude chase them all?</b></summary>

No. The hook checks only the files Claude changes in the session, never the whole tree, and basedpyright uses your project's configuration. Legacy files stay as they are until Claude edits them.

</details>

<details>
<summary><b>basedpyright reports a missing import that runs fine.</b></summary>

The checker is looking at a different environment than the one that has your packages: a script with inline dependencies, or a project without a `.venv`. Claude explains the mismatch instead of changing the import; point basedpyright at the right interpreter in your configuration, or with `--pythonpath` for PEP 723 scripts.

</details>

<details>
<summary><b>Does it change my project's lint or type-checking settings?</b></summary>

No. Claude uses your configuration as it is, and the plugin's defaults apply only to a file for which ruff or basedpyright would find no configuration at all.

</details>

<details>
<summary><b>I already use another Python language server plugin.</b></summary>

Each file extension gets one server. When two enabled plugins claim `.py`, the first registered handles it and `/plugin` → **Errors** shows that the other isn't used. Keep one of them enabled.

</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

Through Git Bash: start Claude Code from a Git Bash shell that has `python3`, `ruff` and `basedpyright` on its `PATH`.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🐚 [Bash LSP Intelligence](../bash-lsp-intelligence/README.md) · 🟦 [TypeScript 7 LSP Intelligence](../typescript7-lsp-intelligence/README.md) · 🟦 [TypeScript 6 LSP Intelligence](../typescript6-lsp-intelligence/README.md)
- 📖 [Claude Code code intelligence docs](https://code.claude.com/docs/en/plugins/code-intelligence)
- 📖 [basedpyright docs](https://docs.basedpyright.com/latest/) · [Ruff docs](https://docs.astral.sh/ruff/)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=python-lsp-intelligence) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=python-lsp-intelligence) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=python-lsp-intelligence)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
