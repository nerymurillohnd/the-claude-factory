# Set up JetBrains IDEs

Read https://tailwindcss.com/docs/editor-setup#jetbrains-ides and https://www.jetbrains.com/help/webstorm/tailwind-css.html for anything this file does not cover. Where they differ, follow them.

## Set it up

- Configure a Node.js runtime for the project and enable the bundled CSS and Tailwind CSS plugins: WebStorm, PhpStorm and the other web-capable JetBrains IDEs run the Tailwind CSS language server through them.
- Make sure the project has `tailwindcss` in `package.json` and a CSS file importing Tailwind (v4) or a `tailwind.config.js` (v3): the server finds the project from them.
- Point the IDE to a current `@tailwindcss/language-server` in Settings | Languages & Frameworks | Style Sheets | Tailwind CSS when the bundled one lags behind Tailwind. Ask before installing it globally: it changes the user's machine.
- Restart the server from the Language Services widget in the status bar after a config change it does not pick up.

## When assistance stops

- Check Settings | Languages & Frameworks | JavaScript Runtime when the widget shows an error and the server does not start: set Node.js as the preferred runtime, with a valid path.
- On v4, reduce the CSS entry file to `@import "tailwindcss"`, restart the server, then restore the file piece by piece to find the fragment that stops it from starting.
- Point the IDE to a current server when the bundled one is outdated.
