# Set up class sorting with Prettier

Read the README for every option: https://github.com/tailwindlabs/prettier-plugin-tailwindcss
Follow it over this file.

## Set it up

1. Install `prettier` and `prettier-plugin-tailwindcss` as dev dependencies.
2. Add the plugin as the last entry of `plugins` in the Prettier config.
3. On v4, set `tailwindStylesheet` to the CSS entry file.
4. On v3, set `tailwindConfig` if the config is not next to Prettier's.
5. Write both paths relative to the Prettier config.
6. Add class helpers to `tailwindFunctions`.
7. Add custom class attributes to `tailwindAttributes`.

## Avoid the traps

- Keep the plugin last among Prettier plugins.
- Check that the other Prettier plugins are on the README's list.
- Never load it with `require()`: it is ESM-only.
- Write patterns as `"/regex/"` strings, not regex literals.
- On v3, confirm `tailwindConfig` finds the real file.
- Keep duplicates in Blade or Fluid with the README's option.
- Use the `sort_classes` tool to sort without Prettier.
