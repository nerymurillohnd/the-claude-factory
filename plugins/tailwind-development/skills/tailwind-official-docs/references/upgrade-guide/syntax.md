# Check syntax changes

Read each section below on https://tailwindcss.com/docs/upgrade-guide. Follow it over this file.

## `#removed-tailwind-directives`

- Replace `@tailwind base/components/utilities` with `@import "tailwindcss";`.

## `#using-a-prefix`

- Move the prefix to the start of the class: `tw:flex`.
- Write theme variables without the prefix.

## `#the-important-modifier`

- Move `!` to the end of the class: `flex!`.

## `#adding-custom-utilities`

- Rewrite classes in `@layer utilities` or `@layer components` as `@utility`.

## `#container-configuration`

- Rebuild `container` options like `center` and `padding` with `@utility container`.

## `#variant-stacking-order`

- Reverse order-sensitive stacked variants: `first:*:` becomes `*:first:`.

## `#variables-in-arbitrary-values`

- Replace `[--var]` with `(--var)`.

## `#arbitrary-values-in-grid-and-object-position-utilities`

- Replace commas meant as spaces with `_` in `grid-cols-[…]`, `grid-rows-[…]`, `object-[…]`.

## `#hover-styles-on-mobile`

- Find `hover:` that touch devices need on tap.
- Ask the user before restoring the old hover with `@custom-variant hover (&:hover);`.
