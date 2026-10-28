# Style states with variants

Read the matching section of https://tailwindcss.com/docs/hover-focus-and-other-states.
Follow it over this file.

## `#pseudo-classes`

- Use `focus-visible:` for keyboard focus rings, not `focus:` (`#hover-focus-and-active`).
- Remember `hover:` applies only on devices that can hover.
- Use `first:`, `last:`, `odd:`, `even:` instead of index checks in JavaScript.
- Use `required:`, `disabled:` and the form-state variants for form controls.
- Use `has-*` and `not-*` instead of JavaScript that toggles classes (`#has`, `#not`).

## `#styling-based-on-parent-state`

- Mark the parent with `group` and style children with `group-*`.
- Name nested groups: `group/item` and `group-hover/item:`.
- Read the h4 sections for arbitrary and implicit groups.

## `#styling-based-on-sibling-state`

- Mark the sibling with `peer` and style later siblings with `peer-*`.
- Place the `peer` element before the elements it styles.
- Name peers when several share a parent: `peer/name`.

## `#pseudo-elements`

- Use `before:` and `after:` with a `content-` class for decoration.
- Style native parts with `placeholder:`, `file:`, `marker:`, `selection:`, `backdrop:`.
- Use `first-line:` and `first-letter:` for typographic openings.

## `#media-and-feature-queries`

- Read `responsive-design` for breakpoints (`#responsive-breakpoints`).
- Read `dark-mode` for `dark:` (`#prefers-color-scheme`).
- Wrap animations in `motion-safe:` or `motion-reduce:` (`#prefers-reduced-motion`).
- Use `contrast-more:` and `forced-colors:` for accessibility modes.
- Use `pointer-coarse:` for touch targets instead of a breakpoint (`#pointer-and-any-pointer`).
- Use `print:`, `portrait:`, `landscape:` and `noscript:` for their environments.
- Use `supports-[…]:` for a feature check (`#supports`).
- Use `starting:` for entry transitions of dialogs and popovers (`#starting-style`).
- Check the installed version before a recent variant.

## `#attribute-selectors`

- Use `aria-*` variants for ARIA states (`#aria-states`).
- Use `data-*` variants for headless library states (`#data-attributes`).
- Use `rtl:` and `ltr:` only where logical utilities cannot help (`#rtl-support`).
- Use `open:` for `<details>`, `<dialog>` and popovers (`#openclosed-state`).
- Use `inert:` for content disabled behind a modal (`#styling-inert-elements`).

## `#child-selectors`

- Use `*:` for direct children you cannot class (`#styling-direct-children`).
- Use `**:` for all descendants (`#styling-all-descendants`).
- Prefer classes on the children when you control their markup.

## `#custom-variants`

- Use `[&…]:` for a one-off selector (`#using-arbitrary-variants`).
- Register a repeated selector with `@custom-variant` (`#registering-a-custom-variant`).

## `#appendix`

- Look up a variant's selector in `#quick-reference`.
- Read the variant's own entry in `#pseudo-class-reference`.
