# [Theme variables](https://tailwindcss.com/docs/theme)

Using utility classes as an API for your design tokens.

- [Overview](https://tailwindcss.com/docs/theme#overview): Design tokens as utility APIs
  - [What are theme variables?](https://tailwindcss.com/docs/theme#what-are-theme-variables): CSS variables in `@theme` that create utilities
  - [Relationship to utility classes](https://tailwindcss.com/docs/theme#relationship-to-utility-classes): Which utilities each token creates
  - [Theme variable namespaces](https://tailwindcss.com/docs/theme#theme-variable-namespaces): `--color-*`, `--spacing`, `--breakpoint-*` and the rest
  - [Default theme variables](https://tailwindcss.com/docs/theme#default-theme-variables): What `@import "tailwindcss"` defines
- [Customizing your theme](https://tailwindcss.com/docs/theme#customizing-your-theme): Change tokens in `@theme`
  - [Extending the default theme](https://tailwindcss.com/docs/theme#extending-the-default-theme): Add tokens
  - [Overriding the default theme](https://tailwindcss.com/docs/theme#overriding-the-default-theme): Redefine or clear a namespace
  - [Using a custom theme](https://tailwindcss.com/docs/theme#using-a-custom-theme): Start empty with `--*: initial`
  - [Defining animation keyframes](https://tailwindcss.com/docs/theme#defining-animation-keyframes): `@keyframes` inside `@theme` for `--animate-*`
  - [Referencing other variables](https://tailwindcss.com/docs/theme#referencing-other-variables): `@theme inline` for tokens that use `var()`
  - [Generating all CSS variables](https://tailwindcss.com/docs/theme#generating-all-css-variables): `@theme static` to emit every variable
  - [Sharing across projects](https://tailwindcss.com/docs/theme#sharing-across-projects): Import a shared theme file
- [Using your theme variables](https://tailwindcss.com/docs/theme#using-your-theme-variables): Use tokens outside utilities
  - [With custom CSS](https://tailwindcss.com/docs/theme#with-custom-css): `var(--…)` in custom CSS
  - [With arbitrary values](https://tailwindcss.com/docs/theme#with-arbitrary-values): Tokens in `calc()` and `[…]`
  - [Referencing in JavaScript](https://tailwindcss.com/docs/theme#referencing-in-javascript): CSS variables and `getComputedStyle` in JS
- [Default theme variable reference](https://tailwindcss.com/docs/theme#default-theme-variable-reference): Every default theme variable
