# Installing through the Vite plugin

Official page: https://tailwindcss.com/docs/installation/using-vite. Read it whole; where it differs from this file, follow the page.

## When this path fits

- The project has a `vite.config.*`, or its framework builds through Vite and has no guide of its own in the framework-guides list.
- A project with no build tool needs a Vite project first. Ask before scaffolding one inside an existing repository.

## What the setup consists of

1. The packages the page names (`tailwindcss` and `@tailwindcss/vite`), installed with the package manager the lockfile names.
2. The plugin added to the Vite config's `plugins`, beside the project's other plugins.
3. `@import "tailwindcss";` in the CSS file the app already loads.
4. The project's usual dev or build script, unchanged.

## Check in the project

- A PostCSS config that also loads Tailwind: with the Vite plugin, Tailwind runs once, through Vite. Remove that entry only with the user's agreement.
- v3 leftovers: `@tailwind` directives, the `tailwindcss` package used as a PostCSS plugin, `autoprefixer` or `postcss-import` added for Tailwind (`upgrade-guide#using-vite`).

## Verify

Add one class the existing styles cannot produce, run the dev server or build, confirm the generated CSS contains it, then remove it.
