# Template Syntax

> Precedence: the Svelte changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").

## Contents

- [Markup and attributes](#markup-and-attributes)
- [Event attributes](#event-attributes)
- [Conditional, list and key blocks](#conditional-list-and-key-blocks)
- [Await blocks](#await-blocks)
- [Snippets and render tags](#snippets-and-render-tags)
- [Raw HTML](#raw-html)
- [Attachments](#attachments)
- [Declaration tags](#declaration-tags)
- [Debug tag](#debug-tag)
- [Bindings](#bindings)
- [Class and style attributes](#class-and-style-attributes)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Markup and attributes

- A lowercase tag is an element; a capitalized tag or dot notation (`<item.component>`) is a component. A component held in a variable renders directly: `<Thing />` re-renders when `Thing` changes.
- Boolean attributes are present when truthy. Other attributes are omitted when `null` or `undefined`. `{name}` is shorthand for `name={name}`. With spreads, later attributes win.
- Text expressions are escaped; `null`/`undefined` render as an empty string. Wrap a regular-expression literal in parentheses.
- Quoting a single expression (`disabled="{x}"`) still passes the value today, but warns `attribute_quoted` on components and custom elements: Svelte 6 will turn it into a string. Write `disabled={x}`.
- JavaScript comments are allowed between attributes inside a tag (since 5.53).

## Event attributes

- Events are attributes: `onclick={handler}`, `{onclick}`, or spread with the other props. Put a local handler after a spread, or the spread overwrites it.
- Names are case sensitive: `onclick` listens to `click`, `onClick` listens to an event literally named `Click`.
- There are no modifiers: call `event.preventDefault()` in the handler, or write wrapper functions. Capture phase is a suffix: `onclickcapture`. Duplicate handlers on one element are not allowed; call both from one function.
- Event attributes fire after binding updates (`oninput` sees the new `bind:value`).
- These events are delegated to one listener at the application root: `beforeinput`, `click`, `change`, `dblclick`, `contextmenu`, `focusin`, `focusout`, `input`, `keydown`, `keyup`, `mousedown`, `mousemove`, `mouseout`, `mouseover`, `mouseup`, `pointerdown`, `pointermove`, `pointerout`, `pointerover`, `pointerup`, `touchend`, `touchmove`, `touchstart`. Consequences: a manually dispatched event needs `{ bubbles: true }`; a manual `addEventListener` that calls `stopPropagation` silently blocks declarative handlers. Use `on(target, type, handler, options)` from `svelte/events`, which preserves ordering and returns a remover.
- `ontouchstart` and `ontouchmove` are passive. If you truly must call `preventDefault`, attach the listener with `on(...)` inside an attachment.
- For `window`, `document` and `body` events, use `<svelte:window>`, `<svelte:document>` and `<svelte:body>` attributes, not `onMount` or `$effect`.

## Conditional, list and key blocks

- `{#if a}...{:else if b}...{:else}...{/if}` may wrap text as well as elements.
- `{#each}` accepts arrays, array-likes and iterables (`Map`, `Set`; converted with `Array.from`). `null`/`undefined` behave as an empty list, which renders `{:else}`.
- Since 5.4, `as` is optional: `{#each { length: 8 }, i}` renders eight times.
- Prefer keyed blocks: `{#each items as item (item.id)}`. The key must uniquely identify the item and be stable; prefer strings or numbers. Never use the index. A key that is recomputed as a new value each time (`[item.a, item.b]`) triggers `each_key_volatile`; build a primitive such as `` `${item.a}-${item.b}` ``.
- Destructuring and rest patterns are allowed (`as { id, ...rest }`), but keep the item variable when you need `bind:value={item.qty}`.
- `animate:` only works on an immediate child of a keyed each block.
- `{#key value}...{/key}` destroys and recreates its content when `value` changes. It is expensive; to re-run logic in a child, use `$derived` there instead. Use it mainly to replay a transition.

## Await blocks

- `{#await p}pending{:then v}done{:catch e}failed{/await}`; the shorthand forms `{#await p then v}` and `{#await p catch e}` exist.
- Server rendering shows only the pending branch. A non-promise value renders `{:then}`, including on the server.
- `{#await import('./Chart.svelte') then { default: Chart }}<Chart />{/await}` lazy-loads a component.
- For `await` directly in markup, scripts or deriveds (experimental), see the async reference.

## Snippets and render tags

- `{#snippet name(a, b = 1, { c })}...{/snippet}` declares reusable markup inside the template. Parameters accept defaults and destructuring, not rest parameters.
- Snippets are visible to their siblings and the siblings' descendants, can be recursive, and can reference script values. Snippets at the top level of the template can be referenced in `<script>`.
- Render with `{@render name(args)}`; the callee can be any expression (`{@render (cond ? a : b)()}`). A snippet can only be called through `{@render}`.
- Optional snippet: `{@render children?.()}`, or `{#if children}...{:else}fallback{/if}`.
- Passing to components: as an explicit prop (`<Table {row} />`), or by declaring the snippet between the component's tags, which makes it a prop of that name. Any other content between the tags becomes the `children` snippet, so a component cannot receive both a `children` prop and inner content.
- Type with `Snippet` from `svelte`; its argument is a tuple: `row: Snippet<[Item]>`. Tie types together with `<script lang="ts" generics="T">`. Snippet declarations accept generics since 5.30; the docs do not show the syntax, so fetch it before writing one.
- Since 5.5, a top-level snippet can be exported from `<script module>` (`export { add };`) if it references nothing from the instance script, directly or through other snippets.
- `createRawSnippet` from `svelte` builds a snippet programmatically (advanced).

```svelte
<script lang="ts" generics="T">
	import type { Snippet } from 'svelte';
	let { items, row, empty }: { items: T[]; row: Snippet<[T]>; empty?: Snippet } = $props();
</script>

{#each items as item}
	{@render row(item)}
{:else}
	{@render empty?.()}
{/each}
```

## Raw HTML

- `{@html content}` inserts a string without escaping: never pass unsanitized input (XSS). Sanitize, or render only trusted content.
- Each tag must be standalone valid HTML (no open tag in one and close tag in another). The content is not compiled as Svelte.
- The content is invisible to scoped styles; style it with `:global` under a scoped parent (`article :global { a { ... } }`).
- Since 5.52 the expression may be a `TrustedHTML` value; since 5.51 Svelte uses Trusted Types for its own HTML handling where supported.
- A server/client difference is not repaired during hydration (`hydration_html_changed`).

## Attachments

Since 5.29, `{@attach fn}` runs `fn(element)` in an effect when the element mounts and again whenever state read inside it changes. The optional returned function runs before each re-run and on removal. An element can have any number of attachments; a falsy value is ignored (`{@attach enabled && tooltip}`).

```svelte
<script lang="ts">
	import type { Attachment } from 'svelte/attachments';
	import tippy from 'tippy.js';
	let content = $state('Hello');

	function tooltip(text: string): Attachment {
		return (element) => {
			const instance = tippy(element, { content: text });
			return instance.destroy;
		};
	}
</script>

<button {@attach tooltip(content)}>Hover</button>
```

- A factory call such as `tooltip(content)` re-creates the attachment whenever its argument changes. When setup is expensive, pass a getter and read it in a nested `$effect` inside the attachment, so only the update re-runs.
- On a component, `{@attach}` becomes a prop keyed by a `Symbol`; spreading `{...props}` onto an element forwards it. To add one programmatically, use `[createAttachmentKey()]: fn` (from `svelte/attachments`).
- Convert a library action with `fromAction` (since 5.32): `{@attach fromAction(action, () => arg)}`. The second argument is a function returning the parameter, not the parameter.
- Prefer attachments over `use:` actions: actions run once and do not re-run when their argument changes.

## Declaration tags

- Since 5.56, `{const x = expr}` and `{let x = $state(...)}` declare variables anywhere in markup. They follow lexical scope: visible to siblings and their descendants, and a nested declaration shadows an outer one.
- When a value must stay reactive, declare it with a rune: `{const v = $derived(expr)}` or `{let v = $state(init)}`.
- `{@const x = y}` is legacy: replace it with `{const x = $derived(y)}`. It was limited to the immediate child of a block, a component or a `<svelte:boundary>`.

```svelte
{#each boxes as box}
	{const area = $derived(box.width * box.height)}
	<p>{box.width} × {box.height} = {area}</p>
{/each}
```

## Debug tag

`{@debug a, b}` logs the named variables (identifiers only, not expressions) when they change and pauses when devtools are open. With no arguments it breaks on any state change.

## Bindings

- `bind:property={lvalue}`; `bind:value` alone when the variable has the same name. Element listeners on the same event run before the bound value updates.
- Function bindings (since 5.9): `bind:value={() => value, (v) => (value = v.trim())}` for validation or transformation. For read-only bindings pass `null` as the getter: `bind:clientWidth={null, redraw}`. With `bind:this`, keep the getter so the value is cleared on destroy.
- Numeric inputs bind numbers; an empty or invalid number input gives `undefined`.
- Form reset: `defaultValue`/`defaultChecked` on inputs (since 5.6) and `defaultValue` on `<select>` (since 5.57) set the value restored on reset. On the first render, the bound value wins unless it is `null`/`undefined`.
- `bind:group` (radios, or checkboxes into an array) only works within one component. `bind:files` accepts only `FileList`, `null` or `undefined`; build a `FileList` with `new DataTransfer()`.
- Dimension bindings (`clientWidth`, `offsetHeight`, `contentRect`, ...) are read-only, use `ResizeObserver`, and do not work on `display: inline` elements.
- `bind:this` is `undefined` until mount: read it in an effect or a handler. On a component it gives the instance exports.
- Binding to a component prop requires `$bindable` in the child. In runes mode you cannot bind to a component export; use `bind:this` and read the export.

## Class and style attributes

- Since 5.16, `class` accepts objects (truthy keys are added) and arrays (truthy entries are added, nested arrays and objects are flattened), via clsx. Since 5.19, `ClassValue` from `svelte/elements` types a `class` prop.
- Prefer this over the `class:` directive. Merge a parent's class with an array: `class={['btn', props.class]}`.
- A primitive falsy value is still stringified (`class={false}` gives `class="false"`); only `null`/`undefined` omit the attribute. A future version will omit every falsy value.
- `style:color={c}`, `style:width="12rem"`, `style:color|important`. A `style:` directive wins over the `style` attribute, even over `!important`. Pass JavaScript values to CSS with `style:--columns={n}`.

```svelte
<script lang="ts">
	import type { ClassValue } from 'svelte/elements';
	let { active, class: extra }: { active: boolean; class?: ClassValue } = $props();
	const flags = $derived({ active, idle: !active });
</script>

<div class={['card', flags, extra]} style:--accent={active ? 'tomato' : 'gray'}>...</div>
```

## Fetch before writing when

- You declare a generic snippet (5.30 syntax not in the docs), use declaration tags (5.56) or `defaultValue` on `<select>` (5.57), or must support a version older than any "since" above.
- You pass `TrustedHTML` to `{@html}` or rely on Trusted Types behavior.
- You need the full list of bindable properties for media, `<details>`, `contenteditable` or `<svelte:window>`.
- You use `fromAction` or `createAttachmentKey` signatures for typing, or attachments on `<svelte:document>`.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["svelte/basic-markup", "svelte/if"]
```

Sections: `svelte/basic-markup`, `svelte/if`, `svelte/each`, `svelte/key`, `svelte/await`, `svelte/snippet`, `svelte/@render`, `svelte/@html`, `svelte/@attach`, `svelte/@const`, `svelte/@debug`, `svelte/declaration-tags`, `svelte/bind`, `svelte/use`, `svelte/style`, `svelte/class`, `svelte/svelte-attachments`, `svelte/svelte-events`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/svelte/@attach/llms.txt'
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


Partly derived from sveltejs/ai-tools (MIT), base 6b5d0da; see the plugin NOTICE.
