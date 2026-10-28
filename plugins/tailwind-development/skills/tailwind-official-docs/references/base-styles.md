# Base styles

## [Preflight](https://tailwindcss.com/docs/preflight)

An opinionated set of base styles for Tailwind projects.

- [Overview](https://tailwindcss.com/docs/preflight#overview): Base styles built on modern-normalize that smooth cross-browser differences
  - [Margins are removed](https://tailwindcss.com/docs/preflight#margins-are-removed): All default margins are reset to zero
  - [Border styles are reset](https://tailwindcss.com/docs/preflight#border-styles-are-reset): Borders default to `0` width and `solid` style, so `border` alone works
  - [Headings are unstyled](https://tailwindcss.com/docs/preflight#headings-are-unstyled): Headings inherit size and weight; style them yourself
  - [Lists are unstyled](https://tailwindcss.com/docs/preflight#lists-are-unstyled): No bullets or numbers; add `role="list"` to keep list semantics
  - [Images are block-level](https://tailwindcss.com/docs/preflight#images-are-block-level): `img`, `svg`, `video` and other replaced elements are `display: block`
  - [Images are constrained](https://tailwindcss.com/docs/preflight#images-are-constrained): Images and video get `max-width: 100%`; override with `max-w-none`
- [Extending Preflight](https://tailwindcss.com/docs/preflight#extending-preflight): Add your own base styles in `@layer base`
- [Disabling Preflight](https://tailwindcss.com/docs/preflight#disabling-preflight): Import only the theme and utilities layers to drop Preflight
