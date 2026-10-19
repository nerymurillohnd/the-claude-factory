# SvelteKit Security

> Precedence: the SvelteKit changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").
>
> Applies to SvelteKit 3 projects. A SvelteKit 2 project migrates first ([migrating-to-kit-3.md](migrating-to-kit-3.md)); write SvelteKit 2 code only when the user declines the migration or the request says to proceed without questions.

## Contents

- [Minimum versions with security fixes](#minimum-versions-with-security-fixes)
- [CSRF protection](#csrf-protection)
- [Redirects](#redirects)
- [Secrets and the server boundary](#secrets-and-the-server-boundary)
- [Data that reaches the browser](#data-that-reaches-the-browser)
- [Remote function hardening](#remote-function-hardening)
- [Raw HTML](#raw-html)
- [Content Security Policy](#content-security-policy)
- [Headers, cookies and proxies](#headers-cookies-and-proxies)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Minimum versions with security fixes

Kit 3.0.0 includes every fix below; a project still on 2.x must be at least on the listed version.

| Package | Version | Fix |
| --- | --- | --- |
| `@sveltejs/kit` | 2.60.1 | `query.batch` cross-talk between callers |
| `@sveltejs/kit` | 2.65.2 | remote function responses sent with `cache-control: private, no-store` |
| `@sveltejs/kit` | 2.69.1 | prototype pollution when deleting file inputs |
| `@sveltejs/kit` | 2.70.0 | CSRF protection enabled in builds with a non-production `NODE_ENV` |
| `@sveltejs/kit` | 2.70.2 | quadratic backtracking in `Accept` header negotiation |
| `svelte` | 5.55.7 | XSS through `hydratable` with user content |

Kit 3.0.0 also fixes off-site trailing-slash redirects from scheme-like path segments, path traversal when previewing prerendered output on Windows, and enhanced form results navigating to another origin. Its `svelte` peer is `^5.57.1`.

## CSRF protection

- Always on in 3.0: `csrf.checkOrigin` is removed and cannot disable it. Same-origin is judged against `paths.origin` when set, otherwise the origin derived from the request.
- It covers mutating form submissions and remote function calls. Since 3.0, a cross-origin mutating request without a `Content-Type` header is also rejected.
- Allow specific partners with full origins: `csrf: { trustedOrigins: ['https://payments.example.com'] }`. `'*'` trusts everyone and is not recommended.
- Checks apply only to production builds, not `vite dev`; test CSRF behaviour against a build.
- `+server` JSON APIs called with `fetch` and `Content-Type: application/json` are outside the form check: authenticate them yourself (for example with `SameSite` cookies and an explicit origin check in `handle`).

## Redirects

Since 3.0, `redirect` to another origin throws unless opted in:

```ts
import { redirect } from "@sveltejs/kit";

redirect(303, "/dashboard"); // same origin: fine
redirect(307, "https://auth.example.com/login", {
  external: ["https://auth.example.com"],
});
redirect(307, url, { external: true }); // any origin except javascript: URLs
```

- Prefer an origin allow-list to `external: true`, especially for `redirectTo` values taken from the query string. `data:` URLs count as external.
- Never call `redirect` inside a `try` block that catches it.
- `command` remote functions cannot redirect.

## Secrets and the server boundary

- Keep secrets in private variables declared in `src/env.ts` and read them from `$app/env/private`, which cannot be imported by browser code. `public: true` variables, and `static: true` public values, ship to every visitor.
- Put database clients and credentials in server-only modules: a `server` file segment or any `server` directory outside `src/routes` and `static`. The build fails if browser code reaches them, even indirectly or through dynamic imports. Use `import type` when only types are needed.
- The boundary check is disabled under `process.env.TEST === 'true'`, so tests do not prove it; a production build does.
- Never store per-user data in module-level variables on the server: they are shared by every request. Use `event.locals`, cookies or a database, and context in components.

## Data that reaches the browser

- Everything a server `load` returns is serialized into the page and the `__data.json` response. Return only fields the user may see.
- Layout data is visible to every child page through `page.data`.
- Form `fail(...)` data and remote form values are echoed back: never return passwords. Name sensitive remote form fields with a leading `_` so they are not repopulated.
- `handleError` with `kind: 'unknown'` receives raw errors that may contain secrets: log them, return a generic message. Do not return validation `issues` unless intended.
- Use ISR (Vercel) or prerendering only for content identical for all visitors.

## Remote function hardening

- Validate every argument with a Standard Schema; `'unchecked'` trusts attacker-controlled input.
- Authorize from `locals` populated in `handle`, never from `event.url`, `params` or `route` (client-controlled in `form` and `command`, and throwing in `query`).
- Always pass a realistic `limit` to `requested(fn, limit)`; the list is client-controlled.
- Do not cache live queries or other `no-store` responses in a service worker.

## Raw HTML

`{@html ...}` inserts markup without escaping. Use it only with content you control or have sanitized with a maintained HTML sanitizer. Markdown or CMS output is untrusted until sanitized. `hydratable` with user content needs `svelte` 5.55.7 or later.

## Content Security Policy

```ts
sveltekit({
  csp: {
    mode: "auto", // nonces for dynamic pages, hashes for prerendered pages
    directives: {
      "script-src": ["self"],
      "object-src": ["none"],
      "base-uri": ["self"],
    },
    reportOnly: { "script-src": ["self"], "report-uri": ["/csp-report"] },
  },
});
```

- SvelteKit adds nonces or hashes for the scripts and styles it generates. Add `nonce="%sveltekit.nonce%"` to scripts you place in `app.html`.
- Nonces on prerendered pages are forbidden; prerendered pages get the policy through a `<meta http-equiv>` tag, which ignores `frame-ancestors`, `report-uri` and `sandbox` (set those as HTTP headers at the host).
- If you configure `trusted-types`, include `'svelte-trusted-html'` (and `'sveltekit-trusted-url'` when the service worker is registered automatically). Since 3.0 the HTML policy is required only when client code ships.
- Outside SvelteKit, Svelte's `render(App, { csp: { nonce } })` or `{ csp: { hash: true } }` covers the inline `hydratable` script; never reuse a nonce across responses.
- For per-request policies beyond the config, set headers in `handle`.

## Headers, cookies and proxies

- Since 3.0, requests with query parameters starting with `x-sveltekit-` are rejected; do not use that prefix for your own parameters.
- Cookies default to `httpOnly: true`, `secure: true` (except in development) and `path: '/'`. Set `sameSite` deliberately for session cookies.
- `PROTOCOL_HEADER`, `HOST_HEADER`, `ADDRESS_HEADER` and `XFF_DEPTH` on Node and Bun trust forwarded headers; set them only behind a proxy that overwrites those headers, and count `XFF_DEPTH` from the right.
- Set `paths.origin` behind proxies so CSRF checks compare against the real public origin.

## Fetch before writing when

- You change `csp`, `csrf` or redirect behaviour, or add `trusted-types`.
- You expose an API to other origins or accept webhooks.
- A security advisory names SvelteKit, Svelte or an adapter: read the changelogs from your installed version upward.
- You handle authentication, sessions or file uploads.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["kit/@sveltejs-kit-vite", "kit/server-only-modules"]
```

Sections: `kit/@sveltejs-kit-vite`, `kit/server-only-modules`, `kit/environment-variables`, `kit/hooks`, `kit/remote-functions`, `kit/state-management`, `kit/auth`, `svelte/@html`, `svelte/hydratable`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/kit/@sveltejs-kit-vite/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/server-only-modules/llms.txt'
curl -sS 'https://svelte.dev/docs/svelte/@html/llms.txt'
```

- Changelogs: `https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md`, `https://raw.githubusercontent.com/sveltejs/svelte/main/packages/svelte/CHANGELOG.md`
- Advisories: `https://github.com/sveltejs/kit/security/advisories`, `https://github.com/sveltejs/svelte/security/advisories`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md'
V="$(node -p "require('@sveltejs/kit/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
