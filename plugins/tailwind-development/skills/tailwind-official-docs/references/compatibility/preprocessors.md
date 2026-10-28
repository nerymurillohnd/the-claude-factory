# Replace Sass, Less and Stylus

Read https://tailwindcss.com/docs/compatibility#sass-less-and-stylus. Follow it over this file.

- Never run Tailwind v4 through Sass, Less or Stylus.
- Tell the user the project needs plain `.css` files for Tailwind.
- Replace preprocessor imports with plain `@import`: Tailwind bundles them.
- Replace preprocessor variables with CSS variables or `@theme` tokens.
- Keep nesting: Tailwind flattens nested CSS itself.
- Replace class-generating loops with utility classes in the markup.
- Replace `darken()` and `lighten()` with palette shades or `color-mix()`.
- Replace preprocessor math with native `calc()`, `min()`, `max()` and `round()`.
- Remove `postcss-import` and `autoprefixer` once only Tailwind needed them.
