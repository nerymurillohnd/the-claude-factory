# [Set up Tailwind CSS IntelliSense in VS Code and Cursor](https://github.com/tailwindlabs/tailwindcss-intellisense)

## Install

- Install `bradlc.vscode-tailwindcss` in VS Code or Cursor.
- Install `tailwindcss` in the workspace, or the extension stays off.
- Give v4 a `.css` entry file: the extension ignores Sass, Less and Stylus.

## Configure

- Set `files.associations` to `"*.css": "tailwindcss"`.
- Set `tailwindCSS.experimental.configFile` when it does not find the project.
- Read its current form in the README first: it is experimental.
- Add class helpers like `clsx` and `cva` to `tailwindCSS.classFunctions`.
- Write `classFunctions` entries as regexes on the function name only.
- Add custom class attributes to `tailwindCSS.classAttributes`.
- Map unserved file types with `tailwindCSS.includeLanguages`.
- Turn on `editor.quickSuggestions` for strings.
- Set lint severities under `tailwindCSS.lint.*`.
- Ask before writing `.vscode/settings.json`: it applies to the whole team.

## When it does not activate

1. Confirm `tailwindcss` is installed.
2. Check that no `files.exclude` setting hides the stylesheet.
3. Run `Tailwind CSS: Show Output` and read the log.
4. Set `tailwindCSS.experimental.configFile` for several entry files.
