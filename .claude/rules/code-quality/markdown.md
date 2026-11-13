---
paths:
  - "**/*.md"
---

# Markdown quality

Format and lint Markdown only with Biome, never with ruff, Prettier or another formatter; `ruff.toml` excludes `*.md`.

## Markdown Claude reads as instructions

- Never format or lint the Markdown Claude reads as instructions: every `CLAUDE.md` and `CLAUDE.local.md`, and the rules, memory, skills, agents, commands and evals, in `.claude/` and in each plugin.
- Leave them as written: a formatter pads their tables, and the padding costs tokens every time they load.
- Write their tables compact: `| Task | Command |` with `| :-- | :-- |` separators.
- When you add a `.claude/` folder of instruction Markdown, add it to the exclusions under `files.includes` in `biome.jsonc`.
- Leave the maintainer working notes unformatted too (records, plans, specs and handoffs); `biome.jsonc` excludes them.

## Markdown written for people

- Format and lint READMEs, CHANGELOGs, policy documents and user guides, plugin ones included, with Biome.
- After editing one, format and lint it in one pass: `npx biome check --write <file>`; fix by hand what it could not fix, then read the file again before the next edit.
- Before a commit, run `npm run lint:js`.
