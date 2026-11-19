---
paths:
  - "**/*.md"
---

# Markdown

- Treat `CLAUDE.md`, `CLAUDE.local.md`, and the rules, memory, skills, agents, commands and evals, in `.claude/` and in each plugin, as the Markdown Claude reads as instructions.
- Write tables in that Markdown compact, each cell as wide as its text, as `| Task | Command |` with `| :-- | :-- |` separators: padding cells to align the columns costs tokens and bytes on every load.
- Add each new `.claude/` folder of instruction Markdown as a `*.md` pattern to the first `overrides` entry of `biome.jsonc`; never exclude a folder in `files.includes`.
- Run `npm run lint:frontmatter -- <file>` after each edit of a skill's, agent's or command's frontmatter.
