---
paths:
  - "scripts/**"
---

# Maintainer scripts

- Put a check of a repository file in `validators/`, a check beyond the file (a free name, a live URL) in `checkers/`, a script that writes repository files in `generators/`, and the release scripts in `release/`.
- Put one JSON Schema per file shape in `schemas/`, and stubs for an untyped dependency in `typings/<package>/`.
- Put tests in `testers/`, mirroring the package under test, in `test_*.py` files written with `unittest`, never pytest.
- Ask the owner before creating a subfolder that is not listed here.
- Look up a script in `.claude/architecture/refactor.md` before writing it, and rebuild it to current official practice instead of copying it from `main`.
- Write the failing test first, then the code, and confirm the test fails without the change.
- Run `npm run test:scripts` after each change.
- Start every new `.py` file under `validators/` and `testers/` with `#!/usr/bin/env python3` and give it mode 100755.
- Import package modules absolutely (`from validators.skill_lint.model import Finding`).
- Add each ruamel.yaml member a script uses to the stubs in `typings/ruamel/yaml/`.
- Delete a subfolder's `.gitkeep` in the same commit as its first script.
