---
status: accepted
date: 2026-10-26
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-26_biome-formats-and-lints-maintainer-markdown
superseded-by: none
---

# Biome never formats the Markdown of plugins and project skills

## Scope

Which Markdown files Biome reads in this repository: `biome.json` (`files.includes`), the never-format list in `.claude/CLAUDE.md`, and step 5 of the `building-plugins` skill. Biome still formats and lints the other Markdown: the root README, `docs/` and the community files. JS, TS, JSON and YAML are out of scope.

## Context and problem statement

ADR_2026-10-26_biome-formats-and-lints-maintainer-markdown had each plugin's Markdown adopt Biome on that plugin's next change, through one `!plugins/<name>/**/*.md` line per plugin in `biome.json`, and had Biome format the skills' references and assets. DEBT-013 tracked the plugins that had not joined yet. On 2026-10-26 Nery listed the paths whose Markdown Biome must never format: `plugins/`, `.claude/skills/`, `.claude/memory/`, `.claude/session-handoff/`, `.claude/maintainer/`, every `CLAUDE.md`, `.claude/plans/`, `.claude/rules/`, `node_modules/` and `.claude/specs/`. All but `plugins/` and the non-`SKILL.md` files of `.claude/skills/` were already excluded.

## Decision drivers

- Nery's explicit rule for these paths.
- One exclusion pattern, the existing never-format list, rather than a second partial one.
- A plugin change should not carry formatting churn of its Markdown.

## Considered options

- **Exclude all Markdown under `plugins/` and `.claude/skills/` from Biome, like the rest of the never-format list**: chosen.
- **Keep the per-plugin adoption on each plugin's next change**: rejected by Nery's rule.
- **Lint the plugin Markdown without formatting it**: not chosen; Nery's rule names formatting, and the never-format list excludes its files from Biome entirely.

## Decision outcome

Chosen option: **exclude them, like the never-format list**, because it applies Nery's rule with the pattern the repository already uses.

- `biome.json` excludes `plugins/**/*.md` and `.claude/skills/**/*.md`; the 17 per-plugin lines are gone (commit fcd793c).
- `.claude/CLAUDE.md` lists every Markdown file under those trees among the files never formatted, and no longer says a plugin's Markdown joins Biome.
- `building-plugins` step 5 no longer formats a plugin's Markdown.

### Consequences

- Good, because a plugin change carries no formatting diff of its Markdown.
- Bad, because Biome no longer checks heading levels or fenced-code languages in plugin READMEs, skills, references and changelogs; reading is the only check there.
- Bad, because the skills' references and assets, formatted until now, are no longer checked by Biome either.

## More information

Decided by Nery on 2026-10-26, in the session that closed DEBT-013 as accepted. `.CLAUDE` in his list is read as every `CLAUDE.md`, since no `.CLAUDE` path exists.
