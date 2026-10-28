# JetBrains IDEs

Sources: https://tailwindcss.com/docs/editor-setup#jetbrains-ides and https://www.jetbrains.com/help/webstorm/tailwind-css.html. Read them for anything this file does not cover; where they differ, follow them.

- WebStorm, PhpStorm and the other JetBrains IDEs with web support run the Tailwind CSS language server. They need a Node.js runtime configured for the project and the bundled CSS and Tailwind CSS plugins enabled.
- The server finds the project from `tailwindcss` in `package.json` and a CSS file importing Tailwind (v4) or a `tailwind.config.js` (v3).
- The bundled server can lag behind Tailwind. JetBrains recommends a global `@tailwindcss/language-server` set in Settings | Languages & Frameworks | Style Sheets | Tailwind CSS; a global install changes the user's machine, so ask first.
- After a config change it does not pick up, restart the server from the Language Services widget in the status bar.

## When assistance stops

- The server shows an error in the Language Services widget and does not start: most often the Node.js runtime. Check Settings | Languages & Frameworks | JavaScript Runtime, where Node.js must be the preferred runtime with a valid path.
- On v4, a broken CSS entry file stops the server from starting. Comment out everything but `@import "tailwindcss"`, restart the server, then restore the file piece by piece until the failing fragment shows.
- An outdated bundled server: point the IDE to a current `@tailwindcss/language-server`, as above.
