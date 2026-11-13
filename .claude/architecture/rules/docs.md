---
paths:
  - "docs/**"
---

# User guides

Guides for people who install plugins from this marketplace; GitHub renders them and the READMEs link to them.

## Where a new file goes
- Put a guide for every plugin user in `docs/`, and add its row to the Documentation table of the root `README.md` through `marketplace-readme-writer`, as `installation.md`, `managing-plugins.md`, `troubleshooting.md` and `faq.md` have.
- Put a guide that serves one plugin in `docs/`, and link it from that plugin's README through `plugin-readme-writer`, not from the root README, as `github-mcp-tools.md` does for `github-operations`.
- Put images the READMEs embed in `assets/`.

## Working here
- Treat `compatibility.md` as the single source for which components load in Claude Code and in Claude: each plugin README's Compatibility cells copy it character for character (`.claude/references/plugin-readme.md`), and each manifest takes its surfaces from it (`.claude/references/plugin-manifest.md`). When it changes, update every plugin README through `plugin-readme-writer`.
- Check each command, flag and UI path against `claude plugin --help`, `claude plugin <subcommand> --help` and the official docs before writing it.
