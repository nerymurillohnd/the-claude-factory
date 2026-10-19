# Map of the official docs

> Precedence: changelogs and source code win over the docs, and the docs win over this file. Call `list-sections` for the live list.

## Contents

- [How to use this map](#how-to-use-this-map)
- [Gaps in the MCP section hints](#gaps-in-the-mcp-section-hints)
- [Svelte](#svelte)
  - [Introduction and file types](#introduction-and-file-types)
  - [Runes](#runes)
  - [Template syntax](#template-syntax)
  - [Styling](#styling)
  - [Special elements](#special-elements)
  - [Runtime and imperative API](#runtime-and-imperative-api)
  - [Async: await expressions and hydratable data](#async-await-expressions-and-hydratable-data)
  - [Reference modules](#reference-modules)
  - [Misc, migration and legacy APIs](#misc-migration-and-legacy-apis)
  - [Errors and warnings](#errors-and-warnings)
- [SvelteKit](#sveltekit)
  - [Getting started, configuration and appendix](#getting-started-configuration-and-appendix)
  - [Routing](#routing)
  - [Data loading and state](#data-loading-and-state)
  - [Forms and remote functions](#forms-and-remote-functions)
  - [Hooks, errors and observability](#hooks-errors-and-observability)
  - [Environment variables and server-only code](#environment-variables-and-server-only-code)
  - [Navigation, page options and client state](#navigation-page-options-and-client-state)
  - [Build, deploy and adapters](#build-deploy-and-adapters)
  - [Best practices](#best-practices)
  - [`$app/*` and `@sveltejs/kit*` reference](#app-and-sveltejskit-reference)
  - [Migration](#migration)
- [CLI](#cli)
  - [CLI commands, add-ons and API](#cli-commands-add-ons-and-api)
- [AI](#ai)
  - [AI tools: MCP, skills, subagents and plugins](#ai-tools-mcp-skills-subagents-and-plugins)
- [Astro](#astro)
- [Tailwind CSS](#tailwind-css)

## How to use this map

- Pick the narrowest sections, then fetch them in one call with the argument from the second column:

  ```text
  mcp__plugin_svelte-development_svelte__get-documentation
    section: ["svelte/$state", "kit/load"]
  ```

  Without the MCP server, download the raw text from the third column, in single quotes so the shell does not expand `$`; or, when the user installed `@sveltejs/mcp` globally, use its command line (sections comma-separated):

  ```sh
  curl -sS 'https://svelte.dev/docs/svelte/$state/llms.txt'
  svelte-mcp get-documentation 'svelte/$state,kit/load'
  ```
- The argument is the `sections.json` key without its leading `docs/`, exactly as `list-sections` prints it after `path:` (`docs/kit/load` becomes `kit/load`). A path that keeps `docs/` does not resolve; the MCP returns only similar results. The exact section title also works.
- Every Svelte, SvelteKit, CLI and AI URL below serves `text/plain`. A 404 means the section was renamed or removed: call `list-sections` for the live list.
- Whole-package files, when one section is not enough: https://svelte.dev/docs/svelte/llms.txt (about 480 KB), https://svelte.dev/docs/kit/llms.txt (about 650 KB), https://svelte.dev/docs/cli/llms.txt (about 53 KB), https://svelte.dev/docs/ai/llms.txt (about 74 KB).
- Site-wide bundles are a last resort: https://svelte.dev/llms-small.txt (about 53 KB), https://svelte.dev/llms-medium.txt (about 870 KB), https://svelte.dev/llms-full.txt (about 1.26 MB).
- Never use WebFetch or any other web-fetch tool for these files; it summarizes instead of returning the text.

## Gaps in the MCP section hints

- The section catalog that `list-sections` returns (reproduced in the MCP prompt at https://svelte.dev/docs/ai/llms.txt) gives `use_cases` hints that steer section choice. 40 sections have none: 9 are missing from the catalog and 31 carry only the placeholder "use title and path to estimate use case". They include every SvelteKit 3 addition (`$app/env`, `$app/manifest`, `$app/service-worker`, `$app/tsconfig`, `@sveltejs/kit/params`, `@sveltejs/kit/adapter`, `@sveltejs/kit/env`, `adapter-bun`, the SvelteKit 3 migration guide). They are marked † below; this map is their classification.
- The same catalog still lists `kit/configuration` and `kit/@sveltejs-kit-node-polyfills`, whose pages return 404. The configuration reference now lives in `kit/@sveltejs-kit-vite`, because SvelteKit 3 reads its options from the Vite plugin.

## Svelte

### Introduction and file types

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Overview | `svelte/overview` | https://svelte.dev/docs/svelte/overview/llms.txt |
| Getting started | `svelte/getting-started` | https://svelte.dev/docs/svelte/getting-started/llms.txt |
| .svelte files | `svelte/svelte-files` | https://svelte.dev/docs/svelte/svelte-files/llms.txt |
| .svelte.js and .svelte.ts files | `svelte/svelte-js-files` | https://svelte.dev/docs/svelte/svelte-js-files/llms.txt |

### Runes

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| What are runes? | `svelte/what-are-runes` | https://svelte.dev/docs/svelte/what-are-runes/llms.txt |
| `$state` | `svelte/$state` | https://svelte.dev/docs/svelte/$state/llms.txt |
| `$derived` | `svelte/$derived` | https://svelte.dev/docs/svelte/$derived/llms.txt |
| `$effect` | `svelte/$effect` | https://svelte.dev/docs/svelte/$effect/llms.txt |
| `$props` | `svelte/$props` | https://svelte.dev/docs/svelte/$props/llms.txt |
| `$bindable` | `svelte/$bindable` | https://svelte.dev/docs/svelte/$bindable/llms.txt |
| `$inspect` | `svelte/$inspect` | https://svelte.dev/docs/svelte/$inspect/llms.txt |
| `$host` | `svelte/$host` | https://svelte.dev/docs/svelte/$host/llms.txt |

### Template syntax

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Basic markup | `svelte/basic-markup` | https://svelte.dev/docs/svelte/basic-markup/llms.txt |
| `{#if ...}` | `svelte/if` | https://svelte.dev/docs/svelte/if/llms.txt |
| `{#each ...}` | `svelte/each` | https://svelte.dev/docs/svelte/each/llms.txt |
| `{#key ...}` | `svelte/key` | https://svelte.dev/docs/svelte/key/llms.txt |
| `{#await ...}` | `svelte/await` | https://svelte.dev/docs/svelte/await/llms.txt |
| `{#snippet ...}` | `svelte/snippet` | https://svelte.dev/docs/svelte/snippet/llms.txt |
| `{@render ...}` | `svelte/@render` | https://svelte.dev/docs/svelte/@render/llms.txt |
| `{@html ...}` | `svelte/@html` | https://svelte.dev/docs/svelte/@html/llms.txt |
| `{@attach ...}` | `svelte/@attach` | https://svelte.dev/docs/svelte/@attach/llms.txt |
| `{@const ...}` | `svelte/@const` | https://svelte.dev/docs/svelte/@const/llms.txt |
| `{@debug ...}` | `svelte/@debug` | https://svelte.dev/docs/svelte/@debug/llms.txt |
| `{let/const ...}` † | `svelte/declaration-tags` | https://svelte.dev/docs/svelte/declaration-tags/llms.txt |
| bind: | `svelte/bind` | https://svelte.dev/docs/svelte/bind/llms.txt |
| use: | `svelte/use` | https://svelte.dev/docs/svelte/use/llms.txt |
| transition: | `svelte/transition` | https://svelte.dev/docs/svelte/transition/llms.txt |
| in: and out: | `svelte/in-and-out` | https://svelte.dev/docs/svelte/in-and-out/llms.txt |
| animate: | `svelte/animate` | https://svelte.dev/docs/svelte/animate/llms.txt |
| style: | `svelte/style` | https://svelte.dev/docs/svelte/style/llms.txt |
| class | `svelte/class` | https://svelte.dev/docs/svelte/class/llms.txt |

### Styling

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Scoped styles | `svelte/scoped-styles` | https://svelte.dev/docs/svelte/scoped-styles/llms.txt |
| Global styles | `svelte/global-styles` | https://svelte.dev/docs/svelte/global-styles/llms.txt |
| Custom properties | `svelte/custom-properties` | https://svelte.dev/docs/svelte/custom-properties/llms.txt |
| `Nested <style> elements` | `svelte/nested-style-elements` | https://svelte.dev/docs/svelte/nested-style-elements/llms.txt |

### Special elements

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| `<svelte:boundary>` | `svelte/svelte-boundary` | https://svelte.dev/docs/svelte/svelte-boundary/llms.txt |
| `<svelte:window>` | `svelte/svelte-window` | https://svelte.dev/docs/svelte/svelte-window/llms.txt |
| `<svelte:document>` | `svelte/svelte-document` | https://svelte.dev/docs/svelte/svelte-document/llms.txt |
| `<svelte:body>` | `svelte/svelte-body` | https://svelte.dev/docs/svelte/svelte-body/llms.txt |
| `<svelte:head>` | `svelte/svelte-head` | https://svelte.dev/docs/svelte/svelte-head/llms.txt |
| `<svelte:element>` | `svelte/svelte-element` | https://svelte.dev/docs/svelte/svelte-element/llms.txt |
| `<svelte:options>` | `svelte/svelte-options` | https://svelte.dev/docs/svelte/svelte-options/llms.txt |

### Runtime and imperative API

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Stores | `svelte/stores` | https://svelte.dev/docs/svelte/stores/llms.txt |
| Context | `svelte/context` | https://svelte.dev/docs/svelte/context/llms.txt |
| Lifecycle hooks | `svelte/lifecycle-hooks` | https://svelte.dev/docs/svelte/lifecycle-hooks/llms.txt |
| Imperative component API | `svelte/imperative-component-api` | https://svelte.dev/docs/svelte/imperative-component-api/llms.txt |

### Async: await expressions and hydratable data

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| await | `svelte/await-expressions` | https://svelte.dev/docs/svelte/await-expressions/llms.txt |
| Hydratable data † | `svelte/hydratable` | https://svelte.dev/docs/svelte/hydratable/llms.txt |

### Reference modules

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| svelte | `svelte/svelte` | https://svelte.dev/docs/svelte/svelte/llms.txt |
| svelte/action | `svelte/svelte-action` | https://svelte.dev/docs/svelte/svelte-action/llms.txt |
| svelte/animate | `svelte/svelte-animate` | https://svelte.dev/docs/svelte/svelte-animate/llms.txt |
| svelte/attachments | `svelte/svelte-attachments` | https://svelte.dev/docs/svelte/svelte-attachments/llms.txt |
| svelte/compiler | `svelte/svelte-compiler` | https://svelte.dev/docs/svelte/svelte-compiler/llms.txt |
| svelte/easing | `svelte/svelte-easing` | https://svelte.dev/docs/svelte/svelte-easing/llms.txt |
| svelte/events | `svelte/svelte-events` | https://svelte.dev/docs/svelte/svelte-events/llms.txt |
| svelte/legacy | `svelte/svelte-legacy` | https://svelte.dev/docs/svelte/svelte-legacy/llms.txt |
| svelte/motion | `svelte/svelte-motion` | https://svelte.dev/docs/svelte/svelte-motion/llms.txt |
| svelte/reactivity/window | `svelte/svelte-reactivity-window` | https://svelte.dev/docs/svelte/svelte-reactivity-window/llms.txt |
| svelte/reactivity | `svelte/svelte-reactivity` | https://svelte.dev/docs/svelte/svelte-reactivity/llms.txt |
| svelte/server | `svelte/svelte-server` | https://svelte.dev/docs/svelte/svelte-server/llms.txt |
| svelte/store | `svelte/svelte-store` | https://svelte.dev/docs/svelte/svelte-store/llms.txt |
| svelte/transition | `svelte/svelte-transition` | https://svelte.dev/docs/svelte/svelte-transition/llms.txt |

### Misc, migration and legacy APIs

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Best practices † | `svelte/best-practices` | https://svelte.dev/docs/svelte/best-practices/llms.txt |
| Testing | `svelte/testing` | https://svelte.dev/docs/svelte/testing/llms.txt |
| TypeScript | `svelte/typescript` | https://svelte.dev/docs/svelte/typescript/llms.txt |
| Custom elements | `svelte/custom-elements` | https://svelte.dev/docs/svelte/custom-elements/llms.txt |
| Browser support † | `svelte/browser-support` | https://svelte.dev/docs/svelte/browser-support/llms.txt |
| Frequently asked questions | `svelte/faq` | https://svelte.dev/docs/svelte/faq/llms.txt |
| Svelte 4 migration guide | `svelte/v4-migration-guide` | https://svelte.dev/docs/svelte/v4-migration-guide/llms.txt |
| Svelte 5 migration guide | `svelte/v5-migration-guide` | https://svelte.dev/docs/svelte/v5-migration-guide/llms.txt |
| Overview | `svelte/legacy-overview` | https://svelte.dev/docs/svelte/legacy-overview/llms.txt |
| Reactive let/var declarations | `svelte/legacy-let` | https://svelte.dev/docs/svelte/legacy-let/llms.txt |
| `Reactive $: statements` | `svelte/legacy-reactive-assignments` | https://svelte.dev/docs/svelte/legacy-reactive-assignments/llms.txt |
| export let | `svelte/legacy-export-let` | https://svelte.dev/docs/svelte/legacy-export-let/llms.txt |
| `$$props and $$restProps` | `svelte/legacy-$$props-and-$$restProps` | https://svelte.dev/docs/svelte/legacy-$$props-and-$$restProps/llms.txt |
| on: | `svelte/legacy-on` | https://svelte.dev/docs/svelte/legacy-on/llms.txt |
| `<slot>` | `svelte/legacy-slots` | https://svelte.dev/docs/svelte/legacy-slots/llms.txt |
| `$$slots` | `svelte/legacy-$$slots` | https://svelte.dev/docs/svelte/legacy-$$slots/llms.txt |
| `<svelte:fragment>` | `svelte/legacy-svelte-fragment` | https://svelte.dev/docs/svelte/legacy-svelte-fragment/llms.txt |
| `<svelte:component>` | `svelte/legacy-svelte-component` | https://svelte.dev/docs/svelte/legacy-svelte-component/llms.txt |
| `<svelte:self>` | `svelte/legacy-svelte-self` | https://svelte.dev/docs/svelte/legacy-svelte-self/llms.txt |
| Imperative component API | `svelte/legacy-component-api` | https://svelte.dev/docs/svelte/legacy-component-api/llms.txt |

### Errors and warnings

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Compiler errors | `svelte/compiler-errors` | https://svelte.dev/docs/svelte/compiler-errors/llms.txt |
| Compiler warnings | `svelte/compiler-warnings` | https://svelte.dev/docs/svelte/compiler-warnings/llms.txt |
| Runtime errors | `svelte/runtime-errors` | https://svelte.dev/docs/svelte/runtime-errors/llms.txt |
| Runtime warnings | `svelte/runtime-warnings` | https://svelte.dev/docs/svelte/runtime-warnings/llms.txt |

## SvelteKit

### Getting started, configuration and appendix

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Introduction | `kit/introduction` | https://svelte.dev/docs/kit/introduction/llms.txt |
| Creating a project | `kit/creating-a-project` | https://svelte.dev/docs/kit/creating-a-project/llms.txt |
| Project types | `kit/project-types` | https://svelte.dev/docs/kit/project-types/llms.txt |
| Project structure | `kit/project-structure` | https://svelte.dev/docs/kit/project-structure/llms.txt |
| Web standards | `kit/web-standards` | https://svelte.dev/docs/kit/web-standards/llms.txt |
| `@sveltejs/kit/vite` | `kit/@sveltejs-kit-vite` | https://svelte.dev/docs/kit/@sveltejs-kit-vite/llms.txt |
| Command Line Interface | `kit/cli` | https://svelte.dev/docs/kit/cli/llms.txt |
| Frequently asked questions | `kit/faq` | https://svelte.dev/docs/kit/faq/llms.txt |
| Integrations | `kit/integrations` | https://svelte.dev/docs/kit/integrations/llms.txt |
| Breakpoint Debugging | `kit/debugging` | https://svelte.dev/docs/kit/debugging/llms.txt |
| Additional resources | `kit/additional-resources` | https://svelte.dev/docs/kit/additional-resources/llms.txt |
| Glossary | `kit/glossary` | https://svelte.dev/docs/kit/glossary/llms.txt |

### Routing

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Routing | `kit/routing` | https://svelte.dev/docs/kit/routing/llms.txt |
| Advanced routing | `kit/advanced-routing` | https://svelte.dev/docs/kit/advanced-routing/llms.txt |
| `@sveltejs/kit/params` † | `kit/@sveltejs-kit-params` | https://svelte.dev/docs/kit/@sveltejs-kit-params/llms.txt |
| `$app/types` | `kit/$app-types` | https://svelte.dev/docs/kit/$app-types/llms.txt |

### Data loading and state

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Loading data | `kit/load` | https://svelte.dev/docs/kit/load/llms.txt |
| State management | `kit/state-management` | https://svelte.dev/docs/kit/state-management/llms.txt |

### Forms and remote functions

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Form actions | `kit/form-actions` | https://svelte.dev/docs/kit/form-actions/llms.txt |
| Remote functions | `kit/remote-functions` | https://svelte.dev/docs/kit/remote-functions/llms.txt |
| `$app/forms` | `kit/$app-forms` | https://svelte.dev/docs/kit/$app-forms/llms.txt |
| `$app/server` | `kit/$app-server` | https://svelte.dev/docs/kit/$app-server/llms.txt |

### Hooks, errors and observability

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Hooks | `kit/hooks` | https://svelte.dev/docs/kit/hooks/llms.txt |
| Errors | `kit/errors` | https://svelte.dev/docs/kit/errors/llms.txt |
| Observability | `kit/observability` | https://svelte.dev/docs/kit/observability/llms.txt |
| `@sveltejs/kit/hooks` | `kit/@sveltejs-kit-hooks` | https://svelte.dev/docs/kit/@sveltejs-kit-hooks/llms.txt |

### Environment variables and server-only code

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Environment variables † | `kit/environment-variables` | https://svelte.dev/docs/kit/environment-variables/llms.txt |
| Server-only modules | `kit/server-only-modules` | https://svelte.dev/docs/kit/server-only-modules/llms.txt |
| `$app/env` † | `kit/$app-env` | https://svelte.dev/docs/kit/$app-env/llms.txt |
| `$app/env/private` † | `kit/$app-env-private` | https://svelte.dev/docs/kit/$app-env-private/llms.txt |
| `$app/env/public` † | `kit/$app-env-public` | https://svelte.dev/docs/kit/$app-env-public/llms.txt |
| `@sveltejs/kit/env` † | `kit/@sveltejs-kit-env` | https://svelte.dev/docs/kit/@sveltejs-kit-env/llms.txt |
| `$app/environment` | `kit/$app-environment` | https://svelte.dev/docs/kit/$app-environment/llms.txt |
| `$env/dynamic/private` | `kit/$env-dynamic-private` | https://svelte.dev/docs/kit/$env-dynamic-private/llms.txt |
| `$env/dynamic/public` | `kit/$env-dynamic-public` | https://svelte.dev/docs/kit/$env-dynamic-public/llms.txt |
| `$env/static/private` | `kit/$env-static-private` | https://svelte.dev/docs/kit/$env-static-private/llms.txt |
| `$env/static/public` | `kit/$env-static-public` | https://svelte.dev/docs/kit/$env-static-public/llms.txt |

### Navigation, page options and client state

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Page options | `kit/page-options` | https://svelte.dev/docs/kit/page-options/llms.txt |
| Link options | `kit/link-options` | https://svelte.dev/docs/kit/link-options/llms.txt |
| Page state & shallow routing | `kit/shallow-routing` | https://svelte.dev/docs/kit/shallow-routing/llms.txt |
| Snapshots | `kit/snapshots` | https://svelte.dev/docs/kit/snapshots/llms.txt |
| Service workers | `kit/service-workers` | https://svelte.dev/docs/kit/service-workers/llms.txt |
| `$app/navigation` | `kit/$app-navigation` | https://svelte.dev/docs/kit/$app-navigation/llms.txt |
| `$app/state` | `kit/$app-state` | https://svelte.dev/docs/kit/$app-state/llms.txt |
| `$app/stores` | `kit/$app-stores` | https://svelte.dev/docs/kit/$app-stores/llms.txt |
| `$app/paths` | `kit/$app-paths` | https://svelte.dev/docs/kit/$app-paths/llms.txt |
| `$app/manifest` † | `kit/$app-manifest` | https://svelte.dev/docs/kit/$app-manifest/llms.txt |
| `$app/service-worker` † | `kit/$app-service-worker` | https://svelte.dev/docs/kit/$app-service-worker/llms.txt |
| `$service-worker` | `kit/$service-worker` | https://svelte.dev/docs/kit/$service-worker/llms.txt |

### Build, deploy and adapters

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Building your app | `kit/building-your-app` | https://svelte.dev/docs/kit/building-your-app/llms.txt |
| Adapters | `kit/adapters` | https://svelte.dev/docs/kit/adapters/llms.txt |
| Zero-config deployments | `kit/adapter-auto` | https://svelte.dev/docs/kit/adapter-auto/llms.txt |
| Node servers | `kit/adapter-node` | https://svelte.dev/docs/kit/adapter-node/llms.txt |
| Bun servers † | `kit/adapter-bun` | https://svelte.dev/docs/kit/adapter-bun/llms.txt |
| Static site generation | `kit/adapter-static` | https://svelte.dev/docs/kit/adapter-static/llms.txt |
| Single-page apps | `kit/single-page-apps` | https://svelte.dev/docs/kit/single-page-apps/llms.txt |
| Cloudflare | `kit/adapter-cloudflare` | https://svelte.dev/docs/kit/adapter-cloudflare/llms.txt |
| Cloudflare Workers | `kit/adapter-cloudflare-workers` | https://svelte.dev/docs/kit/adapter-cloudflare-workers/llms.txt |
| Netlify | `kit/adapter-netlify` | https://svelte.dev/docs/kit/adapter-netlify/llms.txt |
| Vercel | `kit/adapter-vercel` | https://svelte.dev/docs/kit/adapter-vercel/llms.txt |
| Writing adapters | `kit/writing-adapters` | https://svelte.dev/docs/kit/writing-adapters/llms.txt |
| `@sveltejs/kit/adapter` † | `kit/@sveltejs-kit-adapter` | https://svelte.dev/docs/kit/@sveltejs-kit-adapter/llms.txt |
| `@sveltejs/kit/node` | `kit/@sveltejs-kit-node` | https://svelte.dev/docs/kit/@sveltejs-kit-node/llms.txt |
| Packaging | `kit/packaging` | https://svelte.dev/docs/kit/packaging/llms.txt |

### Best practices

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Auth | `kit/auth` | https://svelte.dev/docs/kit/auth/llms.txt |
| Performance | `kit/performance` | https://svelte.dev/docs/kit/performance/llms.txt |
| Icons | `kit/icons` | https://svelte.dev/docs/kit/icons/llms.txt |
| Images | `kit/images` | https://svelte.dev/docs/kit/images/llms.txt |
| Accessibility | `kit/accessibility` | https://svelte.dev/docs/kit/accessibility/llms.txt |
| SEO | `kit/seo` | https://svelte.dev/docs/kit/seo/llms.txt |

### `$app/*` and `@sveltejs/kit*` reference

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| `@sveltejs/kit` | `kit/@sveltejs-kit` | https://svelte.dev/docs/kit/@sveltejs-kit/llms.txt |
| Types | `kit/types` | https://svelte.dev/docs/kit/types/llms.txt |
| `#lib` | `kit/$lib` | https://svelte.dev/docs/kit/$lib/llms.txt |
| `$app/tsconfig` † | `kit/$app-tsconfig` | https://svelte.dev/docs/kit/$app-tsconfig/llms.txt |
| `$app/tsconfig/service-worker` † | `kit/$app-tsconfig-service-worker` | https://svelte.dev/docs/kit/$app-tsconfig-service-worker/llms.txt |

### Migration

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Migrating to SvelteKit v3 † | `kit/migrating-to-sveltekit-3` | https://svelte.dev/docs/kit/migrating-to-sveltekit-3/llms.txt |
| Migrating to SvelteKit v2 | `kit/migrating-to-sveltekit-2` | https://svelte.dev/docs/kit/migrating-to-sveltekit-2/llms.txt |
| Migrating from Sapper | `kit/migrating` | https://svelte.dev/docs/kit/migrating/llms.txt |

## CLI

### CLI commands, add-ons and API

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Overview | `cli/overview` | https://svelte.dev/docs/cli/overview/llms.txt |
| Frequently asked questions | `cli/faq` | https://svelte.dev/docs/cli/faq/llms.txt |
| sv create | `cli/sv-create` | https://svelte.dev/docs/cli/sv-create/llms.txt |
| sv add | `cli/sv-add` | https://svelte.dev/docs/cli/sv-add/llms.txt |
| sv check | `cli/sv-check` | https://svelte.dev/docs/cli/sv-check/llms.txt |
| sv migrate | `cli/sv-migrate` | https://svelte.dev/docs/cli/sv-migrate/llms.txt |
| ai-tools † | `cli/ai-tools` | https://svelte.dev/docs/cli/ai-tools/llms.txt |
| better-auth † | `cli/better-auth` | https://svelte.dev/docs/cli/better-auth/llms.txt |
| drizzle | `cli/drizzle` | https://svelte.dev/docs/cli/drizzle/llms.txt |
| enhanced-img † | `cli/enhanced-img` | https://svelte.dev/docs/cli/enhanced-img/llms.txt |
| eslint | `cli/eslint` | https://svelte.dev/docs/cli/eslint/llms.txt |
| experimental † | `cli/experimental` | https://svelte.dev/docs/cli/experimental/llms.txt |
| mdsvex | `cli/mdsvex` | https://svelte.dev/docs/cli/mdsvex/llms.txt |
| paraglide | `cli/paraglide` | https://svelte.dev/docs/cli/paraglide/llms.txt |
| playwright | `cli/playwright` | https://svelte.dev/docs/cli/playwright/llms.txt |
| prettier | `cli/prettier` | https://svelte.dev/docs/cli/prettier/llms.txt |
| storybook | `cli/storybook` | https://svelte.dev/docs/cli/storybook/llms.txt |
| sveltekit-adapter | `cli/sveltekit-adapter` | https://svelte.dev/docs/cli/sveltekit-adapter/llms.txt |
| tailwindcss | `cli/tailwind` | https://svelte.dev/docs/cli/tailwind/llms.txt |
| vitest | `cli/vitest` | https://svelte.dev/docs/cli/vitest/llms.txt |
| `[create your own]` † | `cli/community` | https://svelte.dev/docs/cli/community/llms.txt |
| sv † | `cli/sv` | https://svelte.dev/docs/cli/sv/llms.txt |
| sv-utils † | `cli/sv-utils` | https://svelte.dev/docs/cli/sv-utils/llms.txt |

## AI

### AI tools: MCP, skills, subagents and plugins

| Title | `get-documentation` argument | Raw text URL |
| --- | --- | --- |
| Overview † | `ai/overview` | https://svelte.dev/docs/ai/overview/llms.txt |
| AGENTS.md † | `ai/instructions` | https://svelte.dev/docs/ai/instructions/llms.txt |
| Overview † | `ai/mcp` | https://svelte.dev/docs/ai/mcp/llms.txt |
| Local setup † | `ai/local-setup` | https://svelte.dev/docs/ai/local-setup/llms.txt |
| Remote setup † | `ai/remote-setup` | https://svelte.dev/docs/ai/remote-setup/llms.txt |
| Tools † | `ai/tools` | https://svelte.dev/docs/ai/tools/llms.txt |
| Resources † | `ai/resources` | https://svelte.dev/docs/ai/resources/llms.txt |
| Prompts † | `ai/prompts` | https://svelte.dev/docs/ai/prompts/llms.txt |
| CLI † | `ai/cli` | https://svelte.dev/docs/ai/cli/llms.txt |
| Overview † | `ai/skills` | https://svelte.dev/docs/ai/skills/llms.txt |
| Overview † | `ai/subagent` | https://svelte.dev/docs/ai/subagent/llms.txt |
| Claude Code † | `ai/claude-plugin` | https://svelte.dev/docs/ai/claude-plugin/llms.txt |
| OpenCode † | `ai/opencode-plugin` | https://svelte.dev/docs/ai/opencode-plugin/llms.txt |
| Cursor † | `ai/cursor-plugin` | https://svelte.dev/docs/ai/cursor-plugin/llms.txt |
| GitHub Copilot CLI † | `ai/copilot-plugin` | https://svelte.dev/docs/ai/copilot-plugin/llms.txt |
| Codex CLI † | `ai/codex-plugin` | https://svelte.dev/docs/ai/codex-plugin/llms.txt |

## Astro

`https://docs.astro.build/llms.txt` returns 404. Read the Markdown sources of the docs site instead:

| Page | Raw source URL |
| --- | --- |
| `@astrojs/svelte` integration guide | https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/guides/integrations-guide/svelte.mdx |
| Framework components (islands, props, children) | https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/guides/framework-components.mdx |
| Directives reference (`client:*`, `server:defer`) | https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/reference/directives-reference.mdx |
| Server islands | https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/guides/server-islands.mdx |
| Upgrade to Astro v7 | https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/guides/upgrade-to/v7.mdx |
| Styling and CSS | https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/guides/styling.mdx |
| Container API reference | https://raw.githubusercontent.com/withastro/docs/main/src/content/docs/en/reference/container-reference.mdx |
| Svelte renderer source, server | https://raw.githubusercontent.com/withastro/astro/main/packages/integrations/svelte/src/server.ts |
| Svelte renderer source, client | https://raw.githubusercontent.com/withastro/astro/main/packages/integrations/svelte/src/client.svelte.ts |

## Tailwind CSS

`https://tailwindcss.com/llms.txt` returns 404. The docs site sources are in `tailwindlabs/tailwindcss.com`. The framework guide paths contain a `(docs)` folder, written `%28docs%29` in the URL.

| Page | Raw source URL |
| --- | --- |
| Functions and directives (`@reference`, `@source`, `@theme`, subpath imports) | https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/functions-and-directives.mdx |
| Compatibility (browsers, `<style>` blocks, preprocessors) | https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/compatibility.mdx |
| Detecting classes in source files | https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/detecting-classes-in-source-files.mdx |
| Theme variables | https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/theme.mdx |
| Dark mode | https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/dark-mode.mdx |
| Adding custom styles (`@utility`, `@custom-variant`) | https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/adding-custom-styles.mdx |
| Styling with utility classes | https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/styling-with-utility-classes.mdx |
| Upgrade guide (v3 to v4) | https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/docs/upgrade-guide.mdx |
| Framework guide: SvelteKit | https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/app/%28docs%29/docs/installation/framework-guides/sveltekit.tsx |
| Framework guide: Astro | https://raw.githubusercontent.com/tailwindlabs/tailwindcss.com/main/src/app/%28docs%29/docs/installation/framework-guides/astro.tsx |
