---
status: accepted
date: 2026-10-26
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# The plugin README template takes the shape of the published READMEs

## Scope

Applies to `.claude/skills/building-plugins/assets/README-template.md`, what `scaffold-plugin.py` fills in it, the README checks of `scripts/check-repo.mjs`, the test fixture of `scripts/tests/scripts.test.mjs`, and the frozen `.claude/templates/`. The 17 published plugin READMEs are out of scope: they keep their shape.

## Context and problem statement

DEBT-011 recorded that the skill's README template had eight sections of its own (Install, Update, Prerequisites, Configuration, Usage, What this plugin runs and sends, Uninstall, License) and one "Works in" line, while the 17 published READMEs, the frozen `.claude/templates/plugin/README.md` and `REQUIRED_PLUGIN_SECTIONS` in `scripts/lib.mjs` shared another shape: a centered hero with five badges, a TL;DR, emoji headings, and Why use it, What's inside, Requirements, Installation, Usage, Updating, Uninstalling, Compatibility, Changelog and License. A plugin the scaffold created failed `check-repo.mjs`, and the skill's own rules asked for badges and Compatibility rows its template lacked. Which shape should the template have?

## Decision drivers

- The published READMEs are what users read; changing them needs one pull request per plugin.
- The README must state what the plugin does on the user's machine (`.claude/CLAUDE.md` → Operating Standard).
- The scaffold should write what its command line already knows.

## Considered options

- **The template takes the published shape and keeps the new template's disclosure section**: chosen.
- **The skill's rules drop badges, Compatibility and emoji headings, and the 17 READMEs move to the new shape**: rejected because it needs 17 plugin pull requests to make the READMEs poorer.
- **The union proposed in `.claude/specs/2026-10-25-plugin-docs-create-and-update-design.md`**: not adopted; that spec stays a dated proposal.

## Decision outcome

Chosen option: **the published shape plus "What this plugin runs and sends"**, because new plugins then match what users already see and what the checks enforce, without touching a published plugin.

- The template keeps `<…>` placeholders: lowercase ones the scaffold fills (plugin, repository, marketplace, description, the Category and Works in badges and line, and the `<app>` / `<code-only>` blocks for the plugin's surfaces), and ones starting with a capital letter the author fills.
- `check-repo.mjs` reports an author placeholder left outside code, the check that replaces the template's former TODO comments.
- The tests build their demo plugin with the scaffold, and `.claude/templates/` is deleted.

### Consequences

- Good, because a plugin the scaffold creates passes `check-repo.mjs` once its author placeholders are filled and its Compatibility rows match what it ships.
- Good, because each template lives once, in the skill that uses it.
- Neutral, because inside code spans and fenced blocks the placeholder check reports only the placeholders the template holds, such as `` `/<plugin>:<Skill>` `` (commit `ba13311`), so other `<…>` text in code, such as `<YYYY-MM-DD>`, passes.

## More information

Decided by Nery on 2026-10-26: he asked to rewrite the template "con las secciones, el orden, los emoji y los badges de los READMEs publicados … y con la sección de divulgación agregada", then to move the test fixture to the scaffold and delete `.claude/templates/`. Closes DEBT-011. Related: ADR_2026-10-25_plugin-readme-rules-live-in-building-plugins, ADR_2026-10-25_scaffold-writes-identity-not-readme-content.
