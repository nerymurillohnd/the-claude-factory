# Legacy Syntax and Migration

> Precedence: the Svelte changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").

## Contents

- [Runes mode and legacy mode](#runes-mode-and-legacy-mode)
- [Replacement table](#replacement-table)
- [Component and event changes](#component-and-event-changes)
- [Worked example](#worked-example)
- [Migration tooling](#migration-tooling)
- [Behavior changes to keep in mind](#behavior-changes-to-keep-in-mind)
- [Svelte 6 forward compatibility](#svelte-6-forward-compatibility)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Runes mode and legacy mode

- Svelte 5 compiles each component in runes mode or legacy (Svelte 4 syntax) mode, inferred from its code; the two kinds of components can be mixed in one app. Force a mode with `<svelte:options runes={true} />` or `runes={false}`.
- Write all new code in runes mode. Legacy features keep working but are deprecated, and several are not allowed once a component uses runes.
- Setting `compilerOptions.runes: true` for the whole project also forces runes mode on components inside `node_modules`, which can break libraries. Since 5.54, `runes` may be a function of `{ filename }` (so are `css` and `customElement`); with Vite, `dynamicCompileOptions` in `@sveltejs/vite-plugin-svelte` also works.

```js
// svelte.config.js (or the Svelte plugin options in vite.config.js)
export default {
  compilerOptions: {
    runes: ({ filename }) =>
      filename.split(/[/\\]/).includes("node_modules") ? undefined : true,
  },
};
```

## Replacement table

| Legacy | Replacement |
| --- | --- |
| Top-level `let count = 0` (implicitly reactive) | `let count = $state(0)` |
| `$: doubled = count * 2` | `const doubled = $derived(count * 2)` |
| `$: { sideEffect(); }` | `$effect(() => { ... })`; usually `$derived` or an event handler is better |
| `export let value = 1` | `let { value = 1 } = $props()` |
| `export { klass as class }` | `let { class: klass } = $props()` |
| `$$props` / `$$restProps` | `let props = $props()` / `let { a, ...rest } = $props()` |
| Every prop bindable | `let { value = $bindable() } = $props()` |
| `on:click={fn}` | `onclick={fn}` |
| `on:click\|preventDefault`, `\|once`, `\|self`, ... | call `event.preventDefault()` in the handler, or a wrapper function |
| `on:click\|capture` | `onclickcapture={fn}` |
| `<button on:click>` (forwarding) | accept an `onclick` prop, or spread `{...props}` |
| `createEventDispatcher` + `on:event` on a component | callback props (`let { onchange } = $props()`), `$host()` for custom elements |
| `<slot />` | `let { children } = $props()` + `{@render children?.()}` |
| `<slot name="x" item={i} />` + `let:item` | snippet prop: `{@render x(i)}` + `{#snippet x(item)}` in the parent |
| `$$slots.x` | check the snippet prop: `{#if x}` |
| `<svelte:fragment slot="x">` | `{#snippet x()}...{/snippet}` |
| `<svelte:component this={C} />` | `<C />` (re-renders when `C` changes) |
| `<svelte:self />` | `import Self from './Tree.svelte'` and `<Self />` |
| `beforeUpdate` / `afterUpdate` | `$effect.pre` / `$effect`, plus `tick()` |
| `use:action={arg}` | `{@attach factory(arg)}`, or `{@attach fromAction(action, () => arg)}` |
| `class:active={on}` | `class={['base', on && 'active']}` (object or array form, since 5.16) |
| `{@const x = y}` | `{const x = $derived(y)}` (declaration tags, since 5.56) |
| `spring()` / `tweened()` stores | `Spring` / `Tween` classes (since 5.8) |
| Stores for shared state | classes with `$state` fields, or a `$state` object, in `.svelte.ts` modules |
| `<script context="module">` | `<script module>` |
| `new App({ target })` | `mount(App, { target })` or `hydrate(...)` |
| `app.$set(...)`, `app.$on(...)`, `app.$destroy()` | mutate a `$state` props object; callback props; `unmount(app)` |
| `App.render(props)` on the server | `render(App, { props })` from `svelte/server` |
| `SvelteComponent`, `ComponentType`, `ComponentEvents` | `Component<Props>`; events are callback props |

## Component and event changes

- Components are functions. `bind:this` returns only the instance exports. In runes mode, `accessors` and `immutable` are ignored, and binding directly to an export (`<A bind:foo />`) is an error: use `bind:this`.
- Temporary bridges from `svelte/legacy`: `createClassComponent`/`asClassComponent` for the Svelte 4 class API, the `compatibility.componentApi: 4` compiler option for code you do not control, and `preventDefault`, `stopPropagation`, `once`, `self`, `trusted`, `passive`, `nonpassive`, `handlers`, `createBubbler` for modifiers. Every export of `svelte/legacy` is deprecated.
- A component using slots can receive snippets from a parent, but not the other way round: a component that uses `{@render}` cannot receive slotted content. Custom elements still use `<slot />`.
- Classes are no longer auto-reactive: assigning `foo.value` on a plain class instance does not update the UI. Use `$state` fields.

## Worked example

A Svelte 4 component, input:

```svelte
<script>
  import { createEventDispatcher } from 'svelte';
  export let open = false;
  export let title;
  const dispatch = createEventDispatcher();
  $: label = open ? 'Hide' : 'Show';
  function toggle() {
    open = !open;
    dispatch('toggle', open);
  }
</script>

<button on:click={toggle} class:active={open}>{label} {title}</button>
{#if open}<slot />{/if}
```

Output:

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';
  let { open = $bindable(false), title, ontoggle, children }:
    { open?: boolean; title: string; ontoggle?: (open: boolean) => void; children?: Snippet } = $props();
  const label = $derived(open ? 'Hide' : 'Show');
  function toggle() {
    open = !open;
    ontoggle?.(open);
  }
</script>

<button onclick={toggle} class={[open && 'active']}>{label} {title}</button>
{#if open}{@render children?.()}{/if}
```

Every change follows the replacement table: props from `$props()` (`$bindable` because the parent may bind `open`), a computed value with `$derived`, a callback prop instead of the dispatcher, an event attribute, a `class` array instead of `class:`, and the default slot as the `children` snippet. Run the autofixer on the result before handing it back.

## Migration tooling

- Run the migration on a committed tree, so its diff can be reviewed and reverted:

  ```sh
  git status --short          # must print nothing
  npx sv migrate svelte-5
  ```

  It bumps dependencies, converts `let`/`$:`/`export let` to runes, `on:click` to `onclick`, slots to snippets and render tags, and `new Component(...)` to `mount(...)`.
- `svelte-5` is a legacy migration: `sv` delegates it to `svelte-migrate@1`, which is kept available but no longer updated. Review the whole diff and run your checks afterwards.
- Clean up after it:
  - `run(() => ...)` from `svelte/legacy` marks a `$:` statement it could not classify. It runs once on the server and as `$effect.pre` in the browser. Rewrite it as `$derived` when it computes a value, otherwise as `$effect` (or an event handler).
  - Modifier helpers from `svelte/legacy` (`preventDefault(...)`, ...): inline `event.preventDefault()`.
  - Not migrated at all: `createEventDispatcher` and `beforeUpdate`/`afterUpdate`. Convert them by hand.
- Self-closing non-void tags (`<div />`) warn `element_invalid_self_closing_tag`; fix them with:

  ```sh
  npx sv migrate self-closing-tags
  ```
- One component at a time: the VS Code command "Migrate Component to Svelte 5 Syntax", or the playground "Migrate" button.

## Behavior changes to keep in mind

- Whitespace between nodes collapses to one space and is trimmed at the start and end of a tag; `<p>foo<span> - bar</span></p>` renders `foo- bar`. Move the space outside the tag or write `{' '}`.
- HTML structure is stricter: markup the browser would repair (a `<tr>` directly in `<table>`) is a compile error.
- `null`/`undefined` render as an empty string. Event attributes no longer accept strings (`onclick="..."`).
- `children` is a reserved prop name. Dot-notation tags (`<item.component>`) are components.
- `<svelte:element this="div">` must be `this={'div'}`.
- `:is()`, `:has()` and `:where()` contents are scoped; scoped CSS uses `:where(.svelte-hash)`.
- `mount` plays intro transitions by default; `mount`/`hydrate` do not run effects synchronously.
- Error and warning codes use underscores (`a11y_autofocus`, not `a11y-autofocus`), including in `svelte-ignore` comments.
- A modern browser is required (proxies, `ResizeObserver`).

## Svelte 6 forward compatibility

- Runes mode becomes the default (`runes` option docs).
- A quoted single expression (`prop="{value}"`) will be converted to a string: write `prop={value}` now (`attribute_quoted` warns on components and custom elements).
- `experimental.async` is removed as a flag and its behavior becomes the default, including `set_context_after_init`. Call `setContext` before the first `await`.
- In "a future version" (no major named): every falsy `class` value omits the attribute instead of stringifying `false`; self-closing non-void tags may become an error; Svelte's internal slot handling is removed, leaving `<slot>` as a plain DOM element.

## Fetch before writing when

- You migrate a real codebase: read the migration guide sections that match what you find, and the `sv migrate` page for the current migration list (`mcp__plugin_svelte-development_svelte__get-documentation` with `section: ["svelte/v5-migration-guide", "cli/sv-migrate"]`).
- You need a `svelte/legacy` export's exact signature or a compiler option such as `compatibility.componentApi`.
- You plan for Svelte 6: the forward-compatibility notes above come from warnings and option docs, not from a release.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["svelte/v5-migration-guide", "svelte/legacy-overview"]
```

Sections: `svelte/v5-migration-guide`, `svelte/legacy-overview`, `svelte/legacy-let`, `svelte/legacy-reactive-assignments`, `svelte/legacy-export-let`, `svelte/legacy-$$props-and-$$restProps`, `svelte/legacy-on`, `svelte/legacy-slots`, `svelte/legacy-$$slots`, `svelte/legacy-svelte-fragment`, `svelte/legacy-svelte-component`, `svelte/legacy-svelte-self`, `svelte/legacy-component-api`, `svelte/svelte-legacy`, `svelte/svelte-compiler`, `cli/sv-migrate`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/svelte/v5-migration-guide/llms.txt'
curl -sS 'https://svelte.dev/docs/cli/sv-migrate/llms.txt'
```

- Changelog: `https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md'
V="$(node -p "require('svelte/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
