# JetBrains IDEs

Sources, checked 2026-10-27: https://tailwindcss.com/docs/editor-setup#jetbrains-ides and JetBrains' page, https://www.jetbrains.com/help/webstorm/tailwind-css.html (WebStorm 2026.2). When they differ from this file, they win.

## Built in

- WebStorm, PhpStorm and the other JetBrains IDEs with web support use the Tailwind CSS language server: class and directive completions, the generated CSS on hover, and Tailwind inspections.
- It needs a Node.js runtime configured in the project, and the bundled CSS and Tailwind CSS plugins enabled (Settings | Plugins).
- It finds the project like the other editors: `tailwindcss` in `package.json`, then a CSS file with `@import "tailwindcss"` (v4) or a `tailwind.config.js` (v3).

## Keep the language server current

The IDE ships its own copy of the server, which can lag behind Tailwind releases. JetBrains recommends installing `@tailwindcss/language-server` globally and pointing the IDE to it: Settings | Languages & Frameworks | Style Sheets | Tailwind CSS, field Language Server. A global install changes the user's machine: ask first.

## Settings

The same page has a Configuration area for the language server's options, such as the class attributes and extra places to complete classes. The IntelliSense README (https://github.com/tailwindlabs/tailwindcss-intellisense) lists the options.

## When it does not pick up a change

Restart the Tailwind CSS language server from the Language Services widget in the status bar.
