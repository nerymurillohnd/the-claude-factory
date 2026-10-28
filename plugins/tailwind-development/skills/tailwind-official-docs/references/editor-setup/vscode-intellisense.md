# VS Code and Cursor: Tailwind CSS IntelliSense

Sources: https://tailwindcss.com/docs/editor-setup and the extension's README, https://github.com/tailwindlabs/tailwindcss-intellisense, which lists every setting. Read them for anything this file does not cover; where they differ, follow them.

## The extension

- The official extension is `bradlc.vscode-tailwindcss`. Cursor runs VS Code extensions, so it works there too.
- It activates only when `tailwindcss` is installed in the workspace and it finds the project: a `.css` file importing Tailwind (v4), or a `tailwind.config.*` or `@config` stylesheet (v3). Sass, Less and Stylus files do not count.

## Editor warnings on `@theme`, `@apply`, `@source`

Open `.css` files in the extension's Tailwind CSS language mode: `files.associations` with `"*.css": "tailwindcss"`.

## Settings worth checking

- Detection fails (several entry stylesheets, a monorepo): `tailwindCSS.experimental.configFile`. One entry is a string; several are an object mapping each entry file to the glob of the files it serves. It is experimental, so read the README's current form before writing it.
- Classes inside `clsx`, `cva`, `cn` or custom attributes: `tailwindCSS.classFunctions` and `tailwindCSS.classAttributes`. `classFunctions` entries are regular expressions on the function name only; they cannot match what comes before or after it.
- Classes in a file type the extension does not serve get no completions or linting: map that language to `html`, `css` or `javascript` with `tailwindCSS.includeLanguages`.
- No completions inside strings: `editor.quickSuggestions` with strings on.
- Each lint rule's severity is set under `tailwindCSS.lint.*`. Several rules only concern v3 syntax (`@screen`, `@variants`, `@tailwind`); `cssConflict` and `suggestCanonicalClasses` report the same conflicts and non-canonical classes this plugin's checks do.

Project settings in `.vscode/settings.json` apply to everyone who opens the repository: write them only with the user's agreement.

## When it does not activate

1. Confirm `tailwindcss` is installed and the v4 entry is a `.css` file.
2. Check that `files.exclude`, `files.watcherExclude` or `tailwindCSS.files.exclude` do not hide it.
3. Read the log: command palette, `Tailwind CSS: Show Output`.
4. With several installs or entry files, set `tailwindCSS.experimental.configFile`.
