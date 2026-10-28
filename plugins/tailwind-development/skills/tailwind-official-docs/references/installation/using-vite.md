# Installing through the Vite plugin

Official page: https://tailwindcss.com/docs/installation/using-vite. It is the source of truth: when this file and the page disagree, the page wins and this file is out of date. Checked against the page on 2026-10-27 (Tailwind CSS v4.3.3).

## When this path fits

- The project has a `vite.config.*`, or its framework builds through Vite and has no guide of its own in the framework-guides list. The page names Laravel, SvelteKit, React Router, Nuxt and SolidJS as frameworks this path suits; several of them also have a dedicated guide, which comes first.
- A project with no build tool at all needs a Vite project first; the page starts one with Create Vite. Ask before scaffolding a new project inside an existing repository.

## What the setup consists of

1. Two packages: `tailwindcss` and `@tailwindcss/vite`, installed with the project's package manager (the one its lockfile names).
2. The plugin registered in the Vite config. The import is the package's default export, and the call goes in `plugins`:

   ```ts
   import tailwindcss from '@tailwindcss/vite'

   export default defineConfig({
     plugins: [tailwindcss()],
   })
   ```

   Keep the project's other plugins and options; add the call beside them.
3. One line in the project's main CSS file: `@import "tailwindcss";`.
4. The project's usual dev or build script, unchanged.
5. The compiled stylesheet linked from the page's `<head>`. Most Vite frameworks already include the CSS entry they import; check before adding a `<link>`.

## Check in the project

- A `postcss.config.*` that also loads Tailwind: with the Vite plugin, Tailwind runs once, through Vite. Remove a Tailwind entry there only with the user's agreement, since other PostCSS plugins may still be needed.
- v3 leftovers: `@tailwind base/components/utilities` (replaced by the single import), the `tailwindcss` package used as a PostCSS plugin, `autoprefixer` and `postcss-import` added for Tailwind. `upgrade-guide#using-vite` covers a project moving from v3.
- Which CSS file the app actually imports: the `@import "tailwindcss"` goes there, not in a new file nothing loads.

## Verify

Add one class the existing styles cannot produce, run the dev server or build, confirm the generated CSS contains it, then remove it.
