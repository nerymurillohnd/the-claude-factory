# Zed

Sources, checked 2026-10-27: https://tailwindcss.com/docs/editor-setup#zed and Zed's page, https://zed.dev/docs/languages/tailwindcss. When they differ from this file, they win.

## Built in

- Zed runs the official Tailwind CSS language server itself: completions, linting and hover previews with no extension to install.
- Languages it serves: Astro, CSS, ERB, Gleam, Go (Templ), HEEx, HTML, JavaScript, TypeScript, PHP, Svelte and Vue.

## Settings

The language server takes the settings the IntelliSense README lists, under `lsp` in Zed's `settings.json`, without the `tailwindCSS.` prefix:

```json
{
  "lsp": {
    "tailwindcss-language-server": {
      "settings": { "classFunctions": ["cva", "cx"] }
    }
  }
}
```

## Tailwind syntax in CSS files

To stop warnings on `@apply`, `@layer` and `@theme`, put `tailwindcss-intellisense-css` before the default CSS server for the CSS language:

```json
{
  "languages": {
    "CSS": {
      "language_servers": ["tailwindcss-intellisense-css", "!vscode-css-language-server", "..."]
    }
  }
}
```

## Class sorting

Zed runs Prettier itself, so `prettier-plugin-tailwindcss` works once it is installed and listed in the Prettier config's `plugins`.
