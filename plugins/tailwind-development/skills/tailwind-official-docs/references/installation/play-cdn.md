# Use the Play CDN

Read https://tailwindcss.com/docs/installation/play-cdn whole. Where it differs from this file, follow the page.

## Use it when

- The task is a browser prototype, a standalone preview page or a bug reproduction, with no build.
- Never use it for production: Tailwind states it is for development only. Give a project that ships a build path or its framework guide.

## Set it up

1. Add the script tag the page shows, loading `@tailwindcss/browser` from jsDelivr, to the page's `<head>`.
2. Put custom CSS with Tailwind features in a `<style type="text/tailwindcss">` block.
3. Pin the project's exact version in the URL when the preview must match it. To add a Subresource Integrity hash, point at the package's own `dist/index.global.js` instead of the short package URL, whose minified copy jsDelivr generates, and take its SHA-256 from `https://data.jsdelivr.com/v1/packages/npm/@tailwindcss/browser@<version>?structure=flat`.

## Tell the user

- The page fetches a script from `cdn.jsdelivr.net` each time it opens.
- The browser generates the styles at run time, unlike a built project: check the result again in the project's own build.

## Verify

Open the page and confirm one utility class renders.
