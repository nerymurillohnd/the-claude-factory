---
paths:
  - "scripts/**"
---

# Where a maintenance script goes

Put each new script in the folder of its responsibility; never at the root of `scripts/`.

- `scripts/generators/`: scripts that create or rewrite files, such as `marketplace.json` and the README catalog.
- `scripts/validators/`: scripts that check a file against a schema or a fixed contract, statically and offline.
- `scripts/checkers/`: scripts that check live state or coherence, such as links that still respond.
- `scripts/testers/`: tests of the maintainer scripts and of plugin scripts, one folder per plugin.
- `scripts/release/`: the version and release scripts that `release.yml`, the version gate and `npm run version:bump` run.
- `scripts/schemas/`: the JSON schemas the validators read.
- Root of `scripts/`: only the existing gate runner (`gates.mjs`), shared libraries (`lib.mjs`, `components.mjs`), the scripts `package.json` or the gates run by path (`check-repo.mjs`, `sync-labels.mjs`, `basedpyright-maintainer.mjs`), and their configuration (`categories.json`, `biome-plugins/`, the `tsconfig` files).
