# Installing through the PostCSS plugin

Official page: https://tailwindcss.com/docs/installation/using-postcss. It is the source of truth: when this file and the page disagree, the page wins and this file is out of date. Checked against the page on 2026-10-27 (Tailwind CSS v4.3.3).

## When this path fits

- The project has a `postcss.config.*` (or PostCSS settings in `package.json`), or its bundler runs PostCSS and the framework has no guide of its own in the framework-guides list. The page names Next.js and Angular as frameworks this path suits; both also have a dedicated guide, which comes first.
- A project built with Vite fits `using-vite.md` better.

## What the setup consists of

1. Three packages: `tailwindcss`, `@tailwindcss/postcss` and `postcss`, installed with the project's package manager (SKILL.md, "Installation", step 1).
2. The plugin added to the PostCSS configuration, wherever the project keeps it. In an ES module config:

   ```js
   export default {
     plugins: {
       "@tailwindcss/postcss": {},
     },
   }
   ```

   Keep the project's other PostCSS plugins; add the entry beside them.
3. One line in the project's main CSS file: `@import "tailwindcss";`.
4. The project's usual dev or build script, unchanged.
5. The compiled stylesheet linked from the page's `<head>`, unless the framework already includes it.

## Check in the project

- v3 leftovers in the PostCSS config: the `tailwindcss` entry (in v4 the plugin is `@tailwindcss/postcss`), and `postcss-import` and `autoprefixer`, which v4 makes unnecessary because it handles imports and vendor prefixes itself (`upgrade-guide#using-postcss`). Remove them only when nothing else in the project needs them.
- `@tailwind base/components/utilities` in the CSS: replaced by the single import.
- The config's module format (`.mjs`, `.cjs`, `.js` with or without `"type": "module"`): write the entry in the format the file already uses.
- Which CSS file the app actually loads: the import goes there.

## Verify

SKILL.md, "Installation", step 3: one probe class that the existing styles cannot produce, the dev server or build, and the generated CSS checked for it.
