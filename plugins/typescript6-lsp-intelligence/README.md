<div align="center">

# 🟦 TypeScript 6 LSP Intelligence

<p><strong>TypeScript and JavaScript code intelligence for Claude Code: connects your TypeScript 6 language server (LSP), type-checks every file Claude edits with your own <code>tsc --strict</code> under your project's <code>tsconfig</code>, and teaches Claude to find the program that owns a file and fix compiler diagnostics without unsafe assertions or suppressions.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Ftypescript6-lsp-intelligence%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
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

💻 **Claude Code only** — it connects a language server, and only Claude Code runs language servers. Claude can install it, but there the language server doesn't start and the post-edit hook runs only where Claude can run tasks and finds your TypeScript 6 and Node.js.

> [!TIP]
> **TL;DR** — For projects that stay on TypeScript 6: after every edit Claude makes to a TypeScript or JavaScript file, your own `tsc --noEmit --strict` checks it under your project's `tsconfig.json`, and Claude gets every error in the files it changed to fix before moving on. Claude also navigates your code by symbol through the TypeScript 6 language server.

TypeScript 6 LSP Intelligence connects the TypeScript 6 language server you install to Claude Code and adds a hook that runs your project's own `tsc` after each edit. Your `tsconfig.json` decides the environment; `--strict` turns on the strict family wherever your config doesn't set an option itself. With each prompt, the plugin also tells Claude to use a skill that researches a change from official sources, navigates with the language server and proves its checks before it calls code clean.

## ✨ Why use it

- **Compiler errors reach Claude as it edits** — after each Edit, Write or Bash call that changes a `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` or `.cjs` file, and when a batch of parallel tool calls ends, your own `tsc` checks every file Claude changed since your last prompt. Claude gets each error with its file, line and column. A compiler that can't run, doesn't type-check, or isn't TypeScript 6 is reported to you and to Claude, never passed in silence.
- **Your project's environment, no second opinion** — `tsc` loads your nearest `tsconfig.json` as it does from a terminal, so module resolution, path aliases, JSX, `lib`, `types` and `include` come from your config. `--strict` applies the strict family even where your config says `"strict": false`; a strict option you set explicitly keeps its value.
- **No noise from code nobody touched, and fixes instead of silencing** — errors only in files Claude didn't change let it continue, and you see how many there are. The skill teaches Claude to navigate by symbol with the language server and to fix a finding without `@ts-ignore`, `any`, `as unknown as T` or a non-null `!` just to make it disappear.

## 🧩 What's inside

| Component     | Name                                                        | What it does                                                                                                                                                                                                                                                                             | How it runs                                                                                                             |
| :------------ | :---------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| 🧠 LSP server | `typescript`                                                | Starts your `typescript-language-server` for `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs` and `.cjs` files; it uses your project's TypeScript when the project has one, else the TypeScript installed beside it                                                                  | Automatically when Claude opens or edits one of those files                                                             |
| 🪝 Hook       | `PostToolUse` on `Edit\|Write` and `Bash` · `PostToolBatch` | Runs your project's own `tsc --noEmit --pretty false --strict` under your project's `tsconfig.json` on every TypeScript or JavaScript file Claude changed since your last prompt, and sends Claude the errors in them                                                                    | Automatically after each Edit, Write or Bash call, and when a batch of parallel tool calls ends                         |
| 🪝 Hook       | `UserPromptSubmit`                                          | Tells Claude to call the `typescript6-lsp-intelligence:ts-6-writing-and-navigation` skill with the Skill tool and apply it end to end before it creates, writes or edits a TypeScript or JavaScript file, with any tool or command, and starts a new list of the files changed this turn | Automatically with each prompt                                                                                          |
| 🎯 Skill      | `typescript6-lsp-intelligence:ts-6-writing-and-navigation`  | Teaches Claude to research a TypeScript or JavaScript change from official docs and release notes, navigate with the language server and confirm with Grep, trust results only after five checks, and prove the checks with fixtures before calling code clean                           | Automatically when you work on TypeScript or JavaScript, or `/typescript6-lsp-intelligence:ts-6-writing-and-navigation` |

## 📋 Prerequisites

| Tool                       | Minimum version | Check                                                                       |
| :------------------------- | :-------------- | :-------------------------------------------------------------------------- |
| Claude Code                | 2.1.295         | `claude --version`                                                          |
| Bash                       | 3.2             | `bash --version`                                                            |
| Node.js                    | 22.22.2         | `node --version`                                                            |
| TypeScript 6               | —               | `npx --no-install tsc --version` (project copy) or `tsc --version` (global) |
| typescript-language-server | —               | `typescript-language-server --version`                                      |

The plugin also uses `sed`, `awk`, `grep`, `tr`, `cut`, `head`, `sort`, `find`, `paste`, `dirname`, `basename`, `mktemp`, `mkdir`, `rm`, `cp` and `cat`, which come with macOS and Linux.

Node.js 22.22.2 is the minimum of typescript-language-server; the hook alone runs on Node.js 14.17 or later, the minimum of `tsc`. Node.js must be on the `PATH` of the shell you start `claude` from: the hook reads each event with it, and without it the check doesn't run. For the check, the hook uses the nearest `node_modules/.bin/tsc` above the edited file, else the first `tsc` on your `PATH`, and only when that `tsc` is TypeScript 6. Install typescript-language-server globally, on the same `PATH`. Claude Code runs the hook with `bash` 3.2 or later, which macOS and Linux ship.

### 🐚 Bash

macOS and Linux ship Bash 3.2 or later.

### 🤖 Claude Code

Already installed? Bring it to the latest version the way you installed it, as the official [Update Claude Code](https://code.claude.com/docs/en/setup#update-claude-code) guide shows for each installation method. New to Claude Code? Follow the [official setup](https://code.claude.com/docs/en/setup).

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

### 🟦 TypeScript 6

Name the `@6` tag: without it, npm installs TypeScript 7, which has no `tsserver` for this language server. The plugin uses TypeScript 6 only.

<details>
<summary>🌐 <b>npm, global</b> — any platform</summary>

```bash
npm install -g typescript@6
```

</details>
<details>
<summary>📁 <b>npm, in your project</b> — any platform</summary>

```bash
npm install --save-dev typescript@6
```

</details>

### 🧠 typescript-language-server

<details>
<summary>📦 <b>npm, with TypeScript 6</b> — any platform</summary>

```bash
npm install -g typescript-language-server typescript@6
```

</details>
<details>
<summary>📦 <b>npm</b> — any platform</summary>

```bash
npm install -g typescript-language-server
```

</details>

## 📥 Installation

### 💻 Terminal

```bash
claude plugin marketplace add nerymurillohnd/the-claude-factory
claude plugin install typescript6-lsp-intelligence@the-claude-factory
```

In one step (Claude Code v2.1.292+):

```bash
claude plugin install typescript6-lsp-intelligence --marketplace nerymurillohnd/the-claude-factory
```

For everyone working in the current repository:

```bash
claude plugin install typescript6-lsp-intelligence@the-claude-factory --scope project
```

No GitHub SSH key? Run this first:

```bash
export CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1
```

### 💬 Inside a Claude Code session

```text
/plugin marketplace add nerymurillohnd/the-claude-factory
/plugin install typescript6-lsp-intelligence@the-claude-factory
```

To confirm it works, ask Claude to add a type error to a TypeScript file and fix it. You see a line like `typescript6-lsp-intelligence: tsc --noEmit --pretty false --strict found 1 issue in src/app.ts (tsc 6.0.3 (/your/project/node_modules/.bin/tsc) in /your/project); Claude received them to fix.` and, once the file is clean, `typescript6-lsp-intelligence: tsc --noEmit --pretty false --strict: the compiler completed without diagnostics under the project's configuration (src/app.ts; tsc 6.0.3 (/your/project/node_modules/.bin/tsc) in /your/project).`

Enable only one plugin that serves TypeScript files at a time. Each file extension gets one language server: with two such plugins enabled, only the first registered serves `.ts` files and `/plugin` → **Errors** shows the other isn't used.

## 🚀 Usage

You don't need to call anything: the language server starts with the first TypeScript file Claude edits, the hook runs after each edit, and the skill loads when you work on TypeScript or JavaScript. To load the skill yourself, type `/typescript6-lsp-intelligence:ts-6-writing-and-navigation`.

With each prompt you send, the plugin tells Claude to call that skill with the Skill tool and apply it end to end before it creates, writes or edits a TypeScript or JavaScript file. When the hook finds errors in the files Claude changed, its message names the skill again for fixing them.

### Example: what happens after an edit

```text
Make loadConfig return the parsed settings instead of the raw text.
```

**Result:** Claude edits the function. If your `tsc` finds errors in the file, Claude sees them right away and fixes them before continuing:

```text
Unresolved type errors in files changed this turn (src/config.ts), from tsc --noEmit --pretty false --strict:
src/config.ts:18:10  TS2322  Type 'string' is not assignable to type 'Settings'.
The skill "typescript6-lsp-intelligence:ts-6-writing-and-navigation" (loaded with the Skill tool when it is not in context) covers navigating with the LSP tool and Grep to fix them.
```

You see a line like `typescript6-lsp-intelligence: tsc --noEmit --pretty false --strict found 1 issue in src/config.ts (tsc 6.0.3 (…) in …); Claude received them to fix. 1 issue in other files (their pre-existence was not verified).` An error only in a file Claude didn't change, such as a caller in `src/server.ts`, isn't sent to Claude: you get that count. Once Claude edits `src/server.ts`, the hook checks it too, and when no error is left you see `typescript6-lsp-intelligence: tsc --noEmit --pretty false --strict: the compiler completed without diagnostics under the project's configuration (src/config.ts, src/server.ts; tsc 6.0.3 (…) in …).`

### Example: rename an export

```text
Rename formatPrice to formatMoney across the repo.
```

**Result:** Claude finds the definition and its references through the language server, loads the other `tsconfig` projects of a monorepo before trusting the list, greps `.astro`, `.svelte`, `.vue` and config files for uses the server can't see, edits only the confirmed ones, and runs `tsc` on every program it touched.

### Example: a file your tsconfig leaves out

```text
Add packages/app/scripts/migrate.ts that renames the old config keys.
```

**Result:** The nearest `tsconfig.json`, `packages/app/tsconfig.json`, only includes `src`, so `tsc` doesn't list the new file in its program and can't type-check it. You and Claude are told: `not type-checked: packages/app/scripts/migrate.ts (not part of the program of packages/app/tsconfig.json).` Add the file to that config's `include` or `files` to have it checked.

## ⚙️ Configuration

Your project decides the environment, and `--strict` decides how strict the check is. The plugin has no options of its own. This is what the hook does with what it finds in your project:

| What the hook finds                                                                                                        | What it does                                                                                                                                                                                                                           |
| :------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A `tsconfig.json` at or above the edited file's folder                                                                     | Runs `tsc --noEmit --pretty false --strict --listFiles --extendedDiagnostics` from the nearest folder that holds one, so `tsc` loads that config as it does from a terminal. Several changed files that share that folder get one run. |
| Your config sets a strict option itself, such as `"strict": false` or `"noImplicitAny": false`                             | `--strict` turns the strict family on wherever your config doesn't set an option; an option you set explicitly keeps its value.                                                                                                        |
| A config that only lists `references`, or one that doesn't include the changed file                                        | Names the file as not type-checked, with the config that leaves it out, to you and to Claude.                                                                                                                                          |
| No `tsconfig.json` above the file                                                                                          | Checks the changed TypeScript files together with your compiler's defaults and `--strict`. A changed JavaScript file there is named as not type-checked.                                                                               |
| A JavaScript file under a `tsconfig.json`                                                                                  | `tsc` type-checks it only when its program has `checkJs` or the file starts with `// @ts-check`. The hook doesn't tell you when neither applies.                                                                                       |
| `skipLibCheck` skips a changed `.d.ts` file                                                                                | The hook doesn't tell you.                                                                                                                                                                                                             |
| `tsc` reports no check time: a broken `tsconfig.json`, a missing type library, a syntax error in another file or `noCheck` | You and Claude are told the changed files were not type-checked, with the errors that stopped `tsc`.                                                                                                                                   |
| A `tsc` that is not TypeScript 6                                                                                           | Not used: you and Claude are told, and what to do about type checking is left to you.                                                                                                                                                  |
| No `tsc` in the nearest `node_modules/.bin` or on your `PATH`                                                              | The check is skipped, with a message to you and to Claude. A Yarn Plug'n'Play project, which has no `node_modules/.bin/tsc`, uses the first `tsc` on your `PATH`.                                                                      |
| Errors only in files Claude didn't change                                                                                  | Claude isn't sent them and continues; you see how many there are.                                                                                                                                                                      |
| `tsc` stops with a status above 2                                                                                          | The check is reported as skipped, with the status.                                                                                                                                                                                     |
| `tsc` prints output the hook can't read, or exits non-zero without a diagnostic                                            | The hook fails and blocks, because the changed files were not verified.                                                                                                                                                                |
| No Node.js on your `PATH`                                                                                                  | The check doesn't run, and you get a message. Nothing blocks.                                                                                                                                                                          |

The plugin never edits your `tsconfig.json`. The only one it creates in your project is the temporary fixture config the skill's script writes and deletes, as [What this plugin runs and sends](#-what-this-plugin-runs-and-sends) describes. It never runs a formatter or linter: Biome, Prettier and ESLint stay your project's tools, and the skill teaches Claude to run them as your `package.json` scripts do.

`.lsp.json` sets `useSyntaxServer` to `never`, so one full TypeScript server answers every request. While a project loads, the default lighter syntax server answers navigation requests such as `findReferences` and `goToDefinition` from partial information, so the first answer of a session can come back incomplete or wrong. With `never`, the first answer is slower and complete, and one process fewer runs. Diagnostics come from the full server in both modes.

**Optional:** after a Bash call, the hook checks only the files Claude Code lists as changed by it, in a Git repository. Claude Code records them in auto and `bypassPermissions` modes, and in every mode once you add this to your user settings (`~/.claude/settings.json`):

```json
{
  "bashEditDiffEnabled": true
}
```

## 🔍 What this plugin runs and sends

- **Hooks:**
  - `PostToolUse` on `Edit|Write` runs `bash hooks/tsc-check.sh` (120-second limit, `onFailure` set to block), which type-checks the file the call edited, plus the files changed earlier in the turn, with your project's own `tsc --noEmit --pretty false --strict` and sends Claude the errors in them.
  - `PostToolUse` on `Bash` runs the same script on the files Claude Code lists as changed by the command (`bashEditDiff`).
  - `PostToolBatch` runs the same script when a batch of parallel tool calls ends, on every file the batch's Edit and Write calls changed, so a file one check misses during a parallel edit is still checked.
  - `UserPromptSubmit` runs two commands, each with a 60-second limit: `cat hooks/typescript6-lsp-skill-instructions.txt`, which adds a short instruction to each prompt you send (before Claude creates, writes or edits a TypeScript or JavaScript file, with any tool or command, it calls the `typescript6-lsp-intelligence:ts-6-writing-and-navigation` skill with the Skill tool and applies it end to end, including its LSP and Grep steps), and `bash hooks/tsc-check.sh --new-turn`, which clears the list of files changed this turn. They send nothing.

  The script reads each event with `node -e`, finds the nearest `tsconfig.json` above each changed file and runs `tsc` once per folder that holds one, from that folder; a changed file with no `tsconfig.json` above it is checked on its own, with the other such files in its folder. It uses the nearest `node_modules/.bin/tsc` above the file, else the `tsc` on your `PATH`, only when it reports TypeScript 6, and installs nothing. It lists the files that changed (`--listFiles`) and reads `tsc`'s own timing report (`--extendedDiagnostics`) to tell whether `tsc` type-checked at all. If the hook fails unexpectedly, `onFailure` blocks the action instead of letting it pass. Hooks run on their own, with your access and without a permission prompt.
- **MCP servers:** none.
- **Network:** the hook makes no network calls. The skill tells Claude to read official docs and release notes through the first that works: WebFetch or WebSearch, `curl` to the official domain (such as typescriptlang.org), or `gh` on the official GitHub repository (such as `microsoft/TypeScript`). Each runs under your own permission rules.
- **Files written:** the hook keeps the list of files changed this turn in `${CLAUDE_PLUGIN_DATA}/turns/<session>-<agent>.list`, one absolute path per line, clears it with each prompt you send, and deletes files in that folder older than 7 days. When that variable is unset or empty, it keeps no list, checks only the files of the current call and tells you. It also makes a temporary folder with the event data, `tsc`'s output and `tsc`'s build-info file (so a config with `incremental` or `composite` writes nothing into your project) and deletes it when it exits. The skill's `scripts/run-fixtures.sh` creates one `lsp-fixture-XXXXXX/` folder at a time in your program's `rootDir`, or beside the owning `tsconfig.json`; each holds a fixture `.ts` file and its own `tsconfig.json`, which extends yours, and the script deletes it after the check. With `--outside`, it uses a temporary folder outside your project instead. Claude Code asks you before the skill runs this script; choose **Yes, and don't ask again** to let it run the script without asking. Neither the hook nor the skill edits your source files or your `tsconfig.json`.
- **Privacy:** the author collects no data. The marketplace's [privacy policy](https://github.com/nerymurillohnd/the-claude-factory/blob/main/PRIVACY.md) covers this plugin and the outside services it can reach.

## 🔄 Updating

```bash
claude plugin update typescript6-lsp-intelligence@the-claude-factory
```

Then, in an open session:

```text
/reload-plugins
```

> [!TIP]
> Auto-update is off for this marketplace until you turn it on: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

Update TypeScript and the language server the way you installed them, for example:

```bash
npm install -g typescript-language-server@latest typescript@6
```

## 🗑️ Uninstalling

```bash
claude plugin uninstall typescript6-lsp-intelligence@the-claude-factory
```

Installed with `--scope project`:

```bash
claude plugin uninstall typescript6-lsp-intelligence@the-claude-factory --scope project
```

Uninstalling from the last scope it's installed at also deletes its saved options and data directory, unless you add `--keep-data`. The data directory holds only the lists of files changed in a turn, under `turns/`. Your TypeScript, your language server and your project's dependencies stay as they are.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component      | Claude Code |                       Claude                        |
| :------------- | :---------: | :-------------------------------------------------: |
| 🎯 Skills      |     ✅      |                         ✅                          |
| 🪝 Hooks       |     ✅      | ⚠️ only in conversations where Claude can run tasks |
| 🧠 LSP servers |     ✅      |                         ➖                          |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. Claude runs agents, hooks and local MCP servers only in conversations where it can run tasks; anything on your computer needs Claude Desktop open.</sub>

The skill loads in Claude, but it relies on the language server, which Claude doesn't run. The hook runs `tsc` with Node.js, so it works only on a machine where TypeScript 6 and Node.js are installed; in Claude Code that's your computer. Claude Code on the web doesn't start plugin language servers either, so there Claude gets no diagnostics or code navigation from this plugin.

**Platforms:** macOS and Linux.

## 🚧 Limitations

- The check is for TypeScript 6 only. A `tsc` that isn't TypeScript 6 is not used, and what to do about type checking is left to you.
- The hook runs on macOS and Linux only. Windows isn't supported.
- After a Bash call, the hook sees only the files Claude Code lists as changed by it. Claude Code records them in a Git repository, in auto and `bypassPermissions` modes or when `bashEditDiffEnabled` is on, and it leaves out files Git ignores. Other Bash changes are not type-checked.
- The hook doesn't run after PowerShell calls or after a Bash call that fails.
- It doesn't tell you when `skipLibCheck` skips a changed `.d.ts` file, or when a changed JavaScript file has neither `checkJs` nor `// @ts-check`, so `tsc` didn't check it.
- A changed file your `tsconfig.json` leaves out, including under a config that only lists `references`, is named as not type-checked. Without a `tsconfig.json` above it, a changed JavaScript file isn't type-checked either.
- Claude gets the errors in the files it changed this turn, at most 100 lines at a time. Errors only in other files are not sent to Claude; you see their count, and the hook doesn't check whether they existed before the edit.
- Without Node.js on your `PATH`, the check doesn't run. Without `CLAUDE_PLUGIN_DATA`, it checks only the files of the current call.
- The hook never installs a compiler. Yarn Plug'n'Play projects, which have no `node_modules/.bin/tsc`, use the first `tsc` on your `PATH`.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/typescript6-lsp-intelligence:` to list its skill. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Which TypeScript does the hook check with?</b></summary>

Your project's own `tsc`: the nearest `node_modules/.bin/tsc` above the edited file, else the first `tsc` on your `PATH`. It uses that `tsc` only when it reports TypeScript 6. Otherwise it skips the check and tells you and Claude, and leaves the choice of what to do to you.

</details>

<details>
<summary><b>I see "this plugin checks TypeScript 6 only".</b></summary>

The `tsc` the hook found isn't TypeScript 6, for example a project whose `tsc` is TypeScript 7. The hook didn't run that `tsc` over Claude's edits and told you and Claude instead. Install TypeScript 6 in your project, or put a TypeScript 6 `tsc` first on your `PATH`:

```bash
npm install --save-dev typescript@6
```

</details>

<details>
<summary><b>I see "no tsc in the project's node_modules/.bin or on PATH".</b></summary>

The hook didn't find a `tsc` it could run, so it didn't block Claude but told it the check didn't run. Install TypeScript 6 in your project or globally:

```bash
npm install -g typescript@6
```

If it's already installed and you still see the message, [report it](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=typescript6-lsp-intelligence).

</details>

<details>
<summary><b>I see "tsc check did not run: Node.js was not found on PATH".</b></summary>

The hook reads each event with Node.js, so without it the check doesn't run, and nothing blocks. Put Node.js on the `PATH` of the shell you start `claude` from.

</details>

<details>
<summary><b>Claude edited a file with a Bash command and nothing was checked.</b></summary>

After a Bash call, the hook sees only the files Claude Code lists as changed by it, and only in a Git repository. Claude Code records them in auto and `bypassPermissions` modes. To record them in every mode, add this to your user settings (`~/.claude/settings.json`):

```json
{
  "bashEditDiffEnabled": true
}
```

</details>

<details>
<summary><b>The language server doesn't start.</b></summary>

Claude Code starts `typescript-language-server` by name from the `PATH` it was launched with. Run this in the shell you start `claude` from:

```bash
which typescript-language-server
```

If nothing prints, install it globally. The desktop app and some IDEs don't load your shell profile, which is where nvm, fnm and Volta add Node.js to the `PATH`: start Claude Code from a terminal, or launch the IDE from one.

</details>

<details>
<summary><b>I already see diagnostics after edits. What does the hook add?</b></summary>

The language server pushes diagnostics for the file Claude edited, on a later turn or never, depending on the server. The hook runs your own `tsc --strict` right after each edit and sends Claude the errors in every file it changed since your last prompt, so Claude fixes them before it moves on. It also counts the errors in files Claude didn't change, such as a caller a changed signature broke, and shows you the number.

</details>

<details>
<summary><b>My project has hundreds of legacy errors. Will Claude chase them all?</b></summary>

No. Claude gets the errors in the files it changed since your last prompt, including any that file already had. Errors only in other files aren't sent to Claude: you see how many there are, and the hook doesn't check whether they existed before the edit. Programs without a changed file are never checked.

</details>

<details>
<summary><b>The check is slow on a large program.</b></summary>

Each check compiles the whole program that owns a changed file with TypeScript 6. Splitting a huge program into several `tsconfig.json` projects makes each check smaller. The hook has a 120-second limit, and `onFailure` is set to block, so a check that can't finish isn't passed in silence.

</details>

<details>
<summary><b>Does it check JavaScript files?</b></summary>

Only as `tsc` does. Under a `tsconfig.json`, `tsc` type-checks a JavaScript file when its program has `checkJs` or the file starts with `// @ts-check`; `allowJs` alone adds the file to the program without checking it. The hook doesn't tell you when neither applies. With no `tsconfig.json` above the file, a changed JavaScript file is named as not type-checked.

</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

No. The hook runs on macOS and Linux only.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 📖 [Claude Code plugin docs](https://code.claude.com/docs/en/plugins/overview)
- 📖 [Claude Code code intelligence docs](https://code.claude.com/docs/en/plugins/code-intelligence)
- 📖 [Claude Code hooks reference](https://code.claude.com/docs/en/hooks)
- 📖 [TSConfig reference](https://www.typescriptlang.org/tsconfig/)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=typescript6-lsp-intelligence) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=typescript6-lsp-intelligence) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=typescript6-lsp-intelligence)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Not affiliated with or endorsed by Microsoft Corporation. _TypeScript_ is a trademark of Microsoft Corporation. Not affiliated with or endorsed by Anthropic. _Claude_ and _Claude Code_ are trademarks of Anthropic.
