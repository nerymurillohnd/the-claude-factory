---
paths:
  - "**/*.md"
---

# Markdown

- Never format or lint the Markdown Claude reads as instructions: `CLAUDE.md`, `CLAUDE.local.md`, rules, memory, skills, agents, commands and evals, in `.claude/` and in each plugin.
- Write tables in instruction Markdown compact: `| Task | Command |` with `| :-- | :-- |` separators.
- Add each new `.claude/` folder of instruction Markdown to the exclusions under `files.includes` in `biome.jsonc`.
- Format and lint every other Markdown file only with Biome; never ruff, Prettier or another formatter.
- Fix every finding before moving on; never leave one as debt.

## After each write or edit of a README, CHANGELOG, policy document or user guide, run in order

1. Format and lint: `npx biome check --write <file>`.
2. Fix every finding, then repeat step 1 until it passes.
3. Read the file again before the next edit.
