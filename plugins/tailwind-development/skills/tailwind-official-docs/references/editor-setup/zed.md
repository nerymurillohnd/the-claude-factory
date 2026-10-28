# Set up Zed

Read https://tailwindcss.com/docs/editor-setup#zed and https://zed.dev/docs/languages/tailwindcss for anything this file does not cover. Where they differ, follow them.

- Install nothing: Zed runs the Tailwind CSS language server itself. Check Zed's page for the languages it serves.
- Put server settings under `lsp` → `tailwindcss-language-server` → `settings` in Zed's `settings.json` when the server misses classes in a language. Name them as the IntelliSense README does, without the `tailwindCSS.` prefix, and nest them as objects: write `"experimental": { "configFile": … }`, never a dotted key.
- Put `tailwindcss-intellisense-css` before the default CSS language server for CSS to stop warnings on `@apply` and `@theme`, as Zed's page shows.
- Add `prettier-plugin-tailwindcss` to the Prettier config for class sorting: Zed runs Prettier itself.
