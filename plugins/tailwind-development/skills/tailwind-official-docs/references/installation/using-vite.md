# Install through the Vite plugin

Read https://tailwindcss.com/docs/installation/using-vite whole. Follow it over this file.

## Use this path when

- The project has a `vite.config.*`.
- The framework builds with Vite and has no framework guide.
- The project has no build tool. Ask before creating a Vite project in it.

## Set it up

1. Install `tailwindcss` and `@tailwindcss/vite` with the project's package manager.
2. Add the plugin to `plugins` in the Vite config.
3. Add `@import "tailwindcss";` to the CSS file the app loads.
4. Leave the dev and build scripts as they are.

## Check the project

- Remove Tailwind from any PostCSS config, with the user's agreement.
- Remove `@tailwind` directives.
- Remove `autoprefixer` and `postcss-import` if only Tailwind needed them.

## Verify

1. Add one class the project could not produce before.
2. Run the dev server or the build.
3. Confirm the generated CSS has it, then remove the class.
