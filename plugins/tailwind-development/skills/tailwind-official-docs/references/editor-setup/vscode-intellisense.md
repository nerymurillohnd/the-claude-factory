# VS Code and Cursor: Tailwind CSS IntelliSense

Sources: https://tailwindcss.com/docs/editor-setup and the extension's README, https://github.com/tailwindlabs/tailwindcss-intellisense, which lists every setting. Read them for anything this file does not cover; where they differ, follow them.

## The extension

- The official extension is `bradlc.vscode-tailwindcss`. Cursor runs VS Code extensions, so it works there too.
- It activates only when `tailwindcss` is installed in the workspace and it finds the project: a `.css` file importing Tailwind (v4), or a `tailwind.config.*` or `@config` stylesheet (v3). Sass, Less and Stylus files do not count.

## Editor warnings on `@theme`, `@apply`, `@source`

Open `.css` files in the extension's Tailwind CSS language mode (`files.associations`: `"*.css": "tailwindcss"`) rather than turning CSS validation off. Turn native validation off only if an editor still rejects the syntax.

## Settings worth checking

- Detection fails (several entry stylesheets, a monorepo): `tailwindCSS.experimental.configFile`.
- Classes inside `clsx`, `cva`, `cn` or custom attributes: `tailwindCSS.classFunctions` and `tailwindCSS.classAttributes`.
- No completions inside strings: `editor.quickSuggestions` with strings on.

Project settings in `.vscode/settings.json` apply to everyone who opens the repository: write them only with the user's agreement.

## When it does not activate

1. Confirm `tailwindcss` is installed and the v4 entry is a `.css` file.
2. Check that `files.exclude`, `files.watcherExclude` or `tailwindCSS.files.exclude` do not hide it.
3. Read the log: command palette, `Tailwind CSS: Show Output`.
4. With several installs or entry files, set `tailwindCSS.experimental.configFile`.
