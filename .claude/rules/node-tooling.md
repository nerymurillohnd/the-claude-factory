# Node.js Tooling Rules

## Root manifest
- Keep the root `package.json` limited to repository-level JavaScript and TypeScript development tooling.
- Set `"private": true` in the root `package.json` to prevent accidental NPM publication.
- Retain the root NPM manifest only while repository-level tooling requires it.
- Recall memory `root-package-json-maintainer-only` before you change the root `package.json`.
- Run `npm ci` in every fresh clone and new worktree, with the `.nvmrc` Node selected: without `node_modules/@types/node` the `.mjs` type check fails with TS2688. Never bring back a global `@types/node` or `--typeRoots`.

## Plugin scope
- Declare plugin-specific runtime and development dependencies in each plugin's own scope.
- Never require root-level Node dependencies to install or run a plugin.

## Python boundary
- Keep Python dependencies outside NPM dependency management; allow the gate runner to invoke installed Python tools and executable maintainer scripts.

## Type checking and linting
- Type-check every `.mjs` file and mod with `tsc` in strict mode: no `any`, unsafe casts, ignore comments or loosened configs. Configs: `scripts/tsconfig.json` (maintainer), `scripts/tsconfig.plugins.json` (plugin `.mjs`), `plugins/<mod>/tsconfig.json` (mods). The maintainer and plugin `.mjs` configs extend `tsconfig.base.json`; a mod's config extends `.claude-plugin/types/tsconfig.json`, which the engine writes when it loads the mod.
- Pass each strict `tsc` flag with an explicit value: `--strict` does not override an explicit `false` in a tsconfig.
- Before the first edit of a `.ts`, `.mts`, `.js` or `.mjs` file in a task, tests and scratch scripts included, invoke the `typescript6-lsp-intelligence:ts-lifecycle` skill; the post-edit `tsc` hook is not that skill.
- Lint and format JavaScript, TypeScript, JSON and JSONC with Biome; `files.includes` in `biome.json` is the list of covered types, and a type outside it is not checked.
- Run `tsc` and `biome` as installed, by bare name; never through `npx`, and never as dependencies of the root `package.json`. The root manifest holds only exact `@types/*` devDependencies so `tsc` resolves Node's types.
- CI pins only TypeScript, to 6.0.3, by ADR; Biome installs at its latest release.
