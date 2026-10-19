# SvelteKit Project Structure and Configuration

> Precedence: the SvelteKit changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").
>
> Applies to SvelteKit 3 projects. A SvelteKit 2 project migrates first ([migrating-to-kit-3.md](migrating-to-kit-3.md)); write SvelteKit 2 code only when the user declines the migration or the request says to proceed without questions.

## Contents

- [Required versions](#required-versions)
- [Project layout](#project-layout)
- [Configuration lives in the Vite plugin](#configuration-lives-in-the-vite-plugin)
- [Top-level options](#top-level-options)
- [Options removed or changed in 3.0](#options-removed-or-changed-in-30)
- [The lib alias](#the-lib-alias)
- [TypeScript configuration](#typescript-configuration)
- [Server-only and remote modules](#server-only-and-remote-modules)
- [Tracing and instrumentation](#tracing-and-instrumentation)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Required versions

`@sveltejs/kit` 3.0.0 declares these peers and engines on npm: Node `>=22.17`, `vite ^8.0.12`, `svelte ^5.57.1`, `@sveltejs/vite-plugin-svelte ^7.0.0`, and `typescript ^6.0.0` (an optional peer: if the project uses TypeScript, it must be 6 or later). `@sveltejs/kit`, `svelte` and `vite` belong in `devDependencies`, and `package.json` has `"type": "module"`.

## Project layout

```text
src/
  lib/                     library code, imported through #lib
  routes/                  the router (required)
  service-worker/          index.ts plus its own tsconfig.json
  app.html                 page template (required)
  error.html               last-resort error page
  env.ts                   explicit environment variables
  params.ts                all route param matchers
  hooks.server.ts  hooks.client.ts  hooks.ts
  instrumentation.server.ts
static/                    files served as-is
vite.config.ts  tsconfig.json  package.json
```

- `app.html` placeholders: `%sveltekit.head%`, `%sveltekit.body%` (wrap it in a `<div>`, not directly in `<body>`), `%sveltekit.assets%`, `%sveltekit.nonce%`, `%sveltekit.version%`, and `%sveltekit.env.NAME%` for a public variable declared in `src/env.ts`.
- `error.html` supports `%sveltekit.status%` and `%sveltekit.error.message%`.
- Files inside a route directory without a `+` prefix are ignored by the router, so colocate components and helpers there. Since 3.0, `+` files whose names contain `test`, `spec` or `stories` (for example `+page.test.ts`) are ignored too.
- `.svelte-kit/` (the `outDir`) is generated; never commit or edit it.
- Paths resolve against the Vite `root` option rather than `process.cwd()` since 3.0, which matters in monorepos and Vitest workspaces.

## Configuration lives in the Vite plugin

Since 3.0, all Svelte and SvelteKit configuration is passed to `sveltekit(...)` in `vite.config.*`. `svelte.config.js` is not read: the plugin calls `vite-plugin-svelte` with `configFile: false`. The former `kit.*` options become top-level plugin options, next to `compilerOptions`, `extensions` and `preprocess`. Options SvelteKit does not use (for example `inspector`) are forwarded to `vite-plugin-svelte`, and the `experimental` namespace is shared between the two.

```ts
// vite.config.ts
import adapter from "@sveltejs/adapter-node";
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    sveltekit({
      adapter: adapter(),
      compilerOptions: { experimental: { async: true } },
      paths: { origin: "https://www.example.com" },
      csrf: { trustedOrigins: ["https://payments.example.com"] },
    }),
  ],
});
```

Configuration in `vite.config.*` was accepted from 2.62 onward, so a 2.x project can move it before upgrading.

## Top-level options

| Option | Notes |
| --- | --- |
| `adapter` | Runs on `vite build`; see the adapters reference. |
| `alias` | Deprecated since 3.0; use `package.json` subpath imports. |
| `appDir` | Default `"_app"`. |
| `csp` | `mode` (`'hash'`, `'nonce'`, `'auto'`), `directives`, `reportOnly`. |
| `csrf` | `trustedOrigins` only; protection cannot be switched off. |
| `embedded` | `true` attaches listeners to the parent of `%sveltekit.body%`. |
| `env.dir` | Directory searched for `.env` files. |
| `experimental` | `remoteFunctions`, `forkPreloads` (both default `false`). |
| `files` | Deprecated (still supported); `files.lib` is gone. |
| `inlineStyleThreshold` | Inline CSS files below this length. |
| `moduleExtensions` | Default `[".js", ".ts"]`. |
| `outDir` | Default `".svelte-kit"`. |
| `output` | `linkHeaderPreload` (default `false`), `bundleStrategy` (`'split'`, `'single'`, `'inline'`). |
| `paths` | `base`, `assets`, `origin`, `relative`. |
| `prerender` | `concurrency`, `crawl`, `entries`, `handle*` error handlers. |
| `router` | `type` (`'pathname'`, `'hash'`), `resolution` (`'client'`, `'server'`). |
| `serviceWorker` | `register`, `options`. |
| `tracing` | `{ server: boolean }`. |
| `typescript.config` | Deprecated; edit `tsconfig.json` directly. |
| `version` | `name` (deterministic, such as a commit hash) and `pollInterval` (default 3600000 ms). |

## Options removed or changed in 3.0

- Removed: `files.lib`, `experimental.handleRenderingErrors`, `experimental.instrumentation`, `vitePlugin` (pass its options directly), `output.preloadStrategy` (`modulepreload` is always used), `prerender.origin` (use `paths.origin`) and `csrf.checkOrigin` (use `csrf.trustedOrigins`).
- Moved: `experimental.tracing` is the top-level `tracing`.
- Added: `paths.origin` (the public origin for CSRF checks and prerendering; on `adapter-node` it replaces the `ORIGIN` variable), `csrf.trustedOrigins`, `output.linkHeaderPreload`.
- Changed: `version.pollInterval` defaults to one hour instead of no polling.

The live config reference still lists some removed options (`checkOrigin`, `preloadStrategy`) with a "removed in 3.0" tag; do not write them.

## The lib alias

`$lib` is no longer generated. Declare `#lib` with Node subpath imports, which Vite and TypeScript resolve natively; `npx sv create` writes this into the projects it scaffolds:

```json
{
  "imports": {
    "#lib": "./src/lib/index.js",
    "#lib/*": "./src/lib/*"
  }
}
```

Because the mapping is literal, imports need the file extension: `import { db } from '#lib/server/db.js'`, `import Card from '#lib/Card.svelte'`. An import such as `#lib/utils` without an extension fails to resolve, even where an example in the docs omits it.

## TypeScript configuration

`tsconfig.json` extends the generated `$app/tsconfig` (written to `node_modules/$app/tsconfig.json`) and must declare its own `include` and `exclude`:

```json
{
  "extends": "$app/tsconfig",
  "include": ["src", "test", "*"],
  "exclude": ["src/service-worker"]
}
```

- Do not override `paths` (derived from subpath imports and the deprecated `alias`), `isolatedModules` or `verbatimModuleSyntax` (both must stay `true`). If you set `types`, keep `"$app/types"` in it.
- The service worker is a separate TypeScript project: `src/service-worker/tsconfig.json` extends `$app/tsconfig/service-worker`, and the root config excludes that folder. SvelteKit warns when the exclusion is missing.

## Server-only and remote modules

A module is server-only, and importing it from browser code fails the build, when:

- its filename has a `server` segment: `server.ts`, `db.server.ts`, `db.server.test.ts` (since 3.0, a file named exactly `server.ts` counts too); or
- it sits in any `server` directory except inside `src/routes` and `static`, for example `src/lib/server/db.ts` or `src/lib/data/server/user.ts` (in 2.x only `src/lib/server` counted).

`$app/env/private` and `$app/server` are server-only as well. The check follows indirect and dynamic imports, so re-exporting a secret from a shared module still fails. Modules in `node_modules` are exempt; a package marks a module server-only by adding `import '$app/server'` at its top. The check is disabled when `process.env.TEST === 'true'`, so unit tests do not prove the boundary holds.

A `remote` segment marks a remote module (`posts.remote.ts`, `remote.ts`). Since 3.0, such a file is an error unless `experimental.remoteFunctions` is enabled.

## Tracing and instrumentation

- `src/instrumentation.server.ts` is loaded automatically, before app code, when the adapter supports it; no flag is required since 3.0.
- `tracing: { server: true }` emits OpenTelemetry spans for `handle`, `load`, form actions and remote functions. It has a real cost; consider enabling it only outside production.

## Fetch before writing when

- You add or rename a config option, or meet an option not listed here.
- You configure `csp`, `paths`, `router.resolution`, `prerender` handlers or `output`.
- You set up a monorepo, a custom `outDir`, or the deprecated `files` option.
- Type-checking reports `tsconfig` or path-alias problems.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["kit/project-structure", "kit/@sveltejs-kit-vite"]
```

Sections: `kit/project-structure`, `kit/@sveltejs-kit-vite`, `kit/$lib`, `kit/$app-tsconfig`, `kit/$app-tsconfig-service-worker`, `kit/server-only-modules`, `kit/observability`, `kit/migrating-to-sveltekit-3`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/kit/project-structure/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/@sveltejs-kit-vite/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/server-only-modules/llms.txt'
```

- Changelog: `https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md`
- Source: `https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/src/exports/vite/index.js`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md'
V="$(node -p "require('@sveltejs/kit/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
