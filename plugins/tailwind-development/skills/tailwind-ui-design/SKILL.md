---
name: tailwind-ui-design
description: Designs, builds, refactors and reviews user interfaces in Tailwind CSS v4 with a product designer's craft, starting from a written visual hierarchy and carrying it through design-system tokens in @theme, OKLCH colour ramps, spacing and type scales, elevation, data and action presentation, states and visual verification, so the result never looks like generic generated UI. Use whenever a task builds or redesigns a page, view, component, form, table, dashboard, card or landing section in a Tailwind project, refactors or polishes an existing Tailwind interface, or asks for a design review of one, even when the request only says make it look better.
license: MIT
---

# Tailwind UI design

## What this skill adds

This skill is the craft layer of interface work in Tailwind CSS v4. Its spine is visual hierarchy: before any styling, every element on the screen is ranked for the user's task, and every later choice (size, weight, colour, space, depth, position) encodes that ranking. Around it sit the systems that make choices consistent (tokens), the composition of space, type, colour, depth and media, every state, and a check of the rendered result.

It works with two neighbours and never repeats them:

- **Aesthetic direction** (the subject-grounded identity, typeface choice, the plan-review-build-critique loop, interface writing): the `frontend-design` skill when it is installed, or the project's own brief. This skill executes a direction; it does not invent a house style.
- **Exact Tailwind syntax and behaviour**: the `tailwind-official-docs` skill of this plugin. Whenever a decision needs a class, variant, directive or `@theme` namespace you are not certain of, route there instead of writing it from memory.

Precedence, highest first: the project's rules and design system, the user's brief, the aesthetic direction, then this skill's defaults. The defaults here apply only where the project leaves an axis free.

## Pick the task

| The request | Workflow |
| --- | --- |
| A new component, view, page or section | Build |
| An existing interface that looks flat, cluttered, dated or generic | Refactor |
| "Review", "critique", "what's wrong with this design" | Review |

All three share the steps below; the table after them says what differs.

## 1. Rank every element

Before any styling, and before reading tokens or choosing colours:

- List every element the screen shows: headings, values, actions, navigation, media, helper text, decoration.
- Rank each one for the user's task on this screen:
  - **primary**: exactly one element, the thing the user came for or must do;
  - **secondary**: a few elements that support it;
  - **tertiary**: everything else that must stay;
  - **remove**: what serves no task (redundant labels, decoration, controls for actions that cannot happen yet).
- Rank the actions the same way: one primary action, a few secondary, the rest tertiary.
- Write the ranking down, in your working notes and in the report. It is the brief every later step encodes.

In a refactor, recover the ranking from the flat view first: say what the current design makes primary (often nothing, or everything), then what should be primary, and the gap between the two is the first thing to fix.

The ranking must read in grayscale, with size, weight, colour value, spacing and position alone, before colour, depth and decoration are added. If it only reads with colour, it does not read yet.

## 2. Read the project

- Read the project's instructions and design rules.
- Read the global stylesheet: `@theme` tokens (colours, fonts, `--text-*`, `--spacing`, `--radius-*`, `--shadow-*`), custom utilities and variants, and how dark mode is activated.
- Find brand or design-system sources: a brand guide, a token file, a component library, a design export, existing pages known to be right.
- Read the components nearest to the task: how they compose, which tokens they use, what radius, shadow and spacing habits they have.
- List the appearance modes the project supports (light, dark, high contrast) and its breakpoints and container sizes.
- Note the content the interface must carry, from real data where you can: lengths, missing fields, counts. Real content can change the ranking; update it when it does.

When there is no project (a pasted snippet, an empty folder), say so, work from Tailwind's default theme, and keep the result internally consistent.

What the project defines wins. A token the project already has is used, never re-invented next to it.

## 3. Settle the direction

- If the project has a visual identity, follow it exactly.
- If the brief leaves the identity open, take it from `frontend-design` or the brief, and write down the few choices that carry it: typefaces and their roles, colour family, radius personality, density, tone of copy.
- Refactor and review inherit the existing direction unless the user asks for a new one; say when the direction itself is the problem rather than silently replacing it.

## 4. Check the systems exist

An interface looks designed when its small decisions come from small, fixed sets. Before composing, confirm each system exists, in tokens, and extend it there when it falls short:

- **Type scale**: a hand-picked set of sizes with paired line heights (`--text-*` and `--text-*--line-height`), two weights for interface text, two or three text colours, enough steps to give each rank its own treatment.
- **Spacing subset**: a non-linear subset of the linear `--spacing` multiples that the project actually uses.
- **Colour ramps**: a neutral ramp of 8 to 10 steps, the brand colour and the state colours (danger, warning, success, info), each with 5 to 10 shades, authored in `oklch()`.
- **Elevation**: about five shadow tokens from a raised button to a modal.
- **Radius**: one personality, with sizes chosen by element size, never mixed square and round.

Never add a one-off value (an arbitrary `[13px]`, a hex colour in a class) where a token belongs. If a value is truly needed twice, it becomes a token. How to build each system: [references/systems.md](references/systems.md).

## 5. Compose to encode the ranking

Work in this order, because each layer depends on the one before it, and check each layer against the written ranking:

1. **Structure.** Give the primary element the strongest treatment on the screen and only it; step secondary and tertiary elements down with size, weight and colour value together. Style actions by rank. Present data by meaning, not as label-value pairs.
2. **Space and layout.** Position and space follow rank: the primary element gets the prime position and the most room; groups are tighter inside than between; each element gets the width it needs; components adapt to their container.
3. **Colour.** Spend the strongest colour on the primary element and the primary action; everything else draws from neutrals and soft tints. Measure contrast.
4. **Depth and media.** Elevation follows rank too: only what should draw attention rises. Frame and treat images for legibility.
5. **Finish.** Upgrade what is there before adding anything; question each component's default form; never add decoration to make up for a weak ranking.

### Craft defaults to apply on every build

These recur in almost every interface; apply them without waiting to open a reference, unless the project's own rules say otherwise:

- **Primary element**: the only element with the strongest weight and size on the screen; its peers step down in weight, size or colour value.
- **Actions by rank**: one solid fill for the primary action (`bg-brand-600 text-white`), an outline or soft fill for secondary ones (`inset-ring inset-ring-neutral-300`, `bg-neutral-100`), link style for tertiary ones (`hover:underline`).
- **Grouping by gap**: express groups with `gap-*` on flex and grid containers, never `space-y-*` or margins on children; the gap inside a group is smaller than the gap between groups (`gap-1.5` from a label to its input, `gap-6` between fields).
- **Mixed sizes on one line**: align them on their baseline with `items-baseline`.
- **Numbers in columns**: `text-right tabular-nums`.
- **Secondary text on a coloured surface**: a light shade of the surface's own hue (`text-indigo-200` on `bg-indigo-800`), never `text-white/…` and never grey.
- **Labels**: fold them into the value or drop them when the format speaks for itself; keep them only where readers scan by label, and then quiet them.
- **User images**: a fixed frame with `object-cover`; `aspect-*` when the width is fluid (`aspect-3/2 w-full object-cover`), `size-*` for a fixed-size avatar.
- **Readable measure**: paragraphs capped at `max-w-prose` or `max-w-[65ch]`.

The decisions of 5.1 and 5.2 in full: [references/composition.md](references/composition.md). 5.3 to 5.5: [references/surface-and-finish.md](references/surface-and-finish.md).

For each decision whose Tailwind syntax you are not certain of, use `tailwind-official-docs`, which reads the exact page.

## 6. Cover every state and real content

Design each state, not only the happy one, and keep the ranking true in each:

- Interaction: hover, focus-visible, active, disabled, selected, loading.
- Data: empty (the first impression of a feature that depends on user content), one item, many items, errors placed where the eye already is.
- Content extremes: long names and words, missing optional fields, large numbers, translated strings that run longer.
- Appearance modes and widths: every supported mode, the narrowest and the widest layout. The primary element must still win at every width and in every mode.

## 7. Verify the rendered result

A class list is not a design. When the environment can render:

- Run the project's build, and its lint, type and test checks.
- Take screenshots in each appearance mode, at a narrow width (about 375 px) and a wide one, and look at them: does the primary element win at first glance? A blurred or grayscale look at the screenshot is a quick test.
- Measure the contrast of rendered text and controls against WCAG 2.2 AA: 4.5:1 for normal text, 3:1 for large text and for the boundaries of controls and focus indicators. Measure the colours as rendered, never infer them from token names.
- Check focus visibility by keyboard, reduced motion, and the states and content extremes of step 6.

When nothing can be rendered, say which checks did not run. Never claim a visual result from a successful build.

## 8. Critique before reporting

Read the result against [references/anti-generic-checklist.md](references/anti-generic-checklist.md), starting with its first item: does one element clearly win, or does everything compete equally? Fix every tell the brief did not ask for. Then look once more and remove one thing that does not earn its place.

## The three workflows

| Step | Build | Refactor | Review |
| --- | --- | --- | --- |
| 1. Rank | Write the ranking for the new screen | Recover the current ranking from the flat view, write the intended one and the gap | Recover the ranking; report the gap first |
| 2. Read the project | Full | Full, plus the view's markup and a screenshot of it | Full, plus the view |
| 3. Direction | Settle it | Inherit it; flag it when it is the problem | Inherit it |
| 4. Systems | Create missing tokens | Map stray values to tokens; add missing ones | Report missing systems and stray values |
| 5. Compose | All five layers | Run [references/refactor-audit.md](references/refactor-audit.md) in its order, fix the highest-impact items first, keep behaviour and semantics | Run the audit; change nothing |
| 6. States | Design them all | Add the missing ones | Report the missing ones |
| 7. Verify | Full | Full, with before and after screenshots | Screenshots of the current state when possible |
| 8. Critique | Yes | Yes | The checklist is part of the findings |

A refactor keeps the component's behaviour, accessibility and public interface; a redesign beyond that needs the user's agreement first.

## Report

Keep it proportional to the change:

- The ranking, labelled with the words primary, secondary, tertiary and removed so the user can check it against the result; for a refactor, also the ranking the old view had.
- What changed, or for a review, the findings in priority order with file and line, each with the fix.
- The tokens added or changed, and why the existing ones did not cover the need.
- Verification: what ran and what it showed, including contrast measurements and screenshots taken; what did not run.
- Choices the user may want to revisit: a direction decision, a trade-off between density and space.

## Further reading

The craft in this skill draws on established interface-design practice; for a book-length treatment, see Refactoring UI, https://www.refactoringui.com.
