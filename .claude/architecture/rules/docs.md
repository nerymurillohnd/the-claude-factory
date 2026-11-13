---
paths:
  - "docs/**"
---

# User guides (`docs/`)

Guides for people who install plugins from this marketplace. GitHub renders them, and the READMEs link to them.

## What each file is for
- `installation.md`, `managing-plugins.md`, `troubleshooting.md`, `faq.md`: marketplace-wide guides, listed in the Documentation table of the root `README.md`.
- `compatibility.md`: the single source for which components load in Claude Code and in Claude. Each plugin README's Compatibility cells copy it character for character, and each `plugin.json` sets its surfaces from it (`.claude/references/plugin-readme.md`, `.claude/references/plugin-manifest.md`).
- `github-mcp-tools.md`: serves only `github-operations`; that plugin's README links to it, and the root README does not.
- `assets/`: images the READMEs embed, such as `banner.svg`.

## Working here
- When `compatibility.md` changes, update the Compatibility section of every plugin README through `plugin-readme-writer`.
- A new marketplace-wide guide gets a row in the root README's Documentation table, through `marketplace-readme-writer`. A guide for one plugin is linked from that plugin's README, through `plugin-readme-writer`.
- Check every command, flag and UI path against `claude plugin --help`, `claude plugin <subcommand> --help` and the official docs before writing it.
