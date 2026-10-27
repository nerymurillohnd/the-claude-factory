# Surface and finish: colour, depth, media, details and states

The decisions of steps 5.3 to 5.5 and 6, applied only once the ranking and spacing already read. Each one follows the written ranking: the strongest colour, the highest elevation and the most finish go to the primary element. Exact utilities: `tailwind-development:tailwind-official-docs`.

## Contents

- Colour in use
- Contrast and accessibility
- Depth
- Images and media
- Finishing
- States and real content

## Colour in use

- Colour reinforces the ranking; it never replaces it. Most of the surface stays neutral.
- Secondary text on a coloured surface: do not use grey, and do not lower the opacity of white (`text-white/60`): it looks washed out and lets images show through. Take a shade of the surface's own hue with a lighter or darker lightness from the ramp (`text-brand-100` on `bg-brand-700`), or a dedicated token.
- When white text forces a very dark fill that dominates the page, flip it: dark text of the same hue on a light tint (`bg-brand-50 text-brand-800`) keeps the colour and quiets the element.
- On a dark coloured panel, gain contrast for secondary text by shifting toward a lighter-looking neighbouring hue rather than toward white.
- Gradients look best between two hues close to each other on the colour wheel, about 30 degrees apart at most.
- `color-mix(in oklab, …)` and the `--alpha()` function are for compositing a known token over a known surface, not for inventing shades.

## Contrast and accessibility

- WCAG 2.2 AA is the floor: 4.5:1 for normal text, 3:1 for large text, for the visible boundary of controls, and for focus indicators. Measure the rendered colours.
- Never carry meaning in colour alone: add an icon, a text label, a sign or a pattern. In charts, separate series by lightness as well as hue.
- Every interactive element keeps a visible `focus-visible` style that meets 3:1 against its surroundings.
- Respect `motion-reduce` for any movement that is not a direct answer to the user's action.

## Depth

- Assume light from above. A raised element has a lighter top edge and a short dark shadow below; a sunken element (an input, a well, a track) has its shade on the top inner edge. Pick the lighter edge colour from the ramp; translucent white over colour drains it.
  - raised: a project shadow token, or a top edge one step lighter than the surface (`border-t border-brand-400` on `bg-brand-500`);
  - sunken: `inset-shadow-*` with a project token.
- Shadow size means elevation: tight for controls, medium for dropdowns and popovers, large for modals. The higher something sits, the more attention it draws, so elevate only what should.
- Elevation can answer interaction: lift a dragged item; reduce or remove a button's shadow while it is pressed.
- Flat styles still have depth: a surface lighter than its background reads as raised, darker reads as sunken; a short offset shadow with no blur adds depth without breaking flatness.
- Overlap builds layers: a card crossing the boundary between two section backgrounds, a control that overhangs its container. Overlapping avatars or images need a ring in the surface colour so they separate cleanly (`ring-2 ring-(--surface)`, or the surface's own colour token).

## Images and media

- Weak imagery ruins a strong layout. Plan for real, good photography or quality stock; never design around placeholders and hope later images fit.
- Text over an image needs steady contrast. Reduce the image's range under the text with one or two of:
  - an overlay layer (`bg-neutral-950/50` over the image);
  - lower image contrast with compensating brightness (`contrast-75 brightness-110`);
  - a single-colour treatment (`grayscale` image, `mix-blend-multiply` over a brand-coloured layer);
  - a soft glow behind the text with no offset (`text-shadow-*`), with a milder overlay.
- Media looks right near the size it was made for. Keep a small icon near its drawn size inside a larger coloured shape instead of enlarging it; show a detail crop or a simplified drawing instead of a shrunken screenshot whose text is unreadable; give tiny marks (favicons) a redrawn simplified version.
- User-uploaded images: fix their frame so any upload fits, `aspect-square` (or another `aspect-*`) with `object-cover` and a fixed size; separate them from a similar background with a faint inner ring (`inset-ring inset-ring-neutral-950/10`), not a solid border.

## Finishing

Upgrade what exists before adding anything new:

- Bullets become icons specific to the content.
- Quotes get a large, colour-tinted quotation mark as a graphic element.
- Links get custom underlines (`decoration-*`, `underline-offset-*`, `decoration-2`).
- Checkboxes and radios take the brand colour (`accent-*`) or become custom controls.
- Important choices become selectable cards: a `label` wrapping the input, styled with `has-checked:` (border, tint, ring) instead of a bare radio list.
- Entrances of newly shown elements can use `starting:` for a short, purposeful transition.

Use colour accents sparingly: a coloured strip on one element (the active navigation item, an alert's edge, the top of the page) adds character; the same strip on every card is a template cliché.

Break monotony with surfaces rather than ornaments: a surface colour change between sections, a subtle gradient of close hues, a low-contrast pattern on a whole section or one edge, one deliberately placed shape. Keep decoration low-contrast so content stays readable.

Let separation come from the cheapest signal that works: more space first, then two slightly different surface colours, then a shadow when the element sits above its background. A border is the last resort, and a border that coincides with a background change goes.

Question the default form of each component: a menu can have sections, descriptions and icons; a table can merge columns and carry images and badges; a long settings page can become grouped panels.

## States and real content

- **Empty**: when a feature depends on content the user creates, the empty state is the first impression. Give it an image or illustration, one sentence on what the feature does, and the action that fills it, emphasised. Hide filters, tabs and bulk actions that do nothing until content exists.
- **Errors**: place the message where the user is already looking, next to the field or the action; say what happened and how to fix it.
- **Loading**: keep the layout stable with placeholders of the final size.
- **Extremes**: test long names and words (`min-w-0`, `truncate` or `break-words` where appropriate), missing optional fields, very large numbers, many items and a single item.
- **Interaction**: hover, focus-visible, active, disabled and selected, each distinguishable without relying on colour alone.
