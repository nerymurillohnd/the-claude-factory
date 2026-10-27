# Refactor audit: what to look for in an existing view

Work through the groups in this order. The early groups change how the whole view reads; the late ones polish it. Fix the highest group with findings first, take a screenshot, then move down. For a review, report findings in the same order, each with file, line and the fix.

Before starting: a screenshot of the current view in each appearance mode at a narrow and a wide width, the project's tokens and rules (SKILL.md step 2), and the ranking recovered from the flat view (SKILL.md step 1). Keep behaviour, semantics, accessibility and the component's public interface unchanged.

## 1. Ranking

- [ ] Does one element clearly win? Name it. If nothing wins, or several elements compete at the same weight, choose the primary from the user's task, write the ranking (primary, secondary, tertiary, remove), and quiet everything that competes with the primary.
- [ ] Does each later choice (size, weight, colour, space, depth, position) follow that ranking, or does a secondary element get a stronger treatment than the primary?
- [ ] Does the ranking hold in grayscale?
- [ ] Is emphasis made by size alone (huge titles, tiny secondary text)? Rebalance with weight and colour.
- [ ] Is there exactly one primary action, styled as one? Secondary and tertiary actions styled by rank? A destructive action styled as primary where it is not the view's goal?
- [ ] Label-value walls: labels that the format or context makes redundant, labels as loud as values, labels that could fold into the value.
- [ ] Headings styled by their `h` level instead of their role.

## 2. Space and grouping

- [ ] Is the space inside each group clearly smaller than the space between groups? Labels equidistant between fields, headings floating midway between sections?
- [ ] Is the layout cramped because space was added only until it stopped looking bad?
- [ ] Are elements stretched to the full width without need (forms, paragraphs, cards)?
- [ ] Margins on children where `gap-*` on the container would express the group?
- [ ] At a narrow width, do large elements shrink more than small ones, and do components placed in narrow columns adapt (container queries)?

## 3. Systems and stray values

- [ ] Arbitrary values (`p-[13px]`, `text-[#3b5bdb]`, `shadow-[…]`) where a token exists or should exist.
- [ ] Spacing values off the project's subset; font sizes off the type scale; more than two or three text colours; weights under 400 on small text.
- [ ] Shades generated in place (opacity or mix tricks) instead of ramp steps.
- [ ] One radius on everything, or square and round corners mixed.
- [ ] Shadows chosen by taste instead of by elevation.

## 4. Colour and contrast

- [ ] Rendered contrast below WCAG 2.2 AA for text, control boundaries or focus indicators.
- [ ] Grey or white-with-opacity text on coloured surfaces or images.
- [ ] Very dark fills forced by white text where a light tint with dark text would be quieter.
- [ ] Meaning carried by colour alone.
- [ ] Pure black, or an untinted grey ramp that clashes with a warm or cool brand.

## 5. Depth, borders and media

- [ ] Borders doing work that space, a surface change or a shadow would do better; borders doubled with a background change.
- [ ] Elevation that does not match the element's role (a modal-sized shadow on a card, every card floating).
- [ ] User images without a fixed `aspect-*` frame and `object-cover`; images bleeding into a similar background.
- [ ] Text over images without a range-reducing treatment.
- [ ] Icons enlarged far beyond their drawn size; screenshots shrunk until unreadable.

## 6. States and content

- [ ] Missing empty, loading or error states; filters and bulk actions shown when there is nothing to act on.
- [ ] Long names, long words and missing optional fields that break the layout.
- [ ] Missing or invisible `focus-visible` styles; hover-only affordances; motion that ignores `motion-reduce`.

## 7. Finish and distinctiveness

- [ ] Default forms nobody questioned: plain radio lists for important choices, bare bullets, browser-default checkboxes in a branded interface.
- [ ] Every tell in [anti-generic-checklist.md](anti-generic-checklist.md) that the brief did not ask for.
