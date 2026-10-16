<div align="center">

# 🟦 TypeScript 6 LSP Intelligence

<p><strong>Connects your TypeScript 6 language server to Claude Code, type-checks every file Claude edits with your own TypeScript under a strictest policy, and teaches Claude to find the program that owns a file and fix compiler findings without unsafe assertions or suppressions.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Ftypescript6-lsp-intelligence%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Language%20Support-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.295-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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
> **TL;DR** — For projects that stay on TypeScript 6: after every edit Claude makes to a TypeScript or JavaScript file, your own `tsc` checks it with your project's settings and the strictest checks on top, and Claude must fix what it finds before moving on. Claude also navigates your code by symbol through the TypeScript 6 language server.

## ✨ Why use it

- **Every edit is held to the strictest checks** — after each edit to a `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` or `.cjs` file, the edited code must pass `strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitReturns`, `checkJs` and the rest of the plugin's strictest policy, even when your `tsconfig.json` is lax or turns them off. JavaScript is type-checked too, not just admitted. Claude has to fix the findings; nothing fails in silence.
- **Your project's environment, never broken by the check** — module resolution, path aliases, JSX, `lib`, `types` and `include` come from your nearest `tsconfig.json` and its project references, so the check never reports an import that works in your build.
- **No noise from code nobody touched** — the strictest policy applies to the edited files only. An error in another file is reported only when your own config also finds it, because the edit probably caused it. A broken `tsconfig.json` is reported instead of letting everything pass.
- **Your TypeScript, wherever you installed it** — the hook uses your project's `node_modules` first, then a global install, and finds Node.js and `tsc` through nvm, fnm, Volta, asdf, mise, n, Homebrew, pnpm, Bun or a custom npm prefix, even when Claude Code starts without your shell profile. The plugin installs nothing.
- **Type errors as Claude edits, plus symbol navigation** — the TypeScript 6 server pushes diagnostics for the edited file right after each edit, and answers go to definition, references, hover, call hierarchy and workspace symbols.
- **Fixes, not silencing** — no `@ts-ignore`, `any`, `as unknown as T` or non-null `!` just to make an error disappear.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🧠 LSP server | `typescript` | Starts your `typescript-language-server` for `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` and `.cjs` files; it uses your project's TypeScript when the project has one, else the TypeScript installed beside it | Automatically when Claude opens or edits one of those files |
| 🪝 Hook | `PostToolUse` · `PostToolUseFailure` | Runs your `tsc --noEmit` with your project's environment and the plugin's strictest policy on each TypeScript or JavaScript file an Edit, Write or Bash call changed | Automatically after each of those tool calls |
| 🎯 Skill | `typescript6-lsp-intelligence:ts-lifecycle` | Teaches Claude to research a TypeScript or JavaScript change from official docs and release notes, navigate with the language server and confirm with Grep, trust results only after five checks, and prove the checks with fixtures before calling code clean | Automatically when you work on TypeScript or JavaScript, or `/typescript6-lsp-intelligence:ts-lifecycle` |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.295 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **Node.js** | 22.22.2 or later, the minimum of typescript-language-server. The hook alone runs `tsc` on Node.js 14.17 or later |
| **TypeScript 6** | In your project's `node_modules`, or installed globally. The hook uses the project's copy first |
| **typescript-language-server** | Installed globally, on the `PATH` of the shell you start `claude` from |
| **Windows** | Git Bash. Start Claude Code from a Git Bash shell that has Node.js on its `PATH` |
| **Accounts / API keys** | None |

Install the language server and TypeScript 6 globally in one step:

```bash
npm install -g typescript-language-server typescript@6
```

Name the `@6` tag: `npm install -g typescript` now installs TypeScript 7, which has no `tsserver` for this language server. If your project is on TypeScript 7, install [TypeScript 7 LSP Intelligence](../typescript7-lsp-intelligence/README.md) instead. The plugin checks with whichever TypeScript it finds and doesn't compare versions, so keep the plugin and your TypeScript on the same major version.

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install typescript6-lsp-intelligence --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install typescript6-lsp-intelligence@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install typescript6-lsp-intelligence --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install typescript6-lsp-intelligence@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

To confirm it works, ask Claude to add a type error to a TypeScript file and fix it. Under the edit you see `Found 1 new diagnostic issue in 1 file` from the language server and, once the file is clean, a line like `typescript6-lsp-intelligence: tsc passed (strictest) · src/app.ts`.

> [!IMPORTANT]
> Enable only one TypeScript plugin at a time. Each file extension gets one language server: with this plugin and `typescript7-lsp-intelligence` (or the official `typescript-lsp`) both enabled, only the first registered serves `.ts` files and `/plugin` → **Errors** shows the other isn't used.

## 🚀 Usage

You don't need to call anything: the language server starts with the first TypeScript file Claude edits, the hook runs after each edit, and the skill loads when you work on TypeScript or JavaScript.

### Example: what happens after an edit

```text
Make loadConfig return the parsed settings instead of the raw text.
```

**Result:** Claude edits the function. If the check finds something, Claude sees it right away and has to fix it before continuing:

```text
TypeScript errors detected after file edit. Fix them before continuing; do not suppress them.

Errors in the edited files under the strictest policy, with the project environment:
src/config.ts(18,10): error TS2322: Type 'string' is not assignable to type 'Settings'.

Errors in other files of the program under the project's own config; this edit may have caused them:
src/server.ts(42,21): error TS2345: Argument of type 'Settings' is not assignable to parameter of type 'string'.
```

Claude fixes the function and the caller it broke, the hook runs again, and the turn ends with `typescript6-lsp-intelligence: tsc passed (strictest) · src/config.ts`.

### Example: rename an export

```text
Rename formatPrice to formatMoney across the repo.
```

**Result:** Claude finds the definition and its references through the language server, loads the other `tsconfig` projects of a monorepo before trusting the list, greps `.astro`, `.svelte`, `.vue` and config files for uses the server can't see, edits only the confirmed ones, and runs `tsc` on every program it touched.

### Example: a file no program includes

```text
Add scripts/migrate.ts that renames the old config keys.
```

**Result:** The new file isn't in the `include` of any program, so the hook checks it on its own on top of your nearest `tsconfig.json`, keeping your path aliases, and tells Claude: `scripts/migrate.ts is not part of the program of tsconfig.json or its references … Add it to include or files.`

## ⚙️ Configuration

Your project decides the environment; the plugin decides how strict the edited code must be:

| Situation | What the hook does |
| :-- | :-- |
| A `tsconfig.json` or `jsconfig.json` exists above the file | `tsc --noEmit -p <that config>` with every strictest option passed on the command line, so it wins over the config's own value, an explicit `false` included |
| That config is a solution file (`files: []` with `references`) | The referenced programs are followed to the one that lists the file |
| Several changed files share a program | One `tsc` run for that program |
| The file isn't in any program | Checked alone on top of the nearest config, with its `types` and path aliases, and the report says so |
| A JavaScript file | Type-checked: `checkJs` is part of the strictest policy, so a `.js` file in your `include` is checked in its program even when your config only sets `allowJs`, or neither |
| No config above the file | Checked alone with the plugin's strictest config |
| Your config itself has errors | Reported, so a broken config never looks like a clean check |
| No usable Node.js or TypeScript is found | Not blocking: you get one message per session listing where the hook searched, and Claude is told the file wasn't checked |

The plugin never creates or edits a `tsconfig.json`, and it never runs a formatter or linter: Biome, Prettier and ESLint stay your project's tools, and the skill teaches Claude to run them as your `package.json` scripts do.

The language server starts one TypeScript server process instead of the usual two: `.lsp.json` sets `useSyntaxServer` to `never`, so a single semantic server answers every request and less memory is used.

**Optional, recommended:** let the hook see exactly which files a Bash command changed by adding this to your user settings (`~/.claude/settings.json`); without it the hook finds them by modification time:

```json
{
  "bashEditDiffEnabled": true
}
```

## 🔄 Updating

```bash
claude plugin update typescript6-lsp-intelligence@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **TypeScript 6 LSP Intelligence** → **Update now**. Then run `/reload-plugins`. Update TypeScript and the language server yourself, the way you installed them.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall typescript6-lsp-intelligence@the-claude-factory
```

In a session: `/plugin` → **Installed** → **TypeScript 6 LSP Intelligence** → **Uninstall**. Your TypeScript, your language server and your project's dependencies stay as they are.

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

Run `/reload-plugins`, then type `/typescript6-lsp-intelligence:` to list its skill. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>I see "no usable TypeScript compiler was found".</b></summary>

The hook didn't find a `tsc` it could run, so it didn't block Claude but told it the file wasn't checked. The message lists every place it searched and every Node.js it skipped as too old. Install TypeScript 6 in your project or globally (`npm install -g typescript@6`); if it's already installed somewhere the list doesn't show, [report it](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=typescript6-lsp-intelligence) with that list.

</details>

<details>
<summary><b>The language server doesn't start.</b></summary>

Claude Code starts `typescript-language-server` by name from the `PATH` it was launched with. Run `which typescript-language-server` in the shell you start `claude` from; if nothing prints, install it globally. The desktop app and some IDEs don't load your shell profile, which is where nvm, fnm and Volta add Node.js to the `PATH`: start Claude Code from a terminal, or launch the IDE from one.

</details>

<details>
<summary><b>I already see diagnostics after edits. What does the hook add?</b></summary>

The language server reports the edited file only, with your project's own strictness. The hook holds the edited code to the strictest policy and checks the whole program that contains it, so a caller broken by a changed signature in another file is reported too.

</details>

<details>
<summary><b>My project has hundreds of legacy errors. Will Claude chase them all?</b></summary>

No. The strictest policy applies to the files Claude edits. Errors in other files appear only when your own config finds them too, because the edit probably caused them. Programs without a changed file are never checked.

</details>

<details>
<summary><b>The check is slow on a large program.</b></summary>

Each edit compiles the whole program with TypeScript 6. Splitting a huge program into project references makes each check smaller, and the sibling TypeScript 7 plugin compiles several times faster once your project can move. The hook stops after 120 seconds and tells Claude it timed out, so a slow program is never passed as checked.

</details>

<details>
<summary><b>Does it check JavaScript files?</b></summary>

Yes. The strictest policy turns on `checkJs`, so a JavaScript file Claude edits is type-checked from its JSDoc types, in its program when your `include` covers it and alone otherwise. JavaScript files Claude didn't touch are reported only when your own config checks them too.

</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

Through Git Bash: start Claude Code from a Git Bash shell that has Node.js and `typescript-language-server` on its `PATH`.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🟦 [TypeScript 7 LSP Intelligence](../typescript7-lsp-intelligence/README.md) for projects on the native compiler · 🐍 [Python LSP Intelligence](../python-lsp-intelligence/README.md) · 🐚 [Bash LSP Intelligence](../bash-lsp-intelligence/README.md)
- 📖 [Claude Code code intelligence docs](https://code.claude.com/docs/en/plugins/code-intelligence)
- 📖 [TSConfig reference](https://www.typescriptlang.org/tsconfig/)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=typescript6-lsp-intelligence) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=typescript6-lsp-intelligence) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=typescript6-lsp-intelligence)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
