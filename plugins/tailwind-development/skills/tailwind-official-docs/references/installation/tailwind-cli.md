# Install with the Tailwind CLI

Read https://tailwindcss.com/docs/installation/tailwind-cli whole. Where it differs from this file, follow the page.

## Use this path when

- The project has no bundler (static HTML, server-rendered templates), or wants Tailwind as a separate build step.
- The machine has no Node.js: use the standalone executable instead of the npm packages.

## Set it up

1. Install the packages the page names (`tailwindcss`, `@tailwindcss/cli`) with the package manager the lockfile names.
2. Add `@import "tailwindcss";` to the input CSS file.
3. Build from the input file to an output file, and keep the commands in `package.json` scripts when the project has them. Take the options from the installed CLI's `--help`, since they change between releases.
4. Link the output file from each page's `<head>`.

## Use the standalone executable

1. Download it from https://github.com/tailwindlabs/tailwindcss/releases, at the release that matches the project's `tailwindcss` version (the latest for a new project), in the file for the user's platform.
2. Verify it against the release's `sha256sums.txt` before running it.
3. Never install the npm package `@tailwindcss/standalone`: it is not this executable.

## Check the project

- Replace `@tailwind` directives and v3 CLI calls (`npx tailwindcss …`): in v4 the CLI is `@tailwindcss/cli` (`upgrade-guide#using-tailwind-cli`).
- Run the build from the directory that holds the templates: the CLI scans from its working directory and misses classes elsewhere (`detecting-classes-in-source-files#setting-your-base-path`).

## Verify

Add one class the existing styles cannot produce, run a build, confirm the output file contains it, then remove the class.
