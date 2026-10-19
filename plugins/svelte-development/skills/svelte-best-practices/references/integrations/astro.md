# Svelte components in Astro

> Precedence: changelogs and source code win over the docs, and the docs win over this file.

## Contents

- [Fetch before writing when](#fetch-before-writing-when)
- [Versions and peers](#versions-and-peers)
- [Install and configure the integration](#install-and-configure-the-integration)
- [Hydration directives](#hydration-directives)
- [Server islands with server:defer](#server-islands-with-serverdefer)
- [Props must be serializable](#props-must-be-serializable)
- [Slots arrive as snippets](#slots-arrive-as-snippets)
- [How the client mounts a component](#how-the-client-mounts-a-component)
- [Container API renderer](#container-api-renderer)
- [Astro 7 changes that affect Svelte users](#astro-7-changes-that-affect-svelte-users)
- [Tailwind in Astro](#tailwind-in-astro)
- [Official sources](#official-sources)

## Fetch before writing when

- The project's `astro` or `@astrojs/svelte` is newer than the versions above, or the slot behavior below does not match what you see.
- You pass children or named slots from `.astro` files into Svelte components: read the renderer of the installed `@astrojs/svelte`:

  ```sh
  npm ls @astrojs/svelte --depth=0
  curl -sS 'https://raw.githubusercontent.com/withastro/astro/main/packages/integrations/svelte/src/server.ts'
  curl -sS 'https://raw.githubusercontent.com/withastro/astro/main/packages/integrations/svelte/src/client.svelte.ts'
  ```
- You upgrade across an Astro major: read the upgrade guide and the `astro` changelog window (both URLs under [Official sources](#official-sources); the window command is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`).

## Versions and peers

- `@astrojs/svelte` 9.0.1 peers: `astro ^7.0.0`, `svelte ^5.43.6`, `typescript ^5.3.3 || ^6.0.0`; engines `node >=22.12.0`. Astro 7 declares the same Node floor.
- 9.0.0 moved to Vite 8 and `@sveltejs/vite-plugin-svelte` 7. Svelte 3 and 4 need `@astrojs/svelte@5`.

## Install and configure the integration

```sh
npx astro add svelte
```

`astro add` installs the package, adds `svelte()` to `integrations` and writes a `svelte.config.js` with `vitePreprocess`. Manual setup:

```js
// astro.config.mjs
import { defineConfig } from "astro/config";
import svelte from "@astrojs/svelte";

export default defineConfig({
  integrations: [svelte({ extensions: [".svelte"] })],
});
```

```js
// svelte.config.js
import { vitePreprocess } from "@astrojs/svelte";

export default { preprocess: vitePreprocess() };
```

- `svelte()` accepts `@sveltejs/vite-plugin-svelte` options. Options in `astro.config` win over the same keys in `svelte.config.js`.
- Keep `svelte.config.js` when you use preprocessors (SCSS, Stylus) so the Svelte language server reads the same setup.
- Compiler options such as `compilerOptions.experimental.async` go in either file; Astro has no Svelte-specific flag of its own.

## Hydration directives

A Svelte component in an `.astro` file renders to static HTML with no JavaScript unless it carries a `client:*` directive. Directives work only on components imported directly into an `.astro` file, not on dynamic tags or MDX `components` props.

| Directive | Hydrates |
| --- | --- |
| `client:load` | Immediately on page load |
| `client:idle` | After `requestIdleCallback` (or `load`); an object value with `timeout` (milliseconds) caps the wait |
| `client:visible` | When it enters the viewport; an object value with `rootMargin` (for example `'200px'`) starts earlier |
| `client:media="(max-width: 50em)"` | When the media query matches |
| `client:only="svelte"` | Skips server rendering and renders in the browser on load; the framework name is required |

```astro
<Chart client:only="svelte">
	<p slot="fallback">Loading chart</p>
</Chart>
```

A child with `slot="fallback"` shows until a `client:only` component is ready.

## Server islands with server:defer

`server:defer` turns a component into a server island: the page ships with its `slot="fallback"` content, and the island's HTML is fetched from a separate route after load. It needs an adapter for on-demand rendering. Props travel encrypted in the URL of a `GET` request; past 2048 bytes Astro switches to `POST`, which browsers do not cache, so pass only the props the island needs.

## Props must be serializable

Props given to a hydrated component or a server island must survive serialization. Supported: plain objects, `number`, `string`, `Array`, `Map`, `Set`, `RegExp`, `Date`, `BigInt`, `URL`, `Uint8Array`, `Uint16Array`, `Uint32Array`, `Infinity`.

- Functions (event callbacks, render functions) and circular objects do not reach the client. A callback prop works during server rendering only.
- Move the interactive logic inside the Svelte component, or wrap the interactive part in one Svelte component that owns its handlers.

## Slots arrive as snippets

The renderer turns every slot passed from Astro into a Svelte raw snippet with no parameters (`createRawSnippet` in `src/server.ts` and `src/client.svelte.ts`):

- The default slot becomes the `children` prop.
- A named slot becomes a prop with the slot's exact name; kebab-case names are kept, so destructure them with a quoted key.
- The HTML is wrapped in `<astro-slot>` (or `<astro-static-slot>` when the component is not hydrated).
- Astro renders slot content to HTML before Svelte sees it, so these snippets cannot take arguments. Use props for data, and keep the snippet call parameterless.

```svelte
<!-- src/components/Sidebar.svelte -->
<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		title,
		children,
		'social-links': socialLinks
	}: { title?: Snippet; children?: Snippet; 'social-links'?: Snippet } = $props();
</script>

<aside>
	<header>{@render title?.()}</header>
	<main>{@render children?.()}</main>
	<footer>{@render socialLinks?.()}</footer>
</aside>
```

```astro
<Sidebar client:visible>
	<h2 slot="title">Menu</h2>
	<p>Body text</p>
	<ul slot="social-links"><li>Link</li></ul>
</Sidebar>
```

- Render with optional calls (`children?.()`), because a slot that the caller omits is `undefined`. Since @astrojs/svelte 8.1.0 the Astro type shims treat snippet props other than `children` as optional.
- The renderer still passes a legacy `$$slots` object, but `<slot>` is Svelte 4 syntax; write snippets. Astro's framework-components guide still shows `<slot name="…">` for Svelte, which is outdated for Svelte 5.

## How the client mounts a component

From `src/client.svelte.ts` in @astrojs/svelte 9.0.1:

- Server-rendered components (`client:load`, `idle`, `visible`, `media`) start with Svelte's `hydrate`.
- `client:only="svelte"` clears the target element and uses `mount`, since there is no server HTML.
- When Astro re-renders the island with new props, the existing instance receives them through a `$state` props object instead of remounting.
- The instance is unmounted when the island element fires `astro:unmount` (for example during view transitions). Put cleanup in `$effect` teardown or `onDestroy`; it runs on that unmount.

## Container API renderer

```js
import { getContainerRenderer } from "@astrojs/svelte/container-renderer";
```

@astrojs/svelte 9.0.0 added the `container-renderer` entry point. Importing `getContainerRenderer` from the package root still works but is deprecated and logs a warning.

## Astro 7 changes that affect Svelte users

- Vite 8 is the dev server and bundler; check Vite-specific plugins and config against the Vite 8 migration guide.
- The Rust compiler is the only `.astro` compiler. Unclosed non-void tags are errors, and invalid nesting (a `<div>` inside a `<p>`) is no longer repaired, so the browser's own recovery can change the output. This applies to `.astro` templates, not to `.svelte` files.
- `compressHTML` defaults to `'jsx'`: whitespace between inline elements in `.astro` templates is removed. Add `{" "}` where a space matters, or set `compressHTML: true` to keep the earlier behavior.
- Advanced routing is on by default, and `src/fetch.ts` (or `.js`) is a reserved file name; rename an unrelated file or set `fetchFile`.
- Markdown renders with Sätteri by default; remark and rehype plugins need `@astrojs/markdown-remark` and the `unified()` processor.
- `@astrojs/db` is removed.

## Tailwind in Astro

Add `@tailwindcss/vite` to `vite.plugins` in `astro.config` and import a stylesheet containing `@import "tailwindcss";` from the layout. [tailwind.md](tailwind.md) covers the setup, `@reference` in Svelte `<style>` blocks and class detection.

## Official sources

- Integration guide: https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/guides/integrations-guide/svelte.mdx
- Framework components: https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/guides/framework-components.mdx
- Directives reference: https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/reference/directives-reference.mdx
- Server islands: https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/guides/server-islands.mdx
- Upgrade to v7: https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/guides/upgrade-to/v7.mdx
- Renderer source, server: https://raw.githubusercontent.com/withastro/astro/main/packages/integrations/svelte/src/server.ts
- Renderer source, client: https://raw.githubusercontent.com/withastro/astro/main/packages/integrations/svelte/src/client.svelte.ts
- @astrojs/svelte changelog: https://raw.githubusercontent.com/withastro/astro/main/packages/integrations/svelte/CHANGELOG.md
- astro changelog: https://raw.githubusercontent.com/withastro/astro/main/packages/astro/CHANGELOG.md
