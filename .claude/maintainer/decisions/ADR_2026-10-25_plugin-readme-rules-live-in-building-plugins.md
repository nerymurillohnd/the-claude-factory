---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-25_marketplace-user-docs-have-their-own-skill
superseded-by: none
---

# Plugin README rules live in building-plugins; the marketplace's docs stay in maintaining-user-docs

## Scope

Where the rules for writing user documentation live:
- the marketplace's own documents (the root `README.md` outside its generated blocks, `docs/`, `SECURITY.md`, `SUPPORT.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, the root `LICENSE`);
- each plugin's `README.md`, and the templates a plugin is built from.

Issues, issue forms and the root `CHANGELOG.md` are out of scope.

## Context and problem statement

ADR_2026-10-25_marketplace-user-docs-have-their-own-skill gave the marketplace's documents the `maintaining-user-docs` skill. It kept `.claude/rules/user-docs.md` for plugin READMEs and their templates, because no skill covered them yet.

Later the same day:
- the `building-plugins` skill was added, and it is where a plugin's README is written;
- an audit found that no skill held `user-docs.md`'s style and template rules for plugin READMEs, nor said how the plugin templates are kept.

That left two places, a rule and a skill, governing the same README. Where should the plugin README rules live?

## Decision drivers

- A gap is closed in the skill that owns the work, not left in a rule beside it.
- New, validated work outranks existing files.
- One source per rule.
- Each skill holds its own templates as assets, with a reference on how to use them.

## Considered options

- **Move the plugin README rules into `building-plugins` and delete `user-docs.md`**: chosen.
- **Keep `user-docs.md` beside the skill**: rejected, because it keeps two sources for one README.
- **Make `building-plugins` follow the older `.claude/templates/plugin/README.md`**: rejected, because new, validated work outranks existing files. It was tried and reverted the same day.

## Decision outcome

Chosen option: **move the rules into `building-plugins`**, because the skill that writes a plugin's README now holds its template and style.

- **`maintaining-user-docs`** still covers the marketplace's own documents, and `references/root-readme.md` holds the root README blueprint.
- **`building-plugins`** holds the plugin README rules:
  - `references/readme-style.md` has the style and the template rules from `user-docs.md`;
  - `references/templates.md` says how each asset is filled and changed;
  - `assets/README-template.md` is the template.
- **`.claude/rules/user-docs.md` is deleted** (commit 9fef01f). The skill's own README template is kept (commit 9ceffb3).
- **The older templates are kept, frozen,** in `.claude/templates/` (commit a8b0554), because older checks still read them (DEBT-011).

### Consequences

- Good, because a plugin README has one owner skill, which holds its template, style and procedure.
- Bad, because until DEBT-011 closes, the repository's checks still enforce the older README shape, and the templates exist twice.

## More information

Decided by Nery on 2026-10-25 in this session. This record replaces the earlier one, whose outcome named `user-docs.md` as the plugin README source. ADR_2026-10-24_workflow-is-a-stage-map still lists `user-docs.md`, `mods.md` and `skill-authoring.md` as path-scoped rules; none of the three exists now.
