---
name: plugin-categories
description: Use when choosing a new plugin's category, changing a plugin's category, deciding whether a plugin belongs in mods, or adding, rewording, reordering, renaming or removing a category in scripts/categories.json. Not for the rest of a plugin's identity, its README style or its release.
---

# Plugin categories

The category is how users browse this marketplace: the root README catalog groups plugins by it, and plugin READMEs that carry a Category badge show it. A wrong or drifting category hides a plugin from the users it serves.

## Where categories live

- `scripts/categories.json` is the only place a category is defined: its `id`, `emoji`, `title` and `description`, and the order of the list, which is the order of the README catalog. Read the ids there; never list them anywhere else.
- A plugin's category is decided in one place, `metadata.category` of its `plugin.json`. Everything else follows it:
  - `npm run generate` copies it into `marketplace.json` (`marketplace.mjs`) and the root README catalog (`catalog.mjs`). Never edit the category in either file by hand. `marketplace.mjs` writes nothing while any plugin's category is missing or not an id of `categories.json`, and `catalog.mjs` does not run after it fails.
  - The first `keywords` entry, which the scaffold sets to the category id, and the README's Category badge, when it has one, are copies you change by hand.
- The catalog shows only the categories some plugin uses, and its links are built from each category's emoji and title.

## Rules

1. Every plugin has exactly one category, chosen by its purpose: what users install it for, not the component types it ships.
2. `mods` only when the plugin is a mod: its `hooks/hooks.json` lists one hooks module under `modules`, and the mod is its purpose. A mod whose purpose is another goes in that category. A plugin in `mods` that no longer has its hooks module must leave `mods`; `check-catalog-categories.py` fails until it does.
3. Every change to `scripts/categories.json` is Nery's decision. When no category fits a plugin, propose a new one to Nery; never stretch an existing one.

## Script

`.claude/skills/plugin-categories/scripts/check-catalog-categories.py` is maintainer tooling: Python with no dependencies, run by path from the repository root, never through `python3`. It never ships in a plugin. It takes no arguments and exits 0 when it passes, 1 when a check fails and 2 when called with arguments.

| Run when | What it does | Fails when |
| :-- | :-- | :-- |
| After `npm run generate` and both generator `--check` runs, in every situation below | Reads `plugins/`, `marketplace.json`, `scripts/categories.json` and the root README's catalog block, and checks each plugin's `hooks/hooks.json` for those in `mods` | A plugin directory has no catalog row or two, a row names no plugin directory, a row sits under another category than the plugin's `marketplace.json` entry, an entry has no category, or a plugin in `mods` is not a mod |

`marketplace.mjs --check` compares `marketplace.json` with every `plugin.json`; this script compares the catalog with `marketplace.json`. Together they cover the chain from `metadata.category` to the README.

The checks after every situation, in order, stopping at the first failure to fix its cause:

1. `npm run generate`
2. `node scripts/generators/marketplace.mjs --check`
3. `node scripts/generators/catalog.mjs --check`
4. `.claude/skills/plugin-categories/scripts/check-catalog-categories.py`

## Situations

### A. A new plugin

Part of step 1 of `building-plugins`, before the scaffold runs.

1. Read the ids in `scripts/categories.json` and choose by rules 1 and 2.
2. When the request names no category, propose the one you chose and wait for Nery's answer. When it names one that breaks rule 1 or 2, say which rule and propose another. When none fits, rule 3.
3. Pass the id to the scaffold with `--category`; it refuses an id that `categories.json` lacks. `building-plugins` step 2 then runs `npm run generate`; run the checks above after it.

### B. Change a plugin's category

1. Set the new id in `metadata.category` of `plugins/<plugin>/.claude-plugin/plugin.json`. When the first `keywords` entry is the old id, replace it too.
2. When the plugin README has a Category badge, change its title to the new one, encoded as the badge already is: `%20` for a space, `%26` for `&`, `--` for `-`. A README built from the current `building-plugins` template has no badge until DEBT-011 closes; then there is nothing to change.
3. Run the checks above.
4. Who versions it:
   - A published plugin (`git cat-file -e origin/main:plugins/<plugin>/.claude-plugin/plugin.json` succeeds): a pull request and a version bump, through `release-and-versioning`.
   - A plugin never published: no bump; its `0.1.0` launch carries the category.
   - Part of a merge: `plugin-renames-and-removals` carries the bump and the changelog; do steps 1 to 3 only.

### C. A plugin gains or loses a mod

While `building-mods` adds or removes the hooks module, or a merge moves one:

- A plugin in `mods` that loses its hooks module follows B (rule 2).
- A plugin that gains one keeps its category unless the mod is now its purpose; then B.

### D. Change `scripts/categories.json`

On Nery's decision (rule 3). It is a maintainer change outside `plugins/`: commit `categories.json`, the regenerated `marketplace.json` and README together, signed, with no pull request. The plugin files it touches go through their own pull requests.

- **Add**: one object with a kebab-case `id`, an `emoji`, a `title` and a one-sentence `description`, at the place in the list Nery chooses. It shows in the catalog once a plugin uses it.
- **Reorder**: move the objects.
- **Reword** the `description`: it changes only the catalog. The `title` or the `emoji`: it also changes the catalog's links, so hand any link to them in the root README or `docs/` to `maintaining-user-docs`, and every plugin README whose Category badge shows the old title changes in a `README.md`-only pull request, with no bump.
- **Rename an id or remove a category**, in this order, because `marketplace.mjs` writes nothing while a plugin uses an id that `categories.json` lacks:
  1. Add the new category, unless the plugins move to an existing one, and commit it to `main`.
  2. Move every plugin that uses the old id, as B says, on branches started from that `main`. List them with `jq -r 'select(.metadata.category == "<old-id>") | .name' plugins/*/.claude-plugin/plugin.json`.
  3. Once those pull requests are merged and the list is empty, remove the old object.

Then run the checks above. A change users see in the catalog (add, rename, remove, reorder, reword) adds a line to the root `CHANGELOG.md`: `- summary.`, with no plugin name or version, under today's `## YYYY-MM-DD` and the matching change type.

## What to hand back

The category chosen or changed and the rule that decided it, the files changed, the raw output of each check, the plugin pull requests the change still needs, and any decision left to Nery.
