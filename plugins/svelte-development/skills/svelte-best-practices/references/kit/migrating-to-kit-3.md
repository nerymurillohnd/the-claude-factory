# Migrating to SvelteKit 3

> Precedence: the SvelteKit changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").

## Contents

- [Before you start](#before-you-start)
- [Running the migration](#running-the-migration)
- [Old to new](#old-to-new)
- [Manual checklist](#manual-checklist)
- [Verifying the result](#verifying-the-result)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Before you start

- Upgrade to the latest 2.x first and fix its deprecation warnings; many 3.0 removals warn there.
- Minimums: Node 22.17, Vite 8.0.12, `@sveltejs/vite-plugin-svelte` 7, Svelte 5.57.1, TypeScript 6 when used, and the adapter majors listed in the adapters reference.
- Commit everything; the migration rewrites many files.

## Running the migration

```sh
npx sv migrate sveltekit-3 --tasks         # list tasks without running them
npx sv migrate sveltekit-3 --tasks params  # run one task (prerequisites always run)
npx sv migrate sveltekit-3 --tasks all     # run everything in one diff
```

Flags for a run without a person at the prompt: `--cwd <path>` picks the project, `--no-git-check` skips the dirty-working-tree prompt, `--confirm` skips only the final confirmation (it does not choose the migration for you), `--install <package-manager>` or `--no-install` controls the dependency install.

`sv` 1.1.x lists 12 tasks (checked on 1.1.1; the CLI docs page lists only 9 of them):

| Task | What it does |
| --- | --- |
| `package-json` (prerequisite) | Updates dependency versions for 3.0. |
| `tsconfig` (prerequisite) | Extends `$app/tsconfig` instead of `.svelte-kit/tsconfig.json`. |
| `svelte-config` | Moves `svelte.config.*` into `vite.config.*`. |
| `environment` | Migrates to explicit env vars (`$app/env/*`, creates `src/env.*`). |
| `paths` | Migrates removed `$app/paths` APIs and path types. |
| `external-redirects` | Opts external redirects into `{ external }`. |
| `shallow-routing` | Replaces `pushState`/`replaceState` with `goto`. |
| `params` | Consolidates matchers into `src/params.*`. |
| `imports` | Moves SvelteKit APIs to their 3.0 modules. |
| `lib-alias` | Replaces `$lib` with `#lib` subpath imports. |
| `app-state` | Migrates `$app/stores` to `$app/state`. |
| `collect-migration-instructions` | Writes `MIGRATION_TASKS.md` with the steps it could not automate. |

- Prefer one task at a time with a commit after each; the project is not expected to work until all applicable tasks ran.
- `sv` formats changed files and offers to install dependencies afterwards.
- Search for the exact marker `@migration-task` and work through `MIGRATION_TASKS.md`; neither is done until empty.
- Detection is pattern-based and changes only what it can identify safely. Review the whole diff; a match can be wrong, and anything unmatched stays as it was.
- `--files <glob>` limits what is saved and can leave the project inconsistent; files it skipped are reported as unmodified.

## Old to new

| 2.x | 3.0 |
| --- | --- |
| `svelte.config.js` with `kit: {…}` | `sveltekit({…})` in `vite.config.*`, options top-level |
| `$lib/x` | `#lib/x.js` via `package.json` `"imports"` (extension required) |
| `extends: './.svelte-kit/tsconfig.json'` | `extends: '$app/tsconfig'` plus own `include`/`exclude` |
| `$app/stores` (`$page`) | `$app/state` (`page`) |
| `$app/environment` | `$app/env` |
| `$env/static/private` and the other `$env/*` | `src/env.ts` + `$app/env/private` / `$app/env/public` (aliases kept until Kit 4) |
| `$service-worker` | `$app/env` (`version`), `$app/manifest`, `$app/paths`, `$app/service-worker` (`self`) |
| `base + resolveRoute('/blog/[slug]', p)` | `resolve('/blog/[slug]', p)` |
| `assets + '/foo.png'` | `asset('foo.png')` |
| `Pathname`, `Asset` types | `Path`, `AssetPath` (no leading `/`) |
| `pushState(url, s)` / `replaceState(url, s)` | `goto(url, { shallow: true, state: s })` (+ `replace: true`) |
| `invalidateAll()` | `refreshAll()` |
| `goto` `noScroll`/`keepFocus` | `reset: false` |
| `goto` `replaceState` / `invalidateAll` options | `replace` / `refreshAll` |
| `data-sveltekit-noscroll`, `data-sveltekit-keepfocus` | `data-sveltekit-reset="false"` |
| `data-sveltekit-*="off"` | `="false"` |
| `src/params/x.js` with `match` | `src/params.ts` with `defineParams` from `@sveltejs/kit/params` |
| `error(404, { message, code })` | `error(404, message, { code })` |
| `handleValidationError` | `handleError` with `kind: 'validation'` |
| `redirect(307, 'https://other.site')` | `redirect(307, url, { external: […] })` |
| `csrf.checkOrigin: false` | `csrf.trustedOrigins: [...]` |
| `prerender.origin`, adapter-node `ORIGIN` | `paths.origin` |
| `experimental.tracing` / `instrumentation` | `tracing: { server: true }` / automatic |
| `vitePlugin: {…}` | options passed directly to `sveltekit(...)` |
| `preloadStrategy` | removed (`modulepreload` always) |
| `export const snapshot` | `snapshot({ capture, restore })` from `$app/navigation` |
| `json(...)`, `text(...)` | `Response.json(...)`, `new Response(text)` |
| `Handle` and hook types from `@sveltejs/kit` | from `@sveltejs/kit/hooks` |
| `defineEnvVars` from `@sveltejs/kit/hooks` | from `@sveltejs/kit/env` |
| remote function types from `@sveltejs/kit` | from `$app/server` |
| navigation types, `GotoOptions` | from `$app/navigation` |
| `ActionResult`, `SubmitFunction` | from `$app/forms` |
| `Page`, `ReadonlyURL` | from `$app/state` |
| `CookieSerializeOptions`, `CookieParseOptions` | `SerializeOptions`, `ParseOptions` |
| `validate({ includeUntouched: true })` | `validate({ all: true })` |
| `platform.env`, `platform.context` (Cloudflare) | `env`, `waitUntil` from `cloudflare:workers`; `request.cf`; global `caches` |
| `await getRequest(...)` / `await setResponse(...)` | synchronous calls |
| `import '@sveltejs/kit/node/polyfills'` | delete |

## Manual checklist

Check each item after the tasks run, whether or not a task touched it:

- Errors: `handleError` receives app errors and 404s; filter routine ones from logs. It may return `status`. `App.Error` always has `status`. Rendering errors go to the nearest `+error.svelte`; an async client `handleError` needs `compilerOptions.experimental.async`.
- Forms: enhanced cross-page actions navigate to the action page (`update({ navigate: false })` restores 2.x). Responses use the `fail` status. Cross-origin posts without `Content-Type` are rejected.
- Navigation: `goto` rejects non-app URLs (use `location.href`). `preloadData` can return `type: 'error'`. `preloadCode` takes a route ID. `delta` exists only on `popstate`. Shallow routing fires navigation hooks. Clicking a link to the current URL refreshes data.
- `page.url` is read-only: copy it with `new URL(page.url.href)` before mutating.
- `updated` polls hourly by default; set `version.pollInterval: 0` if unwanted.
- Cookies: names must be ASCII; `path` defaults to `'/'`. Review cookies that relied on the current-path default.
- Responses: `204` and other empty `2xx` have no body; clients must not parse them.
- Server-only rules: any `server` directory (outside `src/routes` and `static`) and any file named `server.*` is server-only. Browser imports of such files fail.
- Remote functions: enable `experimental.remoteFunctions` (any `*.remote.*` file errors without it); use `field.as(...)` for every control; pass values to queries instead of reading `event.url`/`params`/`route`; handle or `ignore()` every `requested` entry.
- Types: `RouteId` covers only routes with `+page` or `+server`; `Path` values lose the leading `/` (`asset('foo.png')`, `resolve('blog/x')`).
- Route `config` from `+page.ts`/`+layout.ts` overrides the server file's.
- Service worker: separate `src/service-worker/tsconfig.json` extending `$app/tsconfig/service-worker`, root excludes it; registration uses `type: 'module'`.
- Dev CORS for `static/` is handled by Vite: configure `server.cors` if you relied on `*`.
- Adapters: upgrade to the 3.0-compatible majors; Cloudflare code must stop using `platform`; Vercel `edge` and Node 20 runtimes are gone; Netlify reads `publish` from adapter options; `adapter-cloudflare-workers` has no Kit 3 version.
- Custom adapters: follow the migration guide's adapter API section.
- Query parameters beginning with `x-sveltekit-` are rejected.
- `Server` and `SSRManifest` are no longer public types.
- `form.error` is typed `App.Error | undefined`, no longer `any`.
- The `alias` option is deprecated; use `#` subpath imports.
- Sourcemaps are generated and applied to stack traces; adapters must not rebundle the output destructively.

## Verifying the result

1. The project's check with no errors, then the unit tests and the build:

   ```sh
   npm run check        # or: npx --no-install svelte-kit sync && npx --no-install svelte-check
   npm test             # when the project has tests
   npm run build
   ```

2. `npm run preview` (the `vite preview` script sv projects have) against the build: forms (CSRF only runs in builds), redirects, error pages, cookies.
3. Search the code for leftovers; every match needs a decision:

   ```sh
   grep -rnE '\$app/stores|\$lib/|\$env/|\$service-worker|invalidateAll|pushState|replaceState|resolveRoute|checkOrigin|svelte\.config|@migration-task' --exclude-dir=node_modules --exclude-dir=.svelte-kit --exclude-dir=build .
   ```

   Run it from the project root over the whole tree, not only `src`: `$lib` and `svelte.config` leftovers also sit in `vite.config.*`, `tests/` and root files. Exclude `node_modules`, `.svelte-kit` and `build`.

4. Deploy to a preview environment before production.

## Fetch before writing when

- Any table row above is ambiguous for your code, or you meet a 2.x API not listed here.
- You maintain a custom adapter, use `builder.instrument`, or ship a library with `@sveltejs/package`.
- The `sv` version differs from 1.1.x: list its tasks again with `--tasks`.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["kit/migrating-to-sveltekit-3", "cli/sv-migrate"]
```

Sections: `kit/migrating-to-sveltekit-3`, `cli/sv-migrate`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/kit/migrating-to-sveltekit-3/llms.txt'
curl -sS 'https://svelte.dev/docs/cli/sv-migrate/llms.txt'
```

- Changelogs: `https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md`, `https://raw.githubusercontent.com/sveltejs/cli/main/packages/sv/CHANGELOG.md`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md'
V="$(node -p "require('@sveltejs/kit/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
