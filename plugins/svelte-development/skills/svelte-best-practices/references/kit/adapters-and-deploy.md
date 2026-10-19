# SvelteKit Adapters and Deployment

> Precedence: the SvelteKit changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").
>
> Applies to SvelteKit 3 projects. A SvelteKit 2 project migrates first ([migrating-to-kit-3.md](migrating-to-kit-3.md)); write SvelteKit 2 code only when the user declines the migration or the request says to proceed without questions.

## Contents

- [Adapter versions for Kit 3](#adapter-versions-for-kit-3)
- [Choosing and configuring an adapter](#choosing-and-configuring-an-adapter)
- [adapter-auto](#adapter-auto)
- [adapter-node](#adapter-node)
- [adapter-bun](#adapter-bun)
- [adapter-static](#adapter-static)
- [adapter-cloudflare](#adapter-cloudflare)
- [adapter-vercel](#adapter-vercel)
- [adapter-netlify](#adapter-netlify)
- [Related packages](#related-packages)
- [Notes for adapter authors](#notes-for-adapter-authors)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Adapter versions for Kit 3

Every first-party adapter requires SvelteKit 3 in these majors (confirm the current version with `npm view <package> version`):

| Package | First SvelteKit 3 release | Key requirement |
| --- | --- | --- |
| `@sveltejs/adapter-auto` | 8.0.0 |  |
| `@sveltejs/adapter-node` | 6.0.0 | Node `>=22.17` (from Kit) |
| `@sveltejs/adapter-bun` | 1.0.0 | Bun `>=1.4.0` |
| `@sveltejs/adapter-static` | 4.0.0 |  |
| `@sveltejs/adapter-cloudflare` | 8.0.0 | peer `wrangler ^4.118.0` |
| `@sveltejs/adapter-vercel` | 7.0.0 | runtimes `nodejs22.x`, `nodejs24.x`, `bun1.x` |
| `@sveltejs/adapter-netlify` | 7.0.0 | Netlify CLI 17.31.0 or later |

`@sveltejs/adapter-cloudflare-workers` is deprecated on npm; its last release (2.9.0) peers on `@sveltejs/kit ^2.0.0`, so there is no Kit 3 version. Migrate to `adapter-cloudflare`.

## Choosing and configuring an adapter

The adapter is the `adapter` option of `sveltekit(...)` in `vite.config.*` (`svelte.config.js` is not read in 3.0). To install and wire one, on a committed tree:

```sh
npx sv add sveltekit-adapter
```

By hand:

```ts
import adapter from "@sveltejs/adapter-node";
import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    sveltekit({
      adapter: adapter({ precompress: true }),
      paths: { origin: process.env.PUBLIC_ORIGIN },
    }),
  ],
});
```

`vite.config.*` runs at build time, so any `process.env` value read there (such as `PUBLIC_ORIGIN` above) must be present when you build, not only when the server starts.

Per-route settings go in the `config` page option, typed with the adapter's `Config` export. Since 3.0, a universal file's `config` wins over the server file's.

## adapter-auto

Detects the platform at build time and installs the matching adapter: Cloudflare, Netlify, Vercel, Azure Static Web Apps, AWS via SST, Google Cloud Run (node), and Render (node, since 8.0). It takes no options; install the specific adapter as a dev dependency once the target is settled, to set options and pin it in the lockfile.

## adapter-node

```sh
npm run build
npm ci --omit dev   # in the deploy directory with package.json and the lockfile
node build
```

- 6.0 bundles with rolldown and attaches the handler to `http` directly (no polka). `@sveltejs/kit/node/polyfills` is removed, and `getRequest`/`setResponse` from `@sveltejs/kit/node` are synchronous in 3.0.
- The `ORIGIN` variable is removed. Set `paths.origin` in the Vite config, or let the adapter derive the origin from `host` plus `PROTOCOL_HEADER`, `HOST_HEADER` and `PORT_HEADER`.
- Static assets are served from a list recorded at build time: files added to the output afterwards are not served, replaced files keep their old size and `ETag`. Use environment variables for runtime configuration.
- Static assets use content-hash `ETag`s, send no `Last-Modified`, and answer only `GET` and `HEAD` (other methods get 405).
- Runtime variables: `PORT`, `HOST`, `SOCKET_PATH`, `ADDRESS_HEADER` with `XFF_DEPTH` (count trusted proxies from the right), `BODY_SIZE_LIMIT`, `SHUTDOWN_TIMEOUT`, `IDLE_TIMEOUT` (systemd socket activation), `KEEP_ALIVE_TIMEOUT`, `HEADERS_TIMEOUT`. `envPrefix` namespaces them.
- A custom server that imports `handler.js` honours only the handler variables (`PROTOCOL_HEADER`, `HOST_HEADER`, `PORT_HEADER`, `ADDRESS_HEADER`, `XFF_DEPTH`, `BODY_SIZE_LIMIT`); implement the lifecycle ones yourself.
- Forwarded headers are spoofable; set them only when a trusted proxy writes them.

## adapter-bun

Bun-native server (requires Bun 1.4 or later) with static file serving. Options: `out`, `precompress`, `envPrefix`, `serverOptions` (`hostname`, `port`, `unix`, `idleTimeout`, `maxRequestBodySize`, and more), and `buildOptions` with `compile` to produce a single executable at `<out>/server`. Without `paths.origin` it trusts the `Host` header and assumes `https`; configure `paths.origin` or `PROTOCOL_HEADER` when serving plain HTTP.

## adapter-static

- Every page must be prerendered (`export const prerender = true` in the root layout), unless `fallback` is set.
- `fallback: '200.html'` (or the host's convention; avoid `index.html`) produces an SPA entry for unprerendered URLs; combine with `ssr = false` where needed.
- `strict: false` disables the "everything prerendered or fallback set" check.
- Options: `pages`, `assets`, `fallback`, `precompress`, `strict`.
- Set `trailingSlash = 'always'` if the host does not serve `/a.html` for `/a`. On GitHub Pages, use `fallback: '404.html'` and set `paths.base` to the repository name unless the site is served from the domain root.

## adapter-cloudflare

Builds for Workers Static Assets and Cloudflare Pages. 8.0 removes `platform`; use the Workers APIs directly:

```ts
// src/routes/api/visits/+server.ts
import { env, waitUntil } from "cloudflare:workers";
import type { RequestHandler } from "./$types";

export const GET: RequestHandler = async ({ request }) => {
  const count = Number((await env.KV.get("visits")) ?? 0) + 1;
  waitUntil(env.KV.put("visits", String(count)));
  return Response.json({ count, country: request.cf?.country });
};
```

- Bindings and `ctx` members come from `cloudflare:workers`; `cf` is a property of `request`; `caches` is a global. Run `wrangler types` for the types. Prefer `$app/env/*` for plain environment variables.
- `wrangler` must satisfy `^4.118.0`. The 8.0 changelog lists both an earlier `^4.67.0` minimum and the final `4.118.0`; the npm peer is `^4.118.0`. The migration guide still says `^4.67.0`.
- The changelog also lists "remove `platform.context` in favour of `platform.ctx`" from an earlier prerelease; `platform` itself is removed in 8.0, so do not write `platform.ctx` either.
- Add the `nodejs_als` compatibility flag (and `nodejs_compat` when Node APIs are needed). `cloudflare:workers` is emulated in `vite dev` and `vite preview`; `platformProxy` tunes local bindings.
- Options: `config` (Wrangler file path), `platformProxy`, `fallback` (`'plaintext'` or `'spa'`), `routes` (Pages only; up to 100 include and exclude rules).
- There is no `fs`: use `read` from `$app/server`, or prerender. Durable Objects and Workflows that need exported classes are not supported by the adapter. `_headers` and `_redirects` affect only static assets.

## adapter-vercel

- 7.0 removes the `edge` runtime and Node 20. `runtime` is `'nodejs22.x'`, `'nodejs24.x'` or `'bun1.x'` (default: the build's runtime). Older docs or code that set `runtime: 'edge'` or `edge: true` no longer apply.
- Route `config`: `regions`, `split`, `memory`, `maxDuration`, `isr` (`expiration`, `bypassToken`, `allowQuery`). Use ISR only for content identical for every visitor; it has no effect on prerendered routes.
- Skew protection pins clients to their deployment, which can hide later deployments from response-based `updated` detection; polling still works.
- Check the Node version in the Vercel project settings; older projects may default below Kit's minimum.

## adapter-netlify

- 7.0 emits output for the stable Netlify Frameworks API; deploying or previewing with the Netlify CLI requires 17.31.0 or later.
- Options: `edge` (Netlify Edge Functions; build target `es2022`), `split`, and `publish`. The publish directory is an adapter option since 7.0 instead of being read from `netlify.toml`. `edge` and `split` can be combined since 7.0.
- The Node global shims are removed.

## Related packages

- `@sveltejs/enhanced-img` 1.0.0: peers `vite >=8.0.12` and `@sveltejs/vite-plugin-svelte ^7.0.0`; Node `>=22`.
- `@sveltejs/package` 3.0.0: optional TypeScript peer `^6.0.0`; Node `>=22`. `npx sv migrate sveltekit-3` updates it.
- Sourcemaps are generated and applied to production stack traces since 3.0, provided the adapter does not rebundle destructively.

## Notes for adapter authors

`builder.config.kit` is gone (configuration is top-level); `createEntries` and `generateManifest` are removed (use `writeClient`, `writeServer`, `writePrerendered`, `generateServerInstance` and `builder.manifest`); `rimraf` and `mkdirp` are deprecated for `node:fs`; adapters can add Vite plugins (`pre` and `post`); `builder.instrument` requires `createInstrumentationInitializer`. Read the migration guide's adapter section before changing an adapter.

## Fetch before writing when

- You set adapter options or route `config` keys not shown here.
- You deploy behind a proxy, change `BODY_SIZE_LIMIT`, or need graceful shutdown details.
- You use Cloudflare bindings, Durable Objects, or Wrangler configuration.
- You configure Vercel ISR, regions or the Bun executable build.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["kit/adapters", "kit/adapter-auto"]
```

Sections: `kit/adapters`, `kit/adapter-auto`, `kit/adapter-node`, `kit/adapter-bun`, `kit/adapter-static`, `kit/single-page-apps`, `kit/adapter-cloudflare`, `kit/adapter-cloudflare-workers`, `kit/adapter-netlify`, `kit/adapter-vercel`, `kit/writing-adapters`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/kit/adapter-node/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/adapter-cloudflare/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/adapter-vercel/llms.txt'
```

- Changelogs: `https://raw.githubusercontent.com/sveltejs/kit/main/packages/adapter-<name>/CHANGELOG.md` (`auto`, `node`, `bun`, `static`, `cloudflare`, `vercel`, `netlify`)
- npm: `npm view @sveltejs/adapter-<name> version peerDependencies engines`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/kit/main/packages/adapter-node/CHANGELOG.md'  # adapter-<name>
V="$(node -p "require('@sveltejs/adapter-node/package.json').version")"  # the installed adapter version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
