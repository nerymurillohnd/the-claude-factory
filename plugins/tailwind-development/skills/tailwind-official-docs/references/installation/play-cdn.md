# The Play CDN

Official page: https://tailwindcss.com/docs/installation/play-cdn. It is the source of truth: when this file and the page disagree, the page wins and this file is out of date. Checked against the page on 2026-10-27 (Tailwind CSS v4.3.3).

## When it fits

- Trying Tailwind in the browser with no build step: a prototype, a standalone preview page, a bug reproduction.
- Never for production. Tailwind states the Play CDN is for development only. A project that will ship takes one of the build paths (`using-vite.md`, `using-postcss.md`, `tailwind-cli.md`) or its framework guide.

## What it consists of

1. One script tag in the page's `<head>`, loading the browser build of Tailwind from jsDelivr:

   ```html
   <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
   ```

   `@4` follows the latest v4 release. Pin an exact version (`@tailwindcss/browser@4.3.3`) when the preview must match a project's installed version. Only a pinned file can carry a Subresource Integrity hash (`integrity` plus `crossorigin="anonymous"`): the floating `@4` file changes with each release, and the short package URL serves a minified copy jsDelivr generates, which is not a file of the package. For SRI, point at the package's own file, `https://cdn.jsdelivr.net/npm/@tailwindcss/browser@<version>/dist/index.global.js`, and take its SHA-256 from `https://data.jsdelivr.com/v1/packages/npm/@tailwindcss/browser@<version>?structure=flat` as `integrity="sha256-<hash>"`.
2. Utility classes in the markup, generated in the browser as the page runs.
3. Custom CSS with Tailwind features (`@theme`, `@utility`, `@apply`) goes in a `<style type="text/tailwindcss">` block; a plain `<style>` block is not processed by Tailwind.

## What to tell the user

- The page loads a script from `cdn.jsdelivr.net` each time it opens: it needs network access, and it sends the request to a third party.
- Styles are generated at runtime, in the browser. It is not how a built project behaves, so a result that looks right here still needs checking in the project's own build.

## Verify

Open the page in a browser and confirm one utility class renders, for example a large bold heading. The design skill uses this path for previews when a project has no build.
