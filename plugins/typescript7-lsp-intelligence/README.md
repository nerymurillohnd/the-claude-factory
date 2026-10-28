<div align="center">

# 🟦 TypeScript 7 LSP Intelligence

<p><strong>Connects the native TypeScript 7 language server to Claude Code, type-checks every file Claude edits with your own native TypeScript 7 compiler under a strictest policy, and teaches Claude to find the program that owns a file and fix compiler findings without unsafe assertions or suppressions.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Ftypescript7-lsp-intelligence%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Language%20Support-6B7280)](../../README.md#-catalog)
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

💻 **Claude Code only** — it connects a language server and a post-edit hook, and only Claude Code runs language servers. Install it where you write TypeScript, in Claude Code.

> [!TIP]
> **TL;DR** — For projects on TypeScript 7: after every edit Claude makes to a TypeScript or JavaScript file, your own native `tsc` checks it with your project's settings and the strictest checks wherever those settings are silent, and Claude is told to fix what it finds before moving on. Claude also navigates your code by symbol through the TypeScript 7 language server.

## ✨ Why use it

- **Every edit is held to the strictest checks** — after each edit to a `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` or `.cjs` file, the edited code must pass `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitReturns`, `checkJs` and the rest of the plugin's strictest policy, wherever your `tsconfig.json` leaves an option unset; an option it sets itself, `false` included, stays yours. JavaScript is type-checked too, not just admitted. Claude gets every finding with the order to fix it before continuing. A compiler crash, a missing compiler or an edited file the hook skipped is reported too, never passed in silence.
- **Your project's environment, never broken by the check** — module resolution, path aliases, JSX, `lib`, `types` and `include` come from your nearest `tsconfig.json` and its project references, so the check never reports an import that works in your build.
- **No noise from code nobody touched** — the strictest policy applies to the edited files only. An error in another file is reported only when your own config also finds it, because the edit probably caused it. A broken `tsconfig.json` is reported instead of letting everything pass.
- **Your TypeScript, wherever you installed it** — the hook uses your project's `node_modules` first, then a global install, and finds `tsc` through nvm, fnm, Volta, asdf, mise, n, Homebrew, pnpm, Bun or a custom npm prefix, even when Claude Code starts without your shell profile. The plugin installs nothing.
- **The native compiler, no Node.js in the way** — the hook runs the platform binary that ships with the `typescript` package directly, so the check works even where Node.js isn't on the `PATH`.
- **Symbol navigation on TypeScript 7** — go to definition, references, hover, call hierarchy and workspace symbols through the native server. It pushes no diagnostics after edits, so the hook is where type errors come from.
- **Fixes, not silencing** — no `@ts-ignore`, `any`, `as unknown as T` or non-null `!` just to make an error disappear.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧠 LSP server | `typescript` | Starts your TypeScript 7 server (`tsc --lsp --stdio`) for `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` and `.cjs` files | Automatically when Claude opens or edits one of those files |
| 🪝 Hook | `PostToolUse` · `PostToolUseFailure` | Runs your native `tsc --noEmit` with your project's environment and the plugin's strictest policy on each TypeScript or JavaScript file an Edit, Write, Bash or PowerShell call changed | Automatically after each of those tool calls |
| 🎯 Skill | `typescript7-lsp-intelligence:ts-lifecycle` | Teaches Claude that the TypeScript 7 server pushes no diagnostics, to research a TypeScript or JavaScript change from official docs and release notes, navigate with the language server and confirm with Grep, trust results only after five checks, and prove the checks with fixtures before calling code clean | Automatically when you work on TypeScript or JavaScript, or `/typescript7-lsp-intelligence:ts-lifecycle` |

## 📋 Prerequisites

| Tool | Minimum version | Check |
| :-- | :-- | :-- |
| Claude Code | 2.1.295 | `claude --version` |
| TypeScript 7 | — | `tsc --version` |
| Node.js | 16.20.0 | `node --version` |

The language server is a global TypeScript 7 `tsc` on the `PATH` of the shell you start `claude` from; the hook uses your project's TypeScript in `node_modules` first, then the global one. Node.js runs the `tsc` command that starts the language server; the hook runs the native compiler without it. On Windows, start Claude Code from a Git Bash shell that has Node.js on its `PATH`.

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

### 🟦 TypeScript 7

If your project is still on TypeScript 6, install [TypeScript 6 LSP Intelligence](../typescript6-lsp-intelligence/README.md) instead.

<details>
<summary>🌐 <b>npm, global</b> — any platform</summary>

```bash
npm install -g typescript@7
```

</details>
<details>
<summary>📁 <b>npm, in your project</b> — any platform</summary>

```bash
npm install --save-dev typescript@7
```

</details>

### 🟢 Node.js

<details>
<summary>📥 <b>nvm</b> — macOS, Linux</summary>

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | bash
\. "$HOME/.nvm/nvm.sh"
nvm install --lts
```

</details>
<details>
<summary>🍺 <b>Homebrew</b> — macOS, Linux</summary>

```bash
brew install node
```

</details>
<details>
<summary>🍫 <b>Chocolatey</b> — Windows, in PowerShell as administrator</summary>

```powershell
powershell -c "irm https://community.chocolatey.org/install.ps1|iex"
choco install nodejs
```

</details>

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install typescript7-lsp-intelligence@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install typescript7-lsp-intelligence --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install typescript7-lsp-intelligence@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install typescript7-lsp-intelligence@the-claude-factory
```

To confirm it works, ask Claude to add a type error to a TypeScript file and fix it. The hook reports the error under the edit and, once the file is clean, a line like `typescript7-lsp-intelligence: tsc <version> · the edited files pass the strictest policy · src/app.ts`.

> [!IMPORTANT]
> Enable only one TypeScript plugin at a time. Each file extension gets one language server: with this plugin and `typescript6-lsp-intelligence` (or the official `typescript-lsp`) both enabled, only the first registered serves `.ts` files and `/plugin` → **Errors** shows the other isn't used.

## 🚀 Usage

You don't need to call anything: the language server starts with the first TypeScript file Claude edits, the hook runs after each edit, and the skill loads when you work on TypeScript or JavaScript.

When the hook reports an error or a file it couldn't check, its message also tells Claude to use the `typescript7-lsp-intelligence:ts-lifecycle` skill and apply all its knowledge when working on TypeScript and JavaScript files, so a passing or failing check is never mistaken for the whole workflow.

### Example: what happens after an edit

```text
Make loadConfig return the parsed settings instead of the raw text.
```

**Result:** Claude edits the function. If the check finds something, Claude sees it right away and has to fix it before continuing:

```text
tsc found TypeScript errors after this edit. The code does not compile until they are fixed; suppressing them with any, @ts-ignore or a cast does not fix them.

Errors in the edited files under the strictest policy, with the project environment:
src/config.ts(18,10): error TS2322: Type 'string' is not assignable to type 'Settings'.

Errors in other files of the program under the project's own config; this edit may have caused them:
src/server.ts(42,21): error TS2345: Argument of type 'Settings' is not assignable to parameter of type 'string'.
```

Claude fixes the function and the caller it broke, the hook runs again, and the turn ends with `typescript7-lsp-intelligence: tsc <version> · the edited files pass the strictest policy · src/config.ts`.

### Example: rename an export

```text
Rename formatPrice to formatMoney across the repo.
```

**Result:** Claude finds the definition and its references through the language server, loads the other `tsconfig` projects of a monorepo before trusting the list, greps `.astro`, `.svelte`, `.vue` and config files for uses the server can't see, edits only the confirmed ones, and runs `tsc` on every program it touched.

### Example: a file no program includes

```text
Add scripts/migrate.ts that renames the old config keys.
```

**Result:** The new file isn't in the `include` of any program, so the hook checks it on its own on top of your nearest `tsconfig.json`, keeping your path aliases, and tells Claude: `scripts/migrate.ts is not part of the program of tsconfig.json, its references or the tsconfig.<name>.json and jsconfig.<name>.json beside it … Add it to include or files.`

## ⚙️ Configuration

Your project decides the environment; the plugin decides how strict the edited code must be:

| Situation | What the hook does |
| :-- | :-- |
| A `tsconfig.json` or `jsconfig.json` exists above the file | `tsc --noEmit -p <that config>` with each strictest option your config chain leaves unset passed on the command line |
| Your config, or a config it extends, sets an option of the policy, at any value | Yours wins: the hook reads your config with `tsc --showConfig` and passes only the options you leave unset. Setting `strict` keeps the whole strict family yours, and an option `tsc` would reject next to your choice, such as `exactOptionalPropertyTypes` with `strictNullChecks: false`, is left out |
| That config is a solution file (`files: []` with `references`) | The referenced programs are followed to the one that lists the file |
| That config excludes the file and a sibling `tsconfig.<name>.json` or `jsconfig.<name>.json` beside it includes it, such as a `tsconfig.tests.json` for the tests | After the config and its references, the `tsconfig.<name>.json` files and then the `jsconfig.<name>.json` files are tried in name order, and the first program that lists the file checks it, with its own ambient declarations. A sibling `tsc` can't read is skipped, and so is one the config extends, such as a `tsconfig.base.json`, which is a base and not a program |
| Several changed files share a program | One `tsc` run for that program |
| The file isn't in any program | Checked alone on top of the nearest config, with its `types` and path aliases, and the report says so |
| A JavaScript file | Type-checked: `checkJs` is part of the strictest policy, so a `.js` file in your `include` is checked in its program when your config sets neither `checkJs` nor `allowJs`, or only `allowJs`. A `checkJs` or `allowJs` your config sets itself is yours |
| No config above the file | Checked alone with your compiler's own defaults for `target` and `module` (with TypeScript 6, `es2025` and `esnext`; with TypeScript 5, ES5 and CommonJS) and the strictest options; the plugin sets no environment of its own |
| Your project's `tsc` is older than an option of the policy, such as `strictBuiltinIteratorReturn` (TypeScript 5.6) | That option is left out, so the check still runs instead of failing on an unknown option, and Claude is told which options were not applied |
| Your config itself has errors | Reported, so a broken config never looks like a clean check |
| Your config uses an option deprecated in TypeScript 6, such as `baseUrl` | Reported and blocking, since it stops working in TypeScript 7; an `ignoreDeprecations` you set yourself is respected |
| The project sets `noCheck` | Ignored: the policy passes `noCheck false`, so the type check always runs |
| `tsc` crashes or exits non-zero without a TypeScript error | Reported to Claude as not checked, with the compiler's first output lines, never as a pass |
| An edited file is gone, or sits in `node_modules`, `.venv`, `venv` or `site-packages` | Claude is told it wasn't checked |
| No usable Node.js or TypeScript is found | Not blocking: you get one message per session listing where the hook searched, and Claude is told the file wasn't checked |

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

Then, in an open session:

```text
/reload-plugins
```

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update TypeScript the way you installed it, for example:

```bash
npm install -g typescript@7
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall typescript7-lsp-intelligence@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall typescript7-lsp-intelligence@the-claude-factory --scope project
```

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. Your TypeScript and your project's dependencies stay as they are.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads, but it relies on the language server, which the Claude app doesn't run |
| 🪝 Hooks | ✅ | ➖ runs only in Claude Code, next to your TypeScript |
| 🧠 LSP server | ✅ | ➖ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

Claude Code on the web doesn't start plugin language servers either, so there Claude gets no diagnostics or code navigation from this plugin.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/typescript7-lsp-intelligence:` to list its skill. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Which TypeScript does the hook check with?</b></summary>

Whichever TypeScript it finds, your project's copy first, then the global one. It doesn't compare versions, so keep the plugin and your TypeScript on the same major version: on TypeScript 6, use [TypeScript 6 LSP Intelligence](../typescript6-lsp-intelligence/README.md) instead.

</details>

<details>
<summary><b>I see "no usable TypeScript compiler was found".</b></summary>

The hook didn't find a `tsc` it could run, so it didn't block Claude but told it the file wasn't checked. The message lists every place it searched and everything it skipped. Install TypeScript 7 in your project or globally (`npm install -g typescript@7`); if it's already installed somewhere the list doesn't show, [report it](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=typescript7-lsp-intelligence) with that list.

</details>

<details>
<summary><b>The language server doesn't start.</b></summary>

Claude Code starts `tsc --lsp --stdio` by name from the `PATH` it was launched with. Run `tsc --version` in the shell you start `claude` from; it must print a 7.x version. If nothing prints, install TypeScript 7 globally. The desktop app and some IDEs don't load your shell profile, which is where nvm, fnm and Volta add Node.js to the `PATH`: start Claude Code from a terminal, or launch the IDE from one.

</details>

<details>
<summary><b>No <code>Found N new diagnostic issues</code> line appears for TypeScript files. Is the server working?</b></summary>

Yes. The native TypeScript 7 server answers navigation requests but doesn't push diagnostics after edits, so that line never appears for these files. Type errors reach Claude through the hook's check of each edit instead, and the skill teaches Claude to run the compiler itself when it needs a whole program or a caller in another file checked.

</details>

<details>
<summary><b>My project has hundreds of legacy errors. Will Claude chase them all?</b></summary>

No. The strictest policy applies to the files Claude edits. Errors in other files appear only when your own config finds them too, because the edit probably caused them. When the strictest run finds errors in other files that your config accepts, the success line gives their count instead of hiding them. Programs without a changed file are never checked.

</details>

<details>
<summary><b>The check is slow on a large program.</b></summary>

Each edit compiles the whole program; TypeScript 7's native compiler is several times faster than TypeScript 6. Splitting a huge program into project references makes each check smaller. The hook stops after 120 seconds and tells Claude it timed out, so a slow program is never passed as checked.

</details>

<details>
<summary><b>Does it check JavaScript files?</b></summary>

Yes. Unless your config sets `checkJs` or `allowJs` itself, the strictest policy turns on `checkJs`, so a JavaScript file Claude edits is type-checked from its JSDoc types, in its program when your `include` covers it and alone otherwise. JavaScript files Claude didn't touch are reported only when your own config checks them too.

</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

Through Git Bash: start Claude Code from a Git Bash shell that has Node.js and a global TypeScript 7 `tsc` on its `PATH`.

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
