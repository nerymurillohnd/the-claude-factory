<div align="center">

# 🟦 TypeScript 7 LSP Intelligence

<p><strong>Gives Claude Code the native TypeScript 7 language server for TypeScript and JavaScript, plus a skill that teaches Claude to check which program owns a file, fix compiler findings without unsafe assertions or suppressions, and verify every change with evidence.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Ftypescript7-lsp-intelligence%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
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

💻 **Claude Code only** — it connects a language server, and only Claude Code runs language servers. Install it where you write TypeScript or JavaScript, in Claude Code.

> [!TIP]
> **TL;DR** — Install TypeScript 7, add this plugin, and Claude sees the compiler errors its own edits introduce, follows imports and re-exports by symbol, and proves which files the compiler actually checked.

## ✨ Why use it

- **Compiler errors as Claude edits** — after each edit to a `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` or `.cjs` file, the TypeScript 7 server's errors reach Claude, so it fixes what it broke before you build.
- **The native TypeScript 7 server** — the plugin runs `tsc --lsp --stdio` from TypeScript 7 directly, with no extra wrapper package.
- **Diagnostics checked against the real program** — Claude confirms a file belongs to the program and which options apply before trusting or dismissing a finding; a moved file the compiler skipped isn't called healthy.
- **Fixes, not silencing** — external data is validated and narrowed from `unknown`; no `as` assertions, non-null `!`, `any`, `@ts-ignore` or weaker `tsconfig` options to make an error disappear.
- **Honest verification** — compiler, linter, formatter and tests are reported separately, with the files and programs each one covered.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧠 LSP server | `typescript` | Connects TypeScript 7's `tsc --lsp --stdio` for `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` and `.cjs` files | Automatically when Claude opens or edits a TypeScript or JavaScript file |
| 🎯 Skill | `typescript7-lsp-intelligence:typescript7-lsp-intelligence` | Teaches Claude to navigate, diagnose, repair and verify TypeScript and JavaScript with the language server and the compiler | Automatically when you work on TypeScript or JavaScript, or `/typescript7-lsp-intelligence:typescript7-lsp-intelligence` |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.292 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | TypeScript 7's `tsc` on the `PATH` of the shell you start `claude` from: `npm install -g typescript` (needs Node.js; check with `tsc --version`, which must print 7 or later). For the optional control tests only: `bash` (Git Bash on Windows) and `jq` 1.6 or later |
| **Accounts / API keys** | None |

The plugin doesn't install TypeScript; Claude Code starts `tsc` by name from your `PATH`. A TypeScript 6 `tsc` there has no language server mode, so the server won't start.

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install typescript7-lsp-intelligence --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install typescript7-lsp-intelligence@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install typescript7-lsp-intelligence --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install typescript7-lsp-intelligence@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

To confirm the server starts, ask Claude to introduce a type error in a TypeScript file and fix it. A line like `Found 1 new diagnostic issue in 1 file` under the edit means it's working.

## 🚀 Usage

You don't need to call anything: the language server starts with the first TypeScript or JavaScript file Claude edits, and the skill loads when you work on that code.

### Example: rename an exported function

```text
Rename formatPrice to formatAmount everywhere it's used.
```

**Result:** Claude finds the declaration and its references through the language server, also checks re-export barrels, aliased imports, package `exports` and dynamic lookups, edits the confirmed uses, and runs the compiler on the affected programs.

### Example: type untrusted JSON properly

```text
TS7006 and an any in readConfig. Fix it without casting.
```

**Result:** Claude treats the parsed value as `unknown`, validates the fields the function needs, keeps the existing errors for bad input, and shows the compiler result and the tests it ran.

### Example: invoke the skill directly

```text
/typescript7-lsp-intelligence:typescript7-lsp-intelligence why does the editor show an error that tsc doesn't?
```

**Result:** Claude compares the program membership and resolved options of both checks and names the difference, instead of dismissing either result.

## 🔄 Updating

```bash
claude plugin update typescript7-lsp-intelligence@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **TypeScript 7 LSP Intelligence** → **Update now**. Then run `/reload-plugins`.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall typescript7-lsp-intelligence@the-claude-factory
```

In a session: `/plugin` → **Installed** → **TypeScript 7 LSP Intelligence** → **Uninstall**. TypeScript stays installed; remove it with `npm uninstall -g typescript` if you no longer need it.

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

Run `/reload-plugins`, then type `/typescript7-lsp-intelligence:` to list its skill. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Claude never reports diagnostics for TypeScript files.</b></summary>

Open `/plugin` → **Errors**. `Executable not found in $PATH: "tsc"` means TypeScript isn't installed globally. If `tsc --version` prints 6 or earlier, install TypeScript 7 with `npm install -g typescript`. Restart Claude Code afterwards.

</details>

<details>
<summary><b>My project still uses TypeScript 6. Can I use this plugin?</b></summary>

The language server needs TypeScript 7's `tsc` on your `PATH`, but your project can keep its own TypeScript version for builds. The skill tells TypeScript 6 tooling apart from TypeScript 7 and runs the compiler your project declares when it verifies a change.

</details>

<details>
<summary><b>Does it cover Vue or Svelte components?</b></summary>

No. The server handles plain TypeScript and JavaScript files. Claude tells you when a result can't see template or component usage, so you know what was left unchecked.

</details>

<details>
<summary><b>I already use another TypeScript language server plugin.</b></summary>

Each file extension gets one server. When two enabled plugins claim `.ts`, the first registered handles it and `/plugin` → **Errors** shows that the other isn't used. Keep one of them enabled.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🐚 [Bash LSP Intelligence](../bash-lsp-intelligence/README.md) · 🐍 [Python LSP Intelligence](../python-lsp-intelligence/README.md)
- 📖 [Claude Code code intelligence docs](https://code.claude.com/docs/en/plugins/code-intelligence)
- 📖 [Announcing TypeScript 7.0](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=typescript7-lsp-intelligence) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=typescript7-lsp-intelligence) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=typescript7-lsp-intelligence)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
