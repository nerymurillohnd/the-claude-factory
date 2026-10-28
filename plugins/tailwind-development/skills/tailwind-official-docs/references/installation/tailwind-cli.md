# Installing with the Tailwind CLI

Official page: https://tailwindcss.com/docs/installation/tailwind-cli. Read it whole; where it differs from this file, follow the page.

## When this path fits

- The project has no bundler (static HTML, server-rendered templates), or wants Tailwind as a separate build step.
- Without Node.js, the standalone executable replaces the npm packages.

## What the setup consists of

1. The packages the page names (`tailwindcss` and `@tailwindcss/cli`), installed with the package manager the lockfile names.
2. `@import "tailwindcss";` in the input CSS file.
3. A build from the input file to an output file, kept in `package.json` scripts when the project has them. Take the options from the installed CLI's `--help`: they change between releases.
4. The output file linked from each page's `<head>`.

## Standalone executable

- Download it from https://github.com/tailwindlabs/tailwindcss/releases, at the release that matches the project's `tailwindcss` version (the latest for a new project), choosing the file for the user's platform.
- Verify it against the release's `sha256sums.txt` before running it.
- The npm package `@tailwindcss/standalone` is not this executable: never install it.

## Check in the project

- `@tailwind` directives and v3 CLI calls (`npx tailwindcss …`): in v4 the CLI is `@tailwindcss/cli` (`upgrade-guide#using-tailwind-cli`).
- The working directory of the build: the CLI scans from it, so a build started elsewhere can miss classes (`detecting-classes-in-source-files#setting-your-base-path`).

## Verify

Add one class the existing styles cannot produce, run a build, confirm the output file contains it, then remove it.
