---
paths:
  - "package.json"
  - "package-lock.json"
  - "plugins/*/package.json"
  - "plugins/*/package-lock.json"
---

# package.json and lockfiles

## Root

- The root `package.json` serves maintainer tooling only, never a plugin runtime. It stays `"private": true`.
- Its devDependencies are the npm tools (Biome, TypeScript, Husky) and the `@types/*` packages, each pinned to an exact version.
- Every maintenance command is one of its `npm run` scripts.
- Commit a `package-lock.json` change only with the dependency change that caused it. CI runs `npm ci`, which fails when the lockfile and `package.json` disagree.

## Plugins

- A plugin's own `package.json` and `package-lock.json` hold only its runtime dependencies, pinned exactly.
- Claude Code installs them for users when it caches the plugin: registry packages only, install scripts off, no `overrides`, within 60 seconds.
- In the clone, install them with `npm install --prefix plugins/<plugin> --ignore-scripts` for each plugin with a `package-lock.json`. `tsc-plugins` and the plugin's node tests need them. CI uses `npm ci --prefix`.
