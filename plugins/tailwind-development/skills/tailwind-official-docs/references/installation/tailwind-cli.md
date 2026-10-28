# Install with the Tailwind CLI

Read https://tailwindcss.com/docs/installation/tailwind-cli whole. Follow it over this file.

## Use this path when

- The project has no bundler.
- The project wants Tailwind as a separate build step.
- The machine has no Node.js: use the standalone executable.

## Set it up

1. Install `tailwindcss` and `@tailwindcss/cli` with the project's package manager.
2. Add `@import "tailwindcss";` to the input CSS file.
3. Read the installed CLI's `--help` for the build options.
4. Add the build commands to `package.json` scripts.
5. Link the output file in each page's `<head>`.

## Use the standalone executable

1. Download it from https://github.com/tailwindlabs/tailwindcss/releases.
2. Pick the release that matches the project's `tailwindcss` version.
3. Pick the file for the user's platform.
4. Check it against the release's `sha256sums.txt` before running it.
5. Never install the npm package `@tailwindcss/standalone`.

## Check the project

- Replace `npx tailwindcss` calls with `@tailwindcss/cli`.
- Remove `@tailwind` directives.
- Run the build from the templates' root, or it misses classes.

## Verify

1. Add one class the project could not produce before.
2. Run the build.
3. Confirm the output file has it, then remove the class.
