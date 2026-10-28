---
paths:
  - "scripts/**"
  - ".claude/hooks/**"
  - ".claude/skills/*/scripts/**"
---

# Maintainer Scripts

These rules apply only to the scripts that build and maintain this repository, on Nery's machine and in CI. They never apply to plugin scripts.

## Shebang

- Python: `#!/usr/bin/env python3`.
- Python with third-party dependencies: `#!/usr/bin/env -S uv run --script`, with the dependencies in PEP 723 inline metadata; never create a virtual environment.
- Shell: `#!/usr/bin/env bash`, followed by `set -euo pipefail`.
- Omit `-e` only where the script must keep running after a failing command (collecting results, a hook that must fail closed); say why in a comment.
- Never leave `set -x` in a script.
- Quote `"$@"` and `"${arr[@]}"` instead of changing `IFS`.
- Strict POSIX shell: `#!/bin/sh`.
- Node: `#!/usr/bin/env node`.

## Executability

- Run `chmod +x` on every maintainer script.

## Invocation

- Inside a script, call installed tools by bare name (`biome`, `basedpyright`, `uv`), never by full path or a prefix such as `npx`.
