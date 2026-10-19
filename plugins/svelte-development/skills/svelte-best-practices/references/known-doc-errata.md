# Known errors in the official docs

> Precedence: changelogs and source code win over the docs, and the docs win over this file.

## Contents

- [How to use this list](#how-to-use-this-list)
- [Svelte docs](#svelte-docs)
- [SvelteKit docs](#sveltekit-docs)
- [SvelteKit 3 migration guide](#sveltekit-3-migration-guide)
- [sv and svelte-check docs](#sv-and-svelte-check-docs)
- [Svelte AI docs](#svelte-ai-docs)
- [Astro docs](#astro-docs)
- [Tailwind CSS docs](#tailwind-css-docs)

## How to use this list

- Line numbers refer to the whole-package files (`kit/llms.txt`, `svelte/llms.txt`, `cli/llms.txt`) and shift whenever the docs change, so search for the quoted text instead of trusting the number.
- Before relying on a row, check whether the source has been fixed: fetch the page again and search for the quoted text. Drop a row once the docs are corrected.
- When you find a new conflict, follow the higher source (changelog or code) and tell the user which document is wrong.

## Svelte docs

| What the docs say | What is right | Evidence |
| --- | --- | --- |
| Mounting a component with context through a wrapper works "as of version 5.49" | Using `createContext` when instantiating components programmatically arrived in 5.50.0 | `svelte/llms.txt` L4823; svelte CHANGELOG `## 5.50.0` ("allow use of createContext when instantiating components programmatically") |
| `transformError` for server error boundaries is available "since 5.51" | Error boundaries on the server, which `transformError` feeds, arrived in 5.53.0; 5.51.0 has no such entry | `svelte/llms.txt` L4158; svelte CHANGELOG `## 5.53.0` ("allow error boundaries to work on the server"), `## 5.51.0` |
| The `fork` reference ("Available since 5.42") does not mention any requirement | `fork(...)` throws unless `compilerOptions.experimental.async` is `true` | `svelte/llms.txt` L7911; `batch.js` calls `e.experimental_async_required('fork')` (L1403 at commit `7c2fcdae`); error text at `svelte/llms.txt` L16439 |
| The runtime-errors page lists `flush_sync_in_effect`: `flushSync()` cannot be called inside an effect | The restriction was lifted in 5.43.15; `flushSync` in `reactivity/batch.js` throws nothing for it | svelte CHANGELOG `## 5.43.15` ("lift 'flushSync cannot be called in effects' restriction (#17139)") |

## SvelteKit docs

| What the docs say | What is right | Evidence |
| --- | --- | --- |
| Remote form example imports `loginOrRegister` from `'#lib/auth'` | Subpath imports need the file extension: `'#lib/auth.js'` (or `.ts`) | `kit/llms.txt` L3379; the `#lib` section says "you will also have to add the module extensions" (L8831) |
| Page options examples use `config = { runtime: 'edge' }` | The example adapter is generic, but adapter-vercel 7 removed the edge runtime; copying it into a Vercel project fails | `kit/llms.txt` L2301 to L2330; adapter-vercel CHANGELOG `## 7.0.0` ("remove support for edge and Node 20 runtimes") |
| Config reference lists `csrf.checkOrigin` (tagged "removed in 3.0") | The option no longer exists; use `csrf.trustedOrigins: ['*']` | `kit/llms.txt` L14173; Kit CHANGELOG `## 3.0.0` ("remove the deprecated CSRF `checkOrigin` option"). The docs render from the generated `packages/kit/types/index.d.ts`, which still declares it, while `src/exports/public.d.ts` no longer does |
| Config reference lists `output.preloadStrategy` (tagged "removed in 3.0") | Removed; `modulepreload` is always used | `kit/llms.txt` L14644; Kit CHANGELOG `## 3.0.0` ("remove the `preloadStrategy` option") |
| Config reference describes `files.params` as "a directory containing parameter matchers" (default `src/params`) | SvelteKit 3 reads matchers from a single `src/params.js` or `src/params.ts` file | `kit/llms.txt` L14456 to L14468; Kit CHANGELOG `## 3.0.0` ("remove param files in folder in favor of `params.js/ts` file") |
| Remote forms: "call `validate({ includeUntouched: true })`" | The option is `validate({ all: true })` | `kit/llms.txt` L3154; Kit CHANGELOG `## 3.0.0` ("`validate({ includeUntouched })` option is now `all`") |
| Explicit environment variables "were added in SvelteKit 2.62 as an experimental option" | They shipped in 2.63.0 | `kit/llms.txt` L3883; Kit CHANGELOG `## 2.63.0` ("feat: explicit env vars") |
| Shallow routing examples call `goto(url, …)` where the hidden setup sets `url = new URL('https://example.com')` | `goto` rejects URLs outside the app since 3.0.0; use an in-app path | `kit/llms.txt` L7195 to L7225; Kit CHANGELOG `## 3.0.0` ("`goto` now rejects when called with a URL that does not resolve to a route within the app") |
| `Builder` reference: "Generate an initializer that populates `$env/dynamic/private`" | `$env/dynamic/private` is a deprecated alias in SvelteKit 3; the initializer populates the runtime variables that `$app/env/private` reads (wording) | `kit/llms.txt` L10774; `$env/dynamic/private` page marked deprecated (L18627); Kit CHANGELOG `## 3.0.0` (env vars populated before `instrumentation.server.js`) |

## SvelteKit 3 migration guide

| What the guide says | What is right | Evidence |
| --- | --- | --- |
| Import "`resolved` from `$app/paths`" instead of `$service-worker` | `$app/paths` exports `resolve` (with `asset` and `match`); there is no `resolved` | `kit/llms.txt` L9010 (guide source L266); `$app/paths` reference `import { asset, match, resolve } from '$app/paths'` (L16719) |
| "minimum `wrangler` is now `^4.67.0`" | adapter-cloudflare 8.0.0 requires Wrangler 4.118.0 | guide source L495; adapter-cloudflare CHANGELOG `## 8.0.0` ("minimum Wrangler version required is `4.118.0`") |
| Minimum Svelte is v5.57.1 | The Kit changelog says 5.56.4, but `@sveltejs/kit` 3.0.0 declares the peer `svelte ^5.57.1`; follow the peer range (changelog is the stale one) | guide source L19; Kit CHANGELOG `## 3.0.0` ("require Svelte 5.56.4 or newer"); `npm view @sveltejs/kit peerDependencies` |
| `sv migrate sveltekit-3` reports "Rename Cloudflare `platform.context`" to `platform.ctx` | adapter-cloudflare 8.0.0 removed `platform` entirely; import `env` and `ctx` from `cloudflare:workers` | sv 1.1.0 `collect-migration-instructions.ts` L349 to L358; adapter-cloudflare CHANGELOG `## 8.0.0` ("remove cloudflare `platform`, emulate the `cloudflare:workers` module instead"); guide source L456 to L458 |
| Kit prerelease notes: "upgrade to cookie v1" | SvelteKit 3.0.0 ships `cookie` v2 (ASCII-only names, renamed option types) | Kit CHANGELOG `## 3.0.0-next.0` vs `## 3.0.0`; guide "Updated to `cookie` v2" (L350) |

## sv and svelte-check docs

| What the docs say | What is right | Evidence |
| --- | --- | --- |
| `sveltekit-adapter` and `mdsvex` add-ons configure "your `svelte.config.js`" | Projects created by sv keep the config inside `vite.config` and have no `svelte.config.js`; the add-ons edit whichever file holds it | `cli/llms.txt` L729 and L828; same file L1607; sv CHANGELOG `## 0.16.0` ("move svelte config to vite plugin") |
| `prettier` add-on writes "`.prettierignore` and `.prettierrc` files" | It writes `prettier.config.js` | `cli/llms.txt` L798; sv CHANGELOG `## 0.16.2`; `src/addons/common.ts` `prettierConfigPath()` returns `'prettier.config.js'` |
| `sveltekit-3` migration "is divided into these tasks" (nine listed) | The code registers twelve: two prerequisites and ten selectable, adding `imports`, `lib-alias` and `collect-migration-instructions` | `cli/llms.txt` L417 to L427; sv 1.1.0 `src/migrate/migrations/sveltekit-3/index.ts` |
| `drizzle` options list databases postgresql, mysql, sqlite and sqlite clients better-sqlite3, libsql, turso | sv 1.1.0 also offers `d1` (Cloudflare D1) and the `node-sqlite` client; the default database is `sqlite` with `libsql` | `cli/llms.txt` L622 to L640; sv 1.1.0 `src/addons/drizzle.ts` |
| `playwright` add-on always adds "a demo test" | sv 1.1.0 added a `demo` option; the demo page and test are created only when it is on | `cli/llms.txt` L778 to L783; sv CHANGELOG `## 1.1.0` |
| `sv check` "Requires Node 16 or later" | sv warns below Node 22.17.0, and SvelteKit 3 requires 22.17 | `cli/llms.txt` L232; sv `src/core/common.ts` (`minimumVersion = '22.17.0'`); `npm view @sveltejs/kit engines` |
| svelte-check README: "Requires Node 16 or later" | svelte-check 4.7.6 declares `engines.node >= 18.0.0` | `svelte-check` README L9; `npm view svelte-check engines` |

## Svelte AI docs

| What the docs say | What is right | Evidence |
| --- | --- | --- |
| The MCP section catalog lists `kit/configuration` and `kit/@sveltejs-kit-node-polyfills` | Both pages return 404; the configuration reference is `kit/@sveltejs-kit-vite`. Nine current sections are missing from the catalog | `ai/llms.txt` L427 to L625 compared with `sections.json`; `curl` status of both pages |
| The MCP CLI page lists `--version` among the commands to learn the CLI | `svelte-mcp --version` prints `svelte-mcp, 0.0.0` in `@sveltejs/mcp` 0.1.26; check the installed version with `npm ls -g --depth 0 @sveltejs/mcp` | `https://svelte.dev/docs/ai/cli/llms.txt`; runtime output of the 0.1.26 binary |
| The MCP docs and the CLI page run the server and CLI with `npx -y @sveltejs/mcp` | Correct, but it downloads the package on each run; this plugin connects to the remote server `https://mcp.svelte.dev/mcp` and treats an installed `svelte-mcp` as an optional local fallback (design choice, not an error) | `https://svelte.dev/docs/ai/cli/llms.txt`, `ai/local-setup` |

## Astro docs

| What the docs say | What is right | Evidence |
| --- | --- | --- |
| Svelte components receive children "using the `<slot />` element", with `<slot name="title" />` examples | For Svelte 5, slots arrive as snippet props: `children` for the default slot and the exact slot name for named slots; render them with `{@render children?.()}` | `framework-components.mdx` L136 and L179 to L187; @astrojs/svelte `src/server.ts` and `src/client.svelte.ts` (`createRawSnippet`, `renderProps[slotName]`) |

## Tailwind CSS docs

| What the docs say | What is right | Evidence |
| --- | --- | --- |
| The SvelteKit guide styles the page with `background-color: theme(--color-gray-100);` | `theme()` is deprecated; use `var(--color-gray-100)` | `framework-guides/sveltekit.tsx` L148; `functions-and-directives.mdx` L322 ("This function is deprecated") |
| The SvelteKit guide creates `src/app.css` and imports it from the root layout | `sv add tailwindcss` writes `src/routes/layout.css` and imports it from `src/routes/+layout.svelte`. Both work; use one stylesheet and point `tailwindStylesheet` and `@reference` at it (difference, not an error) | `framework-guides/sveltekit.tsx` L78 to L103; sv `src/core/workspace.ts` (`stylesheet` is `${directory.kitRoutes}/layout.css` in Kit projects) |
