# Installing with the Tailwind CLI

Official page: https://tailwindcss.com/docs/installation/tailwind-cli. It is the source of truth: when this file and the page disagree, the page wins and this file is out of date. Checked against the page, the CLI's source and the v4.3.3 release on 2026-10-27.

## When this path fits

- The project has no bundler (static HTML, a server-rendered app whose templates are not built by Vite or PostCSS), or it wants Tailwind as a separate build step.
- Without Node.js, the standalone executable below replaces the npm packages.

## What the setup consists of (npm)

1. Two packages: `tailwindcss` and `@tailwindcss/cli`, installed with the project's package manager (SKILL.md, "Installation", step 1).
2. One line in the input CSS file: `@import "tailwindcss";`.
3. A build that reads the input file and writes the compiled file, through the project's package runner: `npx @tailwindcss/cli -i <input.css> -o <output.css>`, adding `--watch` while developing. Put the commands in `package.json` scripts when the project has them, so the rest of the team runs the same build.
4. The output file linked from each page's `<head>`, with the path relative to that page.

## Build options

From the CLI's source (`packages/@tailwindcss-cli/src/commands/build/index.ts`). Read the installed CLI's own `--help` before relying on one, since options change between versions:

| Option | What it does |
| --- | --- |
| `-i`, `--input` | The input CSS file |
| `-o`, `--output` | The output file (standard output by default) |
| `-w`, `--watch` | Rebuild on changes; `--watch=always` keeps watching when standard input closes |
| `--poll` | Watch by polling instead of filesystem events; added in v4.3.3 |
| `-m`, `--minify` | Optimize and minify, for production |
| `--optimize` | Optimize without minifying |
| `--cwd` | The working directory for the build |
| `--map` | Write a source map |
| `--silent` | Only print errors |

Production builds use `--minify` instead of `--watch`.

## Standalone executable (no Node.js)

- Download it from the Tailwind CSS GitHub releases: https://github.com/tailwindlabs/tailwindcss/releases. Take the release whose version matches the project's `tailwindcss` version, or the latest for a new project (v4.3.3 on 2026-10-27).
- One file per platform: `tailwindcss-macos-arm64`, `tailwindcss-macos-x64`, `tailwindcss-linux-x64`, `tailwindcss-linux-arm64`, their `-musl` variants for Alpine and other musl systems, and `tailwindcss-windows-x64.exe`.
- Verify the download against `sha256sums.txt` from the same release before running it, make it executable on macOS and Linux, and keep it out of version control unless the project already commits tools.
- It takes the same build options as the npm CLI, run as the downloaded file instead of `npx @tailwindcss/cli`.
- Never install the npm package `@tailwindcss/standalone`: it is not the standalone executable.

## Check in the project

- `@tailwind base/components/utilities` in the input CSS, and a v3 `tailwindcss` CLI call (`npx tailwindcss …`): in v4 the CLI is the `@tailwindcss/cli` package (`upgrade-guide#using-tailwind-cli`).
- Where the templates live relative to the working directory: the CLI scans from it, so a build started elsewhere may miss classes (`detecting-classes-in-source-files#setting-your-base-path`).
- The output file in version control: decide with the project whether it is a build artifact.

## Verify

SKILL.md, "Installation", step 3: one probe class that the existing styles cannot produce, a build, and the output file checked for it.
