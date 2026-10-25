---
status: proposed
date: 2026-10-24
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# A plugin's catalog category lives in its manifest's metadata

## Scope

- In scope: where each plugin's catalog category is written, the source that `scripts/generators/marketplace.mjs` reads.
- Out of scope: the category list itself (`scripts/categories.json`) and the rule that `mods` holds only mods (ADR_2026-10-24_mods-category-holds-only-mods).

## Context and problem statement

ADR_2026-10-24_catalog-facts-are-generated-from-plugins builds `marketplace.json` `plugins[]` from `plugins/`. The category was the one entry value that no plugin file held.

Measured on Claude Code 2.1.310:
- `category` at the root of `plugin.json` fails `claude plugin validate --strict` with `✘ Validation failed`;
- `metadata.category` passes with `✔ Validation passed`.

The manifest reference describes `metadata` as "Free-form object for your own data (entitlement, catalog fields). Claude Code does not read it" (`/en/plugins/manifest-reference#fields`).

## Decision drivers

- Every catalog fact comes from `plugins/`.
- No field that fails strict validation.
- As few releases without a user-visible change as possible.

## Considered options

- **`metadata.category` in each `plugin.json`:** applied. Its cost is one patch release for each of the 16 plugins, because the versioning rule ships any non-README plugin change.
- **A `plugins` list per category in `scripts/categories.json`:** not applied. It touches no plugin and needs no release, but the category would live outside the plugin, and a new plugin would need an edit in a second file.
- **`category` at the root of `plugin.json`:** rejected, because it fails `--strict`.

## Decision outcome

Applied option: **`metadata.category`**.

- The 16 manifests, the scaffold template, the `Manifest` typedef and the manifest schema all carry it. The schema checks it as a kebab-case string, and the generator checks it against `categories.json`.
- Every plugin moved one patch version, with the note "The marketplace now reads this plugin's catalog category from its manifest; nothing changes in how the plugin works."

This stays `proposed`: the plan put this choice to Nery, and he ran the plan without picking either option. Applying it was my call so the work could finish. If he picks the `categories.json` list, revert the manifest field and the 16 patch bumps before any push of `main`.

### Consequences

- Good, because measured:
  - `plugin-json-schema.py` and `claude plugin validate --strict` pass on all 16 manifests;
  - a bad id (`"Bad Id"`) fails the schema;
  - an unknown id fails the generator.
- Bad, because the next push of `main` tags and releases all 16 plugins with no change in behavior.

## More information

- Applied in the session of 2026-10-24 while executing `.claude/plans/2026-10-24-marketplace-and-catalog-generators.md`. The plan's decision gate is awaiting Nery's confirmation.
