# VS Code and Cursor: Tailwind CSS IntelliSense

Sources, checked 2026-10-27: https://tailwindcss.com/docs/editor-setup (`#syntax-support`, `#intellisense-for-vs-code`, `#cursor`) and the extension's README, https://github.com/tailwindlabs/tailwindcss-intellisense (v0.16.0). When they differ from this file, they win.

## The extension

- `bradlc.vscode-tailwindcss` on the VS Code Marketplace, the official extension. It gives class and directive completions, linting of CSS and markup, the generated CSS on hover, and a Tailwind CSS language mode for stylesheets.
- Cursor runs VS Code extensions, so the same extension and the Prettier plugin work there. The extension is also published on Open VSX, at the same version, for editors that do not use Microsoft's marketplace.
- It activates only when `tailwindcss` is installed in the workspace and it finds the project: for v4, a `.css` file that imports Tailwind (`@import "tailwindcss"`); for v3, a `tailwind.config.{js,cjs,mjs,ts,cts,mts}` or a stylesheet with `@config`. Sass, Less and Stylus files do not count: v4 needs a `.css` entry.

## Editor warnings on `@theme`, `@apply`, `@source`

VS Code's own CSS mode does not know Tailwind's at-rules and flags them. Open `.css` files in the extension's Tailwind CSS mode instead of turning CSS validation off:

```json
"files.associations": { "*.css": "tailwindcss" }
```

Only when an editor still rejects the syntax, turn its native CSS validation off, as the docs allow.

## Recommended settings

| Setting | Use |
| --- | --- |
| `editor.quickSuggestions` with `"strings": "on"` | Completions inside strings, such as JSX `className` values |
| `tailwindCSS.experimental.configFile` | The CSS entry point (v4) or config file (v3) when detection fails: several entry points, a monorepo, a stylesheet outside the usual places. A string for one file; an object mapping each file to the glob it covers for several |
| `tailwindCSS.classFunctions` | Functions whose strings hold classes (`clsx`, `cva`, `cn`, `tw`); each entry is a regular expression on the function name only |
| `tailwindCSS.classAttributes` | Attributes beyond the defaults `class`, `className`, `ngClass`, `class:list` |
| `tailwindCSS.includeLanguages` | Map another language to `html`, `css` or `javascript` so the extension serves it |
| `tailwindCSS.files.exclude` | Globs the extension ignores; it also inherits `files.exclude` |
| `tailwindCSS.lint.*` | Each rule set to `ignore`, `warning` or `error`. `cssConflict` (two classes setting the same property) and `suggestCanonicalClasses` (a class with a shorter canonical form) are warnings by default |

Write project settings in `.vscode/settings.json` only with the user's agreement: they apply to everyone who opens the repository.

## When it does not activate

1. Confirm `tailwindcss` is installed (not only declared) and the v4 entry is a `.css` file.
2. Check that `files.exclude`, `files.watcherExclude` or `tailwindCSS.files.exclude` do not hide the stylesheet or config.
3. Read the language server log: command palette, `Tailwind CSS: Show Output`.
4. With several Tailwind installs, configs or entry stylesheets, set `tailwindCSS.experimental.configFile`.
