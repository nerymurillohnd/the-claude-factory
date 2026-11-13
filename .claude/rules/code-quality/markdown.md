---
paths:
  - "**/*.md"
---

# Markdown

- Format and lint Markdown only with Biome, never with ruff, Prettier or another formatter; `ruff.toml` excludes `*.md`.
- Fix every issue a check reports before the next step or task; never leave it as debt.

## Gotchas

- Never format or lint the Markdown Claude reads as instructions: `CLAUDE.md`, `CLAUDE.local.md`, rules, memory, skills, agents, commands and evals, in `.claude/` and in each plugin. A formatter pads their tables, and the padding costs tokens on every load.
- Write their tables compact: `| Task | Command |` with `| :-- | :-- |` separators.
- When you add a `.claude/` folder of instruction Markdown, add it to the exclusions under `files.includes` in `biome.jsonc`.
- Leave the maintainer working notes (records, plans, specs, handoffs) unformatted; `biome.jsonc` excludes them.
- Biome refuses an excluded file ("These paths were provided but ignored"); that confirms the exclusion, not an error to fix.

## After writing or editing a README, CHANGELOG, policy document or user guide, in this order

1. Run `npx biome check --write <file>` to format and lint it; fix the rest by hand and run it again.
2. Read the file again before the next edit, because step 1 rewrites it.

## Before a commit

1. Run `npm run lint:js` to check every Markdown file Biome reads.
