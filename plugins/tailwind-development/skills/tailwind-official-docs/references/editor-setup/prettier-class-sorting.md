# Class sorting with Prettier

Sources, checked 2026-10-27: https://tailwindcss.com/docs/editor-setup#class-sorting-with-prettier, the plugin's README, https://github.com/tailwindlabs/prettier-plugin-tailwindcss (v0.8.1), and the sort order in https://tailwindcss.com/blog/automatic-class-sorting-with-prettier#how-classes-are-sorted. When they differ from this file, they win.

## What it is

`prettier-plugin-tailwindcss`, the official plugin. It sorts classes in the order Tailwind emits them in the CSS, wherever Prettier runs: editors, the command line, CI. It needs Prettier v3 or later and Tailwind CSS v3.0 or later, and since v0.5 it is ESM-only.

## Setup

1. Install `prettier` and `prettier-plugin-tailwindcss` as dev dependencies, with the project's package manager.
2. Add it to the Prettier config's `plugins`.
3. On Tailwind v4, set `tailwindStylesheet` to the CSS entry point, so the order knows the project's theme and custom utilities. On v3, `tailwindConfig` points to the config when it is not beside the Prettier config. Both paths resolve from the Prettier config file.

```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./src/app.css"
}
```

## Options

| Option | Use |
| --- | --- |
| `tailwindAttributes` | Attributes to sort beyond `class`, `className`, `:class`, `[ngClass]` and `@apply`; a `/regex/` string matches several |
| `tailwindFunctions` | Functions and tagged templates whose strings hold classes (`clsx`, `cva`, `tw`); also accepts `/regex/` strings |
| `tailwindPreserveWhitespace` | Keep the whitespace around classes |
| `tailwindPreserveDuplicates` | Keep duplicates, for templating languages (Blade, Fluid) whose syntax looks like repeated classes |

## The order

Classes follow the CSS: base, then components (such as `container`), then utilities, roughly layout first and decoration last, so an override comes after what it overrides. Variants such as `hover:` come after plain utilities; responsive variants come last, smallest breakpoint first. Classes Tailwind does not know go to the front. The order is not configurable.

## Other Prettier plugins

It uses Prettier APIs only one plugin can use at a time. It has workarounds for a fixed list (among them `prettier-plugin-svelte`, `prettier-plugin-astro`, `prettier-plugin-organize-imports`, the import sorters, `@shopify/prettier-plugin-liquid`, `@prettier/plugin-pug`), and it must be the last entry in `plugins`. With a plugin outside that list, check that both still work.

## Without Prettier

The plugin exports the sorter (`prettier-plugin-tailwindcss/sorter`, `createSorter`) for tools that need the same order. This plugin's own `sort_classes` tool gives the official order too.
