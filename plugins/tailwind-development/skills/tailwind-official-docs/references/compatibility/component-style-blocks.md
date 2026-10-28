# [Style Vue, Svelte and Astro components](https://tailwindcss.com/docs/compatibility#vue-svelte-and-astro)

- Style components with utility classes in the markup.
- Avoid `<style>` blocks: each one runs through Tailwind separately.
- Add `@reference` to the global stylesheet before `@apply` in a `<style>` block.
- Prefer `var(--color-…)` over `@apply` in a `<style>` block.
- Read `functions-and-directives#reference-directive` for the `@reference` path.
- Point the plugin's `config_file` option at the entry stylesheet when blocks use `@reference`.
