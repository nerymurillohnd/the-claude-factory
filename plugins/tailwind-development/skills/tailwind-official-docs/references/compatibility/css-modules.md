# [Use Tailwind with CSS modules](https://tailwindcss.com/docs/compatibility#css-modules)

- Prefer utility classes in the markup over new CSS modules.
- Keep existing CSS modules working; do not rewrite them unasked.
- Expect slower builds: the bundler runs Tailwind once per module.
- Add `@reference` to the global stylesheet before `@apply` in a module.
- Prefer `var(--color-…)` over `@apply`: Tailwind then skips the file.
- Point the plugin's `config_file` option at the entry stylesheet when modules use `@reference`.
