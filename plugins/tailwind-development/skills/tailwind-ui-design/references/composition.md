# Composition: rank, actions, data, space and type

The decisions of step 4.1 and 4.2: make the screen read in the right order before any colour, depth or decoration is added. Exact utilities and variants: `tailwind-official-docs`.

## Contents

- Start from the feature
- Rank what matters
- Rank the actions
- Present data by meaning
- Group with space
- Give each element its width
- Adapt to the space available
- Set type for reading

## Start from the feature

- Design the piece of functionality the task is about (the checkout step, the filter panel) before any surrounding shell; the shell follows once several features exist.
- Ship the smallest version that works, then improve it with real content and real states. Never show controls for functionality that does not exist yet.

## Rank what matters

- Decide the first, second and third things on the screen. When everything competes, nothing reads.
- Rank with three levers together: size, weight and colour. Size alone makes primary text too large and secondary text too small; a bold title can stay modest in size, and secondary text gets a softer colour from the neutral ramp rather than a tiny size.
- When the important element does not stand out, quiet what competes with it instead of enlarging it: soften inactive navigation, drop the background of a sidebar fighting the main content, lighten icons beside text.
- Balance weight against contrast: heavy elements (solid icons, bold text) need lower contrast to sit beside regular text; thin elements (a hairline border) gain presence through more width, not a darker colour.
- Semantic level and visual level are separate. Choose `h1` to `h6` for the document outline, then style each heading by its role: a section heading in a settings page often acts like a label and stays small.
- Test the ranking in grayscale: if it only reads with colour, it does not read yet.

## Rank the actions

- One primary action per view, a few secondary ones, some tertiary ones. Style by rank, not by meaning:
  - primary: a solid, high-contrast fill (`bg-brand-600 text-white`);
  - secondary: an outline or low-contrast fill (`inset-ring inset-ring-neutral-300` or `bg-neutral-100`);
  - tertiary: link style, no box (`text-brand-700 hover:underline`).
- A destructive action that is not the view's purpose gets secondary or tertiary styling. The strong danger treatment belongs to the confirmation step, where destroying is the primary action.
- Disabled is not a rank: a disabled primary still looks like the primary, only inactive.

## Present data by meaning

- Avoid label-value pairs by default; they flatten every row to the same weight.
- Let the format identify the value: an email address, a currency amount and a date need no label.
- Fold the label into the value when a phrase reads naturally: "4 seats left", "Ships in 2 days", "Updated 3 hours ago".
- When labels are needed (dense dashboards, scannable lists), make them the quiet part: smaller, softer colour or lighter weight, and the value the strong part.
- Where readers search by the label (a technical specification sheet), reverse it: the label is emphasised and the value slightly softer.
- Tables:
  - right-align numeric columns and use tabular figures, `text-right tabular-nums`, so digits line up;
  - one column can carry several related fields with internal hierarchy (name over role, amount over status) when sorting still works;
  - an image or a coloured status badge in a cell often helps scanning more than another column.

## Group with space

- Start with too much space and remove it. Space added only until a layout stops looking cramped is always too little. Dense layouts are a deliberate choice for expert tools, not the default.
- Proximity is grouping. Space around a group must be clearly larger than space inside it:
  - a label sits closer to its input than to the previous field;
  - a heading sits closer to the content it introduces than to the content above it;
  - items of a list sit further apart than the lines inside one item.
- Express groups with `gap-*` on flex and grid containers, inner gaps smaller than outer ones (`gap-1.5` inside a field, `gap-6` between fields), rather than margins on children.

## Give each element its width

- Do not fill the screen because it is there. A form, a reading column or a card has an ideal width (`max-w-md`, `max-w-prose`); it keeps it on wide screens and shrinks only when the screen is narrower.
- Fixed-width parts stay fixed and the rest flexes: `grid-cols-[16rem_1fr]` for a sidebar layout.
- A narrow element lost in a wide layout gets a companion column (help text beside a form) instead of being stretched.
- Content that needs room gets room; never squeeze it to look compact.
- Design the narrow layout first (about 375 to 400 px), then add what wider screens allow.

## Adapt to the space available

- Sizes do not scale in proportion: large elements shrink more than small ones on small screens. A display headline can halve while body text barely changes. Set each size per breakpoint (`text-3xl lg:text-5xl`) instead of deriving one from another.
- Inside a component the same holds: a large button gets disproportionately more padding than a small one.
- A component placed in columns of different widths (a card in a sidebar and in a main grid) adapts to its container with container queries: `@container` on the parent, `@sm:`, `@lg:` and their kin on the children.

## Set type for reading

- Measure: 45 to 75 characters per line for body text (`max-w-prose` or `max-w-[65ch]`), even inside a wide content area.
- Line height moves opposite to size and with measure: long lines and small text need more, large display text needs less.
- Mixed sizes on one line align on their baseline, `items-baseline`, never on their centres.
- Alignment follows the language: left for left-to-right text. Centre only headings and short blocks of two or three lines; shorten copy rather than centre a long block.
- Justified text needs hyphenation and a correct `lang` (`text-justify hyphens-auto`).
- Letter spacing: trust the typeface; tighten a wide-set face at headline size (`tracking-tight`); add tracking to text set in capitals (`uppercase tracking-wide`). Capitals are for a role that needs them, never a default label style.
- Links: in prose a link must look like one. In an interface where most text is clickable, use quieter cues (weight, a darker colour) and keep underlines for hover or for links inside text.
