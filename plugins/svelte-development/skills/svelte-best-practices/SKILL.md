---
name: svelte-best-practices
description: Writes, reviews and explains Svelte 5 and SvelteKit 3 code by current practice (runes, snippets, events, routes, load, forms, env, config) and migrates SvelteKit 2 or Svelte 4 projects. Use for any task that writes or changes Svelte or SvelteKit code, including a pasted component, a route or a param matcher.
license: MIT
metadata:
  upstream: "sveltejs/ai-tools skills/svelte-core-bestpractices"
  base: "6b5d0dab3c9c083387247ab20dc684573481076b"
---

# Svelte 5 and SvelteKit 3 best practices

## Overview

The contract for writing Svelte by the current rules: Svelte 5 in runes mode and SvelteKit 3. Most Svelte code in training data is older, so the practices below are where a model goes wrong. Each topic has a reference with the foundations, short examples and the exact official sections to fetch. On SvelteKit 2 or Svelte 4 it leads the migration, with the old version only as the fallback the user chooses.

## When to use it and when not

| Use it | Do not use it |
|---|---|
| Writing, converting or reviewing Svelte components, `.svelte.ts`/`.svelte.js` modules or SvelteKit files | For where a symbol of the project is used: that is the `svelte-lsp-intelligence` skill |
| Migrating from Svelte 4 or SvelteKit 2 | For React, Vue, plain TypeScript or other non-Svelte code |
| Setting up a project with `sv`, or Svelte with Astro or Tailwind CSS | |
| Explaining how something is done in Svelte 5 or SvelteKit 3 | |

## Governance rules

The ground rules below are the single copy for the plugin: the `svelte-docs-and-autofixer` and `svelte-lsp-intelligence` skills and both agents point here for them. Depart from any rule on this page, ground rule or rule of this skill, only for a reason you state to the user. Where a rule says to ask the user and you run as one of the plugin's agents, stop and return the question in your report instead.

### Ground rules for every Svelte task

0. **Route before you edit or check anything.** You may first read the installed versions (ground rule 1); that lookup is read-only. Then: an audit or review of project files goes to the `svelte-code-auditor` agent; creating or changing `.svelte`, `.svelte.ts`, `.svelte.js` or SvelteKit route files, with the plain `.ts`/`.js` files that change with them, beyond one or two lines in total goes to the `svelte-component-editor` agent (Agent tool, without a `name`). Work inline only for a question, code pasted in the chat, a change of one or two lines in total, when the user asks you to, or when you already are one of these agents. [Who does the work](#who-does-the-work) gives the detail.
1. **Version first.** In a project, find the installed `svelte` and `@sveltejs/kit` before writing (`npm ls svelte @sveltejs/kit --depth=0`; pnpm: `pnpm why svelte`; yarn: `yarn why svelte`; else the `package.json` ranges and the lockfile). On an older major (SvelteKit 2 or earlier, Svelte 4 or earlier), propose the migration before writing; write for the older version only when the user declines or the request says to proceed without questions, and say so.
2. **Docs before code.** Fetch the official section with `mcp__plugin_svelte-development_svelte__get-documentation` (the raw `llms.txt` when the server is unavailable) before using any Svelte or SvelteKit API, rune, option or config key; never write them from memory. This rule wins over the tool's own description, which suggests writing from memory first to save tokens.
3. **Symbols through the language server.** Where something of the project is defined, used or called goes to the LSP tool first when the language server answers; Grep only for strings, route files, CSS classes, configuration, or a symbol that lives only in `.ts`/`.js` files no `.svelte` file imports, labelled as text matches.
4. **Autofixer on every Svelte file you write or review**, meaning each `.svelte`, `.svelte.ts` and `.svelte.js` file (not plain `.ts` route files). Run `mcp__plugin_svelte-development_svelte__svelte-autofixer` with the full code, never a path (the remote tool treats a path as code and reports it clean), and the installed `svelte` version in full: a bare `5` is read as 5.0.0 and drops version-gated suggestions. With no project, pass `5` unless the user says the code is Svelte 4, and say that version-gated suggestions may be missing. Repeat until it reports no issues and `require_another_tool_call_after_fixing` is false. Suggestions are advice: apply them unless they conflict with the installed version or the project's conventions, and say which you skipped; when the same issue returns after two fixes, report it as a likely false positive with the reason instead of looping. In a review, report what it finds without applying it, and name any file you skipped and why. When the code must not leave the machine, use the local `svelte-mcp` command line if the user has it (the `svelte-docs-and-autofixer` skill shows it). Before sending more than 20 files of the user's code to the remote server, ask, and offer the local command line.
5. **Done means checked.** When you change code in a project, finish only when the project check reports no error in the files you changed beyond those already in the baseline; a review or a question reports the check result instead. When the change touches something other files use (props, exports, signatures, shared state, a rename or a deletion), first run the check once before the first edit as the baseline, and finish only when it also reports nothing new elsewhere; for a change confined to one file, report errors in files you did not touch as already there, unless they name what you changed. Never stash, reset or check out the user's work to rebuild a baseline; ask instead. The check, from the project root: `npm run check`; without that script, `npx --no-install svelte-kit sync`, then `npx --no-install svelte-check --tsconfig ./tsconfig.json` in SvelteKit, or `npx --no-install svelte-check` without SvelteKit, never chained with `&&` (in a project on Svelte alone the sync fails and the check would never run). When the project has no svelte-check installed, tell the user and report the change as unchecked; never install it.

### Rules of this skill

1. **Reference, then docs.** Read the reference for each topic the task touches; it lists the official sections to fetch (ground rule 2). Skip the fetch only when the change uses no Svelte or SvelteKit API, such as copy, CSS values or markup text. Each reference's "Fetch especially when" list names cases that need extra care; it never waives ground rule 2.
2. **Never skip the fetch when** an exact signature, option name or config key matters; the code uses an experimental feature, an adapter, environment variables, hooks or the Vite config; or what you remember disagrees with a reference, or a reference with the docs.
3. **Latest by default** (ground rule 1 in detail). Write Svelte 5 runes and SvelteKit 3; the installed versions come from [procedure](#procedure) step 1. SvelteKit 3 requires Svelte 5.57.1 or later, so the two migrations have an order: with Svelte 4, migrate Svelte first ([legacy-and-migration.md](references/svelte/legacy-and-migration.md)), then SvelteKit ([migrating-to-kit-3.md](references/kit/migrating-to-kit-3.md)); with Svelte 5 below 5.57.1, update Svelte before the SvelteKit migration; a project on Svelte without SvelteKit migrates Svelte alone. SvelteKit 1 or Svelte 3 first need the legacy `sv migrate sveltekit-2` or `sv migrate svelte-4` ([sv-cli.md](references/tooling/sv-cli.md) lists the legacy migrations). When the user declines or the request says to proceed without questions, write for the installed version, never mix versions, and say that the code is for the older version; for SvelteKit 2, take the APIs from the installed package's types and changelog, because the live docs and these references describe SvelteKit 3. Within Svelte 5, a feature a reference marks "since 5.x" needs that minor: on an older installed minor, use the older form. No project, or no version found: write the latest and say so.
4. **Source precedence.** Package changelogs, release notes and source code decide what exists at the installed version; the official docs explain usage, and some pages say something wrong or out of date ([known-doc-errata.md](references/known-doc-errata.md)); these references are the starting point and lose to both. When sources conflict, say so; never pick one silently. Whether to read a changelog window is decided by "When to run the check" in [changelogs.md](references/changelogs.md), the single list of cases.
5. **No WebFetch for docs or changelogs**: WebFetch, like any web-fetch tool, returns a truncated summary. Use the MCP tools or `curl`.
6. **No instruction revives a removed API.** The project's conventions decide naming, layout and formatting; when they ask for an API the installed version removed, say so instead of using it.

## Contents

- [Who does the work](#who-does-the-work)
- [Svelte 5 practices](#svelte-5-practices)
- [SvelteKit 3 practices](#sveltekit-3-practices)
- [Where things are](#where-things-are)
- [Procedure](#procedure)

## Who does the work

Decide this before you edit or check anything (ground rule 0). This table is the single copy for the plugin.

| Situation | Who | How |
|---|---|---|
| A question, an explanation, a review or conversion of code pasted in the chat, or a change of one or two lines in total | You | Follow the [procedure](#procedure) inline |
| Creating, editing, refactoring or migrating `.svelte`, `.svelte.ts`, `.svelte.js` or SvelteKit route files, with the plain `.ts`/`.js` files that change with them, beyond one or two lines in total | `svelte-component-editor` agent | Delegate with the Agent tool (below) |
| Reviewing, auditing or checking a codebase, a pull request or a migration without changing it | `svelte-code-auditor` agent | Delegate with the Agent tool (below) |
| The user asks you to work inline, or you already are one of these agents | You | Never delegate further |

The documentation lookups and the autofixer loop then run in the agent's context instead of filling the main conversation. Its prompt names the files, the task, the constraints and what to report. When you already found the locations to change (an edit set from the `svelte-lsp-intelligence` skill), pass them as file and line; the editor then runs the baseline, break and confirm steps itself, so do not run them first. For the editor on an older major, settle the migration first (this skill's rule 3) and say in the prompt whether the user migrated, declined, or asked to proceed without questions; the auditor handles an older major on its own. Call the agent without a `name`: a named call can start an agent-team teammate instead of a subagent, and a teammate gets none of the agent's preloaded skills.

```text
Agent
  subagent_type: "svelte-development:svelte-component-editor"
  description: "Add a filter to TodoList"
  prompt: "In src/lib/TodoList.svelte, add a text filter over the items. Keep its props and callbacks working for its parents …"
```

For an audit, use `subagent_type: "svelte-development:svelte-code-auditor"` and name the scope. Source: https://svelte.dev/docs/ai/subagent and https://svelte.dev/docs/ai/instructions.

## Svelte 5 practices

**State and derived values** ([runes.md](references/svelte/runes.md))

- Use `$state` only for values that drive an effect, a derived or the template; everything else is a plain variable. Objects and arrays become deep proxies; for large values that are only reassigned (API responses), use `$state.raw`.
- Compute with `$derived(expression)`, or `$derived.by(() => …)` for several statements, never with an `$effect` that writes state. Deriveds can be reassigned for optimistic UI and return objects as they are, without a proxy.
- Treat props as values that change: anything computed from a prop is a `$derived`, not a plain `let`. Props come from a typed `$props()` destructuring; `$bindable()` marks one the parent may bind. Pass a getter (`() => count`), not the value, to a function or context that must stay live.
- Share reactive logic with classes whose fields are `$state`, in `.svelte.ts` modules, instead of stores.

**Effects are an escape hatch** ([runes.md](references/svelte/runes.md), [context-lifecycle-and-reactivity-classes.md](references/svelte/context-lifecycle-and-reactivity-classes.md))

- Avoid updating state inside `$effect`. Instead: sync an external library (D3, a map) with `{@attach}`; react to user input in the event handler or with a function binding (`bind:value={get, set}`); log with `$inspect`; observe something outside Svelte with `createSubscriber`.
- Effects run only in the browser: never wrap their body in `if (browser)`.
- To see why something re-runs, put `$inspect.trace(label)` on the first line of the `$effect` or `$derived.by`.

**Template** ([template-syntax.md](references/svelte/template-syntax.md))

- Events are attributes: `onclick={…}`, `{onclick}` and spread props work. For `window` and `document`, use `<svelte:window onkeydown={…} />` and `<svelte:document>`, not `onMount` or `$effect`. Components take callback props, not `createEventDispatcher`.
- Pass content as snippets: `{#snippet name(arg)}` and `{@render name(arg)}`; children arrive as the `children` snippet.
- Key every `{#each}` with a stable unique id, never the index or a freshly built object; do not destructure an item you mutate (`bind:value={item.count}`).
- `{#key}` destroys and recreates everything inside it: use it for transitions, not to re-run a child's logic (use `$derived` there).
- Declaration tags replace `{@const}`: `{const total = $derived(a + b)}` or `{let open = $state(false)}`; they need a component in runes mode. Prefer `{@attach}` over `use:` actions (`fromAction` wraps an existing one), except SvelteKit's `use:enhance`, which stays as it is. Both need a minimum Svelte 5 minor ([template-syntax.md](references/svelte/template-syntax.md) gives it); below it, keep `{@const}` and `use:`.
- `class` takes objects and arrays (`class={[open && 'active']}`) instead of the `class:` directive.

**Styling** ([styling-motion-and-elements.md](references/svelte/styling-motion-and-elements.md))

- Pass a JavaScript value to CSS with a custom property: `<div style:--columns={columns}>`, then `var(--columns)` in `<style>`.
- Let a parent style a child with CSS custom properties (`<Child --color="red" />`). Use `:global` only when that is impossible, such as a library component, and scope it under an element of your own.

**Context and async** ([context-lifecycle-and-reactivity-classes.md](references/svelte/context-lifecycle-and-reactivity-classes.md), [async-and-boundaries.md](references/svelte/async-and-boundaries.md))

- Prefer context to state in a shared module: module state leaks between users during server rendering. Use `createContext`, which is typed, rather than `setContext`/`getContext` (the context reference gives its minimum minor; below it, keep `setContext`/`getContext`).
- `await` in components, `hydratable` and `fork` need `compilerOptions.experimental.async`; they change between minor releases, so fetch their sections first (this skill's rule 2).

**Avoid legacy features** ([legacy-and-migration.md](references/svelte/legacy-and-migration.md)): runes instead of implicit `let` reactivity and `$:`; `$props` instead of `export let`, `$$props`, `$$restProps`; `onclick` instead of `on:click`; snippets instead of `<slot>`, `$$slots`, `<svelte:fragment>`; a component in a capitalized variable (`<Thing />`) instead of `<svelte:component this={…}>`; `import Self from './Self.svelte'` instead of `<svelte:self>`; `$state` classes instead of stores; `{@attach}` instead of `use:` (SvelteKit's `use:enhance` excepted); `class` arrays instead of `class:`; `Spring`/`Tween` instead of `spring`/`tweened`; no `beforeUpdate`/`afterUpdate`, no `svelte/legacy` in new code.

## SvelteKit 3 practices

Each line links the reference to read before relying on it.

- **Config** lives in `sveltekit({ … })` in `vite.config.ts`; there is no `svelte.config.js` ([project-and-config.md](references/kit/project-and-config.md)).
- **Imports**: `#lib/x.js` subpath imports declared in `package.json` `imports`, with the extension; server-only code sits under a `server` segment or directory ([project-and-config.md](references/kit/project-and-config.md)).
- **Page state** comes from `$app/state` (`page`, `navigating`, `updated`); reload data with `refreshAll()` or `invalidate` ([loading-data.md](references/kit/loading-data.md)).
- **Environment variables** are declared with `defineEnvVars` in `src/env.ts` and read from `$app/env/private` or `$app/env/public` ([hooks-errors-and-env.md](references/kit/hooks-errors-and-env.md)).
- **Params** are matched by one `src/params.ts` with `defineParams` from `@sveltejs/kit/params` ([routing.md](references/kit/routing.md)). Paths come from `resolve`: a path without a leading slash (`resolve('blog/x')`), or a route ID with a leading slash and its params (`resolve('/blog/[slug]', { slug })`); static files from `asset('x.png')` ([navigation-and-options.md](references/kit/navigation-and-options.md)).
- **Forms**: form actions are stable; remote functions (`query`, `form`, `command`, `prerender`) need `experimental.remoteFunctions` plus the async flag ([forms-and-remote-functions.md](references/kit/forms-and-remote-functions.md)).
- **Secrets and boundaries**: secrets only in server code (`$app/env/private`, `+page.server.ts`, `+server.ts`, hooks, `server` modules). Universal `load` runs on both sides, so nothing private there; never keep per-user data in module-level variables, use `event.locals` or context; sanitize anything passed to `{@html}` ([security.md](references/kit/security.md)).
- **Requirements** (Node, Vite, TypeScript, adapter majors): [project-and-config.md](references/kit/project-and-config.md), [adapters-and-deploy.md](references/kit/adapters-and-deploy.md).

## Where things are

Read every reference the task touches, each once, for anything this page does not settle: a route with a form action needs `routing.md`, `loading-data.md` and `forms-and-remote-functions.md`. Each topic reference opens with its source precedence and ends with the exact calls that fetch its official sections. Astro and Tailwind CSS docs are not on the Svelte MCP server: fetch them with `curl -sS` from the raw URLs their references and the docs map list.

| Reference | Read when |
| --- | --- |
| [svelte/runes.md](references/svelte/runes.md) | Using `$state`, `$derived`, `$effect`, `$props`, `$bindable`, `$inspect` or `$host` |
| [svelte/template-syntax.md](references/svelte/template-syntax.md) | Writing markup: blocks, snippets, declaration tags, attachments, bindings, events, classes |
| [svelte/async-and-boundaries.md](references/svelte/async-and-boundaries.md) | `await` in components, `<svelte:boundary>`, `fork`, `hydratable`, server rendering |
| [svelte/context-lifecycle-and-reactivity-classes.md](references/svelte/context-lifecycle-and-reactivity-classes.md) | Context, lifecycle, `svelte/reactivity`, stores, `mount`/`hydrate`/`render` |
| [svelte/styling-motion-and-elements.md](references/svelte/styling-motion-and-elements.md) | Styles, transitions, motion, special elements, custom elements, TypeScript |
| [svelte/legacy-and-migration.md](references/svelte/legacy-and-migration.md) | Reading or migrating Svelte 4 code |
| [svelte/gotchas-and-warnings.md](references/svelte/gotchas-and-warnings.md) | A compiler or runtime warning, or behaviour that surprises |
| [kit/project-and-config.md](references/kit/project-and-config.md) | Project layout, `vite.config`, `#lib`, tsconfig, server-only modules |
| [kit/routing.md](references/kit/routing.md) | Routes, layouts, params and matchers, error pages |
| [kit/loading-data.md](references/kit/loading-data.md) | `load`, invalidation, `refreshAll`, `$app/state` |
| [kit/forms-and-remote-functions.md](references/kit/forms-and-remote-functions.md) | Form actions, `use:enhance`, remote functions |
| [kit/hooks-errors-and-env.md](references/kit/hooks-errors-and-env.md) | Hooks, errors, environment variables, service workers, cookies |
| [kit/navigation-and-options.md](references/kit/navigation-and-options.md) | `goto`, link options, page options, `$app/paths` |
| [kit/adapters-and-deploy.md](references/kit/adapters-and-deploy.md) | Choosing or configuring an adapter and deploying |
| [kit/security.md](references/kit/security.md) | CSRF, origins, redirects, secrets, CSP, required security releases |
| [kit/migrating-to-kit-3.md](references/kit/migrating-to-kit-3.md) | Upgrading a SvelteKit 2 project |
| [tooling/sv-cli.md](references/tooling/sv-cli.md) | `sv create`, `sv add`, `sv check`, `sv migrate`, Prettier, testing add-ons |
| [integrations/astro.md](references/integrations/astro.md) | Svelte components inside an Astro site |
| [integrations/tailwind.md](references/integrations/tailwind.md) | Tailwind CSS with SvelteKit or Astro |
| [docs-map.md](references/docs-map.md) | Choosing which official section to fetch |
| [changelogs.md](references/changelogs.md) | Before writing code in a project (its first two steps), and in the cases its "When to run the check" lists |
| [known-doc-errata.md](references/known-doc-errata.md) | Before copying a docs example: the doc statements known to be wrong or out of date |

The sibling skills are `svelte-development:svelte-docs-and-autofixer` and `svelte-development:svelte-lsp-intelligence`.

## Procedure

Run these steps in order for any Svelte code you write, convert or review.

1. **Installed versions**, in a project (skip for code pasted in the chat with no project): ground rule 1's command. When it prints nothing (no `node_modules`, a monorepo), read the ranges in `package.json` and the lockfile; when the version is still unknown, write for Svelte 5 and SvelteKit 3 and say so. This skill's rule 3 decides: on an old major, propose the migration before step 2; [changelogs.md](references/changelogs.md) says when to read the changelog window. With no project, write for Svelte 5 and SvelteKit 3 and say so in the answer. When the change will touch something other files use, run the project check of ground rule 5 now, once, as the baseline.
2. **References.** Read every reference from [Where things are](#where-things-are) that the task touches; the practices above apply to every task. Before copying a docs example, look for its page in [known-doc-errata.md](references/known-doc-errata.md).
3. **Live sections**, in one call, with the paths from the reference's "Official sources" or the docs map (load the tool with ToolSearch if it is deferred):

   ```text
   mcp__plugin_svelte-development_svelte__get-documentation
     section: ["svelte/$props", "svelte/snippet", "svelte/v5-migration-guide"]
   ```

   If the server is unavailable, download the raw section with `curl -sS 'https://svelte.dev/docs/<area>/<slug>/llms.txt'` (the docs map lists every URL) and say the docs were not read through the server.
4. **Write** the code by the rules and the sections. For a review, skip this step and take the code under review to step 5.
5. **Autofix** every Svelte file by ground rule 4: `code`, the installed version from step 1 (or `5` with no project), the file's real name as `filename`, and `async: true` when the project enables experimental async. The `svelte-docs-and-autofixer` skill shows the call.
6. **Check**, in a project (skip with no project): the language server diagnostics, when the server answers, and the project check of ground rule 5, from the project root. In SvelteKit, run the sync first: without it the generated types are missing and the check reports false errors. When you changed code and either reports a problem, fix it and repeat steps 5 and 6; finish when ground rule 5 is met. In a review, report the results instead of fixing them.

Derived from the `svelte-core-bestpractices` skill of sveltejs/ai-tools (MIT), base `6b5d0da`, and extended; see the plugin's NOTICE.txt. Not affiliated with or endorsed by the Svelte project.
