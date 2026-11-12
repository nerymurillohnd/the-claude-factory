---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Biome formats Markdown people read, never Markdown Claude reads as instructions

## Scope

`files.includes` in `biome.jsonc`. Affects every Markdown file in the repository. Ruff does not format Markdown (`ruff.toml` excludes `*.md` from formatting), so Biome is the only Markdown formatter.

## Context and problem statement

Biome 2.6 formats Markdown by default and pads every table cell to the widest cell in its column. A local test with Biome 2.6.6 grew a four-row table from 98 to 221 bytes. The 2.6.6 configuration schema has no option to stop table padding (`markdown.formatter` offers only `enabled`, `formatEmbeds`, `indentStyle`, `indentWidth`, `lineEnding`, `lineWidth`, `proseWrap` and `trailingNewline`). Claude reads instruction, rule, skill, agent and memory files on every session, so padding there spends tokens with no benefit.

## Decision drivers

- Keep human documentation consistently formatted.
- Spend no tokens on padding in files Claude loads.
- Keep the scripts inside skill folders checked.

## Considered options

- **Format Markdown for people; exclude the Markdown Claude reads**: chosen. Formatted: README, CHANGELOG, `docs/`, the community files, and each plugin's README, CHANGELOG and NOTICE. Excluded: `**/CLAUDE.md`, `**/CLAUDE.local.md`, `.claude/rules`, `.claude/memory`, `.claude/references`, `.claude/templates`, `.claude/architecture`, the `.md` files of `.claude/skills`, `.claude/agents`, `.claude/commands`, and of `plugins/*/skills`, `agents`, `commands` and `evals`, plus the maintainer working folders.
- **Never format Markdown (the rule on `main`)**: rejected because human docs would drift with no formatter.
- **Format all Markdown**: rejected because of the token cost above.

## Decision outcome

Chosen option: **format Markdown for people and exclude the Markdown Claude reads**, as the project owner decided, because it keeps human docs consistent and leaves Claude's files compact.

### Consequences

- Good, because the 24 plugin READMEs and changelogs are now formatted (commit 17c5f25).
- Good, because `*.md` patterns inside skill, agent and command folders keep their scripts checked.
- Bad, because a new folder of Claude-read Markdown must be added to the exclusions by hand, or Biome formats it.

## More information

- Sources: Biome 2.6.6 configuration schema in `node_modules/@biomejs/biome/configuration_schema.json`; `biomejs/website` `reference/configuration.mdx` ("Glob syntax reference"); a dry run on sample files.
- Commit: b5dc1a9.
