# Editor warnings on Tailwind's CSS syntax

Source: https://tailwindcss.com/docs/editor-setup#syntax-support. Read it for anything this file does not cover; where it differs, follow it.

Editors that do not know Tailwind's at-rules and functions (`@theme`, `@variant`, `@source`, `@apply`, `--alpha()`) flag them as errors in CSS files. Give the CSS files a language mode that knows them, rather than editing valid CSS to silence the editor:

- VS Code and Cursor: the IntelliSense extension's Tailwind CSS language mode, through `files.associations` (`"*.css": "tailwindcss"`).
- Zed: the `tailwindcss-intellisense-css` language server ahead of the default CSS server, as Zed's Tailwind page shows (https://zed.dev/docs/languages/tailwindcss).
- Other editors, or one that still complains: turn off its native CSS validation, as the page allows. It is an editor setting, so change it only with the user's agreement, and never for the whole machine when the project's settings will do.

A warning that remains after this is worth reading: it may be a real error, such as an `@apply` of a class that does not exist.
