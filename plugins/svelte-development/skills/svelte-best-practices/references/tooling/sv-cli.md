# The sv command line

> Precedence: changelogs and source code win over the docs, and the docs win over this file.

## Contents

- [Fetch before writing when](#fetch-before-writing-when)
- [Running sv and the Node.js floor](#running-sv-and-the-nodejs-floor)
- [sv create: templates and flags](#sv-create-templates-and-flags)
- [sv add: shared flags and option syntax](#sv-add-shared-flags-and-option-syntax)
- [Official add-ons: options and written files](#official-add-ons-options-and-written-files)
- [The ai-tools add-on and Claude Code](#the-ai-tools-add-on-and-claude-code)
- [Testing with the vitest and playwright add-ons](#testing-with-the-vitest-and-playwright-add-ons)
- [Formatting: prettier-plugin-svelte and prettier-plugin-tailwindcss](#formatting-prettier-plugin-svelte-and-prettier-plugin-tailwindcss)
- [sv check: a passthrough to svelte-check](#sv-check-a-passthrough-to-svelte-check)
- [sv migrate: task-based and legacy migrations](#sv-migrate-task-based-and-legacy-migrations)
- [Community add-ons](#community-add-ons)
- [Official sources](#official-sources)

## Fetch before writing when

- The project's `sv`, `svelte-check`, `prettier-plugin-svelte` or `prettier-plugin-tailwindcss` is newer than the versions above.
- You need an add-on option value that is not listed here; the typed options live in each add-on's source file.
- You run `sv migrate`: read the migration guide and the task list first:

  ```sh
  npx sv migrate sveltekit-3 --tasks   # lists the tasks without running them
  ```

## Running sv and the Node.js floor

- Run it as `npx sv <command>`; inside a project that has `sv` installed, `npx` uses the local copy. In a pnpm, Bun, Yarn or Deno project (its lockfile says which), use that manager's executor instead: `pnpm dlx sv`, `bunx sv`, `yarn dlx sv`, `deno run npm:sv`.
- Every command checks the running Node.js against `22.17.0` and prints a warning below it, then continues (`src/core/common.ts`, `runCommand`). SvelteKit 3 itself declares `engines.node >=22.17`, so treat 22.17 as the real minimum.
- `sv` is non-interactive when every choice is given on the command line; pass the add-on options, `--install <pm>` or `--no-install`, and `--no-git-check` for scripted runs.

## sv create: templates and flags

```sh
npx sv create my-app --template minimal --types ts --add eslint prettier --install pnpm
```

| Flag | Effect |
| --- | --- |
| `--template minimal\|demo\|library\|addon` | `minimal` is bare scaffolding, `demo` a no-JS word game, `library` uses `svelte-package`, `addon` scaffolds a community add-on |
| `--types ts\|jsdoc`, `--no-types` | TypeScript files, JSDoc types, or no type checking |
| `--add <add-ons…>` | Applies add-ons during create, same syntax as `sv add` |
| `--no-add-ons` | Skips the add-on prompt; conflicts with `--add` |
| `--from-playground <url>` | Builds a project from a Svelte playground URL, enabling `experimental.async` when the Svelte version allows it |
| `--addon-name <name>` | Package name for the `addon` template |
| `--install <npm\|pnpm\|yarn\|bun\|deno>`, `--no-install` | Installs with that package manager, or skips installing |
| `--no-dir-check` | Does not stop on a non-empty directory |
| `--no-download-check` | Does not warn before downloading community add-ons |

New projects use `#lib` subpath imports instead of `$lib` (sv 1.0.0) and keep the Svelte and SvelteKit options inside `vite.config` (sv 0.16.0), not in `svelte.config.js`.

## sv add: shared flags and option syntax

```sh
npx sv add tailwindcss="plugins:typography" vitest="usages:unit,component" --install npm
```

- Options attach to the add-on name: `name="option:value"`, several options joined with `+`, several values with `,`. Example: `drizzle="database:postgresql+client:postgres.js+docker:yes"`.
- Flags: `-C, --cwd <path>`, `--no-git-check` (no warning on uncommitted changes), `--no-download-check`, `--install <pm>`, `--no-install`.
- Commit before running `sv add`; it rewrites existing files such as `vite.config`, `package.json` and `.vscode/*.json`.

## Official add-ons: options and written files

| Add-on | Options (default first where one exists) | What it writes |
| --- | --- | --- |
| `ai-tools` | `ide` (claude-code, cursor, gemini, opencode, vscode, other), `delivery` (plugin, tools), `tools` (mcp, svelte-code-writer, svelte-core-bestpractices, svelte-file-editor), `mcpSetup` (local, remote) | See the next section |
| `better-auth` | `demo` (password, github) | Better Auth with Drizzle as the adapter, email and password sign-in, optional demo pages; Kit only, pulls in `drizzle` when `drizzle-orm` is absent |
| `drizzle` | `database` (sqlite, postgresql, mysql, d1); client per database: postgresql (postgres.js, neon), mysql (mysql2, planetscale), sqlite (libsql, node-sqlite, better-sqlite3, turso); `docker` (no, yes; only postgres.js or mysql2) | Server-side database module, `drizzle.config`, `.env` credentials, optional Docker Compose. `d1` targets Cloudflare D1 and prints next steps when the Cloudflare adapter is missing; Kit only |
| `enhanced-img` | none | `@sveltejs/enhanced-img` Vite plugin, rewrites eligible `<img>` to `<enhanced:img>`, allows the `sharp` build under pnpm |
| `eslint` | none | `eslint.config.js` with `eslint-plugin-svelte`, TypeScript and Prettier integration when present, `.vscode/extensions.json` |
| `experimental` | `features` (async, remoteFunctions; forkPreloads is offered but off by default) | Sets `compilerOptions.experimental.async`, `experimental.remoteFunctions` or `experimental.forkPreloads` in the project config. The add-on exists in the `sv` source but the `sv add` docs page does not list it. |
| `mdsvex` | none | Adds `mdsvex({ extensions: ['.svx', '.md'] })` to `preprocess` and the extensions to `extensions` |
| `paraglide` | `languageTags` (BCP 47 list), `demo` (yes, no) | Inlang settings, Paraglide Vite plugin, `reroute` and `handle` hooks, `lang` and text direction in `app.html`, `.gitignore` entries; Kit only |
| `playwright` | `demo` (yes, no; added in sv 1.1.0) | `@playwright/test`, a Playwright config, `test:e2e` script that runs `playwright install` first, `.gitignore`, and the `/demo/playwright` page plus test only when `demo` is on |
| `prettier` | none | `prettier.config.js` (JSDoc-typed; replaced `.prettierrc` in sv 0.16.2), `.prettierignore`, `lint` and `format` scripts, `eslint-config-prettier` when ESLint is present |
| `storybook` | none | Runs `create-storybook@latest`; always applied after `vitest` and `eslint` |
| `sveltekit-adapter` | `adapter` (auto, node, static, vercel, cloudflare, netlify), `cfTarget` (workers, pages; Cloudflare only) | Installs and configures the adapter; Kit only |
| `tailwindcss` | `plugins` (typography, forms) | `tailwindcss` and `@tailwindcss/vite` (^4.3.0), the Vite plugin prepended to `plugins`, `@import 'tailwindcss'` in `src/routes/layout.css` imported by `src/routes/+layout.svelte` (`src/app.css` and `App.svelte` outside Kit), VS Code settings, Prettier plugin when Prettier is present |
| `vitest` | `usages` (unit, component) | `vitest` ^4.1, client and server test projects in the Vite config, demo tests, scripts |

## The ai-tools add-on and Claude Code

- `delivery: plugin` for `claude-code` writes only `.claude/settings.json`: it adds `extraKnownMarketplaces.svelte` (GitHub `sveltejs/ai-tools`) and sets `enabledPlugins["svelte@svelte"]` to `true` (`src/addons/ai-tools.ts`). Anyone who trusts the folder gets the official Svelte plugin installed.
- `delivery: tools` instead writes `.mcp.json`, `AGENTS.md`, `.claude/CLAUDE.md` importing `AGENTS.md`, and the chosen skills and subagents under `.claude/skills` and `.claude/agents`.
- Before running it in a project that already uses this plugin, decide which set of Svelte skills you want; two plugins with overlapping skills compete for the same prompts.

## Testing with the vitest and playwright add-ons

```sh
npx sv add vitest="usages:unit,component" playwright="demo:no"
```

- Component tests run in Vitest browser mode through `@vitest/browser-playwright` (sv adopted Vitest 4). Name component test files `*.svelte.spec.ts` (or `.test`) so runes compile in them.
- Playwright tests match `**/*.e2e.{ts,js}`; `npm run test:e2e` installs browsers and runs them.

## Formatting: prettier-plugin-svelte and prettier-plugin-tailwindcss

- `prettier-plugin-svelte` 4 requires Svelte 5 and removed the `svelteBracketNewLine` and `svelteStrictMode` options; delete them from old configs. 4.1.0 formats Svelte 5 declaration tags.
- `prettier-plugin-tailwindcss` 0.8.0 combined with `prettier-plugin-svelte` 4 silently stopped sorting classes in Svelte markup and `class={…}` expressions; 0.8.1 restored it. Require `^0.8.1`; sv writes `^0.8.0`, which resolves to a fixed version on a fresh install but not in an old lockfile.
- 0.8.x needs Prettier 3.7 or newer. Load the Tailwind plugin last and point `tailwindStylesheet` at the stylesheet that imports Tailwind:

```js
// prettier.config.js
/** @type {import('prettier').Config} */
export default {
  plugins: ["prettier-plugin-svelte", "prettier-plugin-tailwindcss"],
  overrides: [{ files: "*.svelte", options: { parser: "svelte" } }],
  tailwindStylesheet: "./src/routes/layout.css",
};
```

## sv check: a passthrough to svelte-check

`sv check` accepts `-C, --cwd` and forwards every other argument to the project's own `svelte-check` (`src/cli/check.ts`); it exits with an install hint when `svelte-check` is missing. The user installs it with `npm i -D svelte-check`; ask before changing dependencies.

| svelte-check flag | Use |
| --- | --- |
| `--output human\|human-verbose\|machine\|machine-verbose` | Output format; machine formats print one timestamped record per line, ending with `COMPLETED` |
| `--watch`, `--preserveWatchOutput` | Keep running and recheck on change |
| `--tsconfig <path>`, `--no-tsconfig` | Diagnose only files the config includes, or only `.svelte` files |
| `--config <path>` | Non-standard `svelte.config` or `vite.config` location (4.7.0) |
| `--fail-on-warnings` | Exit non-zero on warnings |
| `--threshold warning\|error` | Show errors and warnings, or errors only |
| `--compiler-warnings "code:ignore,code:error"` | Remap Svelte compiler warnings |
| `--diagnostic-sources "js,svelte,css"` | Limit diagnostic sources |
| `--incremental`, `--tsgo` | Disk-cached svelte2tsx output, or tsgo for TypeScript diagnostics; both write to `.svelte-kit` or `.svelte-check` |
| `--workspace <path>`, `--ignore "a,b"` | Workspace root; `--ignore` only narrows diagnosis with `--no-tsconfig` |

When no `--output` is given and `CLAUDECODE=1` is set, svelte-check selects `machine` output instead of `human-verbose` (`src/options.ts`, lines 130 to 133). Inside Claude Code the default output is therefore already machine-readable.

## sv migrate: task-based and legacy migrations

```sh
npx sv migrate sveltekit-3 --tasks            # list the tasks without running them
npx sv migrate sveltekit-3 --tasks environment # run one selectable task
```

- Task-based migrations in sv: `sveltekit-3` and `app-state`. The two prerequisite tasks (`package-json`, `tsconfig`) always run. The code registers ten selectable tasks: `svelte-config`, `environment`, `paths`, `external-redirects`, `shallow-routing`, `params`, `imports`, `lib-alias`, `app-state`, `collect-migration-instructions`. The docs list only nine tasks in total.
- Run one task at a time and commit after each. After a task, sv formats with the project's `format` or `fmt` script, or Prettier, then offers to install dependencies. Search for `@migration-task` comments before calling the migration complete.
- Legacy migrations (`svelte-5`, `svelte-4`, `sveltekit-2`, `self-closing-tags`, `package`, `routes`) delegate to `svelte-migrate@1` and receive no fixes.
- Flags for both kinds: `--cwd <path>`, `--no-git-check`, `--confirm`. Task-based only: `--tasks [ids…|all|prerequisite]`, `--files <glob>` (an escape hatch that can leave the project inconsistent), `--install <pm>`, `--no-install`.

## Community add-ons

- Any npm package can be an add-on: `npx sv add my-addon`, `npx sv add @org/sv`, or the shorthand `npx sv add @org` for a package named `sv`. A local add-on uses a `file:` path.
- Svelte maintainers do not review community add-ons; sv warns before downloading one unless `--no-download-check` is set. Read the package before running it.
- Scaffold one with `npx sv create --template addon`; sv 1.0.0 made the add-on API official.

## Official sources

Fetch the CLI sections the task touches in one call:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["cli/sv-add", "cli/sv-check"]
```

Sections: `cli/overview`, `cli/sv-create`, `cli/sv-add`, `cli/sv-check`, `cli/sv-migrate`, and one per add-on (`cli/tailwind`, `cli/vitest`, `cli/playwright`, `cli/drizzle` …; the docs map lists them all). Without the MCP server, download the raw text:

```sh
curl -sS 'https://svelte.dev/docs/cli/sv-check/llms.txt'
```


- sv docs, whole package: https://svelte.dev/docs/cli/llms.txt
- sv changelog: https://raw.githubusercontent.com/sveltejs/cli/main/packages/sv/CHANGELOG.md
- sv add-on sources (options): https://github.com/sveltejs/cli/tree/main/packages/sv/src/addons
- sv check source: https://raw.githubusercontent.com/sveltejs/cli/main/packages/sv/src/cli/check.ts
- svelte-check options source: https://raw.githubusercontent.com/sveltejs/language-tools/master/packages/svelte-check/src/options.ts
- svelte-check changelog: https://raw.githubusercontent.com/sveltejs/language-tools/master/packages/svelte-check/CHANGELOG.md
- prettier-plugin-svelte changelog: https://raw.githubusercontent.com/sveltejs/prettier-plugin-svelte/master/CHANGELOG.md
- prettier-plugin-tailwindcss changelog: https://raw.githubusercontent.com/tailwindlabs/prettier-plugin-tailwindcss/main/CHANGELOG.md
