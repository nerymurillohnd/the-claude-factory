# Set up class sorting with Prettier

Read https://tailwindcss.com/docs/editor-setup#class-sorting-with-prettier and the plugin's README, https://github.com/tailwindlabs/prettier-plugin-tailwindcss, which lists every option and the compatible Prettier plugins, for anything this file does not cover. Where they differ, follow them.

## Set it up

1. Install `prettier` and `prettier-plugin-tailwindcss` as dev dependencies.
2. Add the plugin to the Prettier config's `plugins`, as its last entry.
3. On v4, set `tailwindStylesheet` to the CSS entry point; without it, the order ignores the project's theme and custom utilities. On v3, set `tailwindConfig` when the config is not beside the Prettier config. Write both paths relative to the Prettier config file.
4. Add class helpers (`clsx`, `cva`) to `tailwindFunctions` and custom attributes to `tailwindAttributes`, writing patterns as slash-wrapped strings (`"/data-.*/"`), never as JavaScript regex literals.

## Avoid the traps

- Keep `prettier-plugin-tailwindcss` last among the Prettier plugins, and check that every other plugin is on the README's compatible list and still works.
- Load it by name in `plugins`, never with `require()`: it is ESM-only.
- On v3, confirm `tailwindConfig` points to the real file: when the plugin cannot find one, it falls back to the default config without warning.
- Turn on the README's option to keep duplicates in templating languages whose syntax looks like repeated classes (Blade, Fluid).
- Do not look for a way to change the order: there is none. Use this plugin's `sort_classes` tool to get the same order without Prettier.
