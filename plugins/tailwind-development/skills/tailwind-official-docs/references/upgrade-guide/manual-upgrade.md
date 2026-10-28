# [Upgrade by hand](https://tailwindcss.com/docs/upgrade-guide#upgrading-manually)

## `#using-postcss`

- Replace the `tailwindcss` PostCSS entry with `@tailwindcss/postcss`.
- Remove `postcss-import` and `autoprefixer` if only Tailwind needed them.

## `#using-vite`

- Move from the PostCSS plugin to `@tailwindcss/vite`.

## `#using-tailwind-cli`

- Replace `npx tailwindcss` with `npx @tailwindcss/cli` in every build command.
