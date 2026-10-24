---
status: accepted
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Catalog facts are generated from plugins/

## Scope

- In scope:
  - `plugins[]` of `.claude-plugin/marketplace.json`;
  - the generated blocks of the root `README.md`;
  - the scripts that write them: `scripts/generators/`, `new-plugin.mjs` and `bump-version.mjs`;
  - the gates that check them.
- Out of scope:
  - the top-level fields of `marketplace.json` (`name`, `description`, `owner`, `renames`), which no plugin holds and which stay hand-written;
  - where the category lives, which ADR_2026-10-24_plugin-category-lives-in-metadata covers.

## Context and problem statement

Nery asked for a generator of the README catalog "contra realidad en plugins/". `scripts/catalog.mjs` already built the catalog, but from the entries of `marketplace.json`. Those entries were edited by hand, by `new-plugin.mjs` or by a person.

Measured on the 16 plugins:
- each entry's `name` and `source` follow from its directory;
- each entry's `description` is the `description` of its `plugin.json`.

Every value except the category was a copy. The question was whether to chain plugins/ → marketplace → catalog, or to build both files from plugins/ in parallel.

## Decision drivers

- One value per fact, written in one place.
- The catalog shows what users receive, and that is `marketplace.json`.
- No second copy of logic the Node scripts already share.

## Considered options

- **Chain: `generators/marketplace.mjs` builds `plugins[]` from `plugins/`, and `generators/catalog.mjs` builds the README from `marketplace.json`, both in Node:** chosen.
- **Both from plugins/:** rejected. Two independent derivations of the same facts can disagree, and the catalog could list a plugin the marketplace does not publish.
- **Both generators in Python, like the validators:** rejected. The catalog needs component detection (`components.mjs`) and the surface profiles (`SURFACE_PROFILES` in `lib.mjs`), which `check-repo.mjs` and `new-plugin.mjs` also use. A Python port would leave two copies of both.

## Decision outcome

Chosen option: **the Node chain**, because it gives each fact one source and one direction, and it reuses the shared modules.

- `scripts/generators/marketplace.mjs` keeps every top-level field. It rebuilds `plugins[]` sorted by name, with `name`, `source`, `description` and `category`. It fails, and writes nothing, when a plugin has:
  - no manifest;
  - a symlinked directory;
  - a name that differs from its directory;
  - an empty description;
  - a missing or unknown category.
- `scripts/catalog.mjs` moved to `scripts/generators/catalog.mjs` with the same output.
- `new-plugin.mjs` registers a plugin by regenerating the marketplace.
- `npm run generate` runs both generators.
- A `marketplace` policy gate runs before the `catalog` gate.
- `check-repo.mjs` dropped the entry category, entry description and README catalog checks, which the two `--check` gates own.

### Consequences

- Good, because measured: the generated `marketplace.json` and README are byte-identical to the committed ones. Nine generator tests and a `new-plugin` test watched RED, then GREEN, prove the failures above and the registration of every plugin directory.
- Bad, because a hand edit to `plugins[]` is now overwritten. A rename or removal edits the plugin and `renames`, then regenerates; the rename procedure says so.
- Bad, because the policy gate group stops at `node-tests` on its three pre-existing failures (DEBT-007), so `npm run gates` reaches the new `marketplace` gate only once those are fixed.

## More information

- Decided by Nery in the session of 2026-10-24: "dos scripts. uno que genera desde plugins/ el marketplace.json y otro que genera desde el markeplace json el catalogo". He then approved the plan `.claude/plans/2026-10-24-marketplace-and-catalog-generators.md`.
- Related: ADR_2026-10-24_repository-checks-move-to-python-validators, ADR_2026-10-21_gates-run-from-one-script.
