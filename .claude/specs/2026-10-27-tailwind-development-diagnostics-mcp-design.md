# tailwind-development: Tailwind CSS diagnostics through a bundled MCP server

Status: approved by Nery on 2026-10-27 with every recommendation of section 7; decision 5 pins `vscode-jsonrpc` 9.0.3 (2026-09-25). Implementation follows the plan on branch `feat/tailwind-development-diagnostics-mcp`.

## 1. Goal

Give Claude the Tailwind CSS language server's diagnostics after every edit of a file the user chose, in any project that uses Tailwind CSS, without taking any file extension away from another language server the user runs.

The user decides, per group of file types, which files get the automatic check. A user with no other language server leaves every group on and gets the check on every type the server supports. A user who runs another server for `.svelte` or `.tsx` keeps it: this plugin never claims an extension.

## 2. Why not `.lsp.json`

Checked on 2026-10-27 against the official docs and Claude Code 2.1.311 (no plugin or LSP entry in the changelog after 2.1.310 changes this).

- Each file extension gets one language server. When two enabled servers claim it, the first registered wins and the other is not used for those files (`/en/plugins/components`, LSP servers).
- In an LSP server config, `${...}` resolves only in `command`, `args`, `env` and `workspaceFolder` (`/en/plugins/manifest-reference`, Where each variable resolves). `extensionToLanguage` is fixed, so a `userConfig` choice cannot change which extensions the server claims.
- No setting turns off one plugin's LSP server. `enabledPlugins` turns off the whole plugin.
- The LSP recommendation dialog offers a marketplace's LSP plugin when the plugin's binary is installed. With `command: "node"` that holds for nearly every user, so users who only added this marketplace could be offered this plugin on their first `.css`, `.html`, `.vue` or `.astro` edit. Unverified whether the check reads `command` alone.

Mods were also reviewed (types of 2.1.311): they have no LSP API, `$.process.spawn` cannot hold a two-way stdio conversation, they run in Claude Code only, and the plugin directory lists a plugin with a mod as Claude Code only. A `settings.read` hook cannot help: no setting controls plugin LSP servers.

### 2.1 Why not an existing LSP-to-MCP bridge

Checked on 2026-10-27 (GitHub API, npm registry):

| Bridge | Why not |
| :-- | :-- |
| `isaacphi/mcp-language-server` (BSD-3-Clause) | Go: users would need `go install`, which the plugin's npm dependency install cannot provide. Ships write tools (`edit_file`, `rename_symbol`), against a read-only design. Last release v0.1.1, 2025-05 |
| `Tritlo/lsp-mcp` (MIT) | Last push 2025-07, on `@modelcontextprotocol/sdk` ^0.5.0, not published to npm under its own name |
| `lsp-mcp-server` on npm (`ProfessioneIT/lsp-mcp-server`, MIT) | Generic, on SDK 1.x and its 17 dependencies, one maintainer |
| VS Code LSP MCP extensions | Need VS Code running; nothing the plugin can declare for strangers |

They share two gaps that matter here. A `PostToolUse` hook reaches Claude only through `additionalContext` JSON, which a generic `diagnostics` tool does not return. And the Tailwind CSS server asks its client for `workspace/configuration`, which a generic bridge may not answer. The pattern they prove (an MCP server that owns a language server process) is the one this design uses.

## 3. Design

### 3.1 Components

| Component | Path | Job |
| :-- | :-- | :-- |
| MCP server (stdio, Node, plain ES module, no build step) | `.mcp.json`, server key `tailwindcss`; code in `mcp/server.mjs` | Starts the Tailwind CSS language server on first use, keeps it running for the session, and answers the plugin's tools |
| `PostToolUse` hook, `type: "mcp_tool"` | `hooks/hooks.json` | After `Edit` or `Write`, calls the server's check tool with `${tool_input.file_path}` and returns the diagnostics to Claude as `additionalContext` |
| Runtime dependencies | `package.json`, `package-lock.json` | `@tailwindcss/language-server` 0.16.0 (MIT), `@modelcontextprotocol/server` 2.3.1 (Apache-2.0, with `@modelcontextprotocol/core` and `zod` (MIT): four packages in all), pinned exactly; Claude Code installs them when it caches the plugin |
| `userConfig` | `.claude-plugin/plugin.json` | One boolean per file-type group (3.3), and the language-server settings of 3.8 |

No `bin/`, no `.lsp.json`, no mod. Identities, by the formulas in `building-plugins` (`references/mcp-hooks-and-lifecycle.md`):

| Purpose | Value |
| :-- | :-- |
| `mcp_tool.server` | `plugin:tailwind-development:tailwindcss` |
| Callable tool | `mcp__plugin_tailwind-development_tailwindcss__<tool>` |
| Matcher for the whole server | `^mcp__plugin_tailwind-development_tailwindcss__.*$` |

### 3.2 Flow

1. Claude Code starts the MCP server with the session. The server does not start the language server yet.
2. Claude edits or writes a file. The `PostToolUse` hook calls `check_file` with the file's path and `format: "hook"`.
3. The server checks the file's extension against the groups the user turned on. Outside them, it answers with no output and the hook adds nothing.
4. On the first matching file, the server starts `node <plugin root>/node_modules/@tailwindcss/language-server/bin/tailwindcss-language-server --stdio` with the project root (`CLAUDE_PROJECT_DIR`) as its workspace, and initializes it.
5. It sends the file's current text (`didOpen`, or `didChange` for a file already open), waits for `textDocument/publishDiagnostics` for that file, up to a bounded wait, and answers the hook with the diagnostics as `additionalContext`. No diagnostics: no output.
6. The language server stays up for the session; Claude Code stops the MCP server, and with it the language server, when the session ends.

A project without Tailwind CSS gets no diagnostics: the language server finds no Tailwind project and reports nothing. The language server activates only when `tailwindcss` is installed in the project through npm, pnpm or yarn, and for v4 only from a `.css` entry point (`@import "tailwindcss"`); Less, Sass and Stylus files cannot hold a v4 configuration (`vscode-tailwindcss` README, Troubleshooting). The automatic check stays silent then; an explicit `check_file`, `class_css` or `project_classes` call answers that no Tailwind CSS project was found and why.

### 3.3 File-type groups

The language server 0.16.0 accepts the language ids below (read from its bundled code). Each group is one `boolean` option, default `true`, reaching the server through `env` as `${user_config.<key>}`.

| Option key | Title | Extensions → language id |
| :-- | :-- | :-- |
| `check_css` | CSS and preprocessors | `.css` css, `.scss` scss, `.sass` sass, `.less` less, `.pcss` `.postcss` postcss, `.styl` stylus, `.sss` sugarss (preprocessor files are checked for their class use; they cannot be a v4 entry point) |
| `check_html` | HTML | `.html` `.htm` html |
| `check_js_ts` | JavaScript and TypeScript | `.js` `.mjs` `.cjs` javascript, `.jsx` javascriptreact, `.ts` `.mts` `.cts` typescript, `.tsx` typescriptreact |
| `check_vue` | Vue | `.vue` vue |
| `check_svelte` | Svelte | `.svelte` svelte |
| `check_astro` | Astro | `.astro` astro |
| `check_markdown` | Markdown and MDX | `.md` markdown, `.mdx` mdx |
| `check_templates` | Server templates | `.php` php, `.erb` erb, `.twig` twig, `.liquid` liquid, `.hbs` `.handlebars` handlebars, `.njk` nunjucks, `.ejs` ejs, `.haml` haml, `.slim` slim, `.heex` phoenix-heex, `.razor` razor, `.cshtml` aspnetcorerazor, `.gohtml` gohtml, `.mustache` mustache, `.jade` jade, `.latte` latte, `.edge` edge, `.leaf` leaf |

The options show in the install dialog, in `/plugin` → Configure options and as rows of `/config`.

### 3.4 Tools

All tools of the server are visible to Claude in every conversation, so the surface stays small (one tool per action, `build-mcp-server` → `references/tool-design.md`):

| Tool | Input | Output |
| :-- | :-- | :-- |
| `check_file` | `file_path`; `format`: `"text"` (default) or `"hook"` | The file's Tailwind CSS diagnostics, each with its line, rule and message and, when the server offers a quick fix (`codeAction` of kind `quickfix`, such as "Replace with '…'" or "Delete …"), the exact current text and replacement. With `"hook"`, the same inside the `PostToolUse` JSON as `additionalContext` |
| `class_css` | `classes` (space-separated), optional `file_path` for the project context | The CSS each class generates in this project (hover, with pixel equivalents of `rem` values), and for color classes the resolved color (`textDocument/documentColor`) |
| `sort_classes` (decision 7) | `classes` (space-separated), optional `file_path` | The same classes in Tailwind CSS's official order |
| `project_classes` | `prefix` (required, at least one character, such as `bg-` or `font-`), optional `file_path` for the project context, `limit` (default 50, at most 200) | The class names that exist in this project's theme for that prefix, from the server's completion, with the count of the rest past the limit |

Only the server's diagnostics, quick fixes, hover, colors and completion are used. It has no definition, reference, rename, formatting or symbol support, and code lenses and document links add nothing for Claude, so no tool exposes them. Generic LSP bridges list some 40 tools; three keep the context cost low.

**Writes stay with Claude.** No tool applies an edit: the fixes come back as text for Claude to apply with `Edit`, so every change shows the user its diff, goes through Claude Code's permission flow and is covered by checkpoints and rewind, which do not track a file an MCP server writes itself. A prompt-injected call can at worst read.

Each tool carries the annotations `title`, `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` and `openWorldHint: false`, and tight zod schemas with a `describe` on every field. Descriptions say what the tool does, what it returns and what it does not do; they never tell Claude how to behave. A failure answers `isError: true` with a text that says what to do next, never a crash of the transport. No server `instructions`: every line of them is always-on context, and the tool descriptions carry what Claude needs.

### 3.5 MCP protocol

`@modelcontextprotocol/server` with `serveStdio(createServer)`, as the 2026-07-28 build-server guide shows. `serveStdio` answers both the 2026-07-28 revision (`server/discover`), which Claude Code's v2 client runtime asks for, and the 2025-era `initialize` handshake of the v1 runtime (`/en/mcp`, MCP client runtimes). `createServer` returns a new `McpServer` per call, as the guide requires; the language-server child lives at module level, so a discarded discovery instance does not start or lose it. A hand-written server would have to implement both handshakes, which is why the SDK is used.

2.3.1 rather than 2.4.0: 2.4.0 was published on 2026-10-23, four days before this spec; 2.3.1 (2026-10-05) exports `serveStdio` too. Revisit at implementation.

### 3.6 Language-server protocol client

Inside `mcp/server.mjs`. Framing (`Content-Length`), request ids and notifications either written by hand or taken from `vscode-jsonrpc` (MIT, Microsoft, no dependencies, the library the language server itself speaks through); decision 5. It answers the requests the language server sends to its client: `workspace/configuration` (the `tailwindCSS` settings of 3.8), `client/registerCapability`, `window/workDoneProgress/create`.

The server also speaks custom messages under `@/tailwindCSS/` (read from the bundled code of 0.16.0; the same ones the VS Code extension and editor clients such as tailwind-tools.nvim use). The client uses three kinds:

- **Readiness**: `@/tailwindCSS/getProject` (`{ uri }` → `{ version }`, or null while no loaded project covers the document). The client opens the document, polls it until it answers or a 20-second bound passes, then sends the text again so the server lints it with the loaded project. `serverReady` and `documentReady` exist but the server sends them only in its `testMode` (read in the bundled code of 0.16.0), so they are not used. Measured on a v4.3.3 fixture: 1.5 s to the first diagnostics, 0.5 s warm.
- **Project facts**: `getProject` and `projectDetails`, to say in an explicit tool answer which entry point or config file and which Tailwind CSS version the server found, or that it found none.
- **Sorting**: `sortSelection`, the official class order (the one `prettier-plugin-tailwindcss` applies), for `sort_classes` if decision 7 keeps it. Nothing is written to stdout except protocol messages: logs go to stderr only, in the MCP server and from the child.

### 3.8 Language-server settings

The server answers `workspace/configuration` itself, so these settings never depend on what the MCP client supports. Names and defaults from the `vscode-tailwindcss` README in `tailwindlabs/tailwindcss-intellisense` (main, 2026-10-27):

| Setting | Value sent | Source |
| :-- | :-- | :-- |
| `tailwindCSS.classFunctions` | The `class_functions` option: a `multiple` string list of regexes on function names. The server's default is empty, so without it the classes inside `clsx(...)`, `cn(...)` or `cva(...)` get no diagnostics | `userConfig`, decision 6 |
| `tailwindCSS.classAttributes` | The `class_attributes` option, a `multiple` string list. Default as the server's: `class`, `className`, `ngClass`, `class:list` | `userConfig` |
| `tailwindCSS.experimental.configFile` | The `config_file` option: one path to the v4 CSS entry point (or v3 config file), relative to the project root, empty by default for auto-detection. Needed in monorepos and projects with several `@import "tailwindcss"` stylesheets. The object form for several entry points is left out of `userConfig`; marked experimental by Tailwind Labs | `userConfig` |
| `tailwindCSS.validate`, `codeActions`, `hovers`, `suggestions` | `true` | Fixed |
| `tailwindCSS.lint.*` | The server's defaults (`suggestCanonicalClasses`, `cssConflict`, `recommendedVariantOrder` as warnings, the rest as errors) | Fixed |
| `tailwindCSS.showPixelEquivalents`, `rootFontSize` | `true`, `16` | Fixed |
| `tailwindCSS.colorDecorators` | `true`: the server answers `textDocument/documentColor` only with it on (measured: an empty list with `false`), and `class_css` reports colors from it | Fixed |
| `tailwindCSS.emmetCompletions`, `inspectPort` | Off or `null`: an editor feature with no use here; `inspectPort` would open a debugger port | Fixed |

### 3.9 Local security (`build-mcpb` → `references/local-security.md`)

Tool inputs are untrusted, even from Claude: a prompt-injected page can make Claude call a tool with any path.

- **Root.** `CLAUDE_PROJECT_DIR`, which Claude Code sets for stdio servers. `roots/list` is not used: protocol revision 2026-07-28 removed server-to-client requests (SEP-2577), so the SDK's `listRoots` throws on that era and the replacement is a multi-round-trip `input_required` result; `@modelcontextprotocol/server` 2.3.1 marks `listRoots` deprecated and advises passing paths as tool parameters or configuration. Directories added with `--add-dir` are therefore outside what the tools read. Every `filePath` is resolved, its real path taken, and refused when it leaves the root.
- **Read only.** No tool writes, deletes or runs anything the input names. The only process started is the language server, by a fixed argv with no shell.
- **Caps.** Files above 1 MB are not sent to the language server; the answer says so. Diagnostics per answer are capped, with the count of the rest.
- **No secrets** are read, logged or returned.

## 4. What the plugin does on the host (README disclosures)

- At install and update, Claude Code runs npm to download the four pinned packages of 3.1 from the npm registry into the plugin's cached copy. No install scripts run.
- In every session where the plugin is enabled, a Node process (the MCP server) runs for the session, and after the first matching edit a second one (the language server).
- The language server reads the project's files to find its Tailwind CSS configuration and watches them while it runs. It writes nothing to the project.
- After each `Edit` or `Write`, the hook sends the edited file's path to the plugin's own server; nothing leaves the machine. Runtime network use by the language server: none expected, to verify (section 8).
- Prerequisites: Node 20 or later and npm on `PATH` (`engines` of `@modelcontextprotocol/server`; the language server asks for 18).

## 5. Surfaces

- Claude Code: full.
- Claude app: the skills work everywhere as today. The MCP server and the hook run only in Cowork sessions on the user's computer (`docs/compatibility.md`); whether the dependency install runs there is unverified. Cowork is a secondary target: it must not break, it need not be proven before release. `metadata.surfaces` stays `["claude-code", "claude-app"]`.

## 6. Already on the branch

`plugins/tailwind-development/package.json` (`private`, MIT, one dependency `@tailwindcss/language-server` `0.16.0`) and `package-lock.json` (`lockfileVersion` 3, one package, `https` registry link with integrity). The language server has no runtime dependencies of its own. Implementation adds `@modelcontextprotocol/server` 2.3.1 to both files.

## 7. Decisions for Nery

1. **MCP protocol: the official SDK 2.x, decided in 3.5.** The earlier draft recommended a hand-written server, against `@modelcontextprotocol/sdk` 1.32.2 and its 17 direct dependencies (express, hono, jose and others). The split SDK 2.x (`@modelcontextprotocol/server`) needs only `core` and `zod`, and serves both protocol revisions Claude Code speaks, which a hand-written server would have to reimplement.
2. **Defaults of the groups.** Recommended: all on, as section 1 says. Alternative: all on except `check_js_ts`, where most users already run a TypeScript server (which this design does not disturb either way).
3. **Do the explicit tools follow the groups?** My call: no. The groups decide the automatic check after edits; `check_file`, `class_css` and `project_classes` work on any supported type when Claude asks.
4. **Version:** a new component, so `0.2.0` (minor), through `release-and-versioning`.
5. **LSP framing: `vscode-jsonrpc` or by hand.** Recommended: `vscode-jsonrpc`, one more pinned package with no dependencies, against roughly a hundred lines of framing and id bookkeeping to own and test. Pin a version at least two weeks old (10.0.0 was published 2026-10-22).
6. **Default of `class_functions`.** Recommended: `clsx`, `cn`, `cva`, `tw`, `twMerge`: the helpers most Tailwind CSS projects wrap classes in. A name a project does not use costs nothing. Alternative: empty, as the server ships.
7. **A fourth tool, `sort_classes`.** Input: `classes`, optional `file_path`. Output: the same classes in Tailwind CSS's official order, from `@/tailwindCSS/sortSelection`, for Claude to apply with `Edit`. Useful where a project sorts classes with `prettier-plugin-tailwindcss`, so new markup matches it; one more tool description in every session. Recommended: include it.

## 8. Verification

Static, while building (`building-plugins` step 5): `check-manifest-schema.py`, `check-mcp-schema.py`, `claude plugin validate --strict`, and the repository's `tsc` strict check on `mcp/server.mjs`.

Live, run by Nery in a separate session with `--plugin-dir` after `npm ci` in the plugin folder (that flag loads the plugin in place and skips the dependency install), with the prompts I provide; later the `testing-plugins` live MCP checks before release:

0. Before any session: `npx @modelcontextprotocol/inspector --cli node mcp/server.mjs --protocol-era modern --method tools/list`, then the same with `--protocol-era legacy`. Both list `check_file` and `class_css`.
1. The server connects (`/mcp` shows `plugin:tailwind-development:tailwindcss`) and its tools carry the callable names of 3.1.
2. An edit that introduces a Tailwind conflict (`flex block`) in a `.html` file returns diagnostics to Claude on the first edit of the session, and how long that first check takes.
3. A later edit returns diagnostics fast (warm server).
4. Turning a group off in `/config` stops the check for its files in the same session, without a restart. Also shows how a boolean reaches `env` (`true` or `"true"`).
5. With another LSP plugin enabled for `.svelte`, both work: its diagnostics and ours.
6. A project without Tailwind CSS: no output, no errors.
7. The language server makes no network requests at runtime.
7b. With `class_functions` at its default, a misspelled class inside `cn("...")` in a `.tsx` file gets a diagnostic; with the option emptied in `/config`, it does not.
7c. `check_file` with a path outside the session's roots (`../../etc/hosts`, a symlink that leaves the project) answers `isError` and reads nothing.
8. `claude plugin details` from an HTTPS install of the branch: the dependency is installed in the cached copy, and the always-on token cost of the tools.

## 9. Not in this change

- The phase 2 scanner (`scan-v4-traps.mjs`) and its plan file: after this lands, check which of its traps the language server already reports, so the scanner keeps only what the server misses.
- An MCPB bundle: the fallback if Cowork proves not to install the dependency. `build-mcpb` calls MCPB the sanctioned way to ship a local server without a toolchain; here the plugin is the distribution channel and its users already run Node for Tailwind CSS, so the reviewable source and lockfile win over a binary zip of about 10 MB.
- Elicitation, sampling, resources, prompts and MCP app widgets: no tool needs input mid-call, a model, or a UI.

## 10. Sources

- `/en/mcp` (raw, 2026-10-27): stdio `CLAUDE_PROJECT_DIR`, `roots/list`, MCP client runtimes v1 and v2; `@modelcontextprotocol/server` 2.3.1 type declarations (`listRoots` deprecated by SEP-2577).
- `https://modelcontextprotocol.io/docs/2026-07-28/develop/build-server` (2026-10-27): `@modelcontextprotocol/server`, `serveStdio`, stdout rule, Inspector `--protocol-era`.
- `/en/hooks` (`mcp_tool`), `/en/plugins/components`, `/en/plugins/manifest-reference`, `/en/plugins/loading` (dependency install), `/en/plugins/code-intelligence`.
- Skills: `building-plugins` (`references/mcp-servers.md`, `references/mcp-hooks-and-lifecycle.md`), `.claude/rules/plugins/mcp-component.md`, `mcp-server-dev:build-mcp-server` (`tool-design.md`, `server-capabilities.md`), `mcp-server-dev:build-mcpb` (`local-security.md`). The `mcp-server-dev` references were last verified in 2026-03, before revision 2026-07-28; where they differ (the SDK package and `StdioServerTransport`), the 2026-07-28 guide wins.
- `tailwindlabs/tailwindcss-intellisense` (main, 2026-10-27): `packages/vscode-tailwindcss/README.md` (settings, lint rules, Troubleshooting) and `packages/tailwindcss-language-server/README.md` (`--stdio`); the server's capabilities read from the bundled code of 0.16.0, the latest release (2026-07-17).
- npm registry: `@tailwindcss/language-server` 0.16.0, `@modelcontextprotocol/server` 2.3.1 and 2.4.0, `@modelcontextprotocol/sdk` 1.32.2.
