# [Responsive design](https://tailwindcss.com/docs/responsive-design)

Using responsive utility variants to build adaptive user interfaces.

- [Overview](https://tailwindcss.com/docs/responsive-design#overview): Breakpoint prefixes and the viewport meta tag
- [Working mobile-first](https://tailwindcss.com/docs/responsive-design#working-mobile-first): Unprefixed applies everywhere; prefixes apply upward
  - [Targeting mobile screens](https://tailwindcss.com/docs/responsive-design#targeting-mobile-screens): Style mobile with unprefixed classes, not `sm:`
  - [Targeting a breakpoint range](https://tailwindcss.com/docs/responsive-design#targeting-a-breakpoint-range): Ranges with `md:max-xl:`
  - [Targeting a single breakpoint](https://tailwindcss.com/docs/responsive-design#targeting-a-single-breakpoint): One breakpoint with `md:max-lg:`
- [Using custom breakpoints](https://tailwindcss.com/docs/responsive-design#using-custom-breakpoints): Your own breakpoints
  - [Customizing your theme](https://tailwindcss.com/docs/responsive-design#customizing-your-theme): `--breakpoint-*` theme variables
  - [Removing default breakpoints](https://tailwindcss.com/docs/responsive-design#removing-default-breakpoints): `--breakpoint-*: initial`
  - [Using arbitrary values](https://tailwindcss.com/docs/responsive-design#using-arbitrary-values): One-off `min-[…]:` and `max-[…]:`
- [Container queries](https://tailwindcss.com/docs/responsive-design#container-queries): Style by parent size
  - [What are container queries?](https://tailwindcss.com/docs/responsive-design#what-are-container-queries): Container vs viewport sizing
  - [Basic example](https://tailwindcss.com/docs/responsive-design#basic-example): `@container` and `@md:`
  - [Max-width container queries](https://tailwindcss.com/docs/responsive-design#max-width-container-queries): `@max-md:`
  - [Container query ranges](https://tailwindcss.com/docs/responsive-design#container-query-ranges): `@sm:@max-md:`
  - [Named containers](https://tailwindcss.com/docs/responsive-design#named-containers): `@container/name` and `@md/name:`
  - [Using size containers](https://tailwindcss.com/docs/responsive-design#using-size-containers): `@container-size` for block-size units
  - [Using custom container sizes](https://tailwindcss.com/docs/responsive-design#using-custom-container-sizes): `--container-*` theme variables
  - [Using arbitrary values](https://tailwindcss.com/docs/responsive-design#using-arbitrary-container-query-values): One-off `@min-[…]:` and `@max-[…]:`
  - [Using container query units](https://tailwindcss.com/docs/responsive-design#using-container-query-units): `cqw` and `cqi` in arbitrary values
  - [Container size reference](https://tailwindcss.com/docs/responsive-design#container-size-reference): Default container sizes
