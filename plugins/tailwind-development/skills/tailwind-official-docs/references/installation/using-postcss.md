# [Install through the PostCSS plugin](https://tailwindcss.com/docs/installation/using-postcss)

## Use this path when

- The project has a `postcss.config.*` or PostCSS settings in `package.json`.
- The bundler runs PostCSS and the framework has no framework guide.
- Use the Vite path instead if the project builds with Vite.

## Set it up

1. Install `tailwindcss`, `@tailwindcss/postcss` and `postcss` with the project's package manager.
2. Add `@tailwindcss/postcss` to the PostCSS config, in the file's module format.
3. Add `@import "tailwindcss";` to the CSS file the app loads.
4. Leave the dev and build scripts as they are.

## Check the project

- Replace a `tailwindcss` PostCSS entry with `@tailwindcss/postcss`.
- Remove `autoprefixer` and `postcss-import` if only Tailwind needed them.
- Replace `@tailwind` directives with the single import.

## Verify

1. Add one class the project could not produce before.
2. Run the dev server or the build.
3. Confirm the generated CSS has it, then remove the class.
