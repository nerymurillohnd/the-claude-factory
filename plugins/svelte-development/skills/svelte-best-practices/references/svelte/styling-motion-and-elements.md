# Styling, Motion and Special Elements

> Precedence: the Svelte changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").

## Contents

- [Scoped styles](#scoped-styles)
- [Global styles](#global-styles)
- [Styling children and passing values](#styling-children-and-passing-values)
- [Transitions and animations](#transitions-and-animations)
- [Motion classes](#motion-classes)
- [Special elements](#special-elements)
- [Custom elements](#custom-elements)
- [TypeScript](#typescript)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Scoped styles

- CSS in a component's top-level `<style>` is scoped: matching elements get a hash class (`svelte-xyz123`) and each selector gains 0-1-0 specificity; repeated scoping uses `:where(.svelte-xyz123)` so specificity does not grow further.
- `@keyframes` names are scoped the same way. Selectors that match nothing in the component's markup are removed and warned about; there is no option to keep them.
- Selectors inside `:is(...)`, `:has(...)` and `:where(...)` are analyzed against the component like any other selector, so rules that relied on them acting globally become "unused". Use `:global(...)` inside them.
- Only one top-level `<style>` is allowed. A `<style>` nested inside an element or block is inserted as is, unscoped and unprocessed, so it applies to the whole page.

## Global styles

- `:global(selector)` for one selector, or partially global selectors such as `.wrapper :global(p)`.
- A `:global { ... }` block for a group, or nested under a scoped selector: `.prose :global { a { ... } }` (the nested form is preferred over `.prose :global a`).
- Global keyframes: prefix the name with `-global-` (the prefix is removed at compile time).
- Tailwind `@apply` with variants that generate `:is(...)`: wrap the rule as `main :global { @apply ... }`.

## Styling children and passing values

- Preferred: CSS custom properties. `<Slider --track-color="black" />` wraps the component in `<svelte-css-wrapper style="display: contents; ...">` (a `<g>` inside SVG). It does not affect layout, but it does break child combinators such as `.parent > .child`.
- From JavaScript values: `<div style:--columns={columns}>` and `var(--columns)` in the stylesheet.
- When the child is not yours (a library component), wrap it in your own element and use `:global` beneath it.
- To let callers add classes, accept a `class` prop typed `ClassValue` and merge it: `class={['base', className]}`.

## Transitions and animations

- `transition:fn` (reversible), `in:fn` / `out:fn` (independent). Built-ins live in `svelte/transition` (`fade`, `fly`, `slide`, `scale`, `blur`, `draw`, `crossfade`), easings in `svelte/easing`.
- Transitions are local by default: they play only when their own block is created or destroyed. Add `|global` to also play when a parent block changes.
- A block that is transitioning out keeps all its elements in the DOM until every transition in it finishes.
- Parameters are an object expression: `transition:fly={flyParams}` with `const flyParams = { y: 200, duration: 300 }`.
- Transitions and animations run on the **Web Animations API**, not CSS transitions, so a global `@media (prefers-reduced-motion: reduce)` rule that zeroes durations has no effect. Read `prefersReducedMotion.current` (from `svelte/motion`, since 5.7) and reduce or disable the motion.
- A custom transition is `(node, params, { direction }) => ({ delay, duration, easing, css, tick })`; prefer `css(t, u)` (runs off the main thread) over `tick(t, u)`. Returning a function instead of an object defers it to the next microtask (used by `crossfade`).
- Elements with transitions dispatch `introstart`, `introend`, `outrostart`, `outroend` (listen with `onintroend={...}`).
- `animate:flip` (from `svelte/animate`) runs when items of a **keyed** each block are reordered, not when they are added or removed, and must be on an immediate child of that block. A custom animation receives `(node, { from, to }, params)`.

```svelte
<script lang="ts">
	import { fly } from 'svelte/transition';
	import { prefersReducedMotion } from 'svelte/motion';
	let visible = $state(false);
	const flyParams = $derived({ y: prefersReducedMotion.current ? 0 : 200 });
</script>

{#if visible}
	<p transition:fly={flyParams}>Hello</p>
{/if}
```

## Motion classes

- `Spring` and `Tween` (since 5.8, from `svelte/motion`) hold `target` and `current`. Set or bind `target`; read `current`. `set(value, options)` returns a promise that resolves when `current` arrives; `Spring.set` accepts `{ instant, preserveMomentum }`.
- `Spring.of(() => value)` and `Tween.of(() => value)` follow a reactive value; call them where an effect root exists (component initialization).
- Since 5.17, tweening a non-numeric value snaps to the new value. The option types (`TweenOptions`, `SpringOptions`, `SpringUpdateOptions`, `Updater`) are exported since 5.55.
- The `spring` and `tweened` store functions are deprecated: replace them with the classes.

```svelte
<script lang="ts">
	import { Spring } from 'svelte/motion';
	let { value }: { value: number } = $props();
	const smooth = Spring.of(() => value, { stiffness: 0.2, damping: 0.6 });
</script>

<progress value={smooth.current} max="100"></progress>
```

## Special elements

- `<svelte:window>`, `<svelte:document>`, `<svelte:body>` and `<svelte:head>` must be at the top level of the component, never inside a block or an element. They clean up their listeners automatically and are safe during server rendering.
- `<svelte:window onkeydown={...} bind:scrollY={y} />`: bindable `innerWidth`, `innerHeight`, `outerWidth`, `outerHeight`, `scrollX`, `scrollY`, `online`, `devicePixelRatio`; only `scrollX`/`scrollY` are writable, and their initial value does not scroll the page. For read-only values, `svelte/reactivity/window` avoids the element entirely.
- `<svelte:document>`: events such as `visibilitychange`, attachments, and read-only bindings `activeElement`, `fullscreenElement`, `pointerLockElement`, `visibilityState`.
- `<svelte:body>`: events such as `mouseenter`/`mouseleave`, and actions.
- `<svelte:head>`: elements for `document.head`; returned separately as `head` by server rendering.
- `<svelte:element this={tag}>`: a tag chosen at runtime; `this` must be an expression; a nullish `this` renders nothing; children on a void tag throw in development; only `bind:this` works; set `xmlns` when the namespace cannot be inferred.
- `<svelte:options>`: `runes`, `namespace` (`html`, `svg`, `mathml`), `customElement`, `css="injected"`. `immutable` and `accessors` are deprecated and do nothing in runes mode. Content inside the tag is an error.
- `<svelte:boundary>`: see the async reference. `<svelte:component>`, `<svelte:self>` and `<svelte:fragment>` are legacy.

## Custom elements

- Compile with the `customElement: true` compiler option and name the tag with `<svelte:options customElement="my-element" />`, or with an object: `tag`, `shadow` (`"none"`, `"open"`, or a `ShadowRootInit` object since 5.49), `props` (per prop: `attribute`, `reflect`, `type` of `'String' | 'Boolean' | 'Number' | 'Array' | 'Object'`) and `extend` (wrap the generated class, for example for `ElementInternals`).
- Without a tag name, register later with `customElements.define('my-element', Component.element)`.
- Declare every prop explicitly in the destructuring (or in `props` options): with `let props = $props()` Svelte cannot know which properties to expose on the element.
- `$host()` gives the host element, for example to `dispatchEvent(new CustomEvent('change'))`.
- The inner component is created in the tick after `connectedCallback` and destroyed in the tick after `disconnectedCallback`. Properties set before connection are kept; exported functions exist only after mount.
- Caveats: styles are encapsulated in the shadow root (page styles and `:global` do not reach in) and inlined as a JavaScript string; custom elements are poorly suited to server rendering; context does not cross custom-element boundaries; `<slot>` content renders eagerly; never name a prop starting with `on`, since it is treated as an event listener.

## TypeScript

- `<script lang="ts">` supports only type-only syntax: annotations, interfaces, `as`, generics. Enums, constructor parameter properties with access modifiers, and not-yet-standard syntax require a preprocessor: `vitePreprocess({ script: true })` from `@sveltejs/vite-plugin-svelte`.
- `tsconfig.json`: `target` of at least `ES2015`, `verbatimModuleSyntax: true`, `isolatedModules: true` (SvelteKit 3 includes the last two in `$app/tsconfig`).
- Generic components: `<script lang="ts" generics="Item extends { id: string }">`; the attribute content is what goes between `<...>` in a generic function.
- `$state<number>()` is `number | undefined`; in classes, `value = $state() as number` is acceptable when the constructor assigns it.
- Types: `Component<Props>` for component values, `ComponentProps<typeof X>` for props, `Snippet<[Args]>` for snippets, and `svelte/elements` (`HTMLButtonAttributes`, `SvelteHTMLElements['div']`, `ClassValue`) for wrappers. Add custom attributes or elements by augmenting `declare module 'svelte/elements'` in a `.d.ts` that ends with `export {}`.

## Fetch before writing when

- You need the exact options of a built-in transition or easing, or the `Spring`/`Tween` option defaults.
- You target an older version than any "since" above (`ShadowRootInit` 5.49, motion classes 5.8, option types 5.55).
- You write custom element options or `extend` with TypeScript (only erasable syntax is allowed there).
- You need the full list of `<svelte:window>`/`<svelte:document>` bindings, or a CSS warning code.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["svelte/scoped-styles", "svelte/global-styles"]
```

Sections: `svelte/scoped-styles`, `svelte/global-styles`, `svelte/custom-properties`, `svelte/nested-style-elements`, `svelte/transition`, `svelte/in-and-out`, `svelte/animate`, `svelte/svelte-motion`, `svelte/svelte-transition`, `svelte/svelte-animate`, `svelte/svelte-easing`, `svelte/svelte-window`, `svelte/svelte-document`, `svelte/svelte-body`, `svelte/svelte-head`, `svelte/svelte-element`, `svelte/svelte-options`, `svelte/custom-elements`, `svelte/$host`, `svelte/typescript`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/svelte/transition/llms.txt'
```

Same pattern for each slug above.

- Changelog: `https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md'
V="$(node -p "require('svelte/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
