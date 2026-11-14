---
paths:
  - "**/*.md"
---

# Markdown

- Never format the Markdown Claude reads as instructions: `CLAUDE.md`, `CLAUDE.local.md`, and the rules, memory, skills, agents, commands and evals, in `.claude/` and in each plugin. Biome still lints it.
- Write tables in that Markdown compact, as `| Task | Command |` with `| :-- | :-- |` separators, because padding costs tokens on every load.
- Add each new `.claude/` folder of instruction Markdown as a `*.md` pattern to the first `overrides` entry of `biome.jsonc`; never exclude a folder in `files.includes`.
- Run `npm run lint:frontmatter -- <file>` after each edit of a skill's, agent's or command's frontmatter.
- Run `npx biome check --write <file>` after each edit of a README, CHANGELOG, policy document or user guide to format and lint it, because no hook runs Biome; then read the file again.
