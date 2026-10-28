# [Adding custom styles](https://tailwindcss.com/docs/adding-custom-styles)

Best practices for adding your own custom styles in Tailwind projects.

- [Customizing your theme](https://tailwindcss.com/docs/adding-custom-styles#customizing-your-theme): Change colors, spacing, type or breakpoints with `@theme`
- [Using arbitrary values](https://tailwindcss.com/docs/adding-custom-styles#using-arbitrary-values): One-off values with `[…]`, such as `top-[117px]`
  - [Arbitrary properties](https://tailwindcss.com/docs/adding-custom-styles#arbitrary-properties): Any CSS property with `[property:value]`
  - [Arbitrary variants](https://tailwindcss.com/docs/adding-custom-styles#arbitrary-variants): One-off selectors with `[&…]:`
  - [Handling whitespace](https://tailwindcss.com/docs/adding-custom-styles#handling-whitespace): Write spaces as `_` inside `[…]`
  - [Resolving ambiguities](https://tailwindcss.com/docs/adding-custom-styles#resolving-ambiguities): Type hints like `text-(length:--x)` when a value is ambiguous
- [Using custom CSS](https://tailwindcss.com/docs/adding-custom-styles#using-custom-css): Plain CSS beside Tailwind
  - [Adding base styles](https://tailwindcss.com/docs/adding-custom-styles#adding-base-styles): Page defaults on `html` or `body`, or in `@layer base`
  - [Adding component classes](https://tailwindcss.com/docs/adding-custom-styles#adding-component-classes): Classes like `.card` in `@layer components`
  - [Using variants](https://tailwindcss.com/docs/adding-custom-styles#using-variants): `@variant` inside custom CSS
- [Adding custom utilities](https://tailwindcss.com/docs/adding-custom-styles#adding-custom-utilities): Register your own utilities with `@utility`
  - [Simple utilities](https://tailwindcss.com/docs/adding-custom-styles#simple-utilities): `@utility name { … }`
  - [Complex utilities](https://tailwindcss.com/docs/adding-custom-styles#complex-utilities): Nested rules inside `@utility`
  - [Functional utilities](https://tailwindcss.com/docs/adding-custom-styles#functional-utilities): Utilities that take values: `@utility tab-*` with `--value()`
- [Adding custom variants](https://tailwindcss.com/docs/adding-custom-styles#adding-custom-variants): Register variants with `@custom-variant`
