# SvelteKit Navigation, Links and Page Options

> Precedence: the SvelteKit changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").
>
> Applies to SvelteKit 3 projects. A SvelteKit 2 project migrates first ([migrating-to-kit-3.md](migrating-to-kit-3.md)); write SvelteKit 2 code only when the user declines the migration or the request says to proceed without questions.

## Contents

- [Programmatic navigation with goto](#programmatic-navigation-with-goto)
- [Shallow routing](#shallow-routing)
- [Navigation lifecycle](#navigation-lifecycle)
- [Snapshots](#snapshots)
- [Preloading](#preloading)
- [Link options](#link-options)
- [Building paths](#building-paths)
- [Page options](#page-options)
- [App-level routing and output options](#app-level-routing-and-output-options)
- [Version detection](#version-detection)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Programmatic navigation with goto

```ts
import { goto } from "$app/navigation";
import { resolve } from "$app/paths";

await goto(resolve("/blog/[slug]", { slug }), {
  replace: true,
  reset: false,
  refreshAll: true,
});
```

`GotoOptions` in 3.0:

| Option | Meaning |
| --- | --- |
| `replace` | Replace the history entry (`replaceState` is a deprecated alias). |
| `reset` | Reset scroll and focus; default `true`, or `false` when `shallow`. Replaces `noScroll` and `keepFocus`. |
| `refreshAll` | Rerun every `load` and query (`invalidateAll` is a deprecated alias). |
| `invalidate` | Array of URLs or predicates to invalidate. |
| `shallow` | Update the URL and `page.state` without navigating. |
| `state` | Value for `page.state`. |
| `persistState` | Restore `page.state` after a full reload. |

- `goto` rejects for URLs that do not resolve to a route of the app (since 3.0, not only for external URLs). Use `window.location.href = url` for other destinations.
- `goto` is browser-only; on the server, use `redirect(...)`.

## Shallow routing

`pushState` and `replaceState` are deprecated since 3.0. Use `goto` with `shallow: true`:

```svelte
<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import Modal from './Modal.svelte';
</script>

<button onclick={() => goto('', { shallow: true, state: { showModal: true } })}>Open</button>
{#if page.state.showModal}<Modal close={() => history.back()} />{/if}
```

- Shallow navigations run `beforeNavigate`, `onNavigate` and `afterNavigate` since 3.0 (`type: 'goto'`, `shallow: true`); filter on `navigation.shallow` where needed.
- `page.shallow` is `{ url, params, route }` for the visible URL while `page.url` stays on the rendered page. A normal `goto` or link click leaves shallow mode.
- To render another route inside a modal, call `preloadData(href)` and pass `result.data` through `state`.
- `page.state` is empty during SSR; a reload lands on the shallow URL. Provide a no-JavaScript fallback.

## Navigation lifecycle

- `beforeNavigate(cb)`: `cancel()` stops the navigation; for `type: 'leave'` it triggers the browser unload prompt. `to.route.id` is `null` for non-app URLs.
- `onNavigate(cb)`: may return a promise (for example to start a view transition) and a cleanup function run after the DOM updates. Not called for full-page loads.
- `afterNavigate(cb)`: runs on mount and after each navigation; use it to reset component state.
- `delta` exists only for `popstate` navigations since 3.0.
- All three must be called during component initialization. Navigation types moved to `$app/navigation` in 3.0.

## Snapshots

Since 3.0, call the `snapshot` helper from `$app/navigation` during component initialization, in any component. `export const snapshot` in `+page.svelte` is deprecated.

```svelte
<script lang="ts">
	import { snapshot } from '$app/navigation';
	let comment = $state('');
	snapshot({ id: 'comment', capture: () => comment, restore: (v) => (comment = v) });
</script>
```

Values are serialized with devalue and the `transport` hook, stored in `sessionStorage`, and restored on back/forward and reloads. Pass an explicit `id` to keep snapshots stable across deployments; the optional `reset` runs when there is nothing to restore. Keep captured values small.

## Preloading

- `preloadData(href)` loads code and runs `load`; the next navigation to `href` reuses the result. Since 3.0, it returns `{ type: 'error', status, error }` when the page fails, and `'redirect'` carries the correct `status`. Handle all three result types.
- `preloadCode(routeId)` takes a route ID (`'/blog/[slug]'`) since 3.0, never base-prefixed. Convert a pathname with `match` from `$app/paths`.
- Data is never preloaded when the user enables reduced data usage (`saveData`).

## Link options

`data-sveltekit-*` attributes apply to an element or any ancestor, and also to `<form method="GET">`:

| Attribute | Values |
| --- | --- |
| `data-sveltekit-preload-data` | `"hover"`, `"tap"`, `"false"` |
| `data-sveltekit-preload-code` | `"eager"`, `"viewport"`, `"hover"`, `"tap"`, `"false"` |
| `data-sveltekit-reload` | full-page navigation (as does `rel="external"`) |
| `data-sveltekit-replacestate` | replace instead of push |
| `data-sveltekit-reset` | `"false"` keeps scroll and focus |

- Since 3.0, `"false"` disables an inherited option; the `"off"` value is removed.
- `data-sveltekit-reset` replaces `data-sveltekit-noscroll` and `data-sveltekit-keepfocus` in 3.0. Avoid preserving focus on links, because assistive technology expects focus to move.
- The default template sets `data-sveltekit-preload-data="hover"` on `<body>`.

## Building paths

`$app/paths` exports `resolve`, `asset` and `match`. `base`, `assets` and `resolveRoute` are removed in 3.0.

```ts
import { asset, match, resolve } from "$app/paths";

resolve("blog/hello-world"); // a path: no leading slash since 3.0
resolve("/blog/[slug]", { slug: "hello-world" }); // a route ID: leading slash
asset("favicon.png"); // a static file: no leading slash
const route = await match("blog/hello-world"); // { id, params } | null
```

- Only route IDs start with `/`. `resolve` adds `paths.base` (and returns `#…` URLs under the hash router).
- During SSR, paths are relative when `paths.relative` is `true` (the default).
- `$app/paths` is importable in service workers since 3.0.
- `paths.origin` (config, since 3.0) sets the public origin used for CSRF checks and as `url.origin` while prerendering (otherwise `http://sveltekit-prerender`). Set it when the origin cannot be derived from request headers, for example behind a reverse proxy.

## Page options

Export from `+page.ts`, `+page.server.ts`, `+layout.ts`, `+layout.server.ts` (layout values are defaults for children) and, for `prerender` and `trailingSlash`, from `+server.ts`.

- `prerender`: `true`, `false` or `'auto'` (prerender but keep the route in the SSR manifest). The crawler starts from `prerender.entries` (default `['*']`) and follows links; dynamic routes need links or an `entries()` export (`EntryGenerator`). Prerendered pages cannot read `url.searchParams`, cannot have actions, and must give every visitor the same content. `building` from `$app/env` is `true` while prerendering.
- `ssr = false` renders an empty shell (SPA); `csr = false` ships no JavaScript (no hydration, no enhancement, browser navigation). Setting both to `false` renders nothing.
- `trailingSlash`: `'never'` (default), `'always'` or `'ignore'` (not recommended). It decides between `about.html` and `about/index.html` when prerendering.
- `config`: adapter-specific object merged one level deep with parents. Since 3.0, a universal file's `config` takes precedence over the server file's. The docs' `runtime: 'edge'` example does not apply to `adapter-vercel` 7, which removed the edge runtime.
- Keep option values literal so SvelteKit can read them statically; otherwise it imports the module on the server, where browser-only code must not run at module load.

## App-level routing and output options

- `router.type: 'hash'` uses `location.hash` for routing and disables SSR, prerendering and all server logic; every link must start with `#/`.
- `router.resolution: 'server'` resolves routes on the server, hiding the route list and shrinking the initial payload.
- `output.bundleStrategy`: `'split'` (default), `'single'`, or `'inline'` (one HTML file usable without a server).
- `embedded: true` scopes listeners to the parent of `%sveltekit.body%`; multiple SvelteKit apps on one page are not supported.

## Version detection

`updated.current` from `$app/state` turns `true` when a later deployment is detected. Since 3.0, detection happens on server data, remote and form responses (`x-sveltekit-version`), on tab focus and visibility, and by polling every hour (`version.pollInterval`, `0` disables polling). Force a full-page navigation when it is set:

```ts
beforeNavigate(({ willUnload, to }) => {
  if (updated.current && !willUnload && to?.url) location.href = to.url.href;
});
```

Vercel skew protection can hide a deployment from response-based checks; polling and focus checks still work.

## Fetch before writing when

- You need the exact `GotoOptions`, navigation types, or `preloadData` result shape.
- You use shallow routing with modals or `persistState`.
- You configure prerendering of dynamic routes, `handleHttpError`, or `trailingSlash` for a static host.
- You use the hash router, server route resolution, `bundleStrategy` or `embedded`.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["kit/$app-navigation", "kit/shallow-routing"]
```

Sections: `kit/$app-navigation`, `kit/shallow-routing`, `kit/snapshots`, `kit/link-options`, `kit/$app-paths`, `kit/page-options`, `kit/@sveltejs-kit-vite`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/kit/$app-navigation/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/page-options/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/link-options/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/$app-paths/llms.txt'
```

- Changelog: `https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md'
V="$(node -p "require('@sveltejs/kit/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
