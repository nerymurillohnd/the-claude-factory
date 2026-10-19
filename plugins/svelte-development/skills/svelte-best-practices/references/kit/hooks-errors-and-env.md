# SvelteKit Hooks, Errors, Environment and Service Workers

> Precedence: the SvelteKit changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").
>
> Applies to SvelteKit 3 projects. A SvelteKit 2 project migrates first ([migrating-to-kit-3.md](migrating-to-kit-3.md)); write SvelteKit 2 code only when the user declines the migration or the request says to proceed without questions.

## Contents

- [Hook files](#hook-files)
- [handle and handleFetch](#handle-and-handlefetch)
- [handleError](#handleerror)
- [init, reroute and transport](#init-reroute-and-transport)
- [Throwing errors](#throwing-errors)
- [Environment variables](#environment-variables)
- [Build and runtime flags](#build-and-runtime-flags)
- [Cookies](#cookies)
- [Service workers](#service-workers)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Hook files

| File | Hooks |
| --- | --- |
| `src/hooks.server.ts` | `handle`, `handleFetch`, `handleError`, `init` |
| `src/hooks.client.ts` | `handleError`, `init` |
| `src/hooks.ts` (both sides) | `reroute`, `transport` |

Hook types (`Handle`, `HandleFetch`, `HandleServerError`, `HandleClientError`, `ServerInit`, `ClientInit`, `Reroute`, `Transport`) are imported from `@sveltejs/kit/hooks` since 3.0, not from `@sveltejs/kit`; `sequence` comes from the same module. SvelteKit warns when a file is named `hook` instead of `hooks`.

## handle and handleFetch

```ts
// src/hooks.server.ts
import { sequence } from "@sveltejs/kit/hooks";
import type { Handle, HandleFetch } from "@sveltejs/kit/hooks";
import * as auth from "#lib/server/auth.js";

const session: Handle = async ({ event, resolve }) => {
  event.locals.user = await auth.fromSession(event.cookies.get("sessionid"));
  return resolve(event);
};

const headers: Handle = async ({ event, resolve }) => {
  const response = await resolve(event, {
    filterSerializedResponseHeaders: (name) => name === "content-range",
    preload: ({ type }) => type === "js" || type === "css",
  });
  response.headers.set("x-frame-options", "DENY");
  return response;
};

export const handle = sequence(session, headers);

export const handleFetch: HandleFetch = ({ request, fetch }) => {
  if (request.url.startsWith("https://api.example.com/")) {
    request = new Request(
      request.url.replace("https://api.example.com/", "http://api.internal/"),
      request,
    );
  }
  return fetch(request);
};
```

- `handle` runs for every server request, including prerendering (guard build-only work with `building` from `$app/env`), but not for static or prerendered assets. `resolve` always returns a `Promise<Response>` (typed so since 3.0) and never throws.
- `resolve` options: `transformPageChunk`, `filterSerializedResponseHeaders`, `preload` (fonts also receive the source `filename` since 3.0).
- Some responses have immutable headers; clone before mutating if needed.
- For remote-function requests, `event.url`, `params` and `route` describe the calling page, are client-controlled, and must never drive authorization.
- `handleFetch` rewrites `event.fetch` calls made on the server. It forwards cookies for same-origin and subdomain requests; for sibling subdomains, set the `cookie` header yourself.

## handleError

Since 3.0, every error reaches `handleError`, with a `kind`:

| `kind` | Source | `error` received | Default exposed value |
| --- | --- | --- | --- |
| `'app'` | `error(...)` | the `App.Error` body | the body |
| `'framework'` | SvelteKit (404, 405, 413…) | `{ status, message }` | the same |
| `'validation'` | remote-function argument (server only) | `{ status: 400, message: 'Bad Request' }`, plus `issues` | `error`, without issues |
| `'unknown'` | any other thrown value | raw value (may be sensitive) | `{ status: 500, message: 'Internal Error' }` |

```ts
import type { HandleServerError } from "@sveltejs/kit/hooks";

export const handleError: HandleServerError = ({ kind, error, event }) => {
  if (kind === "app" || kind === "framework") return error;
  const errorId = crypto.randomUUID();
  console.error(errorId, kind, error, event.url.pathname);
  return { message: "Something went wrong", errorId };
};
```

- Return an `App.Error`; `status` and `message` are optional overrides, so the hook can change the HTTP status since 3.0. Add your own required fields to `App.Error` in `src/app.d.ts` and always return them.
- `handleValidationError` is removed in 3.0. Never return validation `issues` to clients unless you mean to.
- The client hook receives a `NavigationEvent`; errors already handled on the server are not passed to it again. An async client `handleError` needs `compilerOptions.experimental.async` because rendering errors go through it since 3.0.
- `handleError` must never throw. Do not log routine `framework` 404s.

## init, reroute and transport

- `init` runs once at server start or app start in the browser; async work there delays hydration.
- `reroute({ url, fetch })` maps a URL to a different route without changing the address bar or `event.url`. It may be async (use the provided `fetch`), must be pure and idempotent, and its result is cached per URL on the client. It also runs for server route-resolution requests.
- `transport` defines `encode`/`decode` pairs for custom classes crossing the server/client boundary (`load` data, actions, remote functions, `page.state`, snapshots).

## Throwing errors

```ts
import { error } from "@sveltejs/kit";

error(404, "Not found");
error(403, "Forbidden", { code: "NO_ACCESS" }); // extra App.Error fields go third
```

- Since 3.0, the second argument is the message string and extra properties go in a third argument; `error(status, { message, ... })` is deprecated.
- `error`, `redirect`, `isHttpError` and `isRedirect` refer to public types; never `instanceof` the internal classes.
- `App.Error` always includes `status` and `message`. `<svelte:boundary>` `failed` snippets receive an `App.Error` that has passed through `handleError`.

## Environment variables

Explicit environment variables (introduced in 2.63.0) are the 3.0 model. Declare every variable in `src/env.ts`:

```ts
// src/env.ts
import { defineEnvVars } from "@sveltejs/kit/env";
import { building } from "$app/env";
import * as v from "valibot";

export const variables = defineEnvVars({
  DATABASE_URL: {
    schema: building ? v.optional(v.string()) : v.pipe(v.string(), v.url()),
  },
  PUBLIC_ANALYTICS_ID: { public: true, description: "Analytics property ID" },
  SHOW_DEBUG: {
    public: true,
    static: true,
    schema: v.pipe(
      v.optional(v.string(), ""),
      v.transform((s) => s !== ""),
    ),
  },
});
```

```ts
import { DATABASE_URL } from "$app/env/private"; // server-only module
import { PUBLIC_ANALYTICS_ID } from "$app/env/public";
```

- Variables are private by default; `public: true` exposes them through `$app/env/public` and `%sveltekit.env.NAME%` in `app.html`.
- `static: true` inlines the build-time value (enables dead-code elimination); otherwise values are read when the app starts.
- `schema` takes a Standard Schema or a function returning the value (or throwing). Invalid values stop the app from starting or building. Without a schema, a variable must be set but may be empty. Public dynamic values must be devalue-serializable.
- `defineEnvVars` and the `EnvVarConfig` types live in `@sveltejs/kit/env` since 3.0 (they were in `@sveltejs/kit/hooks`).
- `.env` and `.env.local` are loaded during development and build; `env.dir` changes the directory.
- `$env/static/private`, `$env/static/public`, `$env/dynamic/private`, `$env/dynamic/public` and `$app/environment` remain as deprecated aliases until Kit 4. In a SvelteKit 3 project, do not write them in new code; a SvelteKit 2 project keeps them unless it enabled `kit.experimental.explicitEnvironmentVariables` (2.63 or later).

## Build and runtime flags

`$app/env` (renamed from `$app/environment`) exports `browser`, `building`, `dev` and `version` (`config.version.name`). It is importable in service workers. `dev` does not necessarily match `NODE_ENV`.

## Cookies

- 3.0 uses `cookie` v2: names must be ASCII (non-ASCII names such as `á` are rejected), and the option types are `SerializeOptions` and `ParseOptions`.
- `path` defaults to `'/'` since 3.0; pass `path: ''` for the current path and its children.
- `httpOnly` and `secure` default to `true` (`secure` is `false` in development). Disable them only deliberately.
- `cookies.parse(setCookieHeader)` (since 3.0) applies cookies from an upstream response; iterate `headers.getSetCookie()`.
- `event.fetch` forwards cookies only to the app host and its subdomains.

## Service workers

`src/service-worker/index.ts` is bundled for production and registered automatically as a module worker (`type: 'module'` since 3.0). `$service-worker` is removed in 3.0:

| Need | Import |
| --- | --- |
| Typed `self` | `self` from `$app/service-worker` (service workers only) |
| Cache key | `version` from `$app/env` |
| Files to cache | `immutable`, `assets`, `prerendered` from `$app/manifest` |
| URLs | `resolve`, `asset` from `$app/paths` |

`$app/manifest` paths are relative to the base path, so map them through `resolve(...)` before caching. Give the folder its own `tsconfig.json` extending `$app/tsconfig/service-worker` and exclude it from the root config. Do not cache responses marked `no-store` (live queries and remote calls). Browsers do not check for a worker update on client-side navigations; call `registration.update()` yourself if needed.

## Fetch before writing when

- You need exact hook input types or the `kind`-specific fields of `handleError`.
- You add `reroute` with server route resolution, or `transport` for a custom class.
- You validate env vars, use `static` variables, or deploy where variables differ between build and runtime.
- You write a service worker caching strategy.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["kit/hooks", "kit/errors"]
```

Sections: `kit/hooks`, `kit/errors`, `kit/environment-variables`, `kit/@sveltejs-kit-hooks`, `kit/@sveltejs-kit-env`, `kit/$app-env`, `kit/service-workers`, `kit/$app-service-worker`, `kit/$app-manifest`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/kit/hooks/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/errors/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/environment-variables/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/service-workers/llms.txt'
```

- Changelog: `https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md'
V="$(node -p "require('@sveltejs/kit/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
