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

## Run in this order after each write or edit of a README, CHANGELOG, policy document or user guide

1. Run `npx biome check --write <file>` to format and lint it.
2. Fix every finding, then run step 1 again until it passes.
3. Read the file again before the next edit.
