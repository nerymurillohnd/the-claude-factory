# Use the Play CDN

Read https://tailwindcss.com/docs/installation/play-cdn whole. Follow it over this file.

## Use it when

- The task is a prototype, a preview page or a bug reproduction.
- Never use it in production.

## Set it up

1. Add the page's `@tailwindcss/browser` script tag to the `<head>`.
2. Put custom Tailwind CSS in `<style type="text/tailwindcss">`.
3. Pin the project's version in the URL when the preview must match it.

## Add Subresource Integrity

1. Pin an exact version.
2. Link the package file `dist/index.global.js`, not the short package URL.
3. Get its SHA-256 from jsDelivr's package API.
4. Add `integrity="sha256-<hash>"` and `crossorigin="anonymous"`.

## Tell the user

- The page loads a script from `cdn.jsdelivr.net` on every visit.
- Recheck the result in the project's own build.

## Verify

Open the page and confirm one class renders.
