# Runes

> Precedence: the Svelte changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").

## Contents

- [Runes are compiler keywords](#runes-are-compiler-keywords)
- [State and deep proxies](#state-and-deep-proxies)
- [State in classes](#state-in-classes)
- [Raw, snapshot and eager state](#raw-snapshot-and-eager-state)
- [Derived values](#derived-values)
- [Effects](#effects)
- [Props and bindable props](#props-and-bindable-props)
- [Debugging with inspect](#debugging-with-inspect)
- [Host element](#host-element)
- [Misuse patterns and their warnings](#misuse-patterns-and-their-warnings)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Runes are compiler keywords

- Runes (`$state`, `$derived`, `$effect`, `$props`, `$bindable`, `$inspect`, `$host`) work only in `.svelte`, `.svelte.js` and `.svelte.ts` files. They are not imported, are not values, and are valid only in specific positions.
- A component is in runes mode when it uses a rune (or `<svelte:options runes />`); `.svelte.js`/`.svelte.ts` modules are always in runes mode.
- Only declare `$state` for values that drive an effect, a derived or the template. Everything else is a plain variable.

## State and deep proxies

- `$state(value)` on a primitive gives a plain variable that the compiler instruments: read and write it directly, there is no `.value`.
- Arrays and plain objects become deep proxies, recursively, until a non-plain value (class instance, `Object.create(...)`) is reached. Values pushed later are proxied too. The original object is never mutated.
- Proxies cost performance. For large data that is only ever replaced (API responses), use `$state.raw`.
- Destructuring a proxy captures the current values; the new bindings are not reactive.
- Functions receive values, not variables. To give a function live access, pass getters or a proxy/object, not a destructured primitive.
- A `.svelte.js` module cannot export state that it reassigns (importers would receive the internal signal). Export a proxy and mutate its properties, or export accessor functions:

```ts
// counter.svelte.ts
export const counter = $state({ count: 0 }); // fine: mutated, never reassigned

let total = $state(0);
export const getTotal = () => total; // fine: not exported directly
export const addToTotal = (n: number) => (total += n);
```

## State in classes

- Class instances are never proxied, and wrapping `new Foo()` in `$state` does nothing. Make the fields reactive instead: `$state` (or `$state.raw`, `$derived`) in a public or private field declaration, or, since 5.31, as the first assignment to a property inside the constructor.
- The compiler turns these fields into prototype `get`/`set` pairs over private storage, so they are **not enumerable**: object spread, `Object.keys` and `JSON.stringify` do not see them.
- Passing a method as a handler (`onclick={todo.reset}`) loses `this`. Use an arrow-function field or an inline arrow.

```js
class Todo {
  done = $state(false);
  constructor(text) {
    this.text = $state(text); // since 5.31
  }
  reset = () => {
    this.text = "";
    this.done = false;
  };
}
```

## Raw, snapshot and eager state

- `$state.raw(value)`: no proxy; mutation has no effect, only reassignment updates. It may contain reactive values. Allowed in class fields.
- `$state.snapshot(proxy)`: returns a plain, static copy for APIs that reject proxies (`structuredClone`, third-party libraries, logging). If a value has `toJSON`, the snapshot clones what `toJSON` returns.
- `$state.eager(value)` (since 5.41): returns the new value immediately even while `await`-driven updates hold the rest of the UI back. Use it only for instant feedback to a user action, such as `aria-current` on the clicked link.

## Derived values

- `$derived(expression)` takes an expression, not a function. For multi-statement logic use `$derived.by(() => { ... })`. `$derived(x)` is equivalent to `$derived.by(() => x)`.
- Dependencies are the values read **synchronously** while evaluating. If the expression itself contains `await`, state read after the `await` is tracked too; this does not extend into functions it calls. Use `untrack(() => ...)` to exclude a read.
- Deriveds must be free of side effects: writing state inside one throws `state_unsafe_mutation`. Derive every value instead of setting two at once.
- Since 5.25 a derived can be reassigned (unless declared with `const`); the override holds until a dependency changes. This is the tool for optimistic UI, not `$effect`.
- The derived value is returned as is, never proxied. If it points into a `$state` proxy (`$derived(items[index])`), mutating it mutates the source. For a deeply reactive derived object, create `$state` inside `$derived.by`.
- Destructuring a derived makes every binding reactive: `let { a, b } = $derived(compute())`.
- Push-pull: dependents are marked dirty immediately, but recomputed only when read. If the new value is referentially equal to the old one, downstream updates are skipped.

```svelte
<script lang="ts">
	let { post, like }: { post: { likes: number }; like: () => Promise<void> } = $props();
	let likes = $derived(post.likes);

	async function onclick() {
		likes += 1; // optimistic override (since 5.25)
		try {
			await like();
		} catch {
			likes -= 1;
		}
	}
</script>

<button {onclick}>{likes}</button>
```

## Effects

- `$effect` runs only in the browser, after mount, then in a microtask after its dependencies change; re-runs are batched and happen after DOM updates. Never guard its body with `if (browser)`.
- Return a teardown function; it runs before each re-run and when the effect is destroyed (component unmounted or parent effect re-run). An effect can be created anywhere while a parent effect is running.
- Dependencies are the reactive values read synchronously in the body, including inside called functions. Reads after `await` or inside `setTimeout` are not tracked. Reading a proxy object without reading its properties does not track its contents. Dependencies are re-collected on every run, so a branch not taken contributes none. `$state`/`$derived` created inside the effect are not dependencies.
- `$effect.pre`: same as `$effect`, but runs before the DOM updates scheduled after it (a parent's DOM may already be updated). With `experimental.async`, `{#if}`/`{#each}` updates in the same component run before it.
- `$effect.tracking()`: `true` inside an effect or the template, `false` in setup code. Used to build abstractions such as `createSubscriber`.
- `$effect.root(fn)`: a non-tracked scope that is not cleaned up automatically and can be created outside component initialization; it returns a `destroy` function.
- `$effect.pending()`: with `experimental.async`, the number of pending promises in the current boundary (child boundaries excluded).

Effects are an escape hatch. Before writing one, check:

| Intent | Use instead |
| --- | --- |
| Compute a value from state | `$derived` / `$derived.by` |
| Keep two inputs in sync | a function binding `bind:value={get, set}` |
| React to a user action | the event handler |
| Drive a DOM library on an element | `{@attach ...}` |
| Log reactive values | `$inspect` |
| Observe an external event source | `createSubscriber` from `svelte/reactivity` |
| Listen on `window`/`document` | `<svelte:window>` / `<svelte:document>` attributes |

If an effect really must write state it also reads, read it through `untrack` to avoid `effect_update_depth_exceeded`.

## Props and bindable props

- `let { a, b = 'fallback', class: klass, ...rest } = $props()`. Fallbacks apply when the prop is absent or `undefined`, and are never proxied.
- Props change over time: compute dependent values with `$derived`, not a plain `let` (a plain initializer captures only the first value and triggers `state_referenced_locally`).
- A child may reassign a prop temporarily, but must not mutate it: a plain object mutation does nothing, and mutating a parent's proxy works but warns `ownership_invalid_mutation`. Communicate upward with callback props, or share with `$bindable`.
- `$bindable(fallback?)` makes a prop bindable (`bind:value` in the parent is then optional). When the prop is bound and has a fallback, the parent must pass a value other than `undefined` or a runtime error is thrown.
- `children` is reserved for the implicit snippet; do not declare another prop with that name.
- Type props with an interface on the destructuring; for wrappers extend `svelte/elements` types (`HTMLButtonAttributes`); type snippet props with `Snippet<[...]>` from `svelte`.
- `$props.id()` (since 5.20): an ID unique to the component instance and stable between server render and hydration, for `for`/`aria-*` links.

```svelte
<script lang="ts">
	let { value = $bindable(''), label }: { value?: string; label: string } = $props();
	const uid = $props.id();
</script>

<label for="{uid}-input">{label}</label>
<input id="{uid}-input" bind:value />
```

## Debugging with inspect

- `$inspect(...values)` logs on init and on every deep change, in development only (a no-op in production). `.with((type, ...values) => ...)` replaces `console.log`; `type` is `"init"` or `"update"`.
- `$inspect.trace(label?)` (since 5.14) must be the first statement of a function body (an `$effect`, a `$derived.by`, or a function they call). It prints which state caused the re-run; source names are included since 5.34.
- Logging a proxy with `console.log` warns `console_log_state`: use `$inspect` or `$state.snapshot`.

## Host element

`$host()` returns the host element, and only works when the component is compiled as a custom element (for example, to dispatch `CustomEvent`s).

## Misuse patterns and their warnings

| Code | Cause | Fix |
| --- | --- | --- |
| `non_reactive_update` | A plain `let` is reassigned and read in the template or another reactive context | Declare it with `$state` |
| `state_referenced_locally` | State or a prop is read once at setup (`setContext('k', count)`, `const c = type === 'x'`) | Use `$derived`, or pass a getter or a proxy |
| `state_unsafe_mutation` | State written inside `$derived`, `$inspect` or a template expression | Derive every value |
| `effect_update_depth_exceeded` | An effect reads and writes the same state (including `array.push`) | `$derived`, plain (non-state) storage, or `untrack` |
| `derived_inert` | A derived created inside an effect is read after that effect was destroyed | Create it outside the effect, or in `$effect.root` |
| `ownership_invalid_mutation` | A child mutates a prop object it does not own | Callback prop or `$bindable` |

Props were added to `state_referenced_locally` in 5.45.3; since 5.51.2 non-destructured props warn as well.

## Fetch before writing when

- You need the exact rules for constructor state fields, `$state.eager` or writable deriveds, or are targeting a version older than 5.31, 5.41 or 5.25 respectively.
- A warning code is not in the table above, or its wording differs from what you see.
- You use `$effect.pending()` or any rune together with `experimental.async`, which can change outside semver.
- Your memory says deriveds are read-only, `$state` proxies class instances, or `$inspect` runs in production: all of these are wrong.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["svelte/what-are-runes", "svelte/$state"]
```

Sections: `svelte/what-are-runes`, `svelte/$state`, `svelte/$derived`, `svelte/$effect`, `svelte/$props`, `svelte/$bindable`, `svelte/$inspect`, `svelte/$host`, `svelte/compiler-warnings`, `svelte/runtime-warnings`, `svelte/runtime-errors`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/svelte/$state/llms.txt'
```

Same pattern for `$derived`, `$effect`, `$props`, `$bindable`, `$inspect`, `$host`.

- Changelog: `https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md'
V="$(node -p "require('svelte/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```


Partly derived from sveltejs/ai-tools (MIT), base 6b5d0da; see the plugin NOTICE.
