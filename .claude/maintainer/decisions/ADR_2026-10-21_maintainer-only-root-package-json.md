---
status: superseded
date: 2026-10-21
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: ADR_2026-10-26_npm-tools-and-git-hooks-are-pinned-dev-dependencies
---

# A root package.json for maintainer type packages only, never a plugin runtime

## Scope

- In scope: the root `package.json` and `package-lock.json`, the `node_modules/` they install, the `tsc` gate in `.claude/CLAUDE.md` and `.pre-commit-config.yaml`, the rule in `.github/scripts/check-repo.mjs` (`rootPackageProblems`), and Dependabot's `npm` entry.
- Out of scope: the CLIs the gates run (TypeScript, Biome, markdownlint-cli2, the Claude Code CLI), which stay on `npx --yes <pkg>@<version>` or a pinned global install in CI; Python tooling, which stays on `uvx` at pinned versions with no `pyproject.toml` or virtual environment; a plugin's own `package.json` and lockfile inside `plugins/<name>/`, which Claude Code installs into that plugin's cache and which stays allowed when the plugin's architecture needs it.

## Context and problem statement

`.github/scripts/tsconfig.json` declares `"types": ["node"]`, but the repository had no `node_modules`. The type check passed only because the gate added `--typeRoots "$(npm root -g)/@types"`, so it depended on a global `@types/node` installed on the maintainer's machine (the same kind of machine-specific path that b5fc4ee had already removed from `tsconfig.base.json`). Every other reader of the config failed with `error TS2688: Cannot find type definition file for 'node'`: the post-edit hook of `typescript6-lsp-intelligence`, the language server and any fresh clone. How does the repository give its own scripts their Node types without depending on a global and without giving plugins a dependency no user receives?

## Decision drivers

- The type check must read the config as written, the same way the gate, the hook, the language server and a fresh clone do.
- Nothing on the maintainer's machine may be a dependency of the repository.
- Plugins are installed by third parties, who receive only `plugins/<name>/`. Node resolves imports by walking up the folders, so a package in a root `node_modules` would let a plugin's code or tests pass in this repository and fail for users.
- No second set of tool versions to keep in step with the pins that already exist in the Commands and in `validate.yml`.

## Considered options

- **A root `package.json` that pins only `@types/*` packages, starting with `@types/node` on the Node major of `.nvmrc`, enforced by `check-repo.mjs`**: chosen.
- **Keep the global `@types/node` and the `--typeRoots "$(npm root -g)/@types"` flag**: rejected because it depends on the maintainer's machine, and the hook, the language server and a fresh clone keep failing with TS2688.
- **Move every JavaScript tool into `devDependencies` (TypeScript, Biome, markdownlint-cli2)**: rejected because those tools already run at pinned versions through `npx`, they cause no defect, and moving them would add a second set of versions to keep in step with the CI pins.
- **uv and a `pyproject.toml`**: rejected because uv does not install npm packages, so it cannot provide `@types/node`, and it would add a virtual environment and a config file that ruff, mypy and basedpyright read.

## Decision outcome

Chosen option: **a root `package.json` for maintainer type packages only**, because it fixes the one defect (the missing Node types) with the smallest change, reads the config the same way for every tool, and its rule is checked by a gate instead of only written down.

The package is `"private": true`, declares no `dependencies`, `main`, `exports`, `bin`, `type` or `workspaces`, and pins each `@types/*` devDependency to an exact version. It sets no `"type"`, because an explicit one would change how Node and `tsc` (`module: nodenext`) read the `.js` and `.ts` files of plugins that ship no `package.json` of their own. `@types/node` installs no `node_modules/.bin/tsc`, so the compiler the post-edit hook finds does not change. `check-repo.mjs` fails on any field that could make the package a runtime, on a devDependency that is not `@types/*` or not exact, and on an `@types/node` whose major differs from `.nvmrc`. The global `@types/node` was uninstalled and the `--typeRoots` flag removed from the gate.

### Consequences

- Good, because `tsc -p .github/scripts/tsconfig.json --noEmit` passes with no extra flag, and the hook and language server resolve `node:*` modules.
- Good, because the rule "maintainer tooling only, never a plugin runtime" fails the repository gate the moment someone breaks it.
- Good, because the major of `@types/node` follows `.nvmrc` under a check, not a memory.
- Bad, because a fresh clone needs `npm ci` before the type check, and a change of the Node major in `.nvmrc` needs the matching `@types/node` in the same change.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The scripts type-check without `--typeRoots` | `npx --yes --package typescript@6.0.3 tsc -p .github/scripts/tsconfig.json --noEmit` | Passed on 2026-10-21, `@types/node` loaded from `node_modules/@types/node` (`--explainFiles`) | Each push (gate 18) |
| The package stays maintainer-only | `node .github/scripts/check-repo.mjs`, and the `root package.json rules` tests in `.github/scripts/tests/scripts.test.mjs` | Passed on 2026-10-21; a `dependencies` field added on purpose failed it | Each push (gates 4 and 5) |
| `@types/node` follows `.nvmrc` | `check-repo.mjs` compares the majors | Passed on 2026-10-21 (26.6.5 against 26.12.1) | Each change of `.nvmrc` |

## More information

- Nery decided this on 2026-10-21, while fixing the post-edit `tsc` hook. He chose the minimal package (types only) over moving the CLIs into it.
- Plugin dependencies follow the documented route: a `package.json` and an npm or Bun lockfile at the plugin's root, installed by Claude Code into the plugin's copied version directory, or a hook that installs into `${CLAUDE_PLUGIN_DATA}` ([plugins/loading](https://code.claude.com/docs/en/plugins/loading), [manifest-reference](https://code.claude.com/docs/en/plugins/manifest-reference)).
