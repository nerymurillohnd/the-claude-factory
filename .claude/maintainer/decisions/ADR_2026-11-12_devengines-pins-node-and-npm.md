---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Pin the maintainer Node and npm with devEngines, and keep every npm tool exact

## Scope

`devEngines` and `devDependencies` in the root `package.json`, alongside `.nvmrc` (26.13.0) and `.npmrc` (`save-exact=true`).

## Context and problem statement

Nothing stopped a maintainer from running the scripts on another Node or npm major. `@types/node` sat in `dependencies` with a `^` range, unlike every other maintainer tool, because the `.npmrc` with `save-exact` did not exist when it was installed.

## Decision drivers

- Fail early on an unsupported Node or npm.
- Exact versions for every maintainer tool.

## Considered options

- **`devEngines` with `runtime` node `^26.13.0` and `packageManager` npm `^12.2.1`, `onFail: error`, and `@types/node` 26.6.6 exact in `devDependencies`**: chosen.
- **Rely on `.nvmrc` alone**: rejected because nvm only selects a version and does not stop a run on another one.

## Decision outcome

Chosen option: **`devEngines` plus exact dev pins**, because npm checks `devEngines` before `install`, `ci` and `run`, and `@types/node` only types the editor and `tsc`.

### Consequences

- Good, because a mismatched Node or npm stops before any script runs (`EBADDEVENGINES`).
- Bad, because a maintainer on a newer major is blocked until the ranges change.

## More information

- Source: npm docs v12, `package.json` `devEngines` ("before `install`, `ci`, and `run`"; `onFail` defaults to `error`).
- The owner first installed `@types/node` with `npm install --save`; the research results moved it, and the owner had agreed to apply them.
- Commit: 57b77f6.
