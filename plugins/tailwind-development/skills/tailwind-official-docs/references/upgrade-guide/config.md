# [Check configuration and build changes](https://tailwindcss.com/docs/upgrade-guide)

## `#browser-requirements`

- Compare the page's browser floor with the project's targets.
- Tell the user to stay on v3 if a required browser falls below it.

## `#using-a-javascript-config-file`

- Load a kept JavaScript config with `@config`.
- Replace `safelist` with `@source inline()`.

## `#disabling-core-plugins`

- Remove `corePlugins` and `separator`: v4 does not support them.

## `#using-the-theme-function`

- Replace `theme()` with CSS variables.
- Use `theme(--var)` only in media queries.

## `#theme-values-in-javascript`

- Replace `resolveConfig` imports with CSS variables or `getComputedStyle`.

## `#using-apply-with-vue-svelte-or-css-modules`

- Add `@reference` before `@apply` in CSS modules and component `<style>` blocks.

## `#using-sass-less-and-stylus`

- Tell the user that Sass, Less and Stylus files must become plain CSS.
