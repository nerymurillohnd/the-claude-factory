# Section anchors of the long Tailwind docs pages

The cross-cutting pages are long: a fetch tool returns or summarizes the whole page, and the part you need gets lost. Name the section instead.

- **Fetching a URL:** fetch `https://tailwindcss.com/docs/<slug>`, and ask the fetch tool to quote the section with that anchor and heading verbatim, such as "quote the section `#openclosed-state` (Open/closed state)". Give the anchor in links you report: `https://tailwindcss.com/docs/hover-focus-and-other-states#openclosed-state`.
- **Querying Context7:** query by the heading text, such as "Open/closed state open variant details", one section per query.

Copy an anchor exactly as listed. Never derive one from a heading: the page strips punctuation in ways you can't predict (Open/closed state is `#openclosed-state`, "::before and ::after" is `#before-and-after`). When a heading you need is missing here, the page changed: read its current headings and use the anchor the page itself shows.

Each line is `#anchor` followed by the heading text; indentation follows the heading levels. They come from the id attributes of each page's h2 to h4 headings; a repeated anchor on one page is listed once.

Pages: [`preflight`](#preflight)

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
