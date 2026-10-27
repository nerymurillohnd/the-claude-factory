# Systems: the tokens a design is made from

Build these before composing, or extend them when a task needs a value they lack. In Tailwind v4 a token in `@theme` both stores the value and creates the utilities that use it, so a system expressed as tokens is enforced by which classes exist. Check exact namespaces and syntax with `tailwind-development:tailwind-official-docs` (`theme`, `colors`, `font-size`, `box-shadow`, `border-radius`).

## Contents

- How to choose any value
- Type scale
- Spacing subset
- Colour ramps
- Neutrals
- Elevation
- Radius and personality

## How to choose any value

- Choose from a small set, never from a continuous range. Put a first guess on the scale, look at the step on each side, keep the one that is clearly best.
- Adjacent steps must differ enough to make that comparison easy: about 25% or more apart, closer together at the small end of a scale and further apart at the large end.
- Use absolute units (rem) for sizes. Sizes that multiply through nesting (em chains) drift off the scale.
- Decide once. When the same small question comes up again, the token answers it.

## Type scale

- Pick sizes by hand for the interface's real roles (caption, body, emphasised body, section title, page title, display), rather than from a mathematical ratio, which yields fractional pixels and too few useful small sizes.
- In v4 each size is a `--text-*` token, with its line height paired as `--text-*--line-height`. Pair tight line heights with large sizes and looser ones with small sizes: display text near 1 to 1.25, body text near 1.5, small text and long lines up to about 1.75.
- Two weights carry most interface text: regular, and semibold or bold for emphasis. Weights under 400 belong to large display text only.
- Two or three text colours (primary, secondary, tertiary), taken from the neutral ramp.
- Typeface quality: prefer families with many weights and styles. For small text choose faces with a tall x-height and open spacing; keep condensed, short-x-height faces for display use. The typeface choice itself belongs to the aesthetic direction.

```css
@theme {
  --font-sans: "Your Text Face", ui-sans-serif, system-ui, sans-serif;
  --text-sm: 0.875rem;
  --text-sm--line-height: 1.5;
  --text-display: 3.5rem;
  --text-display--line-height: 1.05;
}
```

## Spacing subset

- v4 spacing is linear: every spacing utility is a multiple of `--spacing` (`p-4` is 4 × `--spacing`). Linear values give too many near-identical choices.
- Choose a non-linear subset and stay on it, for example 1, 2, 3, 4, 6, 8, 12, 16, 24, 32. Record it in the project's rules, or restrict it with tokens when the project wants enforcement.
- Large containers get disproportionately more padding than small ones; never derive padding from font size.

## Colour ramps

Author colours in `oklch()`, as v4's default palette is. OKLCH is perceptually uniform: equal lightness steps look equally light across hues, so ramps of different hues line up without manual correction.

Build each ramp once, then freeze it:

1. **Base**: the shade that works as a solid button fill with white or near-white text at AA contrast. Make it the 500 or 600 step.
2. **Ends**: the darkest shade, dark enough for text on the lightest tints; the lightest shade, light enough for a tinted background behind dark text. A success or warning banner is a good test.
3. **Middle**: fill 900, 500 and 100 first, then 700 and 300, then the rest, comparing each step with its neighbours on screen.
4. **Chroma toward the ends**: as lightness approaches white or black, colours lose colourfulness. Raise chroma at the light and dark ends so they still read as the hue.
5. **Hue drift**: hues differ in how light they look. To make a shade lighter or darker without dulling it, shift the hue a little (no more than 20 to 30 degrees) toward a lighter-looking or darker-looking neighbour instead of only changing lightness. A green ramp can lean toward teal in its darks, a yellow ramp toward amber.
6. **Freeze**: never generate shades on the fly with mix or lighten functions in components. Ad hoc shades multiply into dozens of near-duplicates. `color-mix()` and the `--alpha()` function serve one-off compositing, never as a second palette.

A real interface needs far more than a handful of colours: most of it is neutral, plus one or two brand hues and the state hues, each with its shades. A complex product may need ten hues.

```css
@theme {
  --color-brand-50: oklch(0.97 0.02 265);
  --color-brand-600: oklch(0.52 0.19 265);
  --color-brand-950: oklch(0.25 0.09 268);
}
```

## Neutrals

- 8 to 10 steps, carrying most of the interface: text, surfaces, borders, dividers.
- Give neutrals a temperature with a small, consistent chroma: a cool tint toward blue, a warm tint toward yellow or orange. Raise that chroma slightly at the ends of the ramp, as with colour ramps.
- The darkest neutral is a very dark tinted shade, not pure black.

## Elevation

- About five shadow tokens, from smallest to largest: a raised control, a card that sits slightly above the page, a dropdown or popover, a floating panel, a modal. Choose a shadow by the element's elevation, never by taste.
- A convincing shadow is often two layers: a larger soft offset layer and a small tight dark layer close to the edge. As elevation grows, the tight layer fades out.
- Keep shadows small and fairly sharp in interface work; realism is not the goal.

```css
@theme {
  --shadow-raised: 0 1px 2px oklch(0.2 0.02 265 / 0.12), 0 1px 1px oklch(0.2 0.02 265 / 0.08);
  --shadow-overlay: 0 12px 32px -8px oklch(0.2 0.02 265 / 0.22), 0 2px 6px oklch(0.2 0.02 265 / 0.08);
}
```

## Radius and personality

- Radius is part of the personality: none reads formal, small reads neutral, large reads playful.
- Choose radius by element size within that personality: a small control takes a smaller radius than a large panel of the same style.
- Never mix square and rounded corners in one interface, and never put one radius on everything regardless of size and role.
- The other personality carriers sit beside it: the typefaces, the colour family and the tone of the words. Keep each consistent across the interface.
- Colour associations help explain why a hue suits the subject and audience: cool blues tend to read as dependable, deep earthy or metallic warm tones as premium, saturated pinks and oranges as light-hearted, deep greens as natural or financial. Use them as a reasoning aid, never as a psychology chart to obey; the brand and the eye decide.
