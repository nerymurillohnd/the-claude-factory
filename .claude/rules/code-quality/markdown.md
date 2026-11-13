---
paths:
  - "**/*.md"
---

# Markdown

- Never format or lint the Markdown Claude reads as instructions: `CLAUDE.md`, `CLAUDE.local.md`, and the rules, memory, skills, agents, commands and evals, in `.claude/` and in each plugin.
- Write tables in that Markdown compact, as `| Task | Command |` with `| :-- | :-- |` separators, because padding costs tokens on every load.
- Add each new `.claude/` folder of instruction Markdown to the exclusions under `files.includes` in `biome.jsonc`.
- Run `npx biome check --write <file>` after each edit of a README, CHANGELOG, policy document or user guide to format and lint it, because no hook runs Biome; then read the file again.
