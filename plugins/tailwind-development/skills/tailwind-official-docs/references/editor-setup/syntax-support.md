# Fix editor warnings on Tailwind's CSS syntax

Read https://tailwindcss.com/docs/editor-setup#syntax-support. Follow it over this file.

- Never edit valid CSS to silence the editor.
- VS Code and Cursor: set `files.associations` to `"*.css": "tailwindcss"`.
- Zed: put `tailwindcss-intellisense-css` before the default CSS server.
- Other editors: turn off native CSS validation, with the user's agreement.
- Change the project's settings, not the whole machine's.
- Read any warning left: it may be a real error.
