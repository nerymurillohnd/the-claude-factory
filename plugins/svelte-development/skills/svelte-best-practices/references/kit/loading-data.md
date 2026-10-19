# SvelteKit Loading Data

> Precedence: the SvelteKit changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").
>
> Applies to SvelteKit 3 projects. A SvelteKit 2 project migrates first ([migrating-to-kit-3.md](migrating-to-kit-3.md)); write SvelteKit 2 code only when the user declines the migration or the request says to proceed without questions.

## Contents

- [Universal and server load](#universal-and-server-load)
- [The load event](#the-load-event)
- [Parent data and waterfalls](#parent-data-and-waterfalls)
- [Streaming with promises](#streaming-with-promises)
- [When load reruns](#when-load-reruns)
- [Invalidation and refreshAll](#invalidation-and-refreshall)
- [Reading app state](#reading-app-state)
- [Page state](#page-state)
- [Auth checks and load](#auth-checks-and-load)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Universal and server load

|  | `+page.ts` / `+layout.ts` (universal) | `+page.server.ts` / `+layout.server.ts` (server) |
| --- | --- | --- |
| Runs | Server during SSR, again during hydration (reusing `fetch` responses), then in the browser | Always on the server |
| Can use | Public APIs, non-serializable return values (classes, components) | Database, private env vars, `cookies`, `locals`, `request`, `platform`, `getClientAddress` |
| Return value | Anything | Must be serializable by devalue (JSON plus `Date`, `Map`, `Set`, `BigInt`, `RegExp`, cycles, and `transport` types) |
| Type | `PageLoad`, `LayoutLoad` | `PageServerLoad`, `LayoutServerLoad` |

When both exist for a route, the server `load` runs first and its result arrives as `data` in the universal `load`; only the universal result reaches the component. With `ssr = false`, universal `load` runs only in the browser. With prerendering, `load` runs at build time.

```ts
// src/routes/blog/[slug]/+page.server.ts
import { error } from "@sveltejs/kit";
import * as db from "#lib/server/db.js";
import type { PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ params }) => {
  const post = await db.getPost(params.slug);
  if (!post) error(404, "Not found");
  return { post };
};
```

## The load event

- `params`, `route.id`, `url`: request data. `url.hash` is unavailable in `load`. Server `load` also gets `cookies`, `locals`, `request`, `platform`, `getClientAddress`.
- `fetch`: credentialed, accepts relative URLs on the server, calls internal `+server` handlers directly, and inlines responses into the HTML so hydration does not refetch. Response headers are not serialized unless `filterSerializedResponseHeaders` in `handle` allows them. Cookies are forwarded only to the app's host or its subdomains.
- `setHeaders`: set response headers (for example `cache-control`) during SSR; each header can be set once, and `set-cookie` must use `cookies.set`.
- `parent`, `depends`, `untrack`: see below.
- `error(...)` and `redirect(...)` throw; do not call them inside a `try` block that would swallow them.
- `getRequestEvent()` from `$app/server` returns the same event inside server `load`, actions and helpers, which keeps guards like `requireLogin()` out of every signature.

## Parent data and waterfalls

`await parent()` returns the merged data of parent `load` functions (server `load` sees only server parents; universal `load` sees universal parents, and a missing `+layout.ts` passes server data through). Call it after independent work, not before:

```ts
export const load: PageLoad = async ({ params, parent }) => {
  const data = await getData(params); // independent request first
  const { meta } = await parent();
  return { ...data, meta: { ...meta, ...data.meta } };
};
```

All `load` functions of a navigation run in parallel, and server results for one client navigation arrive in a single response.

## Streaming with promises

A server `load` may return promises inside the object; they stream to the browser as they resolve.

```ts
export const load: PageServerLoad = async ({ params }) => ({
  comments: loadComments(params.slug), // streamed
  post: await loadPost(params.slug), // awaited last
});
```

```svelte
{#await data.comments}
	<p>Loading comments…</p>
{:then comments}
	{#each comments as c (c.id)}<p>{c.text}</p>{/each}
{:catch}
	<p>Could not load comments.</p>
{/await}
```

- Attach `.catch(() => {})` to streamed promises that do not come from the event `fetch`, or an early rejection crashes the server as unhandled.
- Headers, status and redirects cannot change once streaming starts.
- Streaming needs JavaScript and a platform that does not buffer responses; promises returned from a universal `load` on an SSR page are recreated in the browser, not streamed.

## When load reruns

A `load` reruns when, during the function body (not inside a later promise):

- a `params` property it read changed;
- a `url` property it read changed (`request.url` is not tracked);
- it called `url.searchParams.get/getAll/has` for a parameter that changed (since 3.0 this includes a change in the number of values);
- it awaited `parent()` and a parent reran (a universal `load` reuses parent data instead of forcing a server parent to rerun);
- a URL it depended on (`fetch` in universal `load`, or `depends`) was invalidated;
- `refreshAll()` was called.

Server `load` never depends on the URLs it fetches, to avoid leaking them. Exclude a read from tracking with `untrack`:

```ts
export const load: PageLoad = async ({ untrack, url }) => {
  if (untrack(() => url.pathname === "/")) return { message: "Welcome!" };
};
```

Since 3.0, clicking a link to the current URL triggers `refreshAll()` instead of doing nothing.

## Invalidation and refreshAll

```ts
// +page.ts
export const load: PageLoad = async ({ fetch, depends }) => {
  depends("app:random"); // custom ids use a scheme such as `app:`
  const res = await fetch("https://api.example.com/random");
  return { n: await res.json() };
};
```

```ts
import { invalidate, refreshAll } from "$app/navigation";

await invalidate("app:random");
await invalidate((url) => url.hostname === "api.example.com");
await refreshAll(); // every load function and every active remote query
```

- `invalidate(resource, keepState?)` accepts a string, a `URL` or a predicate. The docs show the `keepState` parameter in the signature without describing it; read the live reference (`mcp__plugin_svelte-development_svelte__get-documentation` with `section: ["kit/$app-navigation"]`) before relying on it.
- `invalidateAll()` is deprecated since 3.0. It resets `page.state` to `{}`; `refreshAll()` keeps it.
- Since 3.0, invalidating during an in-flight navigation no longer aborts it, and results that arrive after the navigation finishes are discarded.

## Reading app state

`$app/stores` is removed in 3.0. Import the reactive objects from `$app/state` and read them without a `$` prefix:

```svelte
<script lang="ts">
	import { page, navigating, updated } from '$app/state';
	const id = $derived(page.params.id);
</script>

{#if navigating.to}<p>Loading {navigating.to.url.pathname}…</p>{/if}
{#if updated.current}<button onclick={() => location.reload()}>Update available</button>{/if}
<svelte:head><title>{page.data.title}</title></svelte:head>
```

- `page`: `url`, `params`, `route.id`, `status`, `error`, `data` (merged data of all `load` functions, typed through `App.PageData`), `state`, `shallow`, `form`. Since 3.0, `page.url` is a `ReadonlyURL`: copy it (`new URL(page.url.href)`) before changing search params. The `Page`, `ReadonlyURL` and `ReadonlyURLSearchParams` types are exported from `$app/state`.
- Changes are visible only to runes code; a `$:` statement never updates. On the server, `page` can be read only during rendering, not in `load`.
- `navigating`: `from`, `to`, `type`, `delta` (only for `popstate`), or `null` values when idle.
- `updated.current` becomes `true` when a later deployment is detected: on data, remote-function and form-action responses, on tab focus or visibility, and by polling every hour by default (`version.pollInterval`). `updated.check()` forces a check.

## Page state

`page.state` holds state attached to a history entry with `goto(url, { state, shallow: true })` (see the navigation reference). Declare its shape in `App.PageState` in `src/app.d.ts`. It is `{}` during SSR and on the first render until JavaScript loads; values survive reloads only with `persistState: true`, and since 3.0 custom classes in it are serialized through the `transport` hook.

## Auth checks and load

Layout `load` does not rerun on every navigation, and page and layout `load` run in parallel unless the page awaits `parent()`. Protect routes in the `handle` hook or in each `+page.server.ts`, not only in a parent `+layout.server.ts`.

## Fetch before writing when

- You need the exact `LoadEvent` or `ServerLoadEvent` members, or the `keepState` semantics of `invalidate`.
- You stream data on a host or proxy that may buffer responses.
- You combine universal and server `load` on one route, or return non-serializable values.
- You rely on rerun rules for search parameters or shallow routing.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["kit/load", "kit/state-management"]
```

Sections: `kit/load`, `kit/state-management`, `kit/$app-state`, `kit/$app-navigation`, `kit/shallow-routing`, `kit/@sveltejs-kit`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/kit/load/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/$app-state/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/$app-navigation/llms.txt'
```

- Changelog: `https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md'
V="$(node -p "require('@sveltejs/kit/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
