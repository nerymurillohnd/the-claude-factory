---
status: accepted
date: 2026-11-14
decision-makers:
  - "Nery (project owner)"
supersedes: ADR_2026-11-12_biome-formats-only-human-markdown
superseded-by: none
---

# Biome lints every file and skips only the formatting of Markdown Claude reads as instructions

## Scope

`files.includes` and `overrides` in `biome.jsonc`, the Biome line of `.claude/CLAUDE.md` and the Biome line of `.claude/rules/architecture/claude-dir.md`. Affects every file Biome reads. Maintainer scope.

## Context and problem statement

ADR_2026-11-12_biome-formats-only-human-markdown kept Biome off the Markdown Claude reads, so table padding would not spend tokens. It did so in `files.includes`, which removes a file from every Biome tool: ten `.claude/` folders were excluded whole (`rules`, `memory`, `references`, `templates`, `architecture`, `maintainer`, `plans`, `session-handoff`, `specs`, `scheduled-tasks`) and the `*.md` of skills, agents, commands and evals were neither formatted nor linted. `biome check .` read 181 files. On 2026-11-14 those folders held only Markdown and a `.gitkeep`, so no script or JSON was being skipped yet, but any file added there would have been.

The owner stated on 2026-11-14 that Biome must skip only the formatting of that Markdown and run everything else.

## Decision drivers

- Spend no tokens on table padding in files Claude loads.
- Lint every file Biome can read, instruction Markdown included.
- Never leave a folder outside Biome because of one tool.

## Considered options

- **Drop the exclusions; one override turns the formatter off for the `*.md` of instruction folders; a second turns `useTopLevelHeading` off for the bodies of agents, commands, memories and eval prompts and graders**: chosen.
- **The same, with `useTopLevelHeading` on everywhere**: rejected by the owner because those bodies are prompts, not documents, and a level-1 heading in 25 files would cost tokens and tell Claude nothing.
- **Keep the exclusions in `files.includes` (ADR_2026-11-12_biome-formats-only-human-markdown)**: rejected because it also removes those files from linting and drops whole folders.

## Decision outcome

Chosen option: **format off by override, lint on everywhere**, as the owner decided, because it keeps Claude's files compact and lets Biome check them.

### Consequences

- Good, because `biome check .` now reads 654 files instead of 181, and Biome lints instruction Markdown: it found 13 fenced code blocks with no language, 5 documents with more than one level-1 heading and 1 skipped heading level.
- Good, because a new non-Markdown file in a `.claude/` folder is formatted and linted with no configuration change.
- Bad, because `npm run lint:js` fails until the plugins' Markdown findings are fixed (DEBT-006), on top of the ten findings it already had.
- Bad, because a new folder of instruction Markdown must still be added to the first override by hand, or Biome formats it.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Instruction Markdown is not formatted | `npx biome format .claude/CLAUDE.md .claude/rules/plugins.md` | "These paths were provided but ignored" (2026-11-14) | Each Biome upgrade |
| Instruction Markdown is linted | `npx biome lint .claude/CLAUDE.md` | "Checked 1 file" (2026-11-14) | Each Biome upgrade |
| Human Markdown is still formatted | `npx biome format README.md` | "Checked 1 file" (2026-11-14) | Each Biome upgrade |
| `npm run lint:js` passes | `npm run lint:js` | pending: 26 errors, all in plugin files (DEBT-006) | When DEBT-006 closes |

## More information

- The owner decided on 2026-11-14 in this session: format only skipped, everything else runs; `useTopLevelHeading` off for agents, commands, memories and evals.
- The four level-1 headings of `.claude/architecture/refactor.md` were demoted in the same change, so maintainer files have no Biome finding.
- Biome 2.6.6, pinned in `package.json`.
