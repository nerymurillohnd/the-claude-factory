# Class sorting with Prettier

Sources: https://tailwindcss.com/docs/editor-setup#class-sorting-with-prettier and the plugin's README, https://github.com/tailwindlabs/prettier-plugin-tailwindcss, which lists every option and the compatible Prettier plugins. Read them for anything this file does not cover; where they differ, follow them.

## Setup

1. Install `prettier` and `prettier-plugin-tailwindcss` as dev dependencies.
2. Add the plugin to the Prettier config's `plugins`.
3. On Tailwind v4, set `tailwindStylesheet` to the CSS entry point, or the order ignores the project's theme and custom utilities; on v3, `tailwindConfig` when the config is not beside the Prettier config. Paths resolve from the Prettier config file.
4. Classes in `clsx`, `cva` or custom attributes need `tailwindFunctions` or `tailwindAttributes`.

## Traps

- With other Prettier plugins, `prettier-plugin-tailwindcss` must be the last entry in `plugins`, and only the plugins the README lists are compatible. Check both still work.
- The plugin is ESM-only: a Prettier config that loads it with `require()` fails. Name it in `plugins` instead.
- On v3, when the plugin cannot find the Tailwind config, it falls back to the default one without warning, and the order ignores the project's customizations. Check that `tailwindConfig` points to the real file.
- Patterns in `tailwindAttributes` and `tailwindFunctions` are strings wrapped in slashes (`"/data-.*/"`); JavaScript regex literals do not work.
- It removes duplicate classes by default, which breaks templating languages whose syntax looks like repeated classes; the README names the option that keeps them.
- The order is not configurable. This plugin's `sort_classes` tool gives the same order without Prettier.
