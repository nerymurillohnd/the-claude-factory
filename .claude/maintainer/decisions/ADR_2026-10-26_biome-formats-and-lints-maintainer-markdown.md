---
status: superseded
date: 2026-10-26
decision-makers:
  - "Nery"
supersedes: none
superseded-by: ADR_2026-10-26_biome-never-formats-plugin-and-skill-markdown
---

# Biome formats and lints the maintainer Markdown; plugins adopt it on their next change

## Scope

Applies to the Markdown of this repository: which files Biome formats and lints, the Biome version CI installs, the README catalog that `scripts/generators/catalog.mjs` writes, and the italic style of the user docs and plugin READMEs. The files `.claude/CLAUDE.md` says are never formatted stay out of scope.

## Context and problem statement

`.claude/CLAUDE.md` said Biome formats and lints Markdown, while `biome.json` read only JS, TS and JSON (DEBT-009). Biome 2.6 added Markdown support. Research on 2026-10-26 (the configuration reference, the changelog, Context7, and the five `biome_markdown_*` crates at `biomejs/biome@0da9080`) and runs with Biome 2.6.2 and 2.6.3 showed:

- Biome rewrites `*italic*` as `_italic_` with no option to keep `*` (`biome_markdown_formatter/src/markdown/auxiliary/inline_italic.rs:15-46`); Prettier 3 gives the same output.
- Biome pads table columns, which made `catalog.mjs --check` fail; a `<!-- biome-ignore format: <reason> -->` comment right before a table keeps it as written (`gfm/auxiliary/table.rs:156-161`), while `biome-ignore-start/-end` is ignored by the formatter (`comments.rs:77`).
- The Markdown rules are `nursery` rules, which the recommended preset does not turn on.
- Formatting every Markdown file changed 232 files, 202 of them in 17 plugins, where each change needs a pull request and, outside a README-only change, a version bump.
- Biome 2.6.3 fixes two formatter bugs that changed documents (#12524, #12507), and CI installed Biome without a version.

How should the repository's Markdown be formatted and linted?

## Decision drivers

- A doc users read should not ship malformed with every check green.
- A plugin version should carry a change users can use, not whitespace.
- The catalog generator and its `--check` must keep agreeing with what is committed.
- Nursery rules can change behavior in any release.

## Considered options

- **Biome on the Markdown outside `plugins/`; each plugin joins on its next real change**: chosen.
- **Biome on all Markdown at once**: rejected because it ships 17 plugin versions whose only change is formatting.
- **No Markdown formatting, and correct CLAUDE.md**: rejected because the user docs would keep no check at all.

## Decision outcome

Chosen option: **Biome on the maintainer Markdown, plugins on their next change**, because it checks every doc users read from the repository without making them update plugins for whitespace.

- `biome.json` includes `*.md`, excludes the never-format files and lists one `!plugins/<name>/**/*.md` line per plugin not yet adopted; it parses frontmatter, indents with spaces, and turns on `useConsistentHeadingLevel`, `useFencedCodeLanguage` and `useSingleTopLevelHeading` as errors.
- `building-plugins` step 5 removes a plugin's line and formats its Markdown in that plugin's next change.
- `catalog.mjs` writes the suppression comment before each table and the category descriptions as `_…_`.
- `_italics_` is the style in `readme-style.md` and `maintaining-user-docs`.
- `validate.yml` installs `@biomejs/biome@2.6.3`, and the maintainer Biome gate reads `*.md`.

### Consequences

- Good, because the root README, `docs/`, the community files and the skills' references and assets are formatted and linted locally and in CI.
- Good, because the catalog stays exactly as generated, and `catalog.mjs --check` passes after formatting.
- Bad, because Biome checks headings and fenced-code languages only; links, anchors and prose are still checked by reading.
- Bad, because plugin Markdown stays unformatted until each plugin changes (logged as DEBT-013).
- Bad, because Biome upgrades are manual: the CI pin and the local binary move together, by hand.

## More information

Decided by Nery on 2026-10-26 ("aprobado", for option B as presented). Closes DEBT-009. Related: ADR_2026-10-21_remove-markdownlint.
