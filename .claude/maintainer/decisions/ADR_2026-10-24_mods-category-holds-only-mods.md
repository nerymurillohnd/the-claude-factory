---
status: accepted
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# A Mods category that holds only mods

## Scope

- In scope: `scripts/categories.json`, the `category` of plugins in `.claude-plugin/marketplace.json`, and the rule `scripts/validators/readme-catalog-consistency.py` enforces.
- Out of scope: other categories.

## Context and problem statement

Plugins that change Claude Code's own interface had no category: `tool-ledger` and `turn-meter`, whose only component is a mod, sat in Productivity, and `project-maintainer` ships a mod beside its record skills. Should mods get a category, which plugins go there, and what must the validator require?

## Decision drivers

- A plugin has one category, chosen by its purpose.
- A category must not hold a plugin that does not fit its name.

## Considered options

- **A `mods` category; only plugins that are a mod move there; a plugin in `mods` must be a mod, and a mod may sit elsewhere**: chosen.
- **Every plugin that ships a mod moves to `mods`**: rejected because `project-maintainer`'s purpose is its records; its mod only guards them.
- **Create the category empty**: rejected because the two mod plugins would stay misfiled.

## Decision outcome

Chosen option: **🧩 Mods, holding only mods**:

- `tool-ledger` and `turn-meter` move to `mods`; `project-maintainer` stays in `documentation`.
- The catalog validator fails a plugin in `mods` that is not a mod, as the mods reference defines one: `hooks/hooks.json` lists one path under `modules` to a `.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.mts`, `.cts` or `.tsx` module inside the plugin.

### Consequences

- Good, because measured: eight probes (missing module, no `modules`, two paths, a path outside the plugin, a wrong extension, no `hooks/`, a non-mod in `mods`, and the intact copy) behaved as intended.
- Bad, because a new mod-only plugin must be given the category by hand; nothing requires it.

## More information

- Decided by Nery in the session of 2026-10-24.
