# Fix editor warnings on Tailwind's CSS syntax

Read https://tailwindcss.com/docs/editor-setup#syntax-support for anything this file does not cover. Where it differs, follow it.

Editors that do not know Tailwind's at-rules and functions (`@theme`, `@variant`, `@source`, `@apply`, `--alpha()`) flag them as errors. Give the CSS files a language mode that knows them; never edit valid CSS to silence the editor.

- In VS Code and Cursor, set `files.associations` to `"*.css": "tailwindcss"` to use the IntelliSense extension's Tailwind CSS mode.
- In Zed, put the `tailwindcss-intellisense-css` language server ahead of the default CSS server, as https://zed.dev/docs/languages/tailwindcss shows.
- In other editors, or when one still complains, turn off its native CSS validation. Ask the user first, and change the project's settings rather than the whole machine's.

Read any warning that remains: it may be a real error, such as an `@apply` of a class that does not exist.
