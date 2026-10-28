# Zed

Sources: https://tailwindcss.com/docs/editor-setup#zed and https://zed.dev/docs/languages/tailwindcss. Read them for anything this file does not cover; where they differ, follow them.

- Zed runs the Tailwind CSS language server itself: no extension to install. Zed's page lists the languages it serves.
- The server's settings go under `lsp` → `tailwindcss-language-server` → `settings` in Zed's `settings.json`, named as in the IntelliSense README without the `tailwindCSS.` prefix.
- To stop warnings on `@apply` and `@theme` in CSS files, put `tailwindcss-intellisense-css` before the default CSS language server for the CSS language, as Zed's page shows.
- Zed runs Prettier itself, so `prettier-plugin-tailwindcss` works once it is in the Prettier config.
