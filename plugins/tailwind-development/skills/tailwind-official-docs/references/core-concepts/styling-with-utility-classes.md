# [Styling with utility classes](https://tailwindcss.com/docs/styling-with-utility-classes)

Building complex components from a constrained set of primitive utilities.

- [Overview](https://tailwindcss.com/docs/styling-with-utility-classes#overview): Style with single-purpose classes in markup
  - [Why not just use inline styles?](https://tailwindcss.com/docs/styling-with-utility-classes#why-not-just-use-inline-styles): What utilities give that inline styles lack
- [Thinking in utility classes](https://tailwindcss.com/docs/styling-with-utility-classes#thinking-in-utility-classes): Working with utilities day to day
  - [Styling hover and focus states](https://tailwindcss.com/docs/styling-with-utility-classes#styling-hover-and-focus-states): State variants like `hover:`
  - [Media queries and breakpoints](https://tailwindcss.com/docs/styling-with-utility-classes#media-queries-and-breakpoints): Breakpoint variants like `sm:`
  - [Targeting dark mode](https://tailwindcss.com/docs/styling-with-utility-classes#targeting-dark-mode): `dark:`
  - [Using class composition](https://tailwindcss.com/docs/styling-with-utility-classes#using-class-composition): Several classes building one property
  - [Using arbitrary values](https://tailwindcss.com/docs/styling-with-utility-classes#using-arbitrary-values): `[…]` for values outside the theme
  - [Complex selectors](https://tailwindcss.com/docs/styling-with-utility-classes#complex-selectors): Stacked variants like `dark:lg:hover:`
  - [When to use inline styles](https://tailwindcss.com/docs/styling-with-utility-classes#when-to-use-inline-styles): Inline styles for dynamic values
- [Managing duplication](https://tailwindcss.com/docs/styling-with-utility-classes#managing-duplication): Handling repeated class lists
  - [Using loops](https://tailwindcss.com/docs/styling-with-utility-classes#using-loops): Render repeats in loops
  - [Using multi-cursor editing](https://tailwindcss.com/docs/styling-with-utility-classes#using-multi-cursor-editing): Edit repeats at once
  - [Using components](https://tailwindcss.com/docs/styling-with-utility-classes#using-components): Extract components or partials
  - [Using custom CSS](https://tailwindcss.com/docs/styling-with-utility-classes#using-custom-css): Small custom classes
- [Managing style conflicts](https://tailwindcss.com/docs/styling-with-utility-classes#managing-style-conflicts): When classes fight
  - [Conflicting utility classes](https://tailwindcss.com/docs/styling-with-utility-classes#conflicting-utility-classes): Stylesheet order wins, not class order
  - [Using the important modifier](https://tailwindcss.com/docs/styling-with-utility-classes#using-the-important-modifier): `!` suffix: `bg-red-500!`
  - [Using the important flag](https://tailwindcss.com/docs/styling-with-utility-classes#using-the-important-flag): `@import "tailwindcss" important`
  - [Using the prefix option](https://tailwindcss.com/docs/styling-with-utility-classes#using-the-prefix-option): `prefix(tw)` and `tw:` classes
