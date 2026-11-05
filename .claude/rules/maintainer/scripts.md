---
paths:
  - "scripts/**"
  - ".claude/hooks/**"
  - ".claude/skills/*/scripts/**"
---

## Repository Scripts Layout

The `scripts/` directory is organized by responsibility. Scripts and configuration must remain in the designated locations; new scripts must be placed according to the categories below.

- `scripts/generators/`: Scripts that create or rewrite files.
- `scripts/validators/`: Scripts that check a file against a schema or a fixed contract. These checks are static and offline.
- `scripts/checkers/`: Scripts that inspect live state or enforce coherence across the repository.
- `scripts/testers/`: Tests of the maintainer scripts and of plugin scripts. One dedicated folder exists per plugin.
- `scripts/release/`: Version and release scripts consumed by `release.yml`, the version gate, and `npm run version:bump`.
- `scripts/schemas/`: JSON schemas read by the validators.
- Root of `scripts/`: Restricted to the existing gate runner (`gates.mjs`), shared libraries (`lib.mjs`, `components.mjs`), the scripts that `package.json` or the gates run by path (`check-repo.mjs`, `sync-labels.mjs`, `basedpyright-maintainer.mjs`), and their associated configuration (`categories.json`, `biome-plugins/`, and the `tsconfig` files). No other files belong at the root of `scripts/`.

## Maintainer script conventions

These apply to the scripts that build and maintain this repository, on Nery's machine and in CI: `scripts/`, `.claude/hooks/` and `.claude/skills/*/scripts/`. They never apply to plugin scripts.

### Shebang

- Python: `#!/usr/bin/env python3`.
- Python with third-party dependencies: `#!/usr/bin/env -S uv run --script`, with the dependencies in PEP 723 inline metadata; never create a virtual environment.
- Shell: `#!/usr/bin/env bash`, followed by `set -euo pipefail`.
- Omit `-e`, `-u` or `pipefail` only where the script must keep running after a failing command (collecting results, a hook that must fail closed, a SessionStart hook that must never fail the session); say in a comment which flags are omitted and why.
- Never leave `set -x` in a script.
- Quote `"$@"` and `"${arr[@]}"` instead of changing `IFS`.
- Strict POSIX shell: `#!/bin/sh`.
- Node: `#!/usr/bin/env node`.

### Python version

- Target Python 3.15.
- Scripts in `.claude/skills/*/scripts/` and `scripts/release/` target Python 3.12: they run on the `python3` of CI's runner.

### Executability

- Run `chmod +x` on every maintainer script.

### Invocation

- Inside a script, call installed tools by bare name (`biome`, `basedpyright`, `uv`), never by full path or a prefix such as `npx`. Under `npm run`, `node_modules/.bin` comes first on `PATH`, so the npm tools resolve to the versions `package-lock.json` pins; `basedpyright`, `uv` and the other non-npm tools resolve to the ones installed on the machine.
