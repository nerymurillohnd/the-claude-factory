# Tailwind CSS with SvelteKit and Astro

> Precedence: changelogs and source code win over the docs, and the docs win over this file.

## Contents

- [Fetch before writing when](#fetch-before-writing-when)
- [Set up the Vite plugin in SvelteKit 3](#set-up-the-vite-plugin-in-sveltekit-3)
- [Set up the Vite plugin in Astro 7](#set-up-the-vite-plugin-in-astro-7)
- [Style with utilities, not style blocks](#style-with-utilities-not-style-blocks)
- [When a style block needs Tailwind: @reference](#when-a-style-block-needs-tailwind-reference)
- [Class objects and arrays in Svelte 5](#class-objects-and-arrays-in-svelte-5)
- [How Tailwind finds classes](#how-tailwind-finds-classes)
- [Theme, utilities and variants in CSS](#theme-utilities-and-variants-in-css)
- [Dark mode with a class or attribute](#dark-mode-with-a-class-or-attribute)
- [Changes in Tailwind 4.2 and 4.3](#changes-in-tailwind-42-and-43)
- [Class sorting with prettier-plugin-tailwindcss](#class-sorting-with-prettier-plugin-tailwindcss)
- [Browser targets](#browser-targets)
- [Official sources](#official-sources)

## Fetch before writing when

- The project's `tailwindcss` or `@tailwindcss/vite` is not the latest on the registry (`npm view tailwindcss version`): read the changelog window, since 4.x minors add utilities and change generated CSS:

  ```sh
  npm ls tailwindcss --depth=0
  URL='https://raw.githubusercontent.com/tailwindlabs/tailwindcss/main/CHANGELOG.md'
  V="$(node -p "require('tailwindcss/package.json').version")"  # the installed version
  curl -sS "$URL" | awk -v v="$V" 'index($0, "## [" v "]")==1{exit} {print}'
  ```
- You use a utility or directive not listed here, or a v3 config (`tailwind.config.js`, `@config`, `theme()`).
- Classes are missing from the output: check detection rules before adding a safelist.

## Set up the Vite plugin in SvelteKit 3

```sh
npx sv add tailwindcss
```

`sv add tailwindcss` installs `tailwindcss` and `@tailwindcss/vite`, puts the plugin first in `plugins`, writes `@import 'tailwindcss';` to `src/routes/layout.css` and imports that file from `src/routes/+layout.svelte`. The Tailwind guide instead creates `src/app.css` and imports it from the root layout; both work, but keep one main stylesheet and use its path everywhere (Prettier, `@reference`).

```ts
// vite.config.ts
import { sveltekit } from "@sveltejs/kit/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
});
```

```svelte
<!-- src/routes/+layout.svelte -->
<script>
	import './layout.css';

	let { children } = $props();
</script>

{@render children()}
```

```css
/* src/routes/layout.css */
@import "tailwindcss";
@plugin '@tailwindcss/typography';
```

Place `tailwindcss()` before `sveltekit()`. In SvelteKit 3 the Kit options also live in `vite.config`, so there is no `svelte.config.js` to edit.

## Set up the Vite plugin in Astro 7

```js
// astro.config.mjs
import { defineConfig } from "astro/config";
import svelte from "@astrojs/svelte";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  integrations: [svelte()],
  vite: { plugins: [tailwindcss()] },
});
```

Create `src/styles/global.css` with `@import 'tailwindcss';` and import it in the frontmatter of the shared layout. Svelte islands use the same generated stylesheet; their class names are detected like any other source file.

## Style with utilities, not style blocks

- Put utilities in the markup. Svelte (and Astro) `<style>` blocks are processed one by one like CSS modules, so each block that uses Tailwind features costs a separate Tailwind run and sees no theme unless you import one.
- Inside a `<style>` block, prefer theme variables over `@apply`: `background-color: var(--color-blue-500);` needs no Tailwind processing.
- Extract repetition into a Svelte component or a snippet, not into `@apply` classes.

## When a style block needs Tailwind: @reference

`@apply` and `@variant` in a `<style>` block need `@reference`, which loads theme, utilities and variants without emitting CSS.

```svelte
<style>
	@reference 'tailwindcss';

	h1 {
		@apply text-2xl font-bold;
	}
</style>
```

- `@reference 'tailwindcss';` is enough when you use the default theme only.
- With custom `@theme`, `@utility`, `@custom-variant` or `@plugin` rules, reference your main stylesheet instead. A relative path from a component file climbs several directories and breaks when the file moves; use a subpath import. Tailwind resolves `#` specifiers through the `imports` field of `package.json` for `@import`, `@reference`, `@plugin` and `@config` with the CLI, Vite and PostCSS.

```json
{
  "imports": {
    "#lib": "./src/lib/index.js",
    "#lib/*": "./src/lib/*",
    "#app.css": "./src/routes/layout.css"
  }
}
```

```svelte
<style>
	@reference '#app.css';

	.card {
		@apply rounded-lg p-4 shadow-sm;
	}
</style>
```

SvelteKit 3 already uses this field for `#lib`, so the entry sits next to the existing ones. Point the target at the stylesheet your project actually uses (`src/app.css` when you followed the Tailwind guide).

## Class objects and arrays in Svelte 5

Since Svelte 5.16 the `class` attribute accepts objects and arrays (clsx semantics). Tailwind scans files as plain text, so every full class name inside the strings and object keys is detected:

```svelte
<button
	class={[
		'rounded px-4 py-2',
		variant === 'primary' && 'bg-blue-600 text-white',
		{ 'cursor-not-allowed opacity-50': disabled }
	]}
>
	Save
</button>
```

- Never build names from pieces (`bg-${color}-600`); the full name never appears in the source. Map values to complete names (`{ red: 'bg-red-600', blue: 'bg-blue-600' }[color]`).
- Prefer this over the `class:` directive for new code.

## How Tailwind finds classes

- Scanned: every file under the base path (the working directory by default) except files listed in `.gitignore`, `node_modules`, binary files, CSS files and lock files.
- Also ignored by default: `.svelte-kit` (4.1.5) and `.env` and `.env.*` files (4.2.3).
- `@source '<path>';` adds a path, written relative to the stylesheet. Use it for a component library in `node_modules` that ships Tailwind classes.
- `@import 'tailwindcss' source('<dir>');` sets the base path (monorepos); `source(none)` disables automatic detection so only `@source` paths count.
- `@source not '<path>';` excludes a path. `@source inline('{hover:,}bg-red-{100..900..100}');` safelists brace-expanded classes; `@source not inline(…)` blocks them.

## Theme, utilities and variants in CSS

```css
@import "tailwindcss";

@theme {
  --color-brand-500: oklch(0.62 0.19 259);
  --font-display: "Inter", sans-serif;
}

@utility content-auto {
  content-visibility: auto;
}

@custom-variant theme-midnight (&:where([data-theme='midnight'] *));

.prose-link {
  color: var(--color-brand-500);
  @variant hover:focus-visible {
    text-decoration: underline;
  }
}
```

- `@theme` variables create utilities (`bg-brand-500`, `font-display`) and CSS variables.
- `@utility` registers a utility that works with variants.
- `@variant` applies a variant inside CSS. Since 4.3.0 it accepts stacked variants (`@variant hover:focus { … }`) and compound lists (`@variant hover, focus { … }`).
- `@custom-variant` defines a new variant.
- `theme()` is deprecated; use `var(--…)` theme variables.

## Dark mode with a class or attribute

By default `dark:` follows `prefers-color-scheme`. To toggle it from Svelte state, override the variant in the main stylesheet:

```css
@custom-variant dark (&:where(.dark, .dark *));
/* or, attribute based */
@custom-variant dark (&:where([data-theme='dark'], [data-theme='dark'] *));
```

Set the class or attribute on `<html>` before first paint, for example with a small inline script in `src/app.html` that reads the saved preference, to avoid a flash of the wrong theme.

## Changes in Tailwind 4.2 and 4.3

| Version | Change |
| --- | --- |
| 4.2.0 | Logical utilities: `inset-s-*`, `inset-e-*`, `inset-bs-*`, `inset-be-*`, `pbs-*`, `mbs-*`, `inline-*`, `block-*`, `font-features-*`; `start-*` and `end-*` are deprecated |
| 4.2.3 | Canonicalization rewrites `start-*` to `inset-s-*` and `end-*` to `inset-e-*`; `.env` files are no longer scanned |
| 4.3.0 | `@container-size`, `scrollbar-{auto,thin,none}`, `scrollbar-thumb-*`, `scrollbar-track-*`, `scrollbar-gutter-*`, `zoom-*`, `tab-*`; stacked and compound `@variant` |
| 4.3.1 | `m-0`, `left-0` and similar emit `0` instead of `calc(var(--spacing) * 0)`, and the `1` steps emit `var(--spacing)`; tests that match exact CSS need updating |
| 4.3.3 | Fixes only (no new utilities) |

Write `inset-s-*` and `inset-e-*` in new code.

## Class sorting with prettier-plugin-tailwindcss

- Use 0.8.1 or newer with `prettier-plugin-svelte` 4: 0.8.0 silently stopped sorting classes in Svelte markup and `class={…}` expressions.
- 0.8.x requires Prettier 3.7 or newer.
- List it last in `plugins`, after `prettier-plugin-svelte`.
- Set `tailwindStylesheet` to the main stylesheet, for example `./src/routes/layout.css`, so the plugin knows your theme and custom utilities.

## Browser targets

Tailwind 4 requires Chrome 111, Safari 16.4 and Firefox 128 or newer. Projects that must support older browsers need Tailwind 3.4.

## Official sources

- Functions and directives: https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/functions-and-directives.mdx
- Detecting classes: https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/detecting-classes-in-source-files.mdx
- Compatibility (browsers, style blocks): https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/compatibility.mdx
- Theme variables: https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/theme.mdx
- Dark mode: https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/dark-mode.mdx
- SvelteKit guide: https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/app/%28docs%29/docs/installation/framework-guides/sveltekit.tsx
- Astro guide: https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/app/%28docs%29/docs/installation/framework-guides/astro.tsx
- Tailwind changelog: https://raw.githubusercontent.com/tailwindlabs/tailwindcss/main/CHANGELOG.md
- prettier-plugin-tailwindcss changelog: https://raw.githubusercontent.com/tailwindlabs/prettier-plugin-tailwindcss/main/CHANGELOG.md
