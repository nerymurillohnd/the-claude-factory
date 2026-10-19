# Context, Lifecycle and Reactivity Classes

> Precedence: the Svelte changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").

## Contents

- [Context](#context)
- [Lifecycle](#lifecycle)
- [Tick, untrack and flushSync](#tick-untrack-and-flushsync)
- [Reactive built-ins](#reactive-built-ins)
- [Window values](#window-values)
- [Shared state and stores](#shared-state-and-stores)
- [Imperative component API](#imperative-component-api)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Context

- Prefer `createContext<T>()` (since 5.40): it returns a typed `[get, set, has]` triplet and needs no key. `get` throws when no ancestor (or the component itself) called `set`. `has` exists since 5.57.
- `setContext(key, value)`, `getContext(key)`, `hasContext(key)` and `getAllContexts()` remain; keys can be any value. All of them must be called during component initialization, and a `setContext` is visible only to `getContext` calls that run after it.
- Put a `$state` proxy (or a class instance with `$state` fields) in context and **mutate** it; reassigning the local variable breaks the link, and Svelte warns. Pass primitives as getter functions.
- Prefer context to module-level shared state: a module singleton mutated during server rendering is shared by every request, so one user's data can leak into another's response.

```ts
// user-context.ts
import { createContext } from "svelte";
export interface User {
  name: string;
}
export const [getUser, setUser, hasUser] = createContext<User>();
```

```svelte
<!-- Parent.svelte -->
<script lang="ts">
	import { setUser } from './user-context';
	let { children } = $props();
	const user = $state({ name: 'Ada' });
	setUser(user);
</script>

{@render children()}
```

### Providing context to a mounted component

- Pass a `context` map to `mount`, `hydrate` or `render`, or wrap the component in a function that sets context first (since 5.50, so `createContext` setters work there too):

```ts
import { mount } from "svelte";
import { setUser } from "./user-context";
import Profile from "./Profile.svelte";

function WithUser(...args: Parameters<typeof Profile>) {
  setUser({ name: "Bob" });
  return Profile(...args);
}
mount(WithUser, { target: document.body });
```

The docs page says "as of version 5.49"; the changelog entry ("allow use of createContext when instantiating components programmatically") is in 5.50.0.

## Lifecycle

- A Svelte 5 component has only creation and destruction; updates are per effect, so there are no component-wide update hooks.
- `onMount(fn)` runs after mount, in the browser only. A cleanup function returned **synchronously** runs on unmount; an `async` function returns a promise, so its cleanup is never called. `$effect` covers most `onMount` uses.
- `onDestroy(fn)` runs before unmount, and is the only lifecycle hook that also runs during server rendering.
- Both must be called during component initialization (they may live in an imported helper), or `lifecycle_outside_component` is thrown.
- `beforeUpdate`/`afterUpdate` are deprecated and not allowed in runes mode. Replace them with `$effect.pre` and `$effect`, with `tick()` to act after the DOM changes.

## Tick, untrack and flushSync

- `await tick()` resolves after pending state changes are applied to the DOM (or in the next microtask if there are none).
- `untrack(() => value)` reads state inside a derived or an effect without making it a dependency.
- `flushSync(fn?)` applies pending updates synchronously and returns `fn`'s result. Use it in tests and right after `mount`/`hydrate` when effects must have run. It may be called inside an effect since 5.43.15 (the runtime-errors page still lists `flush_sync_in_effect`; see the errata).
- `settled()` waits for async work too; see the async reference.

## Reactive built-ins

Import these from `svelte/reactivity`. Reads in the template, in deriveds and in effects are tracked; stored values are **not** made deeply reactive.

| Class | Reactive reads | Notes |
| --- | --- | --- |
| `SvelteMap` | `get`, `has`, `size`, iteration | `getOrInsert(key, value)` and `getOrInsertComputed(key, fn)` since 5.57 |
| `SvelteSet` | `has`, `size`, iteration |  |
| `SvelteDate` | any getter or formatting (`Intl.DateTimeFormat`) | update with setters such as `setTime` |
| `SvelteURL` | `href`, `pathname`, ... (bindable) | `searchParams` is a `SvelteURLSearchParams` |
| `SvelteURLSearchParams` | `get`, `getAll`, iteration |  |
| `MediaQuery` | `current` | since 5.7; `new MediaQuery('min-width: 800px', fallback)` |

- `MediaQuery` cannot know the right value during server rendering (the second argument is the server fallback), so content may change on hydration. Prefer a CSS media query when CSS can do the job. `prefersReducedMotion` (in `svelte/motion`) is a ready-made instance.
- Plain `Map`, `Set`, `Date` and `URL` inside `$state` are not reactive: use these classes instead.

### Subscribing to external sources

`createSubscriber(start)` (since 5.7) turns any event source into reactive reads. Calling the returned `subscribe()` inside a tracked context (effect, derived, template, even through a getter) calls `start(update)` once while at least one tracker is active; each `update()` re-runs the trackers, and the cleanup returned by `start` runs when the last tracker is gone.

```ts
// online.svelte.ts
import { createSubscriber } from "svelte/reactivity";
import { on } from "svelte/events";

export class Online {
  #subscribe = createSubscriber((update) => {
    const offOnline = on(window, "online", update);
    const offOffline = on(window, "offline", update);
    return () => {
      offOnline();
      offOffline();
    };
  });

  get current() {
    this.#subscribe(); // reactive only when read in a tracked context
    return navigator.onLine;
  }
}
```

## Window values

`svelte/reactivity/window` (since 5.11) exports objects with a reactive `current` property: `innerWidth`, `innerHeight`, `outerWidth`, `outerHeight`, `scrollX`, `scrollY`, `screenLeft`, `screenTop`, `devicePixelRatio`, `online`. Read `innerWidth.current` in markup, deriveds or effects instead of adding `<svelte:window bind:innerWidth>` or your own listeners.

## Shared state and stores

- Share state with a class holding `$state` fields, or an exported `$state` object, in a `.svelte.js`/`.svelte.ts` module, preferably delivered through context (see above).
- Stores (`svelte/store`: `writable`, `readable`, `derived`, `readonly`, `get`) still fit complex async streams and RxJS-style code. `$store` auto-subscription works only for stores declared at the top level of a component.
- Interop: `fromStore(store)` returns an object whose `current` is reactive; `toStore(get, set?)` wraps reactive values as a store for store-based APIs.

## Imperative component API

- Components are functions, not classes. `mount(App, { target, props, anchor, context, intro, transformError })` creates and inserts one; `hydrate(App, { ..., recover })` adopts server-rendered HTML (keep the HTML comments that server rendering emits).
- Neither runs effects or `onMount` before returning: call `flushSync()` afterwards when you need them (tests).
- `mount` plays intro transitions unless `intro: false`.
- To update props from outside, pass a `$state` object as `props` and mutate it (this replaces `$set`). The `events` option is deprecated: use callback props.
- `unmount(app, { outro: true })` plays outro transitions first and returns a promise (since 5.13).
- `render(App, { props, context, idPrefix, csp, transformError })` from `svelte/server` runs only on the server build and returns `head` and `body` (`html` is deprecated) plus `hashes`. `idPrefix` exists since 5.22; the docs give only its type, so fetch the source before relying on its exact effect, and note it must not contain `--` (enforced since 5.55.2). `csp` exists since 5.46. CSS is not returned unless components are compiled with `css: 'injected'`.

## Fetch before writing when

- You use `createContext(...).has` (5.57), `SvelteMap.getOrInsert*` (5.57) or mount-time `createContext` wrappers (5.50), or support older versions.
- You need the full `MountOptions`, `hydrate` or `render` option types.
- You are unsure whether a lifecycle function runs on the server.
- You write a custom store or need the exact store contract.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["svelte/context", "svelte/lifecycle-hooks"]
```

Sections: `svelte/context`, `svelte/lifecycle-hooks`, `svelte/imperative-component-api`, `svelte/stores`, `svelte/svelte`, `svelte/svelte-reactivity`, `svelte/svelte-reactivity-window`, `svelte/svelte-store`, `svelte/svelte-server`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/svelte/context/llms.txt'
curl -sS 'https://svelte.dev/docs/svelte/svelte-reactivity/llms.txt'
curl -sS 'https://svelte.dev/docs/svelte/imperative-component-api/llms.txt'
```

- Changelog: `https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md'
V="$(node -p "require('svelte/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```


Partly derived from sveltejs/ai-tools (MIT), base 6b5d0da; see the plugin NOTICE.
