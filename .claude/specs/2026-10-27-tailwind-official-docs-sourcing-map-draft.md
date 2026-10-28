# tailwind-official-docs sourcing map (draft)

Status: draft input for the phase 3 spec of tailwind-development. Not approved, not built. Written 2026-10-27 from the live pages of https://tailwindcss.com/docs (Tailwind CSS v4.3).

## Why it exists

The skill routes a task to the right page but leaves to Claude which sections of a long page to read, what to look for in the project and when it has read enough. A v3 to v4 migration in a user project read two tables of `upgrade-guide` and skipped the rest. This map closes that gap: for every section of every long page it says when to read it, what to check in the project, and which other pages it hands off to.

## Inventory (measured 2026-10-27)

| Kind | Pages | Sections (h2 to h4) | Rule |
| --- | --- | --- | --- |
| Long pages (core concepts, `preflight`, `upgrade-guide`, `compatibility`, `editor-setup`) | 13 | 287 | This map, one row per section or section group |
| Property pages | 184 | 1,055 | The property-page rule below |
| Installation pages (Getting Started, `installation/*`, 19 framework guides) | 25 | 0 | Read whole: they are numbered steps without h2 to h4 headings |
| **Total** | **222** | **1,342** | 1,564 URLs |

The visible "On this page" list of each page shows h2 and h3 only. The map always works from the h2 to h4 headings of the HTML: the h4 sections hold facts the list hides (the shifted shadow, radius and blur scales, `#why-theme-instead-of-root`, the 37 entries of `#pseudo-class-reference`).

## Columns

- **Read when**: the task or the signal in the request or the project that makes the section required.
- **Check in the project**: what to search for, so the section gets a verdict from evidence ("not present" names the search that found nothing).
- **Hands off to**: pages or sections to read next. Links the page itself makes are marked (page); the rest are written here because the docs do not cross-link them.

## Coverage rules

1. A task the whole page governs reads every section, one at a time, and gives each one a verdict: a v3 to v4 migration (`upgrade-guide`), adopting v4 (`compatibility`), replacing the theme (`theme`, `colors`), changing the dark-mode mechanism (`dark-mode`).
2. Any other task reads the rows its signals match, plus their hand-offs.
3. A section no row assigns does not exist in this map: the maintainer check fails.

## Property-page rule (184 pages)

Each property page has the same structure: a quick-reference table (no anchor), `#examples` (184 of 184), `#responsive-design` (178), `#using-a-custom-value` (107), `#customizing-your-theme` (47), and page-specific example sections.

- Always read the quick-reference table and the example section that matches the intent (a single side, inset, ring, subgrid, logical properties, negative values, percentage).
- Add `#using-a-custom-value` when the value is outside the theme; then `adding-custom-styles#using-arbitrary-values`.
- Add `#customizing-your-theme` (and its `#customizing-*` sub-sections) when a token is added or changed; then the namespace row of `theme#theme-variable-namespaces`.
- Add `#responsive-design` or `#applying-on-hover` only for the first use of variants in the task.

## Long pages

### `styling-with-utility-classes` (21)

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#overview`, `#why-not-just-use-inline-styles` | Adopting Tailwind; "why not inline styles" | Static values in `style=` | `hover-focus-and-other-states`, `responsive-design`, `theme` (page) |
| `#thinking-in-utility-classes`, `#styling-hover-and-focus-states` | First use of state variants | Hand-written `:hover`/`:focus` rules | `hover-focus-and-other-states` (page) |
| `#media-queries-and-breakpoints` | First use of breakpoints | Hand-written `@media` | `responsive-design` (page) |
| `#targeting-dark-mode` | First use of `dark:` | The project's dark-mode mechanism | `dark-mode` (page) |
| `#using-class-composition` | Several classes building one property (filters, gradients, shadows, transforms) | `filter:`/`transform:` in custom CSS | `background-image#adding-a-linear-gradient`, `box-shadow#setting-the-shadow-color`, `translate` (page) |
| `#using-arbitrary-values`, `#how-does-this-even-work` | A value outside the theme; classes that generate no CSS | Repeated `-[…]` values that should be tokens; interpolated class names | `adding-custom-styles#using-arbitrary-values`, `theme`, `detecting-classes-in-source-files` (page) |
| `#complex-selectors` | Several conditions on one class; child selectors | Nested selectors in custom CSS | `adding-custom-styles#arbitrary-variants`, `hover-focus-and-other-states#styling-based-on-parent-state` (page) |
| `#when-to-use-inline-styles` | Values from a database or API | Dynamic versus static `style=` values | `theme#with-arbitrary-values` |
| `#managing-duplication`, `#using-loops`, `#using-multi-cursor-editing`, `#using-components`, `#using-custom-css` | Repeated class lists; the urge to use `@apply` | Identical class lists across files; `@apply` in `@layer components` | `theme#with-custom-css` (page), `adding-custom-styles#adding-component-classes` |
| `#managing-style-conflicts`, `#conflicting-utility-classes` | "The last class doesn't win"; conditional classes | Conflicting pairs (`flex grid`, `p-2 p-4`) | The plugin's `check_file` diagnostics |
| `#using-the-important-modifier` | A utility that loses on specificity | `!` prefix (v3) versus suffix (v4) | `upgrade-guide#the-important-modifier` |
| `#using-the-important-flag` | Tailwind beside high-specificity legacy CSS | `@import "tailwindcss" important` | `functions-and-directives#import-directive` |
| `#using-the-prefix-option` | Class-name collisions with other CSS | `prefix(…)` on the import; `tw-` (v3) versus `tw:` (v4) | `upgrade-guide#using-a-prefix` |

### `hover-focus-and-other-states` (88)

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#pseudo-classes`, `#hover-focus-and-active` | Interactive states, visible focus | Hand-written `:hover`/`:focus`; `focus:` where `focus-visible:` fits | `upgrade-guide#hover-styles-on-mobile`, `outline-*` pages |
| `#first-last-odd-and-even`, `#required-and-disabled` | Lists, tables, forms | Classes set by index in JavaScript | The variant's entry in `#pseudo-class-reference` |
| `#has`, `#not` | Styling by content, negation | JavaScript that adds classes from children or state | `#styling-based-on-the-descendants-of-a-group`, `#styling-based-on-the-descendants-of-a-peer` |
| `#styling-based-on-parent-state` with `#styling-based-on-the-descendants-of-a-group`, `#differentiating-nested-groups`, `#arbitrary-groups`, `#implicit-groups` | A parent's state styles a child | Parent state passed down by JavaScript; nested unnamed `group`s | `adding-custom-styles#using-arbitrary-values` (page) |
| `#styling-based-on-sibling-state` with `#styling-based-on-the-descendants-of-a-peer`, `#differentiating-peers`, `#arbitrary-peers` | Validation or a checkbox styles a sibling | DOM order: `peer` must come first | `adding-custom-styles#using-arbitrary-values` (page) |
| `#pseudo-elements`, `#before-and-after` | Decoration without extra elements | `::before` in custom CSS | `content` |
| `#placeholder`, `#file`, `#marker`, `#selection`, `#first-line-and-first-letter`, `#backdrop` | Native pseudo-elements | Custom CSS for `::placeholder`, `::file-selector-button`, `::marker`, `::backdrop` | `upgrade-guide#new-default-placeholder-color`; `#openclosed-state` for dialogs |
| `#media-and-feature-queries`, `#responsive-breakpoints` | Breakpoints as variants | Hand-written `@media` | `responsive-design` (page) |
| `#prefers-color-scheme` | Dark mode | The project's dark-mode mechanism | `dark-mode` (page), `color-scheme` |
| `#prefers-reduced-motion`, `#prefers-contrast`, `#forced-colors`, `#inverted-colors` | Accessibility, motion | Animations without `motion-safe:`/`motion-reduce:` | `forced-color-adjust` (page), `animation`, `transition-property` |
| `#pointer-and-any-pointer`, `#orientation`, `#scripting`, `#print`, `#supports` | Input device, environment, print | Breakpoints used to detect touch; hand-written `@media (pointer)`, `@media print`, `@supports`, `<noscript>` | A version question for recent variants |
| `#starting-style` | Entry animations of dialogs and popovers | JavaScript that adds classes after mount | `transition-behavior`, `#openclosed-state` |
| `#attribute-selectors`, `#aria-states`, `#data-attributes` | ARIA or headless-library components | `aria-*`/`data-*` in markup; state classes set from JavaScript | `theme` (custom `--aria-*`), the headless library's docs |
| `#rtl-support` | Multilingual or right-to-left sites | `dir="rtl"`; `ml-`/`pl-` where `ms-`/`ps-` fit | `margin`, `padding`, `top-right-bottom-left` (logical properties) |
| `#openclosed-state` | `<details>`, `<dialog>`, `popover` | JavaScript that toggles open classes | `#starting-style`, `#backdrop` |
| `#styling-inert-elements` | Content disabled behind a modal | `inert` in markup | — |
| `#child-selectors`, `#styling-direct-children`, `#styling-all-descendants` | Children you don't control (CMS content) | `> *` selectors in custom CSS | `styling-with-utility-classes#using-components` |
| `#custom-variants`, `#using-arbitrary-variants` | A selector Tailwind has no variant for | Complex selectors in custom CSS | `adding-custom-styles#using-arbitrary-values` (page) |
| `#registering-a-custom-variant` | A repeated custom variant; class-based dark mode | `@custom-variant` in the CSS | `adding-custom-styles#adding-custom-variants` (page), `functions-and-directives#custom-variant-directive`, `dark-mode` |
| `#appendix`, `#quick-reference`, `#pseudo-class-reference` | "Does variant X exist, which selector does it generate" | The installed version | The entry of each variant the task uses, below, with the h3 that explains it |
| `#hover`, `#focus`, `#focus-within`, `#focus-visible`, `#active`, `#visited`, `#target`, `#first-child`, `#last-child`, `#only-child`, `#nth-childodd`, `#nth-childeven`, `#first-of-type`, `#last-of-type`, `#only-of-type`, `#nth-child`, `#nth-last-child`, `#nth-of-type`, `#nth-last-of-type`, `#empty`, `#disabled`, `#enabled`, `#checked`, `#indeterminate`, `#default`, `#optional`, `#required`, `#valid`, `#invalid`, `#user-valid`, `#user-invalid`, `#in-range`, `#out-of-range`, `#placeholder-shown`, `#details-content`, `#autofill`, `#read-only` | The task uses that variant | The installed version, for recent variants | The h3 that explains its group |

### `responsive-design` (20)

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#overview` | Any responsive work | The viewport meta tag in the document head | — |
| `#working-mobile-first`, `#targeting-mobile-screens` | Styles meant for small screens | `sm:` used to mean "on mobile" | — |
| `#targeting-a-breakpoint-range`, `#targeting-a-single-breakpoint` | A style for one range only | Overrides that undo a style at the next breakpoint | `max-*` variants |
| `#using-custom-breakpoints`, `#customizing-your-theme`, `#removing-default-breakpoints` | A project breakpoint | `--breakpoint-*` in `@theme`; v3 `screens` in the JavaScript config | `theme` (page), `theme#relationship-to-variants` |
| `#using-arbitrary-values` | A one-off breakpoint | Repeated `min-[…]`/`max-[…]` that should be tokens | `adding-custom-styles#using-arbitrary-values` (page) |
| `#container-queries`, `#what-are-container-queries`, `#basic-example` | A component placed in columns of different widths | Viewport breakpoints on reusable components; the `@tailwindcss/container-queries` plugin (built in since v4) | `upgrade-guide` (plugin removal) |
| `#max-width-container-queries`, `#container-query-ranges`, `#named-containers`, `#using-size-containers` | Container ranges, nested containers, height-based units | Nested `@container` without names | — |
| `#using-custom-container-sizes`, `#using-arbitrary-container-query-values`, `#container-size-reference` | Container sizes outside the defaults | `--container-*` in `@theme` | `theme` (page), `max-width` (the same namespace sizes `max-w-*`) |
| `#using-container-query-units` | Sizes relative to the container | `cqw`/`cqi` values | `adding-custom-styles#using-arbitrary-values` |

### `dark-mode` (4)

Read the whole page for any dark-mode setup or change: it has four sections.

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#overview` | Dark mode by system preference (the default) | `dark:` classes with no `@custom-variant dark` | `hover-focus-and-other-states#prefers-color-scheme`, `color-scheme` |
| `#toggling-dark-mode-manually`, `#using-a-data-attribute` | A user toggle | v3 `darkMode: 'class'` or `'selector'` in the JavaScript config; `.dark` or `data-theme` on `<html>` | `functions-and-directives#custom-variant-directive`, `upgrade-guide#using-a-javascript-config-file` |
| `#with-system-theme-support` | A three-way toggle (light, dark, system) | `localStorage` theme scripts; a flash of the wrong theme on load | `theme#referencing-other-variables` and `colors#referencing-other-variables` for semantic tokens |

### `theme` (20)

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#overview`, `#what-are-theme-variables`, `#why-theme-instead-of-root` | Creating or reviewing tokens | Tokens in `:root` that should be in `@theme`; `@theme` nested under a selector or `@media` | `functions-and-directives#theme-directive` |
| `#relationship-to-utility-classes`, `#relationship-to-variants` | "Why doesn't class X exist"; a custom breakpoint or container size | Classes that use an undefined token | `responsive-design` |
| `#theme-variable-namespaces` | Naming a new token | Token prefixes that are no namespace and generate nothing | Namespace to page: `--color-*` `colors`; `--font-*` `font-family`; `--text-*` `font-size`; `--font-weight-*` `font-weight`; `--tracking-*` `letter-spacing`; `--leading-*` `line-height`; `--tab-size-*` `tab-size`; `--breakpoint-*` `responsive-design`; `--container-*` `responsive-design#container-queries`, `max-width`; `--spacing` `padding`, `margin`, `width`, `height`, `gap`; `--radius-*` `border-radius`; `--shadow-*` and `--inset-shadow-*` `box-shadow`; `--drop-shadow-*` `filter-drop-shadow`; `--blur-*` `filter-blur`, `backdrop-filter-blur`; `--perspective-*` `perspective`; `--zoom-*` `zoom`; `--aspect-*` `aspect-ratio`; `--ease-*` `transition-timing-function`; `--animate-*` `animation` |
| `#default-theme-variables`, `#default-theme-variable-reference` | Before adding a token | Project tokens that duplicate a default | `colors#default-color-palette-reference` |
| `#customizing-your-theme`, `#extending-the-default-theme` | Adding a token | Repeated arbitrary values that should be tokens | `styling-with-utility-classes#using-arbitrary-values` |
| `#overriding-the-default-theme`, `#using-a-custom-theme` | Changing a default or closing the system (`--*: initial`) | Partial overrides that let default colors leak; default classes that would disappear | `colors#disabling-default-colors` |
| `#defining-animation-keyframes` | Custom animations | `@keyframes` outside `@theme` | `animation` |
| `#referencing-other-variables` | A token that points at another variable (fonts, semantic colors that switch in dark mode) | `var(--…)` inside `@theme` without `inline` | `dark-mode`, `colors#referencing-other-variables` |
| `#generating-all-css-variables` | Variables read by JavaScript or external CSS but unused by classes | Variables missing from the production CSS | `#referencing-in-javascript` |
| `#sharing-across-projects` | Monorepos, shared design systems | Tokens copied by hand between packages | `detecting-classes-in-source-files#explicitly-registering-sources` |
| `#using-your-theme-variables`, `#with-custom-css` | Custom CSS that needs tokens | Literal values in custom CSS instead of `var(--…)` | `adding-custom-styles`, `functions-and-directives#theme-function` |
| `#with-arbitrary-values` | `calc()` with tokens | `[var(--x)]` where the `(--x)` shorthand fits | `upgrade-guide#variables-in-arbitrary-values` |
| `#referencing-in-javascript` | Tokens in JavaScript (animation, charts) | `resolveConfig` or `tailwind.config` imports (v3) | `upgrade-guide#theme-values-in-javascript` |

### `colors` (11)

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#working-with-colors`, `#using-color-utilities` | Choosing the property a color applies to | Color set on the wrong property (text versus decoration versus ring) | Each color property page (page): `text-color` (redirects to `color`), `background-color`, `border-color`, `outline-color`, `text-decoration-color`, `box-shadow#setting-the-*-color`, `accent-color`, `caret-color`, `fill`, `stroke`, `scrollbar-color` |
| `#adjusting-opacity` | Translucent colors | `bg-opacity-*` and the other v3 opacity utilities | `upgrade-guide#removed-deprecated-utilities` |
| `#targeting-dark-mode` | Colors per mode | Duplicated `dark:` colors that a semantic token would replace | `dark-mode` (page) |
| `#referencing-in-css` | Colors in custom CSS | Hex values in custom CSS that exist as tokens | `theme#with-custom-css` |
| `#customizing-your-colors`, `#overriding-default-colors` | Brand colors | Colors outside `--color-*`; HSL or hex where the palette is OKLCH | `theme` (page) |
| `#disabling-default-colors`, `#using-a-custom-palette` | A closed palette | Default colors still used after `--color-*: initial` | `theme#using-a-custom-theme` |
| `#referencing-other-variables` | Semantic colors that change with the theme | `:root`/`[data-theme]` variables mapped without `@theme inline` | `theme#referencing-other-variables` (page), `dark-mode#using-a-data-attribute` |
| `#default-color-palette-reference` | "Which shade exists" | The installed version (4.2 added palettes) | A version question |

### `adding-custom-styles` (24)

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#customizing-your-theme` | Changing tokens | — | `theme` (page) |
| `#using-arbitrary-values`, `#handling-whitespace`, `#resolving-ambiguities` | A one-off value; a value with spaces; `text-[…]` that could be size or color | `[var(--x)]` versus `(--x)`; spaces in brackets; ambiguous `text-[var(--x)]` without a type hint | The property page's `#using-a-custom-value` |
| `#arbitrary-properties` | A CSS property Tailwind has no utility for | Inline styles or custom CSS for one property | Check the topic index first: the property may have a page |
| `#arbitrary-variants` | A one-off selector | Custom CSS with nested selectors | `hover-focus-and-other-states#using-arbitrary-variants` (page) |
| `#using-custom-css`, `#adding-base-styles` | Page defaults (text, background, font) | Element selectors outside `@layer base` | `preflight#extending-preflight` |
| `#adding-component-classes` | Component classes overridable by utilities | `.card`/`.btn` outside `@layer components`; `@apply` chains | `styling-with-utility-classes#managing-duplication` (page) |
| `#using-variants` | A Tailwind variant inside custom CSS | Hand-written `@media` that duplicates a variant | `functions-and-directives#variant-directive` |
| `#adding-custom-utilities`, `#simple-utilities`, `#complex-utilities` | A CSS feature Tailwind lacks, used as a class | v3 `@layer utilities { … }` (must become `@utility`) | `upgrade-guide#adding-custom-utilities`, `functions-and-directives#utility-directive` |
| `#functional-utilities` with `#matching-theme-values`, `#bare-values`, `#literal-values`, `#arbitrary-values`, `#supporting-theme-bare-and-arbitrary-values-together`, `#default-values`, `#negative-values`, `#modifiers`, `#fractions` | A utility that takes a value (`tab-*`) | Several near-identical `@utility` rules that one functional utility replaces; v3 `matchUtilities` plugins | `theme#theme-variable-namespaces` |
| `#adding-custom-variants` | A reusable variant | `@custom-variant`; v3 `addVariant` plugins | `hover-focus-and-other-states#registering-a-custom-variant`, `functions-and-directives#custom-variant-directive` |

### `detecting-classes-in-source-files` (12)

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#overview`, `#how-classes-are-detected` | Classes that generate no CSS | — | `adding-custom-styles#using-arbitrary-values` (page) |
| `#dynamic-class-names` | Classes built at runtime | Interpolated or concatenated class names (`bg-${color}-500`) | `styling-with-utility-classes#how-does-this-even-work` |
| `#which-files-are-scanned` | Classes in ignored, `node_modules` or binary files | Classes only in `.gitignore`d paths, packages or generated files | `#explicitly-registering-sources` |
| `#explicitly-registering-sources` | A UI library in `node_modules`; monorepos | `@source` lines; v3 `content` globs | `functions-and-directives#source-directive` |
| `#setting-your-base-path` | The build runs from another directory than the stylesheet | `source("…")` on the import | `functions-and-directives#import-directive` |
| `#ignoring-specific-paths` | Large folders that slow the build or add stray classes | `@source not` | — |
| `#disabling-automatic-detection` | Every source registered by hand | `source(none)` | — |
| `#safelisting-specific-utilities`, `#safelisting-variants`, `#safelisting-with-ranges` | Classes that exist only in a CMS or database | v3 `safelist` in the JavaScript config; broad safelists that hide a detection problem | `upgrade-guide#using-a-javascript-config-file`, `functions-and-directives#config-directive` |
| `#explicitly-excluding-classes` | A detected class that must not generate | `@source not inline()` | `adding-custom-styles`, `functions-and-directives` (page) |

### `functions-and-directives` (17)

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#directives`, `#import-directive` | The stylesheet entry, layered imports | `@tailwind` (v3), `postcss-import` | `upgrade-guide#removed-tailwind-directives` |
| `#theme-directive` | Tokens | `@theme` placement | `theme` (page) |
| `#source-directive` | Source registration | `@source` paths | `detecting-classes-in-source-files` (page) |
| `#utility-directive` | Custom utilities | `@layer utilities` (v3) | `adding-custom-styles#adding-custom-utilities` (page) |
| `#variant-directive` | A variant in custom CSS | — | `adding-custom-styles#using-variants` (page) |
| `#custom-variant-directive` | Custom variants, dark-mode selector | `@custom-variant` | `adding-custom-styles#adding-custom-variants` (page), `dark-mode` |
| `#apply-directive` | Utilities inside custom CSS or third-party markup | `@apply` in component `<style>` blocks or CSS modules | `#reference-directive` |
| `#reference-directive` | `@apply` or `@variant` in Vue, Svelte or Astro `<style>`, or CSS modules | `<style>` blocks with `@apply` and no `@reference` | `compatibility#vue-svelte-and-astro`, `compatibility#explicit-context-sharing` |
| `#subpath-imports` | Path aliases in `@import`, `@reference`, `@plugin`, `@config` | `imports` in `package.json` | — |
| `#functions`, `#alpha-function`, `#spacing-function` | Opacity or spacing in custom CSS | `rgba()`/`opacity` hacks; spacing literals in custom CSS | `colors#adjusting-opacity`, `theme#with-custom-css` |
| `#compatibility`, `#config-directive` | A v3 JavaScript config kept in v4 | `tailwind.config.*` with no `@config`; `corePlugins`, `safelist`, `separator` (unsupported) | `detecting-classes-in-source-files#safelisting-specific-utilities` (page), `upgrade-guide#using-a-javascript-config-file` |
| `#plugin-directive` | v3 plugins (typography, forms) | `plugins: [...]` in the JavaScript config | The plugin's own docs for v4 support |
| `#theme-function` | `theme()` in CSS | `theme(spacing.12)` and other dot paths | `theme#using-your-theme-variables` (page), `upgrade-guide#using-the-theme-function` |

### `preflight` (11)

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#overview` | Unexpected resets | — | — |
| `#margins-are-removed` | Missing spacing on headings and paragraphs | Content from a CMS or Markdown without classes | `@tailwindcss/typography` through `functions-and-directives#plugin-directive` |
| `#border-styles-are-reset` | Borders appear or vanish unexpectedly | `border` without a style or color; third-party widgets | `upgrade-guide#default-border-color` |
| `#headings-are-unstyled` | Unstyled headings | Heading styles expected from the browser | `adding-custom-styles#adding-base-styles` (page) |
| `#lists-are-unstyled`, `#accessibility-considerations` | Lists without bullets | Unstyled lists without `role="list"` | `list-style-type`, `list-style-position`, `adding-custom-styles#adding-base-styles` (page) |
| `#images-are-block-level`, `#images-are-constrained` | Inline images break lines or images resize | `inline` needed on an image; fixed sizes overridden | `display`, `max-width` |
| `#elements-with-a-hidden-attribute-stay-hidden` | `hidden` elements that should show | `hidden` plus a display class | `upgrade-guide#hidden-attribute-takes-priority` |
| `#extending-preflight` | Project base styles | Element selectors outside `@layer base` | `adding-custom-styles#adding-base-styles` (page) |
| `#disabling-preflight` | Tailwind added to an existing site | Conflicts with the site's own reset | `functions-and-directives#import-directive` |

### `upgrade-guide` (41)

A migration reads every row (coverage rule 1) and reports each one as changed, not present, kept on purpose or needs a decision.

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#using-the-upgrade-tool` | Any v3 to v4 migration, first | Node.js version; a clean working tree; a new branch | — |
| `#upgrading-manually`, `#using-postcss`, `#using-vite`, `#using-tailwind-cli` | The tool cannot run or fails; the integration | `postcss.config.*`, `vite.config.*`, CLI scripts; `postcss-import`, `autoprefixer` | `installation/using-postcss`, `installation/using-vite`, `installation/tailwind-cli` |
| `#changes-from-v3`, `#browser-requirements` | Adoption and migration | The project's browser targets (Browserslist, analytics) | `compatibility#browser-support` |
| `#removed-tailwind-directives` | Migration | `@tailwind base/components/utilities` | `functions-and-directives#import-directive` |
| `#removed-deprecated-utilities` | Migration; v3 habits | `*-opacity-*`, `flex-shrink-*`, `flex-grow-*`, `overflow-ellipsis`, `decoration-slice`/`decoration-clone` | `colors#adjusting-opacity` |
| `#renamed-utilities`, `#updated-shadow-radius-and-blur-scales`, `#renamed-outline-utility`, `#default-ring-width-change` | Migration | Bare and `-sm` `shadow`, `drop-shadow`, `blur`, `backdrop-blur`, `rounded`; `outline-none`; bare `ring` | `box-shadow`, `border-radius`, `filter-blur`, `outline-style` |
| `#space-between-selector` | Migration | `space-x-*`/`space-y-*` on inline children or with margins on children | `gap` |
| `#divide-selector` | Migration | `divide-*` | `border-width` |
| `#using-variants-with-gradients` | Migration | `from-*`/`via-*`/`to-*` under a variant | `background-image` |
| `#container-configuration` | Migration | `container` with `center` or `padding` in the JavaScript config | `functions-and-directives#utility-directive` |
| `#default-border-color` | Migration | `border`/`divide-*` without a color class | `border-color`; compatibility base styles |
| `#default-ring-width-and-color` | Migration | `ring` without width or color | `box-shadow#adding-a-ring` |
| `#preflight-changes`, `#new-default-placeholder-color`, `#buttons-use-the-default-cursor`, `#dialog-margins-removed`, `#hidden-attribute-takes-priority` | Migration | Placeholders, buttons relying on a pointer cursor, centered `<dialog>`, `hidden` with display classes | `preflight` |
| `#using-a-prefix` | Migration with a prefix | `prefix` in the JavaScript config; `tw-` classes | `styling-with-utility-classes#using-the-prefix-option` |
| `#the-important-modifier` | Migration | `!` before the class name | `styling-with-utility-classes#using-the-important-modifier` |
| `#adding-custom-utilities` | Migration | `@layer utilities`/`@layer components` with classes used as utilities | `adding-custom-styles#adding-custom-utilities` |
| `#variant-stacking-order` | Migration | Stacked variants with order-dependent selectors (`first:*:`) | `hover-focus-and-other-states` |
| `#variables-in-arbitrary-values` | Migration | `[--x]` arbitrary values (now `(--x)`) | `adding-custom-styles#using-arbitrary-values` |
| `#arbitrary-values-in-grid-and-object-position-utilities` | Migration | Commas in `grid-cols-[…]`, `object-[…]` | `grid-template-columns`, `object-position` |
| `#hover-styles-on-mobile` | Migration; a decision | `hover:` on touch-critical controls | `hover-focus-and-other-states#hover-focus-and-active` |
| `#transitioning-outline-color` | Migration | `transition` on elements whose outline color changes on focus | `transition-property` |
| `#individual-transform-properties`, `#resetting-transforms`, `#transitions` | Migration | `transform-none`; `transition-transform` with `scale`/`rotate`/`translate` | `transform`, `transition-property` |
| `#disabling-core-plugins` | Migration | `corePlugins` in the JavaScript config | `#using-a-javascript-config-file` |
| `#using-the-theme-function` | Migration | `theme()` in CSS and in arbitrary values | `functions-and-directives#theme-function` |
| `#using-a-javascript-config-file` | Migration | `tailwind.config.*`, `safelist`, `separator` | `functions-and-directives#config-directive`, `detecting-classes-in-source-files#safelisting-specific-utilities` |
| `#theme-values-in-javascript` | Migration | `resolveConfig` imports | `theme#referencing-in-javascript` |
| `#using-apply-with-vue-svelte-or-css-modules` | Migration | `@apply` in `<style>` blocks or CSS modules | `functions-and-directives#reference-directive`, `compatibility#vue-svelte-and-astro` |
| `#using-sass-less-and-stylus` | Migration | `.scss`, `.less`, `.styl` stylesheets | `compatibility#sass-less-and-stylus` |

### `compatibility` (12)

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#browser-support` | Adopting v4; a browser bug | Browser targets; the installed version (4.1 degrades more gracefully) | `upgrade-guide#browser-requirements`, the v4.1 release post |
| `#sass-less-and-stylus`, `#build-time-imports`, `#variables`, `#nesting`, `#loops`, `#color-and-math-functions` | A project with a preprocessor | `.scss`/`.less`/`.styl` files; Sass variables, mixins, loops, `darken()`/`lighten()` | `colors` (page), `theme` |
| `#css-modules`, `#scoping-concerns`, `#performance`, `#explicit-context-sharing` | CSS modules beside Tailwind | `*.module.css` with `@apply` and no `@reference`; many modules slowing the build | `functions-and-directives#reference-directive` |
| `#vue-svelte-and-astro` | `<style>` blocks in components | `<style>` blocks that use `@apply` or theme tokens | `functions-and-directives#reference-directive`, `theme#with-custom-css` |

### `editor-setup` (6)

| Sections | Read when | Check in the project | Hands off to |
| --- | --- | --- | --- |
| `#syntax-support` | Editor warnings on `@theme`, `@variant`, `@source` | The editor's CSS language mode | — |
| `#intellisense-for-vs-code` | VS Code setup, class diagnostics | `.vscode/settings.json` | `functions-and-directives` (page) |
| `#cursor`, `#zed`, `#jetbrains-ides` | That editor's setup | The editor in use | — |
| `#class-sorting-with-prettier` | Class order | `prettier-plugin-tailwindcss` and its version; Biome's `useSortedClasses` | The plugin's `sort_classes` tool |

## Maintainer check (domain 16)

A script in the repository, outside the plugin:

1. Fetches each long page and extracts its h2 to h4 anchors and the docs links of each section, stopping before the page footer (its previous and next links are not section links).
2. Fails when an anchor is missing from `section-anchors.md`, when the file lists an anchor the page lost, or when a section has no row in this map.
3. Reports links the page added or removed, so the "(page)" hand-offs stay true.
4. Checks the property-page rule: each property page still has `#examples`, and reports pages that lost `#responsive-design`, `#using-a-custom-value` or `#customizing-your-theme`.

## Open points

- Unverified: the release that added `pointer-*`, `inverted-colors:`, `noscript:`, `user-valid:`/`user-invalid:` (4.1 per phase-2 inputs), `details-content:`, and the `--zoom-*` and `--tab-size-*` namespaces. Each becomes a version question in the map once confirmed.
- Where the map lives in the plugin: replace `references/section-anchors.md` (anchors become the first column of the map) or keep both. One file avoids a second copy of each anchor.
- How `SKILL.md` uses it: step 2 of the workflow reads the rows the task's signals match, and coverage rule 1 for whole-page tasks.
- Evals: one coverage case per whole-page task (migration, adoption, theme replacement, dark-mode change), graded on the sections reported, not on the page fetched.
