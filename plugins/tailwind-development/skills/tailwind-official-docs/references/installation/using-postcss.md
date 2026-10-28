# Installing through the PostCSS plugin

Official page: https://tailwindcss.com/docs/installation/using-postcss. Read it whole; where it differs from this file, follow the page.

## When this path fits

- The project has a PostCSS config (a `postcss.config.*` file or PostCSS settings in `package.json`), or its bundler runs PostCSS and the framework has no guide of its own in the framework-guides list.
- A project built with Vite takes the Vite path instead.

## What the setup consists of

1. The packages the page names (`tailwindcss`, `@tailwindcss/postcss`, `postcss`), installed with the package manager the lockfile names.
2. `@tailwindcss/postcss` added to the PostCSS config, beside the project's other plugins and in the module format the file already uses.
3. `@import "tailwindcss";` in the CSS file the app already loads.
4. The project's usual dev or build script, unchanged.

## Check in the project

- v3 leftovers in the PostCSS config: the `tailwindcss` entry, and `postcss-import` and `autoprefixer`, which v4 no longer needs (`upgrade-guide#using-postcss`). Remove them only when nothing else needs them.
- `@tailwind` directives in the CSS: replaced by the single import.

## Verify

Add one class the existing styles cannot produce, run the dev server or build, confirm the generated CSS contains it, then remove it.
