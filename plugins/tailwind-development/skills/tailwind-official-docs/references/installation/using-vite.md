# Install through the Vite plugin

Read https://tailwindcss.com/docs/installation/using-vite whole. Where it differs from this file, follow the page.

## Use this path when

- The project has a `vite.config.*`, or its framework builds through Vite and has no guide in the framework-guides list.
- The project has no build tool: create a Vite project first, and ask before scaffolding one inside an existing repository.

## Set it up

1. Install the packages the page names (`tailwindcss`, `@tailwindcss/vite`) with the package manager the lockfile names.
2. Add the plugin to the Vite config's `plugins`, beside the project's other plugins.
3. Add `@import "tailwindcss";` to the CSS file the app already loads.
4. Keep the project's dev and build scripts as they are.

## Check the project

- Look for a PostCSS config that also loads Tailwind. With the Vite plugin, Tailwind runs once, through Vite: remove that entry only with the user's agreement.
- Remove v3 leftovers: `@tailwind` directives, the `tailwindcss` package used as a PostCSS plugin, and `autoprefixer` or `postcss-import` added for Tailwind (`upgrade-guide#using-vite`).

## Verify

Add one class the existing styles cannot produce, run the dev server or build, confirm the generated CSS contains it, then remove the class.
