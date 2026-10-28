# Check utility changes

Read each section below on https://tailwindcss.com/docs/upgrade-guide. Follow it over this file.

## `#removed-deprecated-utilities`

- Search for `*-opacity-*`, `flex-shrink-*` and `flex-grow-*`.
- Search for `overflow-ellipsis` and `decoration-slice|clone`.
- Replace each with the page's alternative.

## `#renamed-utilities` and `#updated-shadow-radius-and-blur-scales`

- Search for bare and `-sm` `shadow`, `drop-shadow`, `blur`, `backdrop-blur`, `rounded`.
- Rename each as the page's table shows.
- Rename bare ones too: they still work but look different.

## `#renamed-outline-utility`

- Replace `outline outline-<n>` with `outline-<n>`.
- Replace `outline-none` with `outline-hidden`.

## `#default-ring-width-change` and `#default-ring-width-and-color`

- Replace bare `ring` with `ring-3`.
- Add `ring-blue-500` where code relied on the old default color.

## `#default-border-color`

- Add a color to every `border` and `divide-*` that relied on the old gray.
- Ask the user before adding the page's compatibility CSS instead.

## `#space-between-selector` and `#divide-selector`

- Check `space-*` and `divide-*` on inline children.
- Check children that set their own margins or borders.
- Replace a broken `space-*` layout with flex or grid and `gap`.

## `#using-variants-with-gradients`

- Check gradients that a variant overrides.
- Add `via-none` where a three-stop gradient must reset.

## `#individual-transform-properties`, `#resetting-transforms` and `#transitions`

- Replace `transform-none` with `scale-none`, `rotate-none` or `translate-none`.
- Replace `transform` in `transition-[…]` with `scale`, `rotate` or `translate`.

## `#transitioning-outline-color`

- Set outline colors unconditionally where `transition` now animates them.
