---
status: deprecated
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Install git hooks from a tracked .githooks folder, not husky

## Scope

`.githooks/pre-commit`, `.githooks/pre-push` and the `prepare` script. Maintainer machines only; CI installs no hooks.

## Context and problem statement

`main` used husky 9.1.7, whose latest tag dates from 2024-11-18 and which warns that its two-line hook header will fail in v10. npm 12 blocks dependency install scripts by default, which affects hook installers that rely on a dependency `postinstall` (lefthook, simple-git-hooks). The npm/cli source at v12.2.1 runs the root package's own `prepare` outside that gate, and `npm ci --ignore-scripts` skips it.

## Decision drivers

- No extra dependency for a single-maintainer repository.
- Hooks installed on a local `npm install`, never in CI.
- Hooks call the same npm scripts as CI.

## Considered options

- **Tracked `.githooks/` with executable POSIX `sh` hooks, and `"prepare": "git config core.hooksPath .githooks"`**: chosen.
- **husky 9**: rejected because it adds a dependency with no release in about two years and a pending v10 migration.
- **lefthook or simple-git-hooks**: rejected because they install from a dependency `postinstall`, which npm 12 blocks unless approved.

## Decision outcome

Chosen option: **a tracked `.githooks/` folder set through `core.hooksPath`**: pre-commit checks the staged files with Biome, pre-push runs `npm run check`.

### Consequences

- Good, because the pre-commit hook ran on this branch's own commits ("Checked 2 files… No fixes applied").
- Bad, because git ignores a hook without the executable bit; the files must stay mode 100755.
- Bad, because pre-push fails while `npm run check` fails, until the plugin fixes land.

## More information

- Sources: `git` `Documentation/githooks.adoc` and `config/core.adoc` (`core.hooksPath`); `typicode/husky` at v9.1.7; npm/cli v12.2.1 `lib/commands/install.js` and `CHANGELOG.md` 12.0.0.
- Commit: 894b878.
