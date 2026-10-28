# Upgrade by hand

Read https://tailwindcss.com/docs/upgrade-guide#upgrading-manually. Follow it over this file.

Use this when the upgrade tool cannot run or fails.

## `#using-postcss`

- Replace the `tailwindcss` PostCSS entry with `@tailwindcss/postcss`.
- Remove `postcss-import` and `autoprefixer` if only Tailwind needed them.

## `#using-vite`

- Move from the PostCSS plugin to `@tailwindcss/vite`.

## `#using-tailwind-cli`

- Replace `npx tailwindcss` with `npx @tailwindcss/cli` in every build command.
