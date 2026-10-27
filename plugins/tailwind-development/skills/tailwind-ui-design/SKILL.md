---
name: tailwind-ui-design
description: Designs, builds, refactors and reviews user interfaces in Tailwind CSS v4 with a product designer's craft, such as hierarchy, design-system tokens in @theme, OKLCH colour ramps, spacing and type scales, elevation, data and action presentation, states and visual verification, so the result never looks like generic generated UI. Use whenever a task builds or redesigns a page, view, component, form, table, dashboard, card or landing section in a Tailwind project, refactors or polishes an existing Tailwind interface, or asks for a design review of one, even when the request only says make it look better.
license: MIT
---

# Tailwind UI design

## What this skill adds

This skill is the craft layer of interface work in Tailwind CSS v4: how to rank what matters, build and extend a design system in tokens, compose space, type, colour, depth and media, cover every state, and check the rendered result. It works with two neighbours and never repeats them:

- **Aesthetic direction** (the subject-grounded identity, typeface choice, the plan-review-build-critique loop, interface writing): the `frontend-design` skill when it is installed, or the project's own brief. This skill executes a direction; it does not invent a house style.
- **Exact Tailwind syntax and behaviour**: the `tailwind-official-docs` skill of this plugin. Whenever a decision needs a class, variant, directive or `@theme` namespace you are not certain of, route there instead of writing it from memory.

Precedence, highest first: the project's rules and design system, the user's brief, the aesthetic direction, then this skill's defaults. The defaults here apply only where the project leaves an axis free.

## Pick the task

| The request | Workflow |
| --- | --- |
| A new component, view, page or section | Build |
| An existing interface that looks flat, cluttered, dated or generic | Refactor |
| "Review", "critique", "what's wrong with this design" | Review |

All three share the steps below; the table at the end of each step says what differs.

## 1. Read the project first

Before any design decision:

- Read the project's instructions and design rules.
- Read the global stylesheet: `@theme` tokens (colours, fonts, `--text-*`, `--spacing`, `--radius-*`, `--shadow-*`), custom utilities and variants, and how dark mode is activated.
- Find brand or design-system sources: a brand guide, a token file, a component library, a Figma export, existing pages that are known to be right.
- Read the components nearest to the task: how they compose, which tokens they use, what radius, shadow and spacing habits they have.
- List the appearance modes the project supports (light, dark, high contrast) and the breakpoints and container sizes it uses.
- Note the content the interface must carry, from real data where you can get it: lengths, missing fields, counts.

When there is no project (a pasted snippet, an empty folder), say so, work from Tailwind's default theme, and keep the result internally consistent.

What the project defines wins. A token the project already has is used, never re-invented next to it.

## 2. Settle the direction

- If the project has a visual identity, follow it exactly.
- If the brief leaves the identity open, take it from `frontend-design` or the brief, and write down the few choices that carry it: typefaces and their roles, colour family, radius personality, density, tone of copy.
- Refactor and review inherit the existing direction unless the user asks for a new one; say when the direction itself is the problem rather than silently replacing it.

## 3. Check the systems exist

An interface looks designed when its small decisions come from small, fixed sets. Before composing, confirm each system exists, in tokens, and extend it there when it falls short:

- **Type scale**: a hand-picked set of sizes with paired line heights (`--text-*` and `--text-*--line-height`), two weights for interface text, two or three text colours.
- **Spacing subset**: a non-linear subset of the linear `--spacing` multiples that the project actually uses.
- **Colour ramps**: a neutral ramp of 8 to 10 steps, the brand colour and the state colours (danger, warning, success, info), each with 5 to 10 shades, authored in `oklch()`.
- **Elevation**: about five shadow tokens from a raised button to a modal.
- **Radius**: one personality, with sizes chosen by element size, never mixed square and round.

Never add a one-off value (an arbitrary `[13px]`, a hex colour in a class) where a token belongs. If a value is truly needed twice, it becomes a token. How to build each system: [references/systems.md](references/systems.md).

## 4. Compose in layers

Work in this order, because each layer depends on the one before it:

1. **Rank and structure.** Decide what is first, second and third on the screen, and make that read with size, weight, colour, spacing and position alone, as if the screen were grayscale. Rank actions as primary, secondary and tertiary. Present data by meaning, not as label-value pairs.
2. **Space and layout.** Group by proximity (tighter inside a group than between groups), give each element the width it needs, adapt to the container as well as the viewport.
3. **Colour.** Apply colour to support the ranking already built, from the ramps, with measured contrast.
4. **Depth and media.** Elevation by meaning, images framed and treated for legibility.
5. **Finish.** Upgrade what is there before adding anything; question each component's default form.

The decisions of steps 1 and 2: [references/composition.md](references/composition.md). Steps 3 to 5: [references/surface-and-finish.md](references/surface-and-finish.md).

For each decision whose Tailwind syntax you are not certain of, use `tailwind-official-docs`, which reads the exact page.

## 5. Cover every state and real content

Design each state, not only the happy one:

- Interaction: hover, focus-visible, active, disabled, selected, loading.
- Data: empty (the first impression of a feature that depends on user content), one item, many items, errors placed where the eye already is.
- Content extremes: long names and words, missing optional fields, large numbers, translated strings that run longer.
- Appearance modes and widths: every supported mode, the narrowest and the widest layout.

## 6. Verify the rendered result

A class list is not a design. When the environment can render:

- Run the project's build, and its lint, type and test checks.
- Take screenshots in each appearance mode, at a narrow width (about 375 px) and a wide one, and look at them.
- Measure the contrast of rendered text and controls against WCAG 2.2 AA: 4.5:1 for normal text, 3:1 for large text and for the boundaries of controls and focus indicators. Measure the colours as rendered, never infer them from token names.
- Check focus visibility by keyboard, reduced motion, and the states and content extremes of step 5.

When nothing can be rendered, say which checks did not run. Never claim a visual result from a successful build.

## 7. Critique before reporting

Read the result against [references/anti-generic-checklist.md](references/anti-generic-checklist.md) and fix every tell that the brief did not ask for. Then look once more and remove one thing that does not earn its place.

## The three workflows

| Step | Build | Refactor | Review |
| --- | --- | --- | --- |
| 1. Read the project | Full | Full, plus the view's current markup and a screenshot of it | Full, plus the view |
| 2. Direction | Settle it | Inherit it; flag it when it is the problem | Inherit it |
| 3. Systems | Create missing tokens | Map stray values to tokens; add missing ones | Report missing systems and stray values |
| 4. Compose | All five layers | Run [references/refactor-audit.md](references/refactor-audit.md) in its order, fix the highest-impact items first, keep behaviour and semantics | Run the audit; change nothing |
| 5. States | Design them all | Add the missing ones | Report the missing ones |
| 6. Verify | Full | Full, with before and after screenshots | Screenshots of the current state when possible |
| 7. Critique | Yes | Yes | The checklist is part of the findings |

A refactor keeps the component's behaviour, accessibility and public interface; a redesign beyond that needs the user's agreement first.

## Report

Keep it proportional to the change:

- What changed, or for a review, the findings in priority order with file and line, each with the fix.
- The tokens added or changed, and why the existing ones did not cover the need.
- Verification: what ran and what it showed, including contrast measurements and screenshots taken; what did not run.
- Choices the user may want to revisit: a direction decision, a trade-off between density and space.

## Further reading

The craft in this skill draws on established interface-design practice; for a book-length treatment, see Refactoring UI, https://www.refactoringui.com.
