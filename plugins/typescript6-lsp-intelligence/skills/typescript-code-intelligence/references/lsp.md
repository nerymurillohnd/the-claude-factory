# TypeScript / JavaScript (typescript-language-server)

Server: `typescript-language-server --stdio` from the local `ts-lsp` plugin (replaces the official `typescript-lsp`; never enable both: they claim the same extensions and only the first registered server handles them, so one is silently ignored), for `.ts`, `.tsx`,
`.js`, `.jsx`, `.mts`, `.cts`, `.mjs`, `.cjs`. Binary installed with
`npm install -g typescript-language-server typescript@6` (nvm-managed Node; TypeScript 6 because 7 ships no `tsserver`, see the ts-lsp README); it prefers the project's own
`node_modules/typescript` when present. Behaviour below verified 2026-09-29 with typescript-language-server
6.0.1 and TypeScript 6.0.3 on a fixture project.

## Observed behaviour

| Situation | What the server returns | Meaning |
|---|---|---|
| First `findReferences` of a session | Can be partial | Warm-up; repeat until two results match |
| Barrel re-export plus aliased import (`import { f as g } from "./index"`) | `findReferences` on `f` includes the re-export, the import and the **calls to `g`** | Aliases are followed (unlike Python). The list is the full TS-side must-change set |
| Namespace import (`price.f(...)`) | Included | Static member access is tracked |
| Caller in another `tsconfig` project (monorepo package), in a file no `tsconfig` includes, or in a file matched by `exclude` | Missing, and **stable across repeats**: the warm-up check passes on an incomplete set | tsserver only searches projects already loaded. `hover` on any file of the other project (or the outside file) loads it; the next `findReferences` includes it |
| Use inside `.svelte` or `.astro` files | Missing; those files report `No LSP server available for file type` | Components and pages are invisible to this server |
| `prepareCallHierarchy` → `incomingCalls` | Works; module-level calls appear as the module | Svelte/Astro callers are missing here too |

## Before renaming or deleting a TS/JS symbol

List the repo's `tsconfig.json`/`jsconfig.json` files. With more than one, or with `.ts` files outside every
`include` (or matched by an `exclude`), `hover` one file per other project/outside file, then re-run
`findReferences`. Grep hits in those files are must-change, not optional.

In Astro, Svelte, Vue or MDX projects, Grep the name in `*.astro`, `*.svelte`, `*.vue`, `*.mdx` even when
`findReferences` looks complete.

## TypeScript blind spots (static references LSP never reports)

Verified: each case below returned only the definition.

- **Framework files**: `.astro`, `.svelte` (and by the same mechanism `.vue`, `.mdx`)
- **Lookup by string**: `mod[name](...)`, `(obj as Record<string, any>)[key]`, registries keyed by name

Also treat as blind spots: `import()` with a computed path, `package.json` scripts and bundler/framework
config (`astro.config.*`, `vite.config.*`) that reference files by path.
