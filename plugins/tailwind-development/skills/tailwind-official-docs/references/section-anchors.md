# Section anchors of the long Tailwind docs pages

The cross-cutting pages are long: a fetch tool returns or summarizes the whole page, and the part you need gets lost. Name the section instead.

- **Fetching a URL:** fetch `https://tailwindcss.com/docs/<slug>`, and ask the fetch tool to quote the section with that anchor and heading verbatim, such as "quote the section `#openclosed-state` (Open/closed state)". Give the anchor in links you report: `https://tailwindcss.com/docs/hover-focus-and-other-states#openclosed-state`.
- **Querying Context7:** query by the heading text, such as "Open/closed state open variant details", one section per query.

Copy an anchor exactly as listed. Never derive one from a heading: the page strips punctuation in ways you can't predict (Open/closed state is `#openclosed-state`, "::before and ::after" is `#before-and-after`). When a heading you need is missing here, the page changed: read its current headings and use the anchor the page itself shows.

Each line is `#anchor` followed by the heading text; indentation follows the heading levels. They come from the id attributes of each page's h2 to h4 headings; a repeated anchor on one page is listed once.

Pages: [`hover-focus-and-other-states`](#hover-focus-and-other-states) · [`responsive-design`](#responsive-design) · [`dark-mode`](#dark-mode) · [`theme`](#theme) · [`colors`](#colors) · [`adding-custom-styles`](#adding-custom-styles) · [`detecting-classes-in-source-files`](#detecting-classes-in-source-files) · [`functions-and-directives`](#functions-and-directives) · [`preflight`](#preflight)

## `hover-focus-and-other-states`

- `#pseudo-classes` Pseudo-classes
  - `#hover-focus-and-active` :hover, :focus, and :active
  - `#first-last-odd-and-even` :first, :last, :odd, and :even
  - `#required-and-disabled` :required and :disabled
  - `#has` :has()
    - `#styling-based-on-the-descendants-of-a-group` Styling based on the descendants of a group
    - `#styling-based-on-the-descendants-of-a-peer` Styling based on the descendants of a peer
  - `#not` :not()
  - `#styling-based-on-parent-state` Styling based on parent state
    - `#differentiating-nested-groups` Differentiating nested groups
    - `#arbitrary-groups` Arbitrary groups
    - `#implicit-groups` Implicit groups
  - `#styling-based-on-sibling-state` Styling based on sibling state
    - `#differentiating-peers` Differentiating peers
    - `#arbitrary-peers` Arbitrary peers
- `#pseudo-elements` Pseudo-elements
  - `#before-and-after` ::before and ::after
  - `#placeholder` ::placeholder
  - `#file` ::file
  - `#marker` ::marker
  - `#selection` ::selection
  - `#first-line-and-first-letter` ::first-line and ::first-letter
  - `#backdrop` ::backdrop
- `#media-and-feature-queries` Media and feature queries
  - `#responsive-breakpoints` Responsive breakpoints
  - `#prefers-color-scheme` prefers-color-scheme
  - `#prefers-reduced-motion` prefers-reduced-motion
  - `#prefers-contrast` prefers-contrast
  - `#forced-colors` forced-colors
  - `#inverted-colors` inverted-colors
  - `#pointer-and-any-pointer` pointer and any-pointer
  - `#orientation` orientation
  - `#scripting` scripting
  - `#print` print
  - `#supports` @supports
  - `#starting-style` @starting-style
- `#attribute-selectors` Attribute selectors
  - `#aria-states` ARIA states
  - `#data-attributes` Data attributes
  - `#rtl-support` RTL support
  - `#openclosed-state` Open/closed state
  - `#styling-inert-elements` Styling inert elements
- `#child-selectors` Child selectors
  - `#styling-direct-children` Styling direct children
  - `#styling-all-descendants` Styling all descendants
- `#custom-variants` Custom variants
  - `#using-arbitrary-variants` Using arbitrary variants
  - `#registering-a-custom-variant` Registering a custom variant
- `#appendix` Appendix
  - `#quick-reference` Quick reference
  - `#pseudo-class-reference` Pseudo-class reference
    - `#hover` :hover
    - `#focus` :focus
    - `#focus-within` :focus-within
    - `#focus-visible` :focus-visible
    - `#active` :active
    - `#visited` :visited
    - `#target` :target
    - `#first-child` :first-child
    - `#last-child` :last-child
    - `#only-child` :only-child
    - `#nth-childodd` :nth-child(odd)
    - `#nth-childeven` :nth-child(even)
    - `#first-of-type` :first-of-type
    - `#last-of-type` :last-of-type
    - `#only-of-type` :only-of-type
    - `#nth-child` :nth-child()
    - `#nth-last-child` :nth-last-child()
    - `#nth-of-type` :nth-of-type()
    - `#nth-last-of-type` :nth-last-of-type()
    - `#empty` :empty
    - `#disabled` :disabled
    - `#enabled` :enabled
    - `#checked` :checked
    - `#indeterminate` :indeterminate
    - `#default` :default
    - `#optional` :optional
    - `#required` :required
    - `#valid` :valid
    - `#invalid` :invalid
    - `#user-valid` :user-valid
    - `#user-invalid` :user-invalid
    - `#in-range` :in-range
    - `#out-of-range` :out-of-range
    - `#placeholder-shown` :placeholder-shown
    - `#details-content` :details-content
    - `#autofill` :autofill
    - `#read-only` :read-only

## `responsive-design`

- `#overview` Overview
- `#working-mobile-first` Working mobile-first
  - `#targeting-mobile-screens` Targeting mobile screens
  - `#targeting-a-breakpoint-range` Targeting a breakpoint range
  - `#targeting-a-single-breakpoint` Targeting a single breakpoint
- `#using-custom-breakpoints` Using custom breakpoints
  - `#customizing-your-theme` Customizing your theme
  - `#removing-default-breakpoints` Removing default breakpoints
  - `#using-arbitrary-values` Using arbitrary values
- `#container-queries` Container queries
  - `#what-are-container-queries` What are container queries?
  - `#basic-example` Basic example
  - `#max-width-container-queries` Max-width container queries
  - `#container-query-ranges` Container query ranges
  - `#named-containers` Named containers
  - `#using-size-containers` Using size containers
  - `#using-custom-container-sizes` Using custom container sizes
  - `#using-arbitrary-container-query-values` Using arbitrary values
  - `#using-container-query-units` Using container query units
  - `#container-size-reference` Container size reference

## `dark-mode`

- `#overview` Overview
- `#toggling-dark-mode-manually` Toggling dark mode manually
  - `#using-a-data-attribute` Using a data attribute
  - `#with-system-theme-support` With system theme support

## `theme`

- `#overview` Overview
  - `#what-are-theme-variables` What are theme variables?
    - `#why-theme-instead-of-root` Why @theme instead of :root?
  - `#relationship-to-utility-classes` Relationship to utility classes
    - `#relationship-to-variants` Relationship to variants
  - `#theme-variable-namespaces` Theme variable namespaces
  - `#default-theme-variables` Default theme variables
- `#customizing-your-theme` Customizing your theme
  - `#extending-the-default-theme` Extending the default theme
  - `#overriding-the-default-theme` Overriding the default theme
  - `#using-a-custom-theme` Using a custom theme
  - `#defining-animation-keyframes` Defining animation keyframes
  - `#referencing-other-variables` Referencing other variables
  - `#generating-all-css-variables` Generating all CSS variables
  - `#sharing-across-projects` Sharing across projects
- `#using-your-theme-variables` Using your theme variables
  - `#with-custom-css` With custom CSS
  - `#with-arbitrary-values` With arbitrary values
  - `#referencing-in-javascript` Referencing in JavaScript
- `#default-theme-variable-reference` Default theme variable reference

## `colors`

- `#working-with-colors` Working with colors
  - `#using-color-utilities` Using color utilities
  - `#adjusting-opacity` Adjusting opacity
  - `#targeting-dark-mode` Targeting dark mode
  - `#referencing-in-css` Referencing in CSS
- `#customizing-your-colors` Customizing your colors
  - `#overriding-default-colors` Overriding default colors
  - `#disabling-default-colors` Disabling default colors
  - `#using-a-custom-palette` Using a custom palette
  - `#referencing-other-variables` Referencing other variables
- `#default-color-palette-reference` Default color palette reference

## `adding-custom-styles`

- `#customizing-your-theme` Customizing your theme
- `#using-arbitrary-values` Using arbitrary values
  - `#arbitrary-properties` Arbitrary properties
  - `#arbitrary-variants` Arbitrary variants
  - `#handling-whitespace` Handling whitespace
  - `#resolving-ambiguities` Resolving ambiguities
- `#using-custom-css` Using custom CSS
  - `#adding-base-styles` Adding base styles
  - `#adding-component-classes` Adding component classes
  - `#using-variants` Using variants
- `#adding-custom-utilities` Adding custom utilities
  - `#simple-utilities` Simple utilities
  - `#complex-utilities` Complex utilities
  - `#functional-utilities` Functional utilities
    - `#matching-theme-values` Matching theme values
    - `#bare-values` Bare values
    - `#literal-values` Literal values
    - `#arbitrary-values` Arbitrary values
    - `#supporting-theme-bare-and-arbitrary-values-together` Supporting theme, bare, and arbitrary values together
    - `#default-values` Default values
    - `#negative-values` Negative values
    - `#modifiers` Modifiers
    - `#fractions` Fractions
- `#adding-custom-variants` Adding custom variants

## `detecting-classes-in-source-files`

- `#overview` Overview
  - `#how-classes-are-detected` How classes are detected
  - `#dynamic-class-names` Dynamic class names
  - `#which-files-are-scanned` Which files are scanned
- `#explicitly-registering-sources` Explicitly registering sources
  - `#setting-your-base-path` Setting your base path
  - `#ignoring-specific-paths` Ignoring specific paths
  - `#disabling-automatic-detection` Disabling automatic detection
- `#safelisting-specific-utilities` Safelisting specific utilities
  - `#safelisting-variants` Safelisting variants
  - `#safelisting-with-ranges` Safelisting with ranges
  - `#explicitly-excluding-classes` Explicitly excluding classes

## `functions-and-directives`

- `#directives` Directives
  - `#import-directive` @import
  - `#theme-directive` @theme
  - `#source-directive` @source
  - `#utility-directive` @utility
  - `#variant-directive` @variant
  - `#custom-variant-directive` @custom-variant
  - `#apply-directive` @apply
  - `#reference-directive` @reference
  - `#subpath-imports` Subpath Imports
- `#functions` Functions
  - `#alpha-function` --alpha()
  - `#spacing-function` --spacing()
- `#compatibility` Compatibility
  - `#config-directive` @config
  - `#plugin-directive` @plugin
  - `#theme-function` theme()

## `preflight`

- `#overview` Overview
  - `#margins-are-removed` Margins are removed
  - `#border-styles-are-reset` Border styles are reset
  - `#headings-are-unstyled` Headings are unstyled
  - `#lists-are-unstyled` Lists are unstyled
    - `#accessibility-considerations` Accessibility considerations
  - `#images-are-block-level` Images are block-level
  - `#images-are-constrained` Images are constrained
    - `#elements-with-a-hidden-attribute-stay-hidden` Elements with a hidden attribute stay hidden
- `#extending-preflight` Extending Preflight
- `#disabling-preflight` Disabling Preflight
