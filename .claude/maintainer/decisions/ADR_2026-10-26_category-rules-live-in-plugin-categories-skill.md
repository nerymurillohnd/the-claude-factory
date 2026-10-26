---
status: accepted
date: 2026-10-26
decision-makers:
  - "Nery"
supersedes: none
superseded-by: none
---

# Category rules live in the `plugin-categories` skill, with its own catalog check

## Scope

Applies to the rules for choosing and changing a plugin's category and for changing `scripts/categories.json`, and to the check of the root README catalog against `plugins/` and `marketplace.json`. The generators (`scripts/generators/`), `scripts/categories.json` itself and the validators of `scripts/validators/` are out of scope.

## Context and problem statement

`.claude/CLAUDE.md` held a Plugin Categories section: the list of category ids, where a category is defined, one category per plugin, the `mods` rule, and `npm run generate` after a change. It loaded in every session, repeated the ids that `scripts/categories.json` defines, and said nothing about changing a published plugin's category or a category itself. The skills that meet a category (`building-plugins`, `building-mods`, `plugin-renames-and-removals`) pointed to that section or to each other. Where should the category rules live, and what checks them?

## Decision drivers

- `.claude/rules/workflow.md` is a contract of stages, skills and key jobs; procedures live in skills.
- A skill runs the checks of its own scope with its own scripts; gates are a separate layer (ADR_2026-10-25_skill-checks-are-separate-from-gates).
- One source per fact: the category ids live only in `scripts/categories.json`.

## Considered options

- **A `plugin-categories` project skill with its own `check-catalog-categories.py`**: chosen.
- **Keep the rules in `.claude/CLAUDE.md`**: rejected because they load in every session and cover only a new plugin.
- **Move `scripts/categories.json` into the skill**: rejected because the generators, `readme-catalog-consistency.py`, the repository tests and the scaffold read it, so repository tooling would depend on a skill folder.

## Decision outcome

Chosen option: **a `plugin-categories` skill with its own catalog check**, because it gives every category situation one owner and a check it runs while it works, without moving the data the repository tooling reads.

### Consequences

- Good, because the skill covers four situations (a new plugin, a changed category, a plugin gaining or losing a mod, a change to `categories.json`), and `building-plugins`, `building-mods`, `plugin-renames-and-removals` and `workflow.md` load it at those moments.
- Good, because `check-catalog-categories.py` fails on a catalog row under the wrong category, a missing or extra row, and a non-mod in `mods`, checked against planted defects on 2026-10-26.
- Bad, because `check-catalog-categories.py` is a copy of `scripts/validators/readme-catalog-consistency.py` with its own path and usage line, so a fix to one must reach the other.

## More information

Decided by Nery on 2026-10-26: "conviértela en skill, dale entrada en el workflow.md y referencia desde los skills en que aplica", then "empaqueta script de validación del catálogo en el README.md contra plugins existentes y la categoría en el marketplace.json". Related: ADR_2026-10-24_mods-category-holds-only-mods, ADR_2026-10-24_plugin-category-lives-in-metadata.
