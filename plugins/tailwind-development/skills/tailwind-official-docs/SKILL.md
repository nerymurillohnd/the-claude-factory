---
name: tailwind-official-docs
description: Learn from the official Tailwind CSS v4 documentation for knowledge and guidance, and prefer it over training knowledge. Always use it first, before any other skill, when the user asks about Tailwind and when you work on or plan anything Tailwind on your own, from code, integration, setup and migration to front-end design and styles.
license: MIT
---

# Tailwind CSS official documentation

This skill is the contract for Tailwind CSS v4 work.
It routes each task to the official documentation that governs it.
Its references hold the exact page and section routes, grouped by category, each with a short reference of what it covers.
Read the reference that matches the task, then read the linked sections on the live page.
Trust the live page over training knowledge and over this skill.
Check every decision against the Tailwind version the project resolves and its actual configuration.

When the task also designs, builds or generates an interface, also load `tailwind-development:tailwind-ui-design`.

## When to use

- Answer any question about Tailwind CSS.
- Write, edit, review or refactor Tailwind classes, variants or CSS.
- Install, integrate or configure Tailwind in a project.
- Set up an editor, IntelliSense or class sorting for Tailwind.
- Check browser support, preprocessors, CSS modules or component styles.
- Migrate a project from v3 to v4.
- Plan any of the above, even when the user does not name Tailwind.

## When not to use

- The project styles with plain CSS, CSS-in-JS or another framework, and the task does not add Tailwind.
- The task touches no styling, markup classes or Tailwind configuration.

## Custom variants

Use `@custom-variant` when a selector pattern is truly repeated and deserves to become a styling primitive.

Good candidates:

- app theme wrappers
- data-attribute driven states
- repeated container context selectors
- CMS-specific context wrappers (e.g. dark page section, highlighted block)

Do not create custom variants for one-off selector tricks unless the repetition is real.

## Generated DOM and JS-replaced markup

When styling icons or widgets that are transformed by JavaScript, target the rendered DOM, not only the placeholder markup.

Examples:

- icon libraries that replace `<i>` with `<svg>`
- component libraries that inject wrappers
- widgets that rewrite class names or structure

If a shared interaction depends on a specific child element, verify that the final rendered DOM still matches the selector.

This matters a lot for:

- transitions
- hover effects
- focus styles
- icon animation
- nested selectors in component classes

## Responsive strategy

Prefer mobile-first styling:

- define the base case first
- add larger breakpoint changes progressively

Use breakpoint tokens intentionally. In v4, `--breakpoint-*` theme variables define which responsive variants exist.

## Stylesheet structure

For a CSS-first Tailwind v4 setup, this structure is usually sensible:

- entrypoint CSS (`app.css` or `site.css`)
- `theme.css` for tokens
- `base.css` for minimal element defaults
- `utilities.css` for low-level project utilities and variants
- `components.css` for a small stable component API
  - Bigger components, e.g. `rich-text.css` for scoped uncontrolled HTML

## Refactor heuristics

When refactoring an existing Tailwind codebase:

1. Remove dead CSS before adding new CSS.
2. Remove redundant utilities before extracting abstractions.
3. Normalize obvious repeated primitives first.
4. Keep the number of component classes intentionally small.
5. Push page structure back into markup if CSS started owning too much layout.
6. Merge inconsistent implementations of the same affordance.

Watch for these smells:

- several versions of the same button or card
- repeated arbitrary shadows, radii, or spacing
- identical hover interactions implemented in different ways
- state logic split between a shared class and page-specific one-offs
- component classes that are really page fragments in disguise

## Review checklist

Before finalizing a Tailwind change, check:

- Are utilities sufficient here, or did I abstract too early?
- If repetition exists, would extracting markup be better than adding CSS?
- Should repeated values become tokens?
- Are custom utilities truly low-level?
- Are component classes small, stable, and override-friendly?
- Are state and motion rules consistent across similar UI?
- Will Tailwind detect every class I used?
- Are dynamic classes mapped to full strings?
- Is uncontrolled markup scoped instead of styled globally?
- Is the responsive behavior mobile-first and intentional?
- Can any CSS be deleted now?

## Practical defaults

When in doubt:

- keep styling in markup first
- reuse markup before reusing CSS
- use tokens before arbitrary repetition
- use custom utilities before semantic CSS wrappers
- keep component classes few and durable
- keep state behavior inside the shared abstraction if the abstraction exists
- verify that rendered DOM matches your selectors
- prefer deleting complexity over introducing a clever abstraction

## Getting started

### Installation

For any installation task (setup, fix or question), read the matching reference and the page its title links.
Follow the page where they differ.

**Overview**: every install path at a glance → See https://tailwindcss.com/docs/installation
**Vite**: `vite.config.*`, Vite frameworks → See [references/installation/using-vite.md](references/installation/using-vite.md)
**PostCSS**: `postcss.config.*`, Next.js, Angular → See [references/installation/using-postcss.md](references/installation/using-postcss.md)
**Tailwind CLI**: no bundler, standalone executable → See [references/installation/tailwind-cli.md](references/installation/tailwind-cli.md)
**Play CDN**: browser prototypes, no build → See [references/installation/play-cdn.md](references/installation/play-cdn.md)

**Framework guides**: Next.js, Nuxt, SvelteKit, Astro, Laravel and more → See [references/installation/framework-guides.md](references/installation/framework-guides.md)

Read the framework's guide instead of a generic path when it has one.

### Editor setup

For any editor or formatter task (setup, fix or question), read the matching reference and the page its title links.
Follow the page where they differ.

**Syntax support**: warnings on `@theme`, `@apply`, `@source` → See [references/editor-setup/syntax-support.md](references/editor-setup/syntax-support.md)
**VS Code and Cursor**: IntelliSense extension, settings → See [references/editor-setup/vscode-intellisense.md](references/editor-setup/vscode-intellisense.md)
**Prettier**: class sorting → See [references/editor-setup/prettier-class-sorting.md](references/editor-setup/prettier-class-sorting.md)
**Zed**: built-in language server → See [references/editor-setup/zed.md](references/editor-setup/zed.md)
**JetBrains**: WebStorm, PhpStorm → See [references/editor-setup/jetbrains.md](references/editor-setup/jetbrains.md)

### Compatibility

For any compatibility task (setup, fix or question), read the matching reference and the page section its title links.
Follow the page where they differ.

**Browsers**: browser floor, project targets → See [references/compatibility/browser-support.md](references/compatibility/browser-support.md)
**Preprocessors**: Sass, Less, Stylus → See [references/compatibility/preprocessors.md](references/compatibility/preprocessors.md)
**CSS modules**: `@reference`, `@apply` in modules → See [references/compatibility/css-modules.md](references/compatibility/css-modules.md)
**Component styles**: `<style>` in Vue, Svelte, Astro → See [references/compatibility/component-style-blocks.md](references/compatibility/component-style-blocks.md)

### Upgrade guide

To migrate a project, read every reference below in order, with the upgrade-guide sections each one links.
For one v3 habit or a question, read only the matching reference.
Follow the page where they differ.

1. **Upgrade tool**: run it first → See [references/upgrade-guide/upgrade-tool.md](references/upgrade-guide/upgrade-tool.md)
2. **Manual upgrade**: when the tool cannot run → See [references/upgrade-guide/manual-upgrade.md](references/upgrade-guide/manual-upgrade.md)
3. **Utilities**: removed, renamed, defaults → See [references/upgrade-guide/utilities.md](references/upgrade-guide/utilities.md)
4. **Syntax**: directives, prefix, important, variants → See [references/upgrade-guide/syntax.md](references/upgrade-guide/syntax.md)
5. **Preflight**: base style changes → See [references/upgrade-guide/preflight.md](references/upgrade-guide/preflight.md)
6. **Configuration**: JS config, `theme()`, browsers → See [references/upgrade-guide/config.md](references/upgrade-guide/config.md)
7. Report every section with its verdict: changed, not present, kept, or needs a decision.

## Core concepts

For any work, knowledge or guidance on a core concept, read the matching reference.
Then read the linked page sections for your topic.

**Utility classes**: composition, arbitrary values, conflicts, important, prefix → See [references/core-concepts/styling-with-utility-classes.md](references/core-concepts/styling-with-utility-classes.md)
**States**: hover, focus, group, peer, pseudo-elements, ARIA, data, custom variants → See [references/core-concepts/hover-focus-and-other-states.md](references/core-concepts/hover-focus-and-other-states.md)
**Responsive design**: breakpoints, ranges, container queries → See [references/core-concepts/responsive-design.md](references/core-concepts/responsive-design.md)
**Dark mode**: `dark:`, class or data-attribute toggle, system theme → See [references/core-concepts/dark-mode.md](references/core-concepts/dark-mode.md)
**Theme variables**: `@theme`, namespaces, tokens in CSS and JS → See [references/core-concepts/theme.md](references/core-concepts/theme.md)
**Colors**: palette, opacity, custom colors → See [references/core-concepts/colors.md](references/core-concepts/colors.md)
**Custom styles**: arbitrary values, custom CSS, `@utility`, custom variants → See [references/core-concepts/adding-custom-styles.md](references/core-concepts/adding-custom-styles.md)
**Class detection**: dynamic class names, `@source`, safelisting → See [references/core-concepts/detecting-classes-in-source-files.md](references/core-concepts/detecting-classes-in-source-files.md)
**Functions and directives**: `@import`, `@apply`, `@reference`, `--alpha()`, `@config` → See [references/core-concepts/functions-and-directives.md](references/core-concepts/functions-and-directives.md)

## Base styles

Preflight resets, extending or disabling Preflight → See [references/base-styles.md](references/base-styles.md)

## Layout

aspect-ratio, columns, display, float, object-fit, overflow, position, inset, z-index → See [references/layout.md](references/layout.md)

## Flexbox & Grid

flex, grid columns and rows, gap, justify, align, place, order → See [references/flexbox-and-grid.md](references/flexbox-and-grid.md)

## Spacing

padding, margin → See [references/spacing.md](references/spacing.md)

## Sizing

width, height, min and max sizes, logical inline and block sizes → See [references/sizing.md](references/sizing.md)

## Typography

font family, size and weight, line height, text color, decoration, wrapping, lists → See [references/typography.md](references/typography.md)

## Backgrounds

background color, image, gradients, position, size, clip → See [references/backgrounds.md](references/backgrounds.md)

## Borders

border radius, width, color, style, outlines → See [references/borders.md](references/borders.md)

## Effects

box and text shadows, opacity, blend modes, masks → See [references/effects.md](references/effects.md)

## Filters

blur, brightness, contrast, drop shadow, backdrop filters → See [references/filters.md](references/filters.md)

## Tables

border collapse and spacing, table layout, caption side → See [references/tables.md](references/tables.md)

## Transitions & Animation

transition property, duration, easing, delay, animation → See [references/transitions-and-animation.md](references/transitions-and-animation.md)

## Transforms

rotate, scale, skew, translate, perspective, transform origin → See [references/transforms.md](references/transforms.md)

## Interactivity

accent and caret color, cursor, field sizing, pointer events, scrolling, scroll snap, touch, user select → See [references/interactivity.md](references/interactivity.md)

## SVG

fill, stroke, stroke width → See [references/svg.md](references/svg.md)

## Accessibility

forced colors adjustment → See [references/accessibility.md](references/accessibility.md)

## Agents

Delegate to the matching agent when the session can run agents.
Give it the task, the project root and the files involved.

**Documentation**: syntax, behaviour, versions → `tailwind-development:tailwind-docs`
**Audit**: review code or a change → `tailwind-development:tailwind-auditor`
**Refactor**: clean up existing code → `tailwind-development:tailwind-refactorer`
**Migration**: v3 to v4 → `tailwind-development:tailwind-migrator`

## Workflow

Follow these steps yourself when no agent fits or agents cannot run.

1. Read the resolved Tailwind version, not the declared range.
2. Read the integration, the CSS entry, the `@theme` tokens and the project's conventions.
3. Split the task into utilities, conditions, customization and compilation.
4. Read the matching references and their live sections.
5. Read sources as `references/retrieval.md` says → See [references/retrieval.md](references/retrieval.md)
6. Pick between similar pages with the disambiguation list → See [references/disambiguation.md](references/disambiguation.md)
7. Implement with complete, statically detectable classes and existing tokens.
8. Run the project's lint, type-check, tests and build.
9. Check the result in a browser when one is available.

## Completion report

- What changed.
- The resolved Tailwind version, or why it is unresolved.
- The docs section URL behind each decision.
- The checks run and their results.
- What you could not verify.
- Never cite this skill as evidence of Tailwind behaviour.
