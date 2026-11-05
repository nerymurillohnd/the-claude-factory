---
paths:
  - ".claude/hooks/**"
---

# Local Claude Code hook scripts

The scripts in `.claude/hooks/` that `.claude/settings.json` runs as this project's Claude Code hooks. The general conventions in `scripts.md` (shebang, Python version, executability) apply to them too.

- Simple, direct logic: Bash.
- Logic beyond that: Python, with the `python3` shebang.
- Python that needs third-party dependencies: the `uv run --script` shebang with them in PEP 723 inline metadata, or the `python3` shebang with them passed in the hook's `command` (`uv run --with <package> <script>`).
