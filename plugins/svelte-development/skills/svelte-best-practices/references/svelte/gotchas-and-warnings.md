# Gotchas and Warnings

> Precedence: the Svelte changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").

## Contents

- [Events and markup](#events-and-markup)
- [Reactivity](#reactivity)
- [Server rendering and hydration](#server-rendering-and-hydration)
- [Styling and motion](#styling-and-motion)
- [Build and tooling](#build-and-tooling)
- [Errors the compiler does not catch](#errors-the-compiler-does-not-catch)
- [Looking up a warning or error code](#looking-up-a-warning-or-error-code)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Events and markup

1. **Delegated events and `stopPropagation`.** `click`, `input`, `keydown`, pointer, mouse and touch events (full list in the template syntax reference) are handled by one listener at the app root. A manual `addEventListener` that calls `stopPropagation` stops declarative `onclick` handlers from running, and manual listeners inside the root run before them. A manually dispatched event needs `{ bubbles: true }`. Fix: attach manual listeners with `on()` from `svelte/events`.
2. **`onClick` is not `onclick`.** Event attributes are case sensitive; `onClick` listens to an event named `Click`. Always write lowercase DOM event names.
3. **Quoted single expressions.** `prop="{value}"` warns `attribute_quoted` on components and custom elements and will become a string in Svelte 6. Write `prop={value}`.
4. **Whitespace.** Whitespace at the start and end of a tag is removed, so `foo<span> - bar</span>` renders `foo- bar`. Put the space outside the tag or use `{' '}`.
5. **Self-closing non-void tags.** `<div />` and `<span />` warn `element_invalid_self_closing_tag` (browsers parse the following content as children). Write `<div></div>`. To fix a whole codebase, on a committed tree:

   ```sh
   npx sv migrate self-closing-tags
   ```

## Reactivity

6. **Proxy identity (`state_proxy_equality_mismatch`).** `$state(obj)` returns a proxy, so `proxy === obj` is always false and `array.indexOf(rawItem)` fails. Compare values that are both proxies or both raw (`$state.raw` does not proxy).
7. **Logging proxies (`console_log_state`).** `console.log(proxy)` shows the proxy, not the value. Use `$inspect(value)` or `console.log($state.snapshot(value))`.
8. **Effects track synchronous reads only.** State read after an `await`, in `setTimeout`, or in a promise callback is not a dependency. Read it at the top of the effect. In async deriveds, see `await_reactivity_loss` in the async reference.
9. **Writing state while deriving (`state_unsafe_mutation`).** Assigning state inside `$derived`, `$inspect` or a template expression throws. Make every value a `$derived`; move real side effects to a handler or an effect.
10. **Effect loops (`effect_update_depth_exceeded`).** An effect that reads and writes the same state, including `array.push` on a state array, loops until Svelte stops it. Use `$derived`, keep write-only data out of `$state`, or read through `untrack`.
11. **Stale deriveds (`derived_inert`).** A `$derived` created inside an effect stops updating when that effect is destroyed. Create it outside, or inside `$effect.root`.
12. **Captured initial values (`state_referenced_locally`).** `setContext('count', count)` or `const label = type === 'a' ? ... : ...` at setup reads the value once. Use `$derived`, or pass a getter or a proxy.
13. **Exported reassigned state.** A `.svelte.js` module cannot `export let x = $state(...)` and reassign `x`: importers get the internal signal. Export a proxy object and mutate it, or export getter functions.
    A `$derived` cannot be exported from a module at all (`derived_invalid_export`, a compile error): export a function that returns its value. A derived that reads itself fails with `derived_references_self`.

## Server rendering and hydration

14. **Shared module state leaks between requests.** A module-level `$state` mutated during server rendering is shared by every request, so another user can see it. Keep request data in context (`createContext`) or props.
15. **Hydration does not repair `{@html}` or `<img src>`.** If these differ between server and client, Svelte keeps the server value and warns in development (`hydration_html_changed`, `hydration_attribute_changed`). Make them deterministic, or unset them and set them again in an `$effect` after mount.
16. **`mount` plays intros and defers effects.** `mount` runs intro transitions unless `intro: false`, and neither `mount` nor `hydrate` runs effects or `onMount` before returning: call `flushSync()` when a test needs them.

## Styling and motion

17. **Reduced motion is not CSS.** Svelte transitions run on the Web Animations API, so a global `prefers-reduced-motion` CSS rule does not shorten them. Branch on `prefersReducedMotion.current` from `svelte/motion`.
18. **`:is()`, `:has()` and `:where()` are scoped.** Their contents are matched against the component, so selectors for elements outside it are dropped as unused. Wrap those parts in `:global(...)` (also for Tailwind `@apply` with variants).

## Build and tooling

19. **Custom element props must be declared.** With `let props = $props()`, Svelte cannot know which properties to expose on the element. Destructure every prop or list it in the `customElement.props` option, and never name a prop starting with `on`.
20. **TypeScript beyond types needs a preprocessor.** Enums, constructor parameter properties with modifiers, and non-standard syntax fail in `<script lang="ts">` without `vitePreprocess({ script: true })`. Prefer union types or `as const` objects to enums.
21. **Project-wide `runes: true` also hits `node_modules`.** It forces runes mode on library components written in legacy syntax. Since 5.54 make `runes` a function of `{ filename }`, or use `dynamicCompileOptions` in `@sveltejs/vite-plugin-svelte`.

## Errors the compiler does not catch

22. **Snippet without `{@render}` (`snippet_without_render_tag`).** `{snippet}` raises this runtime error instead of rendering the snippet. Write `{@render snippet()}`.
23. **Binding to a prop that is not bindable (`bind_not_bindable`).** The child must declare `let { value = $bindable() } = $props()`. `bind:value={undefined}` fails with `props_invalid_value` when the child gives the prop a fallback.
24. **Duplicate keys (`each_key_duplicate`).** A keyed `{#each}` throws when two items share a key. Key by a unique id.
25. **Runes outside an owner (`effect_orphan`).** `$effect` and similar runes run only during component initialisation or inside another effect. In a callback or module, wrap the work in `$effect.root`.

## Looking up a warning or error code

- Codes use underscores (`a11y_click_events_have_key_events`, `state_referenced_locally`). There are four lists:
  - compile-time warnings, including every `a11y_*` rule: `https://svelte.dev/docs/svelte/compiler-warnings/llms.txt`
  - compile-time errors: `https://svelte.dev/docs/svelte/compiler-errors/llms.txt`
  - runtime warnings (client and server): `https://svelte.dev/docs/svelte/runtime-warnings/llms.txt`
  - runtime errors: `https://svelte.dev/docs/svelte/runtime-errors/llms.txt`
- Look the code up in its list; each entry is a `### <code>` heading with the message and the explanation. Since 5.10, messages link to their documentation. With the MCP server:

  ```text
  mcp__plugin_svelte-development_svelte__get-documentation
    section: ["svelte/compiler-warnings"]
  ```

  Without it, download the list and print the entry:

  ```sh
  curl -sS 'https://svelte.dev/docs/svelte/compiler-warnings/llms.txt' | grep -n -A 12 '^### a11y_click_events_have_key_events'
  ```
- Silence a false positive with `<!-- svelte-ignore code_a, code_b (reason) -->` on the line above the markup. Fix accessibility warnings instead of ignoring them unless the reason is documented. Project-wide filtering uses the `warningFilter` compiler option.

## Fetch before writing when

- A warning or error code appears that this file does not explain, or its message differs from the text here.
- You are about to silence an `a11y_*` warning: read its entry first.
- You hit a hydration warning not covered above (`hydration_mismatch` has several causes).

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["svelte/compiler-warnings", "svelte/compiler-errors"]
```

Sections: `svelte/compiler-warnings`, `svelte/compiler-errors`, `svelte/runtime-warnings`, `svelte/runtime-errors`, `svelte/basic-markup`, `svelte/v5-migration-guide`, `svelte/best-practices`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/svelte/compiler-warnings/llms.txt'
curl -sS 'https://svelte.dev/docs/svelte/compiler-errors/llms.txt'
curl -sS 'https://svelte.dev/docs/svelte/runtime-warnings/llms.txt'
curl -sS 'https://svelte.dev/docs/svelte/runtime-errors/llms.txt'
curl -sS 'https://svelte.dev/docs/svelte/v5-migration-guide/llms.txt'
```

- Changelog: `https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md'
V="$(node -p "require('svelte/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
