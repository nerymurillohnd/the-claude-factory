# Counterpart contracts and release reconciliation

Read for material integrations and release-history corroboration. Discover official counterpart roots from installed metadata, maintainer repositories, or publisher sites. Confirm ownership; third-party tutorials are leads.

| Surface | Investigate on both sides |
| --- | --- |
| Framework/adapter | Supported compiler/runtime ranges, checker/language-plugin ownership, generated tsconfig/types, special file extensions, deployment target, adapter constraints. |
| Bundler/transpiler | Who checks types, consumed config options, conditions/aliases, transforms, declarations, dev/build differences. |
| Runtime | Loading, package conditions, extensions, APIs, native stripping versus transpilation, supported syntax/config and runtime versions. |
| Tests | Transformation versus checking, project association, globals/types, mocks, aliases, worker/browser/server environment. |
| Dependencies/generators | Type/runtime exports, peer/engine compatibility, generated ownership/refresh commands, consumer compiler support. |
| Editor/CI | Selected services/compilers, extensions, projects/files, overrides, runtime and lockfile installation, platform differences. |

Illustrative entrypoints, not required integrations: [Vite features](https://vite.dev/guide/features.html), [Node TypeScript support](https://nodejs.org/api/typescript.html), [VS Code editing](https://code.visualstudio.com/docs/typescript/typescript-editing). For other stacks, such as Angular/esbuild, Deno, Bun, libraries, or alternative editors, discover their own versioned official docs and history. Astro, Cloudflare, and Playwright matter only when the task crosses their contracts.

## Release-history worksheet

Start with [TypeScript announcements](https://devblogs.microsoft.com/typescript/) and [release records](https://github.com/microsoft/TypeScript/releases); follow handbook **What's New** navigation for features. Locate each affected counterpart's official release notes/changelog and compatibility documentation.

Read newest first for corrections, regressions and status changes, then backward through the installed-to-target interval. Without an upgrade, trace the implicated feature's history down to the installed version. Include patch releases when investigating fixes. Distinguish stable, prerelease, experimental and deprecated evidence; future-work announcements do not establish shipped capability.

Record release/version/date, affected behavior, agreement/conflict with documentation, whether installed artifacts contain it, and decision impact. Check changed defaults, breaking changes, fixes, regressions, deprecations, new capabilities and transitions to stable. Follow linked issues/PRs for clarification; an open issue or merged PR alone is not a released-support guarantee.

If docs and history disagree, isolate disputed behavior at actual versions and retain both sources. Reproduction success establishes observed behavior, not the vendor's compatibility commitment. Missing required compatibility evidence blocks that integration recommendation; independent authorized work can proceed.

## Closure

A material relationship is resolved when applicable official evidence and sufficient local observations support producer/consumer versions and behavior, with appropriate checks identified or executed. Otherwise record the precise gap, impacted decision and next evidence needed. Stop when all material relationships have one of these outcomes. New tools, generated inputs or assumptions reopen the implicated research and update category selection/count before dependent changes continue.
