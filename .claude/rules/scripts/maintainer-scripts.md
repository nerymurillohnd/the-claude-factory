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

## Claude Code hook scripts

- Simple, direct logic: Bash.
- Logic beyond that: Python, with the `python3` shebang.
- Python that needs third-party dependencies: the `uv run --script` shebang with them in PEP 723 inline metadata, or the `python3` shebang with them passed in the hook's `command` (`uv run --with <package> <script>`).

## Python version

- Target Python 3.15.
- Scripts in `.claude/skills/*/scripts/` target Python 3.12.

## Executability

- Run `chmod +x` on every maintainer script.

## Invocation

- Inside a script, call installed tools by bare name (`biome`, `basedpyright`, `uv`), never by full path or a prefix such as `npx`.
