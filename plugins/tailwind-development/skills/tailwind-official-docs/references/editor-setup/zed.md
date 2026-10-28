# Set up Zed

Read https://zed.dev/docs/languages/tailwindcss. Follow it over this file.

- Install nothing: Zed runs the Tailwind language server itself.
- Put server settings under `lsp.tailwindcss-language-server.settings`.
- Drop the `tailwindCSS.` prefix from setting names.
- Nest settings as objects, never as dotted keys.
- Put `tailwindcss-intellisense-css` before the default CSS server.
- Add `prettier-plugin-tailwindcss` to the Prettier config to sort classes.
