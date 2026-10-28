# Set up VS Code and Cursor: Tailwind CSS IntelliSense

Read https://tailwindcss.com/docs/editor-setup and the extension's README, https://github.com/tailwindlabs/tailwindcss-intellisense, which lists every setting, for anything this file does not cover. Where they differ, follow them.

## Install

- Install the official extension, `bradlc.vscode-tailwindcss`. In Cursor, install the same extension: Cursor runs VS Code extensions.
- Expect it to activate only when `tailwindcss` is installed in the workspace and it finds a `.css` file importing Tailwind (v4) or a `tailwind.config.*` or `@config` stylesheet (v3). It ignores Sass, Less and Stylus files.

## Configure

- Set `files.associations` to `"*.css": "tailwindcss"` to stop warnings on `@theme`, `@apply` and `@source`.
- Set `tailwindCSS.experimental.configFile` when detection fails (several entry stylesheets, a monorepo): a string for one entry, an object mapping each entry file to the glob it serves for several. Read its current form in the README first, since it is experimental.
- Add `clsx`, `cva`, `cn` and other class helpers to `tailwindCSS.classFunctions`, and custom attributes to `tailwindCSS.classAttributes`. Write `classFunctions` entries as regular expressions on the function name only.
- Map a file type the extension does not serve to `html`, `css` or `javascript` with `tailwindCSS.includeLanguages`.
- Turn on `editor.quickSuggestions` for strings to get completions inside class strings.
- Set each lint rule's severity under `tailwindCSS.lint.*`. Ignore the rules for v3 syntax (`@screen`, `@variants`, `@tailwind`) on v4; `cssConflict` and `suggestCanonicalClasses` report what this plugin's checks report.
- Write project settings to `.vscode/settings.json` only with the user's agreement: they apply to everyone who opens the repository.

## When it does not activate

1. Confirm `tailwindcss` is installed and the v4 entry is a `.css` file.
2. Check that `files.exclude`, `files.watcherExclude` and `tailwindCSS.files.exclude` do not hide it.
3. Read the log: run `Tailwind CSS: Show Output` from the command palette.
4. Set `tailwindCSS.experimental.configFile` when the project has several installs or entry files.
