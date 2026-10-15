---
paths:
  - ".github/**"
---

# GitHub operations

## Issues

- Replies: English, friendly, specific, from `.claude/templates/issue-replies.md`. Never promise dates.
- Close an issue only after its fix is released, linking the GitHub Release; or with a clear explanation for duplicate, wontfix or upstream.

## Workflows

- Pin every action to a full commit SHA with the version in a comment; Linux jobs on `ubuntu-24.04`, never `ubuntu-latest`.

## Labels

- Defined in `.github/labels.json`; `plugin: <name>` labels are derived from the catalog.
- Sync after adding a plugin or editing labels: `node .github/scripts/sync-labels.mjs` (needs authenticated `gh`).
