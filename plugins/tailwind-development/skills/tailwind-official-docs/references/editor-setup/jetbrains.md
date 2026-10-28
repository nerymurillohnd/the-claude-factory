# [Set up JetBrains IDEs](https://www.jetbrains.com/help/webstorm/tailwind-css.html)

## Set it up

- Configure a Node.js runtime for the project.
- Enable the bundled CSS and Tailwind CSS plugins.
- List `tailwindcss` in `package.json`.
- Point the IDE to a current `@tailwindcss/language-server` if the bundled one lags.
- Ask before installing that server globally.
- Restart the server from the Language Services widget after config changes.

## When assistance stops

- Set Node.js as the preferred JavaScript runtime, with a valid path.
- Reduce the v4 CSS entry to its import, then restore it piece by piece.
- Update the language server.
