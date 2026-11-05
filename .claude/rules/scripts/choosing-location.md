---
paths:
  - "scripts/**"
---

## Repository Scripts Layout

The `scripts/` directory is organized by responsibility. Scripts and configuration must remain in the designated locations; new scripts must be placed according to the categories below.

- `scripts/generators/`: Scripts that create or rewrite files.
- `scripts/validators/`: Scripts that check a file against a schema or a fixed contract. These checks are static and offline.
- `scripts/checkers/`: Scripts that inspect live state or enforce coherence across the repository.
- `scripts/testers/`: Tests of the maintainer scripts and of plugin scripts. One dedicated folder exists per plugin.
- `scripts/release/`: Version and release scripts consumed by `release.yml`, the version gate, and `npm run version:bump`.
- `scripts/schemas/`: JSON schemas read by the validators.
- Root of `scripts/`: Restricted to the existing gate runner (`gates.mjs`), shared libraries (`lib.mjs`, `components.mjs`), the scripts `package.json`, the gates that are invoked by path (`check-repo.mjs`, `sync-labels.mjs`, `basedpyright-maintainer.mjs`), and their associated configuration (`categories.json`, `biome-plugins/`, and the `tsconfig` files). No other files belong at the root of `scripts/`.
