---
status: accepted
date: 2026-11-04
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# Node is pinned in the root package.json through devEngines, in step with .nvmrc

## Scope

The root `package.json` (`devEngines.runtime`), `.nvmrc`, and the `rootPackageProblems` rule in `scripts/check-repo.mjs` with its tests in `scripts/testers/scripts.test.mjs` (commit 2506755). Plugins' own `package.json` files are out of scope.

## Context and problem statement

Only `.nvmrc` named the Node version, and nothing stopped npm from running under another one. A container on Node 22 rewrote `package-lock.json` without its `libc` fields, a diff that would have reached CI if committed. Nery asked to pin Node from `package.json`. How should it be pinned so a wrong Node fails at once, without drifting from `.nvmrc`?

## Decision drivers

- A wrong Node must stop npm and the git hooks, not only warn.
- `.nvmrc` stays CI's exact version (`setup-node` reads it); a second pin must not drift from it.
- Updating Node 26.x on the maintainer's machine must not block work until two files change.
- No change to CI's caching or permissions.

## Considered options

- **`devEngines.runtime` with `^` plus the `.nvmrc` version and `onFail: "error"`, kept in step by `check-repo`**: chosen.
- **The exact `.nvmrc` version**: rejected by Nery; every Node patch update would stop npm and the hooks until both files change.
- **The exact version with `onFail: "warn"`**: rejected, because Node 22 would pass again.
- **`engines.node`**: rejected; npm's own docs (`package-json.md`, npm 12.2.1) give `engines` to a package's consumers and `devEngines` to people working on its source.
- **Also `devEngines.packageManager`**: rejected; `setup-node` 7 turns npm caching on when it names npm, `release.yml` runs with `contents: write`, and pinning npm 12 would fail CI's npm 11.

## Decision outcome

Chosen option: **`"devEngines": { "runtime": { "name": "node", "version": "^26.13.0", "onFail": "error" } }`**. `check-repo` requires that one object, with `name` `"node"`, `onFail` `"error"` and `version` exactly `^` plus the `.nvmrc` version, so a change of `.nvmrc` fails the gate until `package.json` follows.

### Consequences

- Good, because npm stops with `EBADDEVENGINES` before `install`, `ci` and `run` on any Node outside the range, which also stops the Husky hooks.
- Good, because the two pins cannot drift without failing `check-repo`, locally and in CI.
- Bad, because a change of `.nvmrc` now needs `package.json` and, on a new major, `@types/node` in the same change.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| A wrong Node stops npm | `npm run check:repo` with Node 24.22.1 and npm 11.19.1, and with npm 12.2.1 | `EBADDEVENGINES` on 2026-11-04 | Each npm major |
| The pin follows `.nvmrc` | `check-repo` and the `root package.json rules` tests | Failed before the field was added, passes after, on 2026-11-04 | Each push |
| The lockfile is untouched | `npm ci`, `npm install --package-lock-only`, `cmp` against the previous lockfile | Identical on 2026-11-04 | Each npm major |

## More information

Nery asked to pin Node from `package.json` and chose the caret range on 2026-11-04; the drift check was Claude's recommendation, applied when he stated no preference.
