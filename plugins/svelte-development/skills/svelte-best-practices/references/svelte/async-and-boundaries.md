# Async Svelte and Boundaries

> Precedence: the Svelte changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").

## Contents

- [Status and opt-in flag](#status-and-opt-in-flag)
- [Await expressions](#await-expressions)
- [Waterfalls and reactivity loss](#waterfalls-and-reactivity-loss)
- [Loading states](#loading-states)
- [Cancellation with getAbortSignal](#cancellation-with-getabortsignal)
- [Forks](#forks)
- [Hydratable data](#hydratable-data)
- [Error boundaries](#error-boundaries)
- [Async server rendering](#async-server-rendering)
- [Context and initialization order](#context-and-initialization-order)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Status and opt-in flag

- Since 5.36, `await` is allowed at the top level of a component `<script>`, inside `$derived(...)` and in markup, behind the experimental compiler option `experimental.async`. Without it, the compiler stops with `experimental_async`.
- Experimental means the details (including `$effect.pending()`) may change outside a semver major. The flag is removed in Svelte 6, where async behavior becomes the default.
- Where to set `compilerOptions: { experimental: { async: true } }`:
  - SvelteKit 3: in the `sveltekit({ ... })` plugin options in `vite.config.js` (`svelte.config.js` is no longer supported).
  - SvelteKit 2: in `svelte.config.js`.
  - Plain Vite: in the `svelte({ ... })` options of `@sveltejs/vite-plugin-svelte`, or in `svelte.config.js`.
- With the flag on, block updates (`{#if}`, `{#each}`) run before `$effect.pre` in the same component.

## Await expressions

```svelte
<script lang="ts">
	let a = $state(1);
	let b = $state(2);
	async function add(x: number, y: number) {
		return x + y;
	}
	const user = await fetch('/api/me').then((r) => r.json()); // top-level await
	let sum = $derived(await add(a, b));
</script>

<p>{user.name}: {a} + {b} = {sum}</p>
<p>{await add(a, 10)}</p>
```

- Synchronized updates: when state used by an `await` changes, the dependent UI keeps showing the old consistent values until the promise resolves. Faster later updates may land while an earlier slow one is still pending.
- Independent `await` expressions in markup run in parallel. Sequential `await`s in a script or an async function run in sequence, like any JavaScript. Two `$derived(await ...)` declarations are created one after the other, but update independently afterwards.
- Errors from `await` expressions go to the nearest error boundary.
- Read every piece of state an async expression needs **before** its first `await`, or pass it as an argument.

## Waterfalls and reactivity loss

- `await_waterfall`: a later async derived waits for an earlier one it does not depend on. Create the promises first, then await them:

```ts
let userPromise = $derived(getUser(id));
let postsPromise = $derived(getPosts(id));
let user = $derived(await userPromise);
let posts = $derived(await postsPromise);
```

- `await_reactivity_loss`: state read inside an async function after an inner `await` is not tracked, because only an `await` written directly in the expression extends tracking. Pass the values as arguments: `$derived(await sum(a, b))`, not a `sum()` that reads `a` and `b` itself.

## Loading states

- A `pending` snippet on `<svelte:boundary>` shows only while the boundary first resolves; later updates are coordinated globally and do not show it again.
- After that, use `$effect.pending()` (number of pending promises in the current boundary, child boundaries excluded) for spinners on subsequent work.
- `settled()` (since 5.36) returns a promise that resolves once current state changes, the async work they cause and the DOM updates are done. Call `await tick()` first if a flag set just before must render on its own.
- `$state.eager(value)` (since 5.41) shows a value immediately while the rest of the update waits.

## Cancellation with getAbortSignal

Since 5.35, `getAbortSignal()` from `svelte` returns an `AbortSignal` that aborts when the current derived or effect re-runs or is destroyed. Call it synchronously while a derived or effect is running (it fails otherwise).

```ts
import { getAbortSignal } from "svelte";
async function getItem(id: string) {
  const res = await fetch(`/items/${id}`, { signal: getAbortSignal() });
  return res.json();
}
let item = $derived(await getItem(id));
```

## Forks

- `fork(fn)` from `svelte` (since 5.42) runs the synchronous state changes in `fn` off-screen, so the `await`s they trigger start early (preloading on hover or focus). It returns a `Fork` with `commit(): Promise<void>` and `discard(): void`.
- Always `discard()` a fork you will not commit, to avoid leaking memory. Committing a discarded fork throws `fork_discarded`; creating one inside an effect or while state changes are pending throws `fork_timing`.
- Without `experimental.async`, `fork` throws `experimental_async_required` (source: `packages/svelte/src/internal/client/reactivity/batch.js`, the `async_mode_flag` check at the top of `fork`).
- It is intended mainly for frameworks such as SvelteKit, to preload when a user signals intent to navigate.

## Hydratable data

- Problem: data awaited during server rendering is fetched again during hydration, blocking it. `hydratable(key, fn)` (since 5.44) serializes the server result into the `head` and returns it during hydration instead of calling `fn`; after hydration it simply calls `fn`.
- It needs `experimental.async` (docs: best practices, async section). Use 5.55.7 or newer: earlier versions allow XSS through user content in `hydratable` values.
- Keys must be unique per value (`hydratable_clobbering` when one key gets two values); library authors prefix keys with the library name. A key rendered on the client but not on the server warns `hydratable_missing_but_expected` and falls back to a blocking call.
- Values are serialized with `devalue` (`Map`, `Set`, `URL`, `BigInt`, ... and promises); failures raise `hydratable_serialization_failed`. It cannot be called outside a `render(...)` call, for example at module top level.
- Also useful for values that must match between server and client, such as `hydratable('seed', () => Math.random())`.
- Content Security Policy: the serialized data is an inline `<script>`. Pass `render(App, { csp: { nonce } })` per response, or `csp: { hash: true }` for prerendered HTML and put `result.hashes.script` in the header (since 5.46). Prefer the nonce.
- Most apps should not call it directly: data libraries and SvelteKit remote functions use it.

```svelte
<script lang="ts">
	import { hydratable } from 'svelte';
	import { getUser } from '$lib/server-api';
	const user = await hydratable('myapp:user', () => getUser());
</script>
```

## Error boundaries

- `<svelte:boundary>` (since 5.3) walls off a subtree. Provide at least one of: a `pending` snippet, a `failed(error, reset)` snippet, or an `onerror(error, reset)` handler. `failed` can be declared inside the boundary or passed as a prop.
- It catches errors thrown while rendering and in effects. It does not catch errors in event handlers, `setTimeout` callbacks or other work outside rendering.
- When it handles an error, the existing content is removed. `reset` re-creates the content, only the first time it is called. An error thrown or rethrown in `onerror` goes to the parent boundary.
- Server: since 5.53, boundaries with a `failed` snippet work during server rendering when `render(App, { transformError })` is given; without it, an error fails the whole render. `transformError(error)` must return a JSON-serializable value (redact messages and stacks), which is rendered by `failed` and serialized for hydration, where `onerror` receives it. If `transformError` throws, `render` rejects. The docs page says "since 5.51", but the feature entry is in the 5.53.0 changelog; 5.53.4 and 5.53.5 fixed it further. Frameworks (SvelteKit) configure `transformError` for you.
- `mount` and `hydrate` also accept `transformError` (default: identity).

```svelte
<svelte:boundary onerror={(e) => report(e)}>
	<Dashboard />
	{#snippet pending()}<p>Loading…</p>{/snippet}
	{#snippet failed(error, reset)}<button onclick={reset}>Retry</button>{/snippet}
</svelte:boundary>
```

## Async server rendering

- Since 5.39, server rendering supports `await`: `const { head, body } = await render(App)`. SvelteKit does this for you.
- `await` expressions outside a boundary with a `pending` snippet are resolved before `render` returns. Inside such a boundary, the server renders the `pending` snippet and skips the rest.
- `render` returns a `RenderOutput` that is both a sync result and awaitable; the types `RenderOutput`, `SyncRenderOutput`, `Csp` and `Sha256Source` are exported from `svelte/server` since 5.57.
- Async server rendering requires Node's `AsyncLocalStorage`; without it, `async_local_storage_unavailable` is thrown.

## Context and initialization order

- `setContext` must run during initialization, before the first `await` in the component script. With `experimental.async`, calling it later throws `set_context_after_init`; since 5.57.1 this also applies during server rendering.
- Read context (`getContext`, or the getter from `createContext`) at the top of the script as well, then use the value after the `await`.

## Fetch before writing when

- You use anything in this file: the whole feature set is experimental, and APIs or ordering can change in any minor release.
- You call `fork`, `hydratable`, `getAbortSignal` or `settled`, or need the exact `render` options (`csp`, `transformError`, `idPrefix`).
- You rely on server-side error boundaries (the docs and the changelog disagree on the version) or on the framework's `transformError` wiring.
- You need to know where the flag goes in a specific SvelteKit or Vite version.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["svelte/await-expressions", "svelte/svelte-boundary"]
```

Sections: `svelte/await-expressions`, `svelte/svelte-boundary`, `svelte/hydratable`, `svelte/$effect`, `svelte/svelte`, `svelte/svelte-server`, `svelte/imperative-component-api`, `svelte/runtime-errors`, `svelte/runtime-warnings`, `svelte/best-practices`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/svelte/await-expressions/llms.txt'
curl -sS 'https://svelte.dev/docs/svelte/svelte-boundary/llms.txt'
curl -sS 'https://svelte.dev/docs/svelte/hydratable/llms.txt'
```

- Changelog: `https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md`
- Source of the `fork` flag check: `https://github.com/sveltejs/svelte/blob/main/packages/svelte/src/internal/client/reactivity/batch.js`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md'
V="$(node -p "require('svelte/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```


Partly derived from sveltejs/ai-tools (MIT), base 6b5d0da; see the plugin NOTICE.
