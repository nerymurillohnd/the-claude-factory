---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Rebuild the tsconfig files for TypeScript 6 and Node-run hooks

## Scope

Root `tsconfig.base.json` and `tsconfig.json`, maintainer scope. Covers the plugins' Node-run `.mjs`, `.cjs` and `.js` files and the future `scripts/`. The six mods (file-tree-pane, macos-grep-guard, model-trace, project-maintainer, tool-ledger, turn-meter) are out of scope: each is checked with the tsconfig Claude Code generates for it.

## Context and problem statement

The configs restored from `main` were written before TypeScript 6.0. With TypeScript 6.0.3, `tsc -p .` reported 726 errors: TypeScript 6.0 sets `types` to `[]` by default, so `@types/node` was not loaded, and the root used `jsx: react-jsx`, which does not match the mods (they use the classic `h` factory and run with no Node). The base also repeated options TypeScript 6.0 now defaults and used the deprecated `diagnostics` option.

## Decision drivers

- Follow TypeScript 6.0's defaults and avoid what TypeScript 7 removes.
- Check Node-run hook code with Node's module rules and types.
- Keep the mods out of a config that would let Node APIs into code that runs without Node.

## Considered options

- **A strict base with only non-default options, and a root config for Node-run JavaScript (`module nodenext`, `target es2023`, `types: ["node"]`)**: chosen.
- **Keep the restored configs and add `types: ["node"]`**: rejected because it keeps `react-jsx` for the mods, the redundant and deprecated options, and `Bundler` resolution, which does not match how Node runs the hooks.

## Decision outcome

Chosen option: **a strict base with only non-default options, and a root config for Node-run JavaScript**, because it matches TypeScript 6.0's defaults, loads Node's types where Node runs the code, and leaves each mod to its generated config.

### Consequences

- Good, because `tsc -p tsconfig.json` passes once tailwind-development's packages are installed, as CI installs them.
- Good, because the config carries no option TypeScript 7 drops.
- Bad, because the mods need a separate check per plugin.
- Bad, because `@types/node` 26 lets code call Node APIs that users on Node 20 lack; the type check does not enforce a plugin's minimum Node version.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The root config checks the Node-run files cleanly | `npm run typecheck:ts` | Passed on 2026-11-12, with tailwind-development's packages installed | Each TypeScript upgrade |
| Each mod checks cleanly with its generated tsconfig | `tsc -p plugins/<mod>` | Pending: no generated tsconfig exists in this environment; file-tree-pane imports `./x.ts`, which gave 26 TS5097 errors under the documented header config | When the mods' check is wired |

## More information

- Sources: the TypeScript 6.0 announcement (devblogs.microsoft.com, "Announcing TypeScript 6.0"), and the mod tsconfig in the header of the `claude-code.d.ts` that Claude Code 2.1.322 generates.
- Commit: 5374c7a.
