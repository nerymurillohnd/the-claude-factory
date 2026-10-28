# Pick the right page

Route by the intended CSS behavior, not by an approximate word match.

- Text foreground color → `color`.
- Palette and shared color tokens → `colors` and `theme`.
- Background color → `background-color`.
- Background images and gradients → `background-image`.
- Text size versus text color → `font-size` versus `color`.
- Font family versus weight → `font-family` versus `font-weight`.
- Line height embedded in text-size syntax → `font-size` and `line-height`.
- Container display mode → `display`.
- Flex shorthand versus direction, growth or shrinkage → the corresponding individual flex pages.
- Grid track definitions versus item placement → `grid-template-columns` and `grid-template-rows` versus `grid-column` and `grid-row`.
- Space between layout items → `gap`.
- Element outer spacing → `margin`.
- Element inner spacing → `padding`.
- Physical versus logical dimensions → the corresponding width and height or inline-size and block-size pages.
- Positioning mode versus offsets → `position` and `top-right-bottom-left`.
- Overflow clipping and scrolling versus scroll chaining → `overflow` versus `overscroll-behavior`.
- Element opacity versus a color's opacity → `opacity` versus `colors` and the relevant color property page.
- Element filtering versus backdrop filtering → `filter-*` versus `backdrop-filter-*`.
- Box shadow, text shadow and filter drop shadow → `box-shadow`, `text-shadow` and `filter-drop-shadow`, respectively.
- Outline utilities → the relevant `outline-*` pages.
- Ring utilities → consult `box-shadow` and confirm the documented ring syntax.
- Transitioned properties, duration, timing, delay and discrete behavior → their separate transition pages.
- Transform behavior → the exact transform page, plus `transform` when composition or transform mode is relevant.
- SVG fill versus stroke color versus stroke thickness → `fill`, `stroke` and `stroke-width`.
- Color-scheme hints versus activating dark variants → `color-scheme` versus `dark-mode`.
- Forced-color adjustment does not substitute for a full accessibility review.

If no reference lists a feature, find its page on the live docs: absence from the references does not prove absence from Tailwind.
