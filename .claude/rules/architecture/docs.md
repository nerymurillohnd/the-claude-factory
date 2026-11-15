---
paths:
  - "docs/**"
---

# User guides

- Put a guide for every plugin user in `docs/`, and add its row to the Documentation table of the root `README.md` with the `docs-maintenance` skill.
- Put a guide for one plugin in `docs/`, and link it from that plugin's README, not from the root README.
- Put images the READMEs embed in `assets/`.
- Treat `compatibility.md` as the single source of which components load in Claude Code and in Claude, and update every plugin README with the `docs-maintenance` skill when it changes.
- Check each command, flag and UI path against `claude plugin --help` and the official docs before writing it.
