# The Play CDN

Official page: https://tailwindcss.com/docs/installation/play-cdn. Read it whole; where it differs from this file, follow the page.

## When it fits

- A browser prototype, a standalone preview page or a bug reproduction, with no build.
- Never production: Tailwind states it is for development only. A project that ships takes a build path or its framework guide.

## What it consists of

- The script tag the page shows, loading `@tailwindcss/browser` from jsDelivr in the page's `<head>`.
- Custom CSS with Tailwind features goes in a `<style type="text/tailwindcss">` block.
- To match a project's installed version, pin that exact version in the URL. Only a pinned file can carry a Subresource Integrity hash: point at the package's own `dist/index.global.js`, not the short package URL, whose minified copy jsDelivr generates, and take its SHA-256 from jsDelivr's package API (`https://data.jsdelivr.com/v1/packages/npm/@tailwindcss/browser@<version>?structure=flat`).

## Tell the user

- The page fetches a script from `cdn.jsdelivr.net` each time it opens.
- Styles are generated in the browser at run time, unlike a built project, so a result here still needs checking in the project's own build.

## Verify

Open the page and confirm one utility class renders.
