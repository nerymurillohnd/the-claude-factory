# Currency check against changelogs

> Precedence: changelogs and source code win over the docs, and the docs win over this file.

## Contents

- [When to run the check](#when-to-run-the-check)
- [Step 1: find the installed version](#step-1-find-the-installed-version)
- [Step 2: find the latest version](#step-2-find-the-latest-version)
- [Step 3: read only the changelog window](#step-3-read-only-the-changelog-window)
- [Step 4: GitHub releases as a second source](#step-4-github-releases-as-a-second-source)
- [Which source wins](#which-source-wins)
- [Changelog URLs and heading formats](#changelog-urls-and-heading-formats)

## When to run the check

Run it before writing code or advice when any of these holds:

- The installed version is not the latest on the registry (`npm view <package> version` against the command in Step 1): read the window between the two. This is the mechanical check; run it whenever the task depends on exact behaviour.
- A reference here disagrees with what the installed version does, or describes an API the installed version does not have.
- The task touches an experimental feature (`experimental.async`, remote functions, `forkPreloads`, `fork`), configuration, an adapter, or a migration.
- The docs and the observed behavior disagree, or a doc page and a changelog disagree.
- The user asks whether something is current, deprecated or removed.

## Step 1: find the installed version

```sh
npm ls @sveltejs/kit --depth=0      # what is installed (pnpm: pnpm why, yarn: yarn why)
grep -n '"version"' node_modules/@sveltejs/kit/package.json
```

- `package.json` holds a range, not a version; the lockfile and `node_modules` hold what runs.
- In a monorepo, run the command in the package that uses the dependency.

## Step 2: find the latest version

```sh
npm view @sveltejs/kit version            # latest on the registry
npm view @sveltejs/kit time --json        # release date of every version
npm view @sveltejs/kit peerDependencies engines --json
```

If installed equals latest and nothing in the task matches the cases above, stop here.

## Step 3: read only the changelog window

Print the entries newer than the installed version and stop at its heading. Confirm first that the heading exists, or the command prints the whole file:

```sh
URL=https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md
V=3.0.0
curl -sS "$URL" | grep -c "^## $V\$"                 # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```

Changesets packages (Svelte, SvelteKit and its adapters, sv, language tools, vite-plugin-svelte, the Svelte MCP, Astro, prettier-plugin-svelte) use plain `## x.y.z` headings, with prerelease headings such as `## 3.0.0-next.4` between releases. Exact string comparison keeps `## 3.0.0` from matching `## 3.0.0-next.4`.

Tailwind CSS and prettier-plugin-tailwindcss use Keep a Changelog headings, `## [x.y.z] - ` followed by the release date, with an `## [Unreleased]` block on top:

```sh
URL=https://raw.githubusercontent.com/tailwindlabs/tailwindcss/main/CHANGELOG.md
V=4.3.0
curl -sS "$URL" | awk -v v="$V" 'index($0, "## [" v "]")==1{exit} {print}'
```

- Read every entry in the window in full, including patch notes. Changesets repeats prerelease entries under the final release heading (the `## 3.0.0` block of SvelteKit does), so a window that spans a major contains the same items twice.
- Use `curl -sS` and read the raw text. Never use WebFetch for changelogs or docs: it returns a summary, not the source.
- The raw `main` or `master` file can include unreleased entries (`## [Unreleased]`); ignore those unless the user runs a prerelease.

## Step 4: GitHub releases as a second source

```sh
curl -sS 'https://api.github.com/repos/sveltejs/kit/releases?per_page=10'
```

- Unauthenticated requests are limited to 60 per hour per IP; the `x-ratelimit-remaining` header shows what is left. Prefer the raw changelog, which has no such limit.
- Monorepos tag one release per package (`@sveltejs/kit@3.0.0`, `@sveltejs/adapter-node@6.0.0`), so filter the `tag_name` by package.
- prettier-plugin-svelte publishes few GitHub releases; use its changelog.

## Which source wins

1. Changelogs, release notes and the package source code (types, option parsers, the code that runs).
2. The official docs.
3. The reference files in this folder.

When a lower source contradicts a higher one, follow the higher one and tell the user which document is out of date. Record the conflict with its evidence; the known cases are in [known-doc-errata.md](known-doc-errata.md).

## Changelog URLs and heading formats

| Package | Changelog (raw) | Heading format |
| --- | --- | --- |
| `svelte` | https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/kit` | https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/adapter-auto` | https://raw.githubusercontent.com/sveltejs/kit/main/packages/adapter-auto/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/adapter-node` | https://raw.githubusercontent.com/sveltejs/kit/main/packages/adapter-node/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/adapter-static` | https://raw.githubusercontent.com/sveltejs/kit/main/packages/adapter-static/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/adapter-vercel` | https://raw.githubusercontent.com/sveltejs/kit/main/packages/adapter-vercel/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/adapter-cloudflare` | https://raw.githubusercontent.com/sveltejs/kit/main/packages/adapter-cloudflare/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/adapter-netlify` | https://raw.githubusercontent.com/sveltejs/kit/main/packages/adapter-netlify/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/adapter-bun` | https://raw.githubusercontent.com/sveltejs/kit/main/packages/adapter-bun/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/enhanced-img` | https://raw.githubusercontent.com/sveltejs/kit/main/packages/enhanced-img/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/package` | https://raw.githubusercontent.com/sveltejs/kit/main/packages/package/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/vite-plugin-svelte` | https://raw.githubusercontent.com/sveltejs/vite-plugin-svelte/main/packages/vite-plugin-svelte/CHANGELOG.md | `## x.y.z` |
| `sv` | https://raw.githubusercontent.com/sveltejs/cli/main/packages/sv/CHANGELOG.md | `## x.y.z` |
| `svelte-language-server` | https://raw.githubusercontent.com/sveltejs/language-tools/master/packages/language-server/CHANGELOG.md | `## x.y.z` |
| `svelte-check` | https://raw.githubusercontent.com/sveltejs/language-tools/master/packages/svelte-check/CHANGELOG.md | `## x.y.z` |
| `svelte2tsx` | https://raw.githubusercontent.com/sveltejs/language-tools/master/packages/svelte2tsx/CHANGELOG.md | `## x.y.z` |
| `@sveltejs/mcp` (ai-tools `packages/mcp-stdio`) | https://raw.githubusercontent.com/sveltejs/ai-tools/main/packages/mcp-stdio/CHANGELOG.md | `## x.y.z` |
| `astro` | https://raw.githubusercontent.com/withastro/astro/main/packages/astro/CHANGELOG.md | `## x.y.z` |
| `@astrojs/svelte` | https://raw.githubusercontent.com/withastro/astro/main/packages/integrations/svelte/CHANGELOG.md | `## x.y.z` |
| `tailwindcss` (also `@tailwindcss/vite`) | https://raw.githubusercontent.com/tailwindlabs/tailwindcss/main/CHANGELOG.md | `## [x.y.z] - ` plus the release date |
| `prettier-plugin-svelte` | https://raw.githubusercontent.com/sveltejs/prettier-plugin-svelte/master/CHANGELOG.md | `## x.y.z` |
| `prettier-plugin-tailwindcss` | https://raw.githubusercontent.com/tailwindlabs/prettier-plugin-tailwindcss/main/CHANGELOG.md | `## [x.y.z] - ` plus the release date |

GitHub releases endpoints:

| Repository | Releases API |
| --- | --- |
| `sveltejs/svelte` | https://api.github.com/repos/sveltejs/svelte/releases?per_page=10 |
| `sveltejs/kit` | https://api.github.com/repos/sveltejs/kit/releases?per_page=10 |
| `sveltejs/cli` | https://api.github.com/repos/sveltejs/cli/releases?per_page=10 |
| `sveltejs/language-tools` | https://api.github.com/repos/sveltejs/language-tools/releases?per_page=10 |
| `sveltejs/vite-plugin-svelte` | https://api.github.com/repos/sveltejs/vite-plugin-svelte/releases?per_page=10 |
| `sveltejs/ai-tools` | https://api.github.com/repos/sveltejs/ai-tools/releases?per_page=10 |
| `withastro/astro` | https://api.github.com/repos/withastro/astro/releases?per_page=10 |
| `tailwindlabs/tailwindcss` | https://api.github.com/repos/tailwindlabs/tailwindcss/releases?per_page=10 |
| `sveltejs/prettier-plugin-svelte` | https://api.github.com/repos/sveltejs/prettier-plugin-svelte/releases?per_page=10 |
| `tailwindlabs/prettier-plugin-tailwindcss` | https://api.github.com/repos/tailwindlabs/prettier-plugin-tailwindcss/releases?per_page=10 |
