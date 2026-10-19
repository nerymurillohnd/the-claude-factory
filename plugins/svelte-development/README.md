<div align="center">

# 🧡 Svelte Development

<p><strong>Writes, reviews and migrates Svelte 5 and SvelteKit 3 code by current practice, checking every change against the official Svelte docs and autofixer, the Svelte language server and your project's own check.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fsvelte-development%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20%C2%B7%20Claude%20app-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Development-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.303-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
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

💻 Built for Claude Code, where it uses all its parts. In the Claude app its skills and the Svelte docs server work too, without the language server; see [Compatibility](#-compatibility).

> [!TIP]
> **TL;DR** — Ask for a Svelte component, a SvelteKit route, a review or a migration, and Claude writes Svelte 5 runes and SvelteKit 3 instead of the Svelte 4 and SvelteKit 2 it learned from. It reads the official docs first, runs the Svelte autofixer on every file and proves the result with your project's own `svelte-check`.

## ✨ Why use it

- **Current Svelte, not what the model remembers** — most Svelte code a model learned from is Svelte 4 and SvelteKit 2. Claude reads the official section before it uses any API, rune or config key, and writes `$state`, `$derived`, `$props`, snippets, event attributes, `#lib` imports, `$app/state` and `vite.config` configuration, matched to the versions installed in your project.
- **Every Svelte file checked before you see it** — each `.svelte`, `.svelte.ts` and `.svelte.js` file Claude writes or reviews goes through the Svelte team's autofixer, with your installed Svelte version, until no issue is left; then your project check (`npm run check`, or `svelte-check`) must report nothing new.
- **Renames and deletions that don't break other files** — Claude finds every use of a component, prop or function through the Svelte language server, searches the text for what the server can't see (route files, paths in strings, CSS classes, configuration), then breaks the declaration on purpose so your project check proves the list is complete before it edits.
- **Migrations in the right order** — on Svelte 4 or SvelteKit 2, Claude proposes the migration first and runs it Svelte before SvelteKit, because SvelteKit 3 requires Svelte 5.57.1 or later. It writes for your older version only when you say so.
- **Reviews with evidence, not opinions** — the auditor reports legacy syntax, runes misuse, SvelteKit 2 leftovers, server and client boundary leaks, CSRF and origin settings, unsafe HTML and accessibility warnings, each with a file, a line, a tool result and the official section that states the rule.
- **Your main conversation stays clean** — edits beyond a line or two and reviews run in two dedicated agents, so the docs lookups and the autofixer rounds stay in their context.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `svelte-development:svelte-best-practices` | The rules for Svelte 5 and SvelteKit 3: runes, snippets, events, routes, `load`, forms and remote functions, hooks, environment variables, config, adapters and security, plus migrations, the Svelte CLI (`sv`), Astro and Tailwind CSS. Decides when the agents take over | Automatically when you write or change Svelte or SvelteKit code, or `/svelte-development:svelte-best-practices` |
| 🎯 Skill | `svelte-development:svelte-docs-and-autofixer` | Looks up the official Svelte, SvelteKit and Svelte CLI docs, checks Svelte code with the autofixer, including code you paste in the chat, and makes playground links | Automatically when an exact API matters or you paste Svelte code, or `/svelte-development:svelte-docs-and-autofixer` |
| 🎯 Skill | `svelte-development:svelte-lsp-intelligence` | Answers where a component, prop, function or type is defined, used or called, and what a change would break, through the Svelte language server and your project check | Automatically for "is X used", "which files break if", renames and "check the project for errors", or `/svelte-development:svelte-lsp-intelligence` |
| 🤖 Agent | `svelte-development:svelte-component-editor` | Writes and edits components, `.svelte.ts`/`.svelte.js` modules and SvelteKit route files, and proves each change with the docs, the autofixer, the language server and the project check | Delegated by Claude for changes beyond one or two lines, or "use the svelte-component-editor agent" |
| 🤖 Agent | `svelte-development:svelte-code-auditor` | Audits Svelte and SvelteKit code without changing it and reports findings with file, line, severity, evidence and fix | Delegated by Claude for a review or audit, or "use the svelte-code-auditor agent" |
| 🔌 MCP server | `svelte` | The Svelte team's remote server at `https://mcp.svelte.dev/mcp`: `list-sections`, `get-documentation`, `svelte-autofixer` and `playground-link`, plus the `svelte-task` prompt and a docs resource for every section | Tools appear as `mcp__plugin_svelte-development_svelte__*`. Nothing to install |
| 🧠 LSP server | `svelte` | Starts your `svelteserver --stdio` for `.svelte` files: diagnostics after each edit, and go to definition, references, hover, implementations, call hierarchy and symbols | Automatically when Claude opens or edits a `.svelte` file |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.303 or later — check with `claude --version` |
| **Surfaces** | See [Compatibility](#-compatibility) |
| **Network access** | To `https://mcp.svelte.dev` for the docs and the autofixer |
| **svelte-language-server** | 0.18.5 or later, installed globally, with `svelteserver` on the `PATH` of the shell you start `claude` from. It needs Node.js 18 or later and brings its own TypeScript (5.9 or 6) |
| **Your project** | Svelte 5 and SvelteKit 3 for the full feature set; older majors get a migration proposal first. The project check uses the `svelte-check` your project already has |
| **Accounts / API keys** | None |

Install the language server once:

```bash
npm install -g svelte-language-server
```

Older servers fail without an error in two common cases: before 0.18.4 they don't read SvelteKit 3's configuration from `vite.config`, and before 0.18.5 they find no configuration in a project under a folder whose name starts with a dot, such as Claude Code's `.claude/worktrees/`. Check yours with `npm ls -g svelte-language-server`.

Without the language server the plugin still works: Claude tells you once, navigates by text search and relies on your project check.

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install svelte-development --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install svelte-development@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install svelte-development --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install svelte-development@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

<details>
<summary><b>🖥️ Claude app (web and desktop)</b></summary>

1. Open **Customize** in the sidebar, then **Plugins**.
2. Select **Add** → **Add marketplace** and enter `nerymurillohnd/the-claude-factory`.
3. Find **Svelte Development** in **Discover** and select **Add**.
4. On the plugin's **Connectors** tab, connect `svelte` so its docs and autofixer tools are available.

In the desktop app's **Code** tab you can also click **+** → **Plugins** → **Add plugin**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

To confirm it works, ask Claude in a Svelte project: *"Where is the Counter component used?"* The answer lists each use with its file and line, found by the language server. Run `/mcp` to see `svelte` connected.

> [!IMPORTANT]
> Svelte's own `svelte` plugin (from the `sveltejs/ai-tools` marketplace) starts the same `svelteserver` for `.svelte` files. Each file extension gets one language server, so with both plugins enabled only the first registered serves `.svelte` files and `/plugin` → **Errors** shows the other isn't used. This plugin's skills and agents keep working either way, but enable one Svelte plugin at a time to avoid two sets of Svelte skills and two Svelte MCP servers.

## 🚀 Usage

You don't need to call anything: the skills load when you work on Svelte, the language server starts with the first `.svelte` file, and Claude hands larger edits and reviews to the agents.

### Example: write a component

```text
Add a TodoList component with a text filter and a "clear done" button.
```

**Result:** Claude reads your installed Svelte and SvelteKit versions, fetches the sections it needs (`$state`, `$derived`, `$props`, each blocks), and the editor agent writes the component with runes, a keyed `{#each}` and callback props. The autofixer runs on the file until no issue is left, your project check runs, and the report lists the docs used, the checks and anything left open.

### Example: rename a prop safely

```text
Rename the `label` prop of CounterButton to `title` everywhere.
```

**Result:** Claude finds every parent that passes `label` through the language server, searches the text for uses it can't see, and runs your project check before the edit. It then renames only the declaration, so the check's new errors show every site the rename must touch, edits them all, and finishes when the check is back to where it started.

### Example: audit a migration

```text
Review the project after our upgrade to SvelteKit 3.
```

**Result:** the auditor runs your project check and the autofixer on every Svelte file in scope, searches for leftovers (`$app/stores`, `$lib/`, `$env/`, `svelte.config.js`, `on:click`, `export let`), and returns a table of findings with severity, file and line, evidence and the fix, with migration items kept apart from defects.

### Example: check code you pasted

```text
Is this component correct for Svelte 5? <your code>
```

**Result:** Claude runs the autofixer on the code, explains each issue with the official section behind it, and offers a Svelte playground link to try the fixed version.

## ⚙️ Configuration

There is nothing to configure. The plugin follows your project:

| Your project | What Claude does |
| :-- | :-- |
| Installed `svelte` and `@sveltejs/kit` (`npm ls`, `pnpm why`, `yarn why`, or the lockfile) | Writes for those versions, passes the full Svelte version to the autofixer, and uses a feature only from the minor release that added it |
| Svelte 4 or SvelteKit 2 | Proposes the migration before writing; writes for the old version only when you decline or ask it to proceed |
| A `check` script in `package.json` | Runs it as the project check; otherwise runs `svelte-kit sync` (SvelteKit only) and then your `svelte-check` |
| `compilerOptions.experimental.async` enabled | Passes the async option to the autofixer |
| A `CLAUDE.md` with your conventions | Follows your naming, layout and formatting, but never uses an API your installed version removed |

The plugin never installs a package. When something is missing (the language server, `svelte-check`, the local Svelte CLI), Claude tells you what to install and reports the result as unchecked.

> [!WARNING]
> The autofixer sends the code of each file it checks to the Svelte team's server at `mcp.svelte.dev`. Svelte states it doesn't log, store or inspect that code. If your code must not leave your machine, install Svelte's command line (`npm install -g @sveltejs/mcp`) and tell Claude: it then runs the docs and the autofixer through the local `svelte-mcp` command instead.

**Using the TypeScript 6 plugin too?** [TypeScript 6 LSP Intelligence](../typescript6-lsp-intelligence/README.md) serves `.ts` and `.js` files while this plugin serves `.svelte` files, so they work side by side. Its post-edit check passes `.svelte.ts` and `+page.ts` files once `svelte-kit sync` has generated SvelteKit's types. For the TypeScript server to find `.svelte` callers of a `.ts` function, install `typescript-svelte-plugin` in your project and list it in your `tsconfig.json`:

```json
{ "compilerOptions": { "plugins": [{ "name": "typescript-svelte-plugin" }] } }
```

**Editor diagnostics:** when Claude Code is connected to VS Code or a JetBrains IDE, the agents also read the editor's diagnostics for each file they change or audit. Without a connected IDE they rely on the language server and your project check.

## 🔄 Updating

```bash
claude plugin update svelte-development@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Svelte Development** → **Update now**. Then run `/reload-plugins`. Update `svelte-language-server` yourself with `npm install -g svelte-language-server`.

Installed from the Claude app? In Claude Code (v2.1.273+, signed in with that claude.ai account) it appears as `svelte-development@synced`: update and uninstall it in the app (**Customize** → **Plugins**); in `/plugin` you can only turn it on or off, unless your organization requires it.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall svelte-development@the-claude-factory
```

In a session: `/plugin` → **Installed** → **Svelte Development** → **Uninstall**. In the Claude app: **Customize** → **Plugins** → **Svelte Development** → its menu → **Remove**. Your `svelte-language-server` and your project's dependencies stay as they are.

## 🧭 Compatibility

**Works in:** 💻 Claude Code · 🖥️ Claude app

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ✅ for writing, reviewing and explaining code with the docs and the autofixer; no language server or project check there |
| 🤖 Agents | ✅ | ⚠️ in Cowork sessions, not in a chat conversation |
| 🔌 MCP server (remote) | ✅ | 🔗 connect `svelte` on the plugin's **Connectors** tab |
| 🧠 LSP server | ✅ | ➖ |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

Claude Code on the web doesn't start plugin language servers, so there Claude navigates by text search and relies on your project check.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's skills don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/svelte-development:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Claude says there is no code intelligence for <code>.svelte</code> files.</b></summary>

Claude Code starts `svelteserver` by name from the `PATH` it was launched with. Run `command -v svelteserver` in the shell you start `claude` from; if nothing prints, run `npm install -g svelte-language-server`, then `/reload-plugins`. The desktop app and some IDEs don't load your shell profile, which is where nvm, fnm and Volta add Node.js to the `PATH`: start Claude Code from a terminal, or launch the IDE from one. `/plugin` → **Errors** shows `Executable not found in $PATH: "svelteserver"` when the binary is missing.

</details>

<details>
<summary><b>Why doesn't the language server answer for <code>.ts</code> files?</b></summary>

The plugin maps only `.svelte` files to the Svelte server, which gives no answers for plain TypeScript. Claude starts from a `.svelte` file and still finds definitions and uses inside `.ts`, `.svelte.ts` and `#lib` modules. To start from TypeScript files too, add a TypeScript language server, as in [Configuration](#%EF%B8%8F-configuration).

</details>

<details>
<summary><b>Results look stale after I moved route files or changed <code>vite.config</code>.</b></summary>

The Svelte language server keeps the configuration it loaded, and it can lag SvelteKit 3 after route files are moved, created or deleted. Run `/reload-plugins`; if answers stay stale, restart Claude Code. Claude trusts your project check over the server whenever they disagree.

</details>

<details>
<summary><b>The project check reports nothing after a change that should fail.</b></summary>

In SvelteKit, run `npx svelte-kit sync` first: without SvelteKit's generated types the check misses errors. Also make sure the file is inside the `include` of your `tsconfig.json` and that your `check` script really runs `svelte-check`. Claude runs these checks itself before calling a silent result clean.

</details>

<details>
<summary><b>Can I keep my code from going to the remote server?</b></summary>

Yes. Install `@sveltejs/mcp` globally and tell Claude your code must stay on your machine; it then uses the local `svelte-mcp` command for the docs and the autofixer. Until a newer release of that command ships, it checks against the Svelte major version only, so it misses the one suggestion that depends on your minor version (the `class` attribute in place of the `class:` directive).

</details>

<details>
<summary><b>Does it work with Astro or Tailwind CSS?</b></summary>

Yes. Claude follows the rules for Svelte components inside an Astro site (`client:*` directives, props that must survive serialization, so no function props on a hydrated island, and slots that arrive as snippets) and for Tailwind CSS 4 with SvelteKit or Astro, including `@reference` before `@apply` in a component's `<style>`. "Unknown at rule" warnings for Tailwind's at-rules are expected from the language server and left alone.

</details>

<details>
<summary><b>Does it work on Windows?</b></summary>

Through Git Bash: start Claude Code from a Git Bash shell that has Node.js and `svelteserver` on its `PATH`.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🟦 [TypeScript 6 LSP Intelligence](../typescript6-lsp-intelligence/README.md) for the `.ts` and `.js` files of a Svelte project
- 📖 [Svelte docs](https://svelte.dev/docs) · [Svelte AI tools](https://svelte.dev/docs/ai/overview)
- 📖 [Claude Code code intelligence docs](https://code.claude.com/docs/en/plugins/code-intelligence)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=svelte-development) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=svelte-development) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=svelte-development)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo. Parts are derived from [sveltejs/ai-tools](https://github.com/sveltejs/ai-tools) (MIT); see [NOTICE.txt](./NOTICE.txt). Not affiliated with or endorsed by the Svelte project.
