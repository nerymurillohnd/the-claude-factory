# SvelteKit Routing

> Precedence: the SvelteKit changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").
>
> Applies to SvelteKit 3 projects. A SvelteKit 2 project migrates first ([migrating-to-kit-3.md](migrating-to-kit-3.md)); write SvelteKit 2 code only when the user declines the migration or the request says to proceed without questions.

## Contents

- [Route files](#route-files)
- [Pages and layouts](#pages-and-layouts)
- [Server endpoints](#server-endpoints)
- [Error pages](#error-pages)
- [Parameters](#parameters)
- [Param matchers in src params](#param-matchers-in-src-params)
- [Sorting and escapes](#sorting-and-escapes)
- [Groups and layout resets](#groups-and-layout-resets)
- [Generated types and route IDs](#generated-types-and-route-ids)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Route files

Directories under `src/routes` define URLs; files with a `+` prefix define behaviour.

| File | Runs | Purpose |
| --- | --- | --- |
| `+page.svelte` | server and client | Page component; receives `data` and `params` props |
| `+page.ts` | server and client | Universal `load`, page options |
| `+page.server.ts` | server | Server `load`, form `actions`, page options |
| `+layout.svelte` | server and client | Wraps children; must `{@render children()}` |
| `+layout.ts` / `+layout.server.ts` | as above | Layout `load`; options become defaults for children |
| `+server.ts` | server | HTTP handlers (endpoint) |
| `+error.svelte` | server and client | Error boundary for the subtree |

Other files in a route directory are ignored, so components and helpers can live next to the route. Shared code goes in `src/lib` and is imported through `#lib/….js`.

## Pages and layouts

```svelte
<!-- src/routes/blog/[slug]/+page.svelte -->
<script lang="ts">
	import type { PageProps } from './$types';
	let { data, params }: PageProps = $props();
</script>

<h1>{data.post.title}</h1>
<p>Slug: {params.slug}</p>
```

- Use `PageProps` and `LayoutProps` from `./$types`, not `export let`.
- Layout data flows to child layouts and pages; when two `load` functions return the same key, the deeper one wins.
- Navigating between pages that share a layout keeps the layout component mounted, and a `load` rerun updates the `data` prop without recreating the component. Derive values from props with `$derived`, or reset state in `afterNavigate`.

## Server endpoints

`+server.ts` exports functions named after HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`, and `QUERY` since 3.0) plus an optional `fallback` for any other method. Each receives a `RequestEvent` and returns a `Response`.

```ts
// src/routes/api/sum/+server.ts
import { error } from "@sveltejs/kit";
import type { RequestHandler } from "./$types";

export const POST: RequestHandler = async ({ request }) => {
  const { a, b } = await request.json();
  if (typeof a !== "number" || typeof b !== "number")
    error(400, "a and b must be numbers");
  return Response.json(a + b);
};

export const fallback: RequestHandler = ({ request }) =>
  new Response(`Method ${request.method} not supported`, { status: 405 });
```

- Use `Response.json(...)` and `new Response(text)`: the `json` and `text` helpers are deprecated since 3.0.
- A `204` (or any empty `2xx`) response has no body since 3.0; clients must not parse one.
- A `HEAD` request uses `GET` when it exists, before `fallback`.
- Next to a `+page`, `PUT`/`PATCH`/`DELETE`/`OPTIONS`/`QUERY` always go to `+server`; `GET`/`POST`/`HEAD` go to the page when `Accept` prefers `text/html`. `GET` responses carry `Vary: Accept`.
- Layouts never apply to `+server` files; put cross-cutting logic in the `handle` hook.
- A prerendered endpoint cannot export `fallback`.

## Error pages

When `load` or rendering throws, SvelteKit renders the nearest `+error.svelte` walking up the tree. An error thrown by a layout `load` is caught by the `+error.svelte` above that layout, not the one beside it. An error in the root layout, in `handle` or in a `+server` file uses `src/error.html` or a JSON body instead.

```svelte
<!-- src/routes/+error.svelte -->
<script lang="ts">
	import { page } from '$app/state';
</script>

<h1>{page.status}: {page.error?.message}</h1>
```

Since 3.0, each `+error.svelte` also acts as a Svelte error boundary for rendering errors, and `App.Error` always includes `status`.

## Parameters

- `[slug]`: required parameter.
- `[[lang]]`: optional, so `/home` and `/en/home` both match `[[lang]]/home`. An optional parameter cannot follow a rest parameter.
- `[...path]`: rest, matches zero or more segments (`/a/[...rest]/z` matches `/a/z`). Validate it.
- A custom 404 inside a section needs a catch-all route such as `marx-brothers/[...path]/+page.ts` that calls `error(404, 'Not Found')`; otherwise no route matches and the root error page is used.
- Param and matcher names may contain hyphens since 3.0.

## Param matchers in src params

Since 3.0, all matchers live in one file, `src/params.ts` (or `.js`), built with `defineParams` from `@sveltejs/kit/params`. The `src/params/` directory with one `match` function per file is removed. Each entry is either a function that returns the parsed value (or `undefined` for no match) or a Standard Schema.

```ts
// src/params.ts
import { defineParams } from "@sveltejs/kit/params";
import * as v from "valibot";

export const params = defineParams({
  integer: v.pipe(v.string(), v.toNumber(), v.integer()),
  fruit: (param) =>
    param === "apple" || param === "orange" ? param : undefined,
});
```

Use it as `src/routes/items/[id=integer]/+page.ts`; `params.id` is then typed as `number`.

- Matchers run on the server and in the browser.
- The output type must be `string`, `number`, `boolean` or `bigint`.
- Transforms must be symmetric (`String(value)` gives back the segment), so `resolve('/items/[id=integer]', { id: 7 })` can build the path.
- A function matcher returns the value to use as the param, or `undefined` for no match; a schema matches when validation succeeds. 2.x matchers returned a truthy value and never transformed the param.

## Sorting and escapes

When several routes match, more specific routes win, a matcher beats no matcher, trailing optional or rest parameters rank lowest, and ties go alphabetically.

Characters that cannot appear in a file name or have meaning to the router are written as escapes: `[x+nn]` (hex) or `[u+nnnn]` (Unicode). Examples: `[x+3a]` for `:`, `[x+2f]` for `/`, `[x+23]` for `#`, `[x+5b]` and `[x+5d]` for brackets, `[x+28]` and `[x+29]` for parentheses, and `[x+2e]well-known` for a `.well-known` directory.

## Groups and layout resets

- `(group)` directories group routes under a shared layout without adding a URL segment. A `+page` may sit directly in a group.
- A `+page` file named with `@` plus an ancestor segment resets the layout chain to that ancestor's layout: `+page@[id].svelte`, `+page@(app).svelte`, or `+page@.svelte` for the root layout. A plain directory name after the `@` works the same way.
- `+layout@.svelte` does the same for a layout and all its children.
- Prefer composition (shared components or `load` helpers in `#lib`) over deep group nesting for one-off exceptions.

## Generated types and route IDs

`./$types` provides `PageProps`, `LayoutProps`, `ErrorProps` (new in 3.0), `PageLoad`, `PageServerLoad`, `LayoutLoad`, `LayoutServerLoad`, `Actions`, `RequestHandler` and `EntryGenerator`. `$app/types` provides app-wide types:

- `RouteId` includes only routes with a `+page` or `+server` since 3.0. Use `PageRouteId` and `EndpointRouteId` to narrow, and `LayoutParams<'/id'>` for layout-only directories.
- `Path` (renamed from `Pathname`) and `AssetPath` (renamed from `Asset`) have no leading `/` since 3.0. Only route IDs start with `/`.
- `RouteParams<'/blog/[slug]'>` gives a route's params.
- `$app/manifest` exports `routes`, each `{ id, page, endpoint }`, for runtime introspection.

## Fetch before writing when

- You need the exact sorting rules for overlapping routes or an escape you have not used before.
- You write matchers with a schema library, or need `MatcherParam` and `ParamDefinition` types.
- You add `QUERY` or `fallback` handlers, or combine `+page` and `+server` in one directory.
- You use `reroute` or `router.resolution: 'server'` to change how URLs map to routes.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["kit/routing", "kit/advanced-routing"]
```

Sections: `kit/routing`, `kit/advanced-routing`, `kit/@sveltejs-kit-params`, `kit/$app-types`, `kit/$app-manifest`, `kit/errors`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/kit/routing/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/advanced-routing/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/@sveltejs-kit-params/llms.txt'
```

- Changelog: `https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md'
V="$(node -p "require('@sveltejs/kit/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
