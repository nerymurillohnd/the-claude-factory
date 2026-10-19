# SvelteKit Form Actions and Remote Functions

> Precedence: the SvelteKit changelog and source code win over the docs, and the docs win over this file. Before relying on an exact signature, fetch the live section (see "Official sources").
>
> Applies to SvelteKit 3 projects. A SvelteKit 2 project migrates first ([migrating-to-kit-3.md](migrating-to-kit-3.md)); write SvelteKit 2 code only when the user declines the migration or the request says to proceed without questions.

## Contents

- [Choosing between them](#choosing-between-them)
- [Form actions](#form-actions)
- [Progressive enhancement with use enhance](#progressive-enhancement-with-use-enhance)
- [Enabling remote functions](#enabling-remote-functions)
- [query, query.batch and query.live](#query-querybatch-and-querylive)
- [form](#form)
- [command](#command)
- [Single-flight mutations](#single-flight-mutations)
- [prerender](#prerender)
- [Validation, errors and the request event](#validation-errors-and-the-request-event)
- [Fetch before writing when](#fetch-before-writing-when)
- [Official sources](#official-sources)

## Choosing between them

Form actions are stable and feature-complete. Remote functions add type safety and single-flight mutations, are where development is focused, and are still experimental in 3.0 (not covered by semantic versioning). Use remote functions when the project already enables them; otherwise use form actions and `load`.

## Form actions

```ts
// src/routes/login/+page.server.ts
import { fail, redirect } from "@sveltejs/kit";
import * as db from "#lib/server/db.js";
import type { Actions } from "./$types";

export const actions = {
  login: async ({ request, cookies, locals }) => {
    const data = await request.formData();
    const email = String(data.get("email") ?? "");
    const user = await db.findUser(email);
    if (!user) return fail(400, { email, missing: true });
    cookies.set("sessionid", await db.createSession(user), { path: "/" });
    locals.user = user; // handle ran before the action; keep locals in sync
    redirect(303, "/dashboard");
  },
} satisfies Actions;
```

- Invoke with `<form method="POST" action="?/login">`, from another page with `action="/login?/login"`, or per button with `formaction`. A page cannot mix `default` with named actions.
- The action result is the page's `form` prop and `page.form`; `fail(status, data)` sets `page.status`. Return only safe fields (never the password).
- Since 3.0, enhanced submissions respond with the `fail` status code (data returns 200, no data returns 204), and a page with actions cannot be prerendered.
- After an action, the page's `load` functions run again.
- `ActionResult` and `SubmitFunction` are exported from `$app/forms` since 3.0.
- A cross-origin form submission without a `Content-Type` header is rejected as CSRF since 3.0.

## Progressive enhancement with use enhance

```svelte
<script lang="ts">
	import { enhance } from '$app/forms';
	import type { PageProps } from './$types';
	let { form }: PageProps = $props();
	let busy = $state(false);
</script>

<form
	method="POST"
	action="?/login"
	use:enhance={() => {
		busy = true;
		return async ({ update }) => {
			await update({ reset: false });
			busy = false;
		};
	}}
>
	<input name="email" value={form?.email ?? ''} />
	{#if form?.missing}<p>Unknown email</p>{/if}
	<button disabled={busy}>Log in</button>
</form>
```

- Without a callback, `use:enhance` emulates the browser: it updates `form`, resets the form, runs `refreshAll` on success, follows redirects with `goto`, and renders the nearest `+error`.
- Since 3.0, a form whose `action` points to another page navigates there on success or failure, as a native submission would. Pass `update({ navigate: false })` to stay on the current page (the 2.x behaviour).
- `update` options: `reset` (default `true`), `refreshAll` (default `true` on success, `false` on failure; `invalidateAll` is a deprecated alias), `navigate`.
- `applyAction(result)` updates `form` and `page.status`, follows a redirect, or renders the error boundary, but does not navigate to a non-redirect `result.location` or refresh data.
- `use:enhance` works only with `method="POST"` forms that target `+page.server` actions. For a hand-written `fetch`, send the `x-sveltekit-action: true` header and parse the reply with `deserialize` from `$app/forms`.

## Enabling remote functions

```ts
sveltekit({
  experimental: { remoteFunctions: true },
  compilerOptions: { experimental: { async: true } },
});
```

Remote functions live in files with a `remote` segment (`posts.remote.ts`) anywhere in `src` except a `server` directory; packages that peer-depend on `@sveltejs/kit` can ship them too. Without the flag, such files fail the build since 3.0. Remote files cannot export schemas; put shared schemas in a normal module. Types (`RemoteQuery`, `RemoteForm`, `RemoteCommand`, and others) are imported from `$app/server` since 3.0.

## query, query.batch and query.live

```ts
// src/routes/blog/posts.remote.ts
import * as v from "valibot";
import { error } from "@sveltejs/kit";
import { query } from "$app/server";
import * as db from "#lib/server/db.js";

export const getPosts = query(async () => db.listPosts());

export const getPost = query(v.string(), async (slug) => {
  const post = await db.getPost(slug);
  if (!post) error(404, "Not found");
  return post;
});
```

```svelte
<script lang="ts">
	import { getPost } from './posts.remote.js';
	let { params } = $props();
	const post = $derived(await getPost(params.slug));
</script>

<h1>{post.title}</h1>
<button onclick={() => getPost(params.slug).refresh()}>Reload</button>
```

- Validate every argument with a Standard Schema; `'unchecked'` skips validation and trusts the client.
- Arguments and results go through devalue (and the `transport` hook). Object, map and set arguments are key-sorted for the cache key.
- Identical calls share one instance: request-scoped on the server, shared while in use on the client. Since 2.61, a query can be awaited anywhere (event handlers, module scope, universal `load`); `.run()` was removed in 2.61, and the live-query `.run()` in 3.0.
- Instances expose `current`, `loading` and `error` (typed `App.Error | undefined` since 3.0) for non-`await` use.
- Queries cannot be used on fully prerendered pages.
- `query.batch(schema, async (args) => (arg, index) => result)` groups calls made in the same macrotask (the n+1 fix). Require 2.60.1 or later for the cross-talk fix.
- `query.live(schema?, async function* (arg) { ... })` streams values over SSE. Instances expose `connected` and `reconnect()`, have no `refresh()`, and are async-iterable. SSR uses the first yielded value. Never cache live responses in a service worker.

## form

```ts
export const createPost = form(
  v.object({ title: v.pipe(v.string(), v.nonEmpty()), body: v.string() }),
  async ({ title, body }, issue) => {
    if (await db.titleTaken(title)) invalid(issue.title("Title already used"));
    const slug = await db.insertPost(title, body);
    redirect(303, `/blog/${slug}`);
  },
);
```

`invalid` comes from `@sveltejs/kit`; `form` from `$app/server`.

```svelte
<form {...createPost} oninput={() => createPost.validate()}>
	<input {...createPost.fields.title.as('text')} />
	{#each createPost.fields.title.issues() ?? [] as i}<p>{i.message}</p>{/each}
	<textarea {...createPost.fields.body.as('text')}></textarea>
	<button disabled={!!createPost.pending}>Publish</button>
</form>
```

- Since 3.0, every control must come from `fields.<name>.as(type, …)`; a hand-written `name` is rejected on submit. `.as(type, value)` sets the rendered and reset value; radios and option checkboxes take the checked state as a third argument.
- Unchecked checkboxes and empty selects send nothing: give booleans and arrays defaults in the schema (`v.optional(v.boolean(), false)`).
- Prefix sensitive fields with `_` (`_password`) so they are never sent back after an invalid submission.
- `validate()` reports only fields the user touched; `validate({ all: true })` checks all (the docs still show the removed `includeUntouched`). `preflight(schema)` validates on the client before sending.
- Field helpers: `value()`, `set()`, `issues()`, `allIssues()`; the changelog adds `dirty()` and `touched()` (3.0) and the form-level `submitted` flag (2.69). Check the live types for their exact shapes.
- `result` holds the returned value until the next submit or navigation. Errors render the nearest `+error.svelte`.
- `form.enhance(async (f) => { if (await f.submit()) f.element.reset(); })` customizes submission; enhanced forms are not reset automatically.
- `form.for(id)` isolates list instances; use `.as('submit', value)` for multi-button forms.

## command

`command(schema, fn)` writes data from event handlers. It cannot run during render, cannot `redirect` (return `{ redirect }` and navigate on the client), and exposes `pending`. Prefer `form` where it fits, because it works without JavaScript.

## Single-flight mutations

By default a successful `form` refreshes every query and `load`; a `command` refreshes nothing. Refresh precisely inside the handler, and the results ride back in the same response:

```ts
export const addLike = command(v.string(), async (id) => {
  await db.like(id);
  void getLikes(id).refresh(); // or getLikes(id).set(value), or liveQuery(arg).reconnect()
});
```

Calling `refresh()`, `set()` or `reconnect()` in a `form` handler replaces its refresh-everything default. When the client knows which instances are on screen, it requests them, and the server must accept them:

```ts
// client
await addPost(data).updates(
  getPosts({ filter }).withOverride((p) => [draft, ...p]),
);
// server, inside the command or form handler
for (const { arg, query, ignore } of requested(getPosts, 10)) {
  if (arg.filter.startsWith("author:")) void query.refresh();
  else ignore();
}
```

- `limit` is required: the list comes from the client, so an unbounded list is a denial-of-service risk.
- Since 3.0, each requested update must be refreshed, set, reconnected or explicitly ignored (`ignore()`, or `await requested(fn, n).ignoreAll()`); otherwise that query errors on the client. `await requested(fn, n).refreshAll()` refreshes all of them.

## prerender

`prerender(schema?, fn, { inputs?, dynamic? })` runs at build time; results are cached with the browser Cache API until the next deployment. Without `dynamic: true`, calls with arguments not prerendered fail.

## Validation, errors and the request event

- A failed argument validation returns a generic 400 and reaches `handleError` with `kind: 'validation'` and `issues`; `handleValidationError` is removed in 3.0. Do not echo issues to attackers.
- `getRequestEvent()` works in all remote functions. Only `form` and `command` may set cookies; none may set headers.
- In `query`, reading `event.url`, `event.params` or `event.route` throws since 3.0: pass the values as arguments. In `form` and `command` they describe the calling page and are client-controlled, so never authorize with them.
- Remote responses carry `cache-control: private, no-store`.

## Fetch before writing when

- You use any remote-function API: the feature is experimental and its signatures move between releases.
- You need `dirty()`, `touched()`, `submitted`, `withOverride`, or `requested` types.
- You write a custom `use:enhance` callback or a manual `fetch` to an action.
- You combine remote functions with prerendering, service workers or `query.live`.

## Official sources

Fetch the sections the task touches in one call, choosing them from this list:

```text
mcp__plugin_svelte-development_svelte__get-documentation
  section: ["kit/form-actions", "kit/remote-functions"]
```

Sections: `kit/form-actions`, `kit/remote-functions`, `kit/$app-forms`, `kit/$app-server`, `kit/@sveltejs-kit`.

Without the MCP server, download the raw text; the single quotes keep the shell from expanding `$` in a path:

```sh
curl -sS 'https://svelte.dev/docs/kit/remote-functions/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/form-actions/llms.txt'
curl -sS 'https://svelte.dev/docs/kit/$app-server/llms.txt'
```

- Changelog: `https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md`

Read only the changelog entries newer than the installed version (the full procedure is in `${CLAUDE_PLUGIN_ROOT}/skills/svelte-best-practices/references/changelogs.md`):

```sh
URL='https://raw.githubusercontent.com/sveltejs/kit/main/packages/kit/CHANGELOG.md'
V="$(node -p "require('@sveltejs/kit/package.json').version")"  # the installed version
curl -sS "$URL" | grep -c "^## $V\$"  # must print 1
curl -sS "$URL" | awk -v v="## $V" '$0==v{exit} {print}'
```
