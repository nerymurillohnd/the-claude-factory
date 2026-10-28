# Flexbox and grid

## Contents

- flex-basis
- flex-direction
- flex-wrap
- flex
- flex-grow
- flex-shrink
- order
- grid-template-columns
- grid-column
- grid-template-rows
- grid-row
- grid-auto-flow
- grid-auto-columns
- grid-auto-rows
- gap
- justify-content
- justify-items
- justify-self
- align-content
- align-items
- align-self
- place-content
- place-items
- place-self

## [flex-basis](https://tailwindcss.com/docs/flex-basis)

Utilities for controlling the initial size of flex items.

- [Examples](https://tailwindcss.com/docs/flex-basis#examples): Examples of each utility
  - [Using the spacing scale](https://tailwindcss.com/docs/flex-basis#using-the-spacing-scale): `basis-<number>`
  - [Using the container scale](https://tailwindcss.com/docs/flex-basis#using-the-container-scale): `basis-xs`, `basis-sm`
  - [Using percentages](https://tailwindcss.com/docs/flex-basis#using-percentages): `basis-<fraction>`
  - [Using a custom value](https://tailwindcss.com/docs/flex-basis#using-a-custom-value): Arbitrary values: `basis-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/flex-basis#responsive-design): Breakpoint variants, such as `md:`
- [Customizing your theme](https://tailwindcss.com/docs/flex-basis#customizing-your-theme): Theme variables: `--container-*`

## [flex-direction](https://tailwindcss.com/docs/flex-direction)

Utilities for controlling the direction of flex items.

- [Examples](https://tailwindcss.com/docs/flex-direction#examples): Examples of each utility
  - [Row](https://tailwindcss.com/docs/flex-direction#row): `flex-row`
  - [Row reversed](https://tailwindcss.com/docs/flex-direction#row-reversed): `flex-row-reverse`
  - [Column](https://tailwindcss.com/docs/flex-direction#column): `flex-col`
  - [Column reversed](https://tailwindcss.com/docs/flex-direction#column-reversed): `flex-col-reverse`
  - [Responsive design](https://tailwindcss.com/docs/flex-direction#responsive-design): Breakpoint variants, such as `md:`

## [flex-wrap](https://tailwindcss.com/docs/flex-wrap)

Utilities for controlling how flex items wrap.

- [Examples](https://tailwindcss.com/docs/flex-wrap#examples): Examples of each utility
  - [Don't wrap](https://tailwindcss.com/docs/flex-wrap#dont-wrap): `flex-nowrap`
  - [Wrap normally](https://tailwindcss.com/docs/flex-wrap#wrap-normally): `flex-wrap`
  - [Wrap reversed](https://tailwindcss.com/docs/flex-wrap#wrap-reversed): `flex-wrap-reverse`
  - [Responsive design](https://tailwindcss.com/docs/flex-wrap#responsive-design): Breakpoint variants, such as `md:`

## [flex](https://tailwindcss.com/docs/flex)

Utilities for controlling how flex items both grow and shrink.

- [Examples](https://tailwindcss.com/docs/flex#examples): Examples of each utility
  - [Basic example](https://tailwindcss.com/docs/flex#basic-example): `flex-<number>`
  - [Initial](https://tailwindcss.com/docs/flex#initial): `flex-initial`
  - [Auto](https://tailwindcss.com/docs/flex#auto): `flex-auto`
  - [None](https://tailwindcss.com/docs/flex#none): `flex-none`
  - [Using a custom value](https://tailwindcss.com/docs/flex#using-a-custom-value): Arbitrary values: `flex-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/flex#responsive-design): Breakpoint variants, such as `md:`

## [flex-grow](https://tailwindcss.com/docs/flex-grow)

Utilities for controlling how flex items grow.

- [Examples](https://tailwindcss.com/docs/flex-grow#examples): Examples of each utility
  - [Allowing items to grow](https://tailwindcss.com/docs/flex-grow#allowing-items-to-grow): `grow`
  - [Growing items based on factor](https://tailwindcss.com/docs/flex-grow#growing-items-based-on-factor): `grow-<number>`
  - [Preventing items from growing](https://tailwindcss.com/docs/flex-grow#preventing-items-from-growing): `grow-0`
  - [Using a custom value](https://tailwindcss.com/docs/flex-grow#using-a-custom-value): Arbitrary values: `grow-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/flex-grow#responsive-design): Breakpoint variants, such as `md:`

## [flex-shrink](https://tailwindcss.com/docs/flex-shrink)

Utilities for controlling how flex items shrink.

- [Examples](https://tailwindcss.com/docs/flex-shrink#examples): Examples of each utility
  - [Allowing flex items to shrink](https://tailwindcss.com/docs/flex-shrink#allowing-flex-items-to-shrink): `shrink`
  - [Preventing items from shrinking](https://tailwindcss.com/docs/flex-shrink#preventing-items-from-shrinking): `shrink-0`
  - [Using a custom value](https://tailwindcss.com/docs/flex-shrink#using-a-custom-value): Arbitrary values: `shrink-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/flex-shrink#responsive-design): Breakpoint variants, such as `md:`

## [order](https://tailwindcss.com/docs/order)

Utilities for controlling the order of flex and grid items.

- [Examples](https://tailwindcss.com/docs/order#examples): Examples of each utility
  - [Explicitly setting a sort order](https://tailwindcss.com/docs/order#explicitly-setting-a-sort-order): `order-<number>`
  - [Ordering items first or last](https://tailwindcss.com/docs/order#ordering-items-first-or-last): `order-first`, `order-last`
  - [Using negative values](https://tailwindcss.com/docs/order#using-negative-values): Use a negative order value, prefix the class name with a dash to convert it to a negative value
  - [Using a custom value](https://tailwindcss.com/docs/order#using-a-custom-value): Arbitrary values: `order-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/order#responsive-design): Breakpoint variants, such as `md:`

## [grid-template-columns](https://tailwindcss.com/docs/grid-template-columns)

Utilities for specifying the columns in a grid layout.

- [Examples](https://tailwindcss.com/docs/grid-template-columns#examples): Examples of each utility
  - [Specifying the grid columns](https://tailwindcss.com/docs/grid-template-columns#specifying-the-grid-columns): `grid-cols-<number>`
  - [Implementing a subgrid](https://tailwindcss.com/docs/grid-template-columns#implementing-a-subgrid): `grid-cols-subgrid`
  - [Using a custom value](https://tailwindcss.com/docs/grid-template-columns#using-a-custom-value): Arbitrary values: `grid-cols-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/grid-template-columns#responsive-design): Breakpoint variants, such as `md:`

## [grid-column](https://tailwindcss.com/docs/grid-column)

Utilities for controlling how elements are sized and placed across grid columns.

- [Examples](https://tailwindcss.com/docs/grid-column#examples): Examples of each utility
  - [Spanning columns](https://tailwindcss.com/docs/grid-column#spanning-columns): `col-span-<number>`
  - [Starting and ending lines](https://tailwindcss.com/docs/grid-column#starting-and-ending-lines): `col-start-<number>`, `col-end-<number>`
  - [Using a custom value](https://tailwindcss.com/docs/grid-column#using-a-custom-value): Arbitrary values: `col-[<value>]`, `col-span-[<value>]`, `col-start-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/grid-column#responsive-design): Breakpoint variants, such as `md:`

## [grid-template-rows](https://tailwindcss.com/docs/grid-template-rows)

Utilities for specifying the rows in a grid layout.

- [Examples](https://tailwindcss.com/docs/grid-template-rows#examples): Examples of each utility
  - [Specifying the grid rows](https://tailwindcss.com/docs/grid-template-rows#specifying-the-grid-rows): `grid-rows-<number>`
  - [Implementing a subgrid](https://tailwindcss.com/docs/grid-template-rows#implementing-a-subgrid): `grid-rows-subgrid`
  - [Using a custom value](https://tailwindcss.com/docs/grid-template-rows#using-a-custom-value): Arbitrary values: `grid-rows-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/grid-template-rows#responsive-design): Breakpoint variants, such as `md:`

## [grid-row](https://tailwindcss.com/docs/grid-row)

Utilities for controlling how elements are sized and placed across grid rows.

- [Examples](https://tailwindcss.com/docs/grid-row#examples): Examples of each utility
  - [Spanning rows](https://tailwindcss.com/docs/grid-row#spanning-rows): `row-span-<number>`
  - [Starting and ending lines](https://tailwindcss.com/docs/grid-row#starting-and-ending-lines): `row-start-<number>`, `row-end-<number>`
  - [Using a custom value](https://tailwindcss.com/docs/grid-row#using-a-custom-value): Arbitrary values: `row-[<value>]`, `row-span-[<value>]`, `row-start-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/grid-row#responsive-design): Breakpoint variants, such as `md:`

## [grid-auto-flow](https://tailwindcss.com/docs/grid-auto-flow)

Utilities for controlling how elements in a grid are auto-placed.

- [Examples](https://tailwindcss.com/docs/grid-auto-flow#examples): Examples of each utility
  - [Basic example](https://tailwindcss.com/docs/grid-auto-flow#basic-example): `grid-flow-col`, `grid-flow-row-dense`
  - [Responsive design](https://tailwindcss.com/docs/grid-auto-flow#responsive-design): Breakpoint variants, such as `md:`

## [grid-auto-columns](https://tailwindcss.com/docs/grid-auto-columns)

Utilities for controlling the size of implicitly-created grid columns.

- [Examples](https://tailwindcss.com/docs/grid-auto-columns#examples): Examples of each utility
  - [Basic example](https://tailwindcss.com/docs/grid-auto-columns#basic-example): `auto-cols-min`, `auto-cols-max`
  - [Using a custom value](https://tailwindcss.com/docs/grid-auto-columns#using-a-custom-value): Arbitrary values: `auto-cols-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/grid-auto-columns#responsive-design): Breakpoint variants, such as `md:`

## [grid-auto-rows](https://tailwindcss.com/docs/grid-auto-rows)

Utilities for controlling the size of implicitly-created grid rows.

- [Examples](https://tailwindcss.com/docs/grid-auto-rows#examples): Examples of each utility
  - [Basic example](https://tailwindcss.com/docs/grid-auto-rows#basic-example): `auto-rows-min`, `auto-rows-max`
  - [Using a custom value](https://tailwindcss.com/docs/grid-auto-rows#using-a-custom-value): Arbitrary values: `auto-rows-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/grid-auto-rows#responsive-design): Breakpoint variants, such as `md:`

## [gap](https://tailwindcss.com/docs/gap)

Utilities for controlling gutters between grid and flexbox items.

- [Examples](https://tailwindcss.com/docs/gap#examples): Examples of each utility
  - [Basic example](https://tailwindcss.com/docs/gap#basic-example): `gap-<number>`
  - [Changing row and column gaps independently](https://tailwindcss.com/docs/gap#changing-row-and-column-gaps-independently): `gap-x-<number>`, `gap-y-<number>`
  - [Using a custom value](https://tailwindcss.com/docs/gap#using-a-custom-value): Arbitrary values: `gap-[<value>]`, `gap-x-[<value>]`, `gap-y-[<value>]`
  - [Responsive design](https://tailwindcss.com/docs/gap#responsive-design): Breakpoint variants, such as `md:`

## [justify-content](https://tailwindcss.com/docs/justify-content)

Utilities for controlling how flex and grid items are positioned along a container's main axis.

- [Examples](https://tailwindcss.com/docs/justify-content#examples): Examples of each utility
  - [Start](https://tailwindcss.com/docs/justify-content#start): `justify-start`
  - [Center](https://tailwindcss.com/docs/justify-content#center): `justify-center`, `justify-center-safe`
  - [End](https://tailwindcss.com/docs/justify-content#end): `justify-end`, `justify-end-safe`
  - [Space between](https://tailwindcss.com/docs/justify-content#space-between): `justify-between`
  - [Space around](https://tailwindcss.com/docs/justify-content#space-around): `justify-around`
  - [Space evenly](https://tailwindcss.com/docs/justify-content#space-evenly): `justify-evenly`, `justify-around`
  - [Stretch](https://tailwindcss.com/docs/justify-content#stretch): `justify-stretch`
  - [Normal](https://tailwindcss.com/docs/justify-content#normal): `justify-normal`, `justify-content`
  - [Responsive design](https://tailwindcss.com/docs/justify-content#responsive-design): Breakpoint variants, such as `md:`

## [justify-items](https://tailwindcss.com/docs/justify-items)

Utilities for controlling how grid items are aligned along their inline axis.

- [Examples](https://tailwindcss.com/docs/justify-items#examples): Examples of each utility
  - [Start](https://tailwindcss.com/docs/justify-items#start): `justify-items-start`
  - [End](https://tailwindcss.com/docs/justify-items#end): `justify-items-end`, `justify-items-end-safe`
  - [Center](https://tailwindcss.com/docs/justify-items#center): `justify-items-center`, `justify-items-center-safe`
  - [Stretch](https://tailwindcss.com/docs/justify-items#stretch): `justify-items-stretch`
  - [Responsive design](https://tailwindcss.com/docs/justify-items#responsive-design): Breakpoint variants, such as `md:`

## [justify-self](https://tailwindcss.com/docs/justify-self)

Utilities for controlling how an individual grid item is aligned along its inline axis.

- [Examples](https://tailwindcss.com/docs/justify-self#examples): Examples of each utility
  - [Auto](https://tailwindcss.com/docs/justify-self#auto): `justify-self-auto`, `justify-items`
  - [Start](https://tailwindcss.com/docs/justify-self#start): `justify-self-start`
  - [Center](https://tailwindcss.com/docs/justify-self#center): `justify-self-center`, `justify-self-center-safe`
  - [End](https://tailwindcss.com/docs/justify-self#end): `justify-self-end`, `justify-self-end-safe`
  - [Stretch](https://tailwindcss.com/docs/justify-self#stretch): `justify-self-stretch`
  - [Responsive design](https://tailwindcss.com/docs/justify-self#responsive-design): Breakpoint variants, such as `md:`

## [align-content](https://tailwindcss.com/docs/align-content)

Utilities for controlling how rows are positioned in multi-row flex and grid containers.

- [Examples](https://tailwindcss.com/docs/align-content#examples): Examples of each utility
  - [Start](https://tailwindcss.com/docs/align-content#start): `content-start`
  - [Center](https://tailwindcss.com/docs/align-content#center): `content-center`
  - [End](https://tailwindcss.com/docs/align-content#end): `content-end`
  - [Space between](https://tailwindcss.com/docs/align-content#space-between): `content-between`
  - [Space around](https://tailwindcss.com/docs/align-content#space-around): `content-around`
  - [Space evenly](https://tailwindcss.com/docs/align-content#space-evenly): `content-evenly`, `content-around`
  - [Stretch](https://tailwindcss.com/docs/align-content#stretch): `content-stretch`
  - [Normal](https://tailwindcss.com/docs/align-content#normal): `content-normal`, `align-content`
  - [Responsive design](https://tailwindcss.com/docs/align-content#responsive-design): Breakpoint variants, such as `md:`

## [align-items](https://tailwindcss.com/docs/align-items)

Utilities for controlling how flex and grid items are positioned along a container's cross axis.

- [Examples](https://tailwindcss.com/docs/align-items#examples): Examples of each utility
  - [Stretch](https://tailwindcss.com/docs/align-items#stretch): `items-stretch`
  - [Start](https://tailwindcss.com/docs/align-items#start): `items-start`
  - [Center](https://tailwindcss.com/docs/align-items#center): `items-center`
  - [End](https://tailwindcss.com/docs/align-items#end): `items-end`
  - [Baseline](https://tailwindcss.com/docs/align-items#baseline): `items-baseline`
  - [Last baseline](https://tailwindcss.com/docs/align-items#last-baseline): `items-baseline-last`
  - [Responsive design](https://tailwindcss.com/docs/align-items#responsive-design): Breakpoint variants, such as `md:`

## [align-self](https://tailwindcss.com/docs/align-self)

Utilities for controlling how an individual flex or grid item is positioned along its container's cross axis.

- [Examples](https://tailwindcss.com/docs/align-self#examples): Examples of each utility
  - [Auto](https://tailwindcss.com/docs/align-self#auto): `self-auto`, `align-items`
  - [Start](https://tailwindcss.com/docs/align-self#start): `self-start`, `align-items`
  - [Center](https://tailwindcss.com/docs/align-self#center): `self-center`, `align-items`
  - [End](https://tailwindcss.com/docs/align-self#end): `self-end`, `align-items`
  - [Stretch](https://tailwindcss.com/docs/align-self#stretch): `self-stretch`, `align-items`
  - [Baseline](https://tailwindcss.com/docs/align-self#baseline): `self-baseline`
  - [Last baseline](https://tailwindcss.com/docs/align-self#last-baseline): `self-baseline-last`
  - [Responsive design](https://tailwindcss.com/docs/align-self#responsive-design): Breakpoint variants, such as `md:`

## [place-content](https://tailwindcss.com/docs/place-content)

Utilities for controlling how content is justified and aligned at the same time.

- [Examples](https://tailwindcss.com/docs/place-content#examples): Examples of each utility
  - [Center](https://tailwindcss.com/docs/place-content#center): `place-content-center`
  - [Start](https://tailwindcss.com/docs/place-content#start): `place-content-start`
  - [End](https://tailwindcss.com/docs/place-content#end): `place-content-end`
  - [Space between](https://tailwindcss.com/docs/place-content#space-between): `place-content-between`
  - [Space around](https://tailwindcss.com/docs/place-content#space-around): `place-content-around`
  - [Space evenly](https://tailwindcss.com/docs/place-content#space-evenly): `place-content-evenly`
  - [Stretch](https://tailwindcss.com/docs/place-content#stretch): `place-content-stretch`
  - [Responsive design](https://tailwindcss.com/docs/place-content#responsive-design): Breakpoint variants, such as `md:`

## [place-items](https://tailwindcss.com/docs/place-items)

Utilities for controlling how items are justified and aligned at the same time.

- [Examples](https://tailwindcss.com/docs/place-items#examples): Examples of each utility
  - [Start](https://tailwindcss.com/docs/place-items#start): `place-items-start`
  - [End](https://tailwindcss.com/docs/place-items#end): `place-items-end`
  - [Center](https://tailwindcss.com/docs/place-items#center): `place-items-center`
  - [Stretch](https://tailwindcss.com/docs/place-items#stretch): `place-items-stretch`
- [Responsive design](https://tailwindcss.com/docs/place-items#responsive-design): Breakpoint variants, such as `md:`

## [place-self](https://tailwindcss.com/docs/place-self)

Utilities for controlling how an individual item is justified and aligned at the same time.

- [Examples](https://tailwindcss.com/docs/place-self#examples): Examples of each utility
  - [Auto](https://tailwindcss.com/docs/place-self#auto): `place-self-auto`, `place-items`
  - [Start](https://tailwindcss.com/docs/place-self#start): `place-self-start`
  - [Center](https://tailwindcss.com/docs/place-self#center): `place-self-center`
  - [End](https://tailwindcss.com/docs/place-self#end): `place-self-end`
  - [Stretch](https://tailwindcss.com/docs/place-self#stretch): `place-self-stretch`
  - [Responsive design](https://tailwindcss.com/docs/place-self#responsive-design): Breakpoint variants, such as `md:`
