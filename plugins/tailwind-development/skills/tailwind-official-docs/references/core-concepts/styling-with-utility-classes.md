# Style with utility classes

Read the matching section of https://tailwindcss.com/docs/styling-with-utility-classes.
Follow it over this file.

## `#overview` and `#why-not-just-use-inline-styles`

- Replace static `style=` values with utility classes.

## `#thinking-in-utility-classes`

- Read `#styling-hover-and-focus-states` before the first state variant.
- Read `#media-queries-and-breakpoints` before the first breakpoint.
- Read `#targeting-dark-mode` before the first `dark:` class.
- Replace hand-written `:hover`, `@media` and dark rules with variants.

## `#using-class-composition`

- Combine classes that build one property, like filters, gradients and transforms.
- Replace custom `filter:` or `transform:` rules with composed classes.

## `#using-arbitrary-values` and `#how-does-this-even-work`

- Use `[…]` only for a value outside the theme.
- Turn an arbitrary value used repeatedly into a theme token.
- Never build class names by interpolation: Tailwind only sees complete names.

## `#complex-selectors`

- Stack variants for combined conditions: `dark:lg:hover:`.
- Read `adding-custom-styles#arbitrary-variants` for selectors without a variant.

## `#when-to-use-inline-styles`

- Use inline styles only for values from a database or an API.
- Pass dynamic values as CSS variables and read them with utilities.

## `#managing-duplication`

- Render repeated markup in a loop (`#using-loops`).
- Edit repetition in one file with multi-cursor (`#using-multi-cursor-editing`).
- Extract a component or partial for reuse across files (`#using-components`).
- Use a small custom class only where a partial is overkill (`#using-custom-css`).

## `#managing-style-conflicts` and `#conflicting-utility-classes`

- Remove one of two classes that set the same property.
- Never rely on class order: the stylesheet order decides.
- Render one class or the other conditionally instead.

## `#using-the-important-modifier`

- Add `!` at the end of a class only when specificity leaves no other way.

## `#using-the-important-flag`

- Use `@import "tailwindcss" important;` only beside high-specificity legacy CSS.

## `#using-the-prefix-option`

- Use `prefix(tw)` only when class names collide with other CSS.
- Write prefixed classes as `tw:flex`, prefix first.
