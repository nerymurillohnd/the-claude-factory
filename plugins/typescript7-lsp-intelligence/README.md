<div align="center">

# 🟦 TypeScript 7 LSP Intelligence

<p><strong>Gives Claude Code a pinned native TypeScript 7 language server for TypeScript and JavaScript, type-checks the program of every file Claude edits with the matching compiler, and teaches Claude to find the program that owns a file and fix compiler findings without unsafe assertions or suppressions.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Ftypescript7-lsp-intelligence%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
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

💻 **Claude Code only** — it connects a language server and a post-edit hook, and only Claude Code runs language servers. Install it where you write TypeScript, in Claude Code.

> [!TIP]
> **TL;DR** — Add this plugin and Claude gets the native TypeScript 7 compiler and language server, pinned inside the plugin: every TypeScript or JavaScript file Claude edits is type-checked in its own `tsconfig.json` program, and Claude navigates your code by symbol instead of by text search. Nothing else to install.

## ✨ Why use it

- **The compiler comes with the plugin** — TypeScript 7.0.2 is pinned in the plugin and installed by Claude Code when it caches it, so the server and the checks never depend on, or change, the `tsc` in your project or on your `PATH`.
- **Every edit is type-checked in its program** — after each edit to a `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` or `.cjs` file, the plugin runs `tsc --noEmit` on the nearest `tsconfig.json` program. Errors in the edited file come first, breakage in sibling files after; a file no program includes is reported, never passed over. A clean run shows you a one-line confirmation.
- **Your `tsconfig.json` is the policy** — strictness, module resolution and JSX come from your project. Without a `tsconfig.json`, the compiler's defaults apply and Claude is told so.
- **Symbol navigation on TypeScript 7** — go to definition, references, hover, call hierarchy and workspace symbols through the native server, which is the generation the `typescript` package now ships.
- **Fixes, not silencing** — no `@ts-ignore`, `any`, `as unknown as T` or non-null `!` just to make an error disappear.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧠 LSP server | `typescript` | Starts the pinned TypeScript 7 server (`tsc --lsp --stdio`) for `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` and `.cjs` files | Automatically when Claude opens or edits one of those files |
| 🪝 Hook | `PostToolUse` · `PostToolUseFailure` | Runs the pinned `tsc --noEmit` on the program of each TypeScript or JavaScript file an Edit, Write or Bash call changed | Automatically after each of those tool calls |
| 🎯 Skill | `typescript7-lsp-intelligence:typescript7-lsp-intelligence` | Teaches Claude to run the compiler after every edit (the TypeScript 7 server pushes no diagnostics), navigate with the language server first, trust its results only after five checks, and work with `tsc` the way your project configures it | Automatically when you work on TypeScript or JavaScript, or `/typescript7-lsp-intelligence:typescript7-lsp-intelligence` |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.292 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **External tools** | Node.js 18 or later and `npm` on the `PATH` of the shell you start `claude` from. Claude Code installs the pinned TypeScript with `npm` when it caches the plugin; the hook runs on `node`. Windows: run Claude Code from Git Bash with Node.js on its `PATH` |
| **Accounts / API keys** | None |

TypeScript 7.0.2 is pinned in the plugin's `package.json` and `package-lock.json`; you don't install it and it doesn't touch your project's dependencies.

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

To confirm it works, ask Claude to add a type error to a TypeScript file and fix it. The hook reports the error under the edit and, once the file is clean, a line like `typescript7-lsp-intelligence: tsc passed · src/app.ts`.

> [!IMPORTANT]
> Enable only one TypeScript plugin at a time. Each file extension gets one language server: with this plugin and `typescript6-lsp-intelligence` (or the official `typescript-lsp`) both enabled, only the first registered serves `.ts` files and `/plugin` → **Errors** shows the other isn't used.

## 🚀 Usage

You don't need to call anything: the language server starts with the first TypeScript file Claude edits, the hook runs after each edit, and the skill loads when you work on TypeScript or JavaScript.

### Example: what happens after an edit

```text
Make loadConfig return the parsed settings instead of the raw text.
```

**Result:** Claude edits the function. If the compiler finds something in that program, Claude sees it right away:

```text
tsc (tsconfig.json):
src/config.ts(18,10): error TS2322: Type 'string' is not assignable to type 'Settings'.
src/server.ts(42,21): error TS2345: Argument of type 'Settings' is not assignable to parameter of type 'string'.
Fix these findings in src/config.ts before continuing; do not suppress them.
```

Claude fixes the function and the caller it broke, the hook runs again, and the turn ends with `typescript7-lsp-intelligence: tsc passed · src/config.ts`.

### Example: rename an export

```text
Rename formatPrice to formatMoney across the repo.
```

**Result:** Claude finds the definition and its references through the language server, loads the other `tsconfig` projects of a monorepo before trusting the list, greps `.astro`, `.svelte`, `.vue` and config files for uses the server can't see, edits only the confirmed ones, and runs `tsc` on every program it touched.

### Example: a file no program includes

```text
Add scripts/migrate.ts that renames the old config keys.
```

**Result:** The hook runs the nearest program, notices the new file is not in its `include`, and tells Claude: `scripts/migrate.ts is not part of tsconfig.json's program; add it to include or files.` Claude adds it, and the next check covers it.

## ⚙️ Configuration

The hook runs the compiler the way you would from a terminal, so **your configuration wins**:

| Situation | What the hook does |
| :-- | :-- |
| A `tsconfig.json` exists above the file | `tsc --noEmit -p <that tsconfig.json>` with the pinned TypeScript 7: your `strict`, `target`, `module`, `jsx` and `include` apply |
| Several changed files share a `tsconfig.json` | One `tsc` run for that program |
| No `tsconfig.json` above the file | `tsc --noEmit <file>` with the compiler's defaults, and the report says so |

The plugin never creates or edits a `tsconfig.json`, and it never runs a formatter or linter: Biome, Prettier and ESLint stay your project's tools, and the skill teaches Claude to run them as your `package.json` scripts do.

**Optional, recommended:** let the hook see exactly which files a Bash command changed by adding this to your user settings (`~/.claude/settings.json`); without it the hook finds them by modification time:

```json
{
  "bashEditDiffEnabled": true
}
```

## 🔄 Updating

```bash
claude plugin update typescript7-lsp-intelligence@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **TypeScript 7 LSP Intelligence** → **Update now**. Then run `/reload-plugins`. An update that changes the pinned TypeScript installs it again automatically.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall typescript7-lsp-intelligence@the-claude-factory
```

In a session: `/plugin` → **Installed** → **TypeScript 7 LSP Intelligence** → **Uninstall**. The pinned TypeScript goes with the plugin; your project's dependencies are untouched.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads, but it relies on the language server, which the Claude app doesn't run |
| 🪝 Hooks | ✅ | ➖ runs only where Claude Code installs the plugin's TypeScript and starts language servers |
| 🧠 LSP server | ✅ | ➖ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

Claude Code on the web doesn't start plugin language servers either, so there Claude gets no diagnostics or code navigation from this plugin.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/typescript7-lsp-intelligence:` to list its skill. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Why does Claude run <code>tsc</code> itself after every edit?</b></summary>

The native TypeScript 7 server answers navigation requests but doesn't push diagnostics after edits, so the usual `Found N new diagnostic issues` line never appears for these files. The hook and the skill cover that: the hook checks each edit, and the skill tells Claude to run the compiler on every program a change touches.

</details>

<details>
<summary><b>The hook says the plugin's TypeScript was not installed.</b></summary>

Claude Code installs it with `npm` when it caches the plugin, within 60 seconds. If that failed (no `npm` on `PATH`, no network), `/plugin` shows a note on the plugin. Put `npm` on the `PATH` of the shell that starts `claude` and reinstall the plugin, or run `npm ci` inside the plugin folder `/plugin` names.

</details>

<details>
<summary><b>I use <code>--plugin-dir</code> to try the plugin from a clone.</b></summary>

Claude Code doesn't install dependencies for a plugin loaded in place. Run `npm ci --ignore-scripts` in the plugin folder once.

</details>

<details>
<summary><b>My project has hundreds of legacy errors. Will Claude chase them all?</b></summary>

The hook reports the program's errors with the edited file's first, because an error elsewhere in the same program is often breakage the edit caused. Claude fixes what its change broke; legacy errors in untouched programs never come up, since the hook runs only on programs that contain a changed file.

</details>

<details>
<summary><b>The check is slow on a large program.</b></summary>

Each edit compiles the whole program; TypeScript 7's native compiler is several times faster than TypeScript 6, which is why this plugin exists. Splitting a huge program into project references makes each check smaller. The hook gives up after 120 seconds and says nothing, so a slow program is never checked in silence for long.

</details>

<details>
<summary><b>A JavaScript file passed but has obvious type errors.</b></summary>

`allowJs` admits JavaScript to the program; only `checkJs` in `tsconfig.json`, or a `// @ts-check` comment at the top of the file, type-checks it. Turn one of them on.

</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

Through Git Bash: start Claude Code from a Git Bash shell that has `node` and `npm` on its `PATH`.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🟦 [TypeScript 6 LSP Intelligence](../typescript6-lsp-intelligence/README.md) for projects that can't move to TypeScript 7 yet · 🐍 [Python LSP Intelligence](../python-lsp-intelligence/README.md) · 🐚 [Bash LSP Intelligence](../bash-lsp-intelligence/README.md)
- 📖 [Claude Code code intelligence docs](https://code.claude.com/docs/en/plugins/code-intelligence)
- 📖 [TSConfig reference](https://www.typescriptlang.org/tsconfig/)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=typescript7-lsp-intelligence) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=typescript7-lsp-intelligence) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=typescript7-lsp-intelligence)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
