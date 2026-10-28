# Install through the PostCSS plugin

Read https://tailwindcss.com/docs/installation/using-postcss whole. Where it differs from this file, follow the page.

## Use this path when

- The project has a PostCSS config (a `postcss.config.*` file or PostCSS settings in `package.json`), or its bundler runs PostCSS and the framework has no guide in the framework-guides list.
- Take the Vite path instead when the project builds with Vite.

## Set it up

1. Install the packages the page names (`tailwindcss`, `@tailwindcss/postcss`, `postcss`) with the package manager the lockfile names.
2. Add `@tailwindcss/postcss` to the PostCSS config, beside the project's other plugins, in the module format the file already uses.
3. Add `@import "tailwindcss";` to the CSS file the app already loads.
4. Keep the project's dev and build scripts as they are.

## Check the project

- Remove v3 leftovers from the PostCSS config: the `tailwindcss` entry, and `postcss-import` and `autoprefixer`, which v4 no longer needs (`upgrade-guide#using-postcss`). Keep any of them something else still needs.
- Replace `@tailwind` directives in the CSS with the single import.

## Verify

Add one class the existing styles cannot produce, run the dev server or build, confirm the generated CSS contains it, then remove the class.
