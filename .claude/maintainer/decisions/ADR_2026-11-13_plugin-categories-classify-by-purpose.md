---
status: accepted
date: 2026-11-13
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Plugin categories classify by purpose: drop `mods`, add `monitoring`

## Scope

The category of every plugin in this marketplace: `metadata.category` in each `plugins/<plugin>/.claude-plugin/plugin.json`, the `category` of its entry in `.claude-plugin/marketplace.json`, the Category badge of its README and its row in the root `README.md` catalog; and the category list in `.claude/rules/plugins/categories.md`. Out of scope: tags, and plugins whose category already names their purpose.

## Context and problem statement

The catalog had 13 categories, and 12 of them name a purpose. `mods` named a component type instead, so mods were classified inconsistently: `model-trace`, `tool-ledger` and `turn-meter` sat in `mods`, while `file-tree-pane` (a mod "for productivity") sat in `productivity` and `macos-grep-guard` (a mod) in `development`. On 2026-11-13 a session moved `file-tree-pane` to `mods` (commit `cf33086`, not pushed), which the owner rejected as not the professional classification.

Evidence read on 2026-11-13:

- The marketplace reference defines two separate fields: `category`, "Free-form category for organizing the catalog", and `tags`, "Free-form tags for search" ([marketplace-reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md)).
- Anthropic's official marketplace (`anthropics/claude-plugins-official`, `.claude-plugin/marketplace.json` on `main`) lists 316 plugins in 13 categories, all purposes or domains (development, productivity, database, monitoring, security, deployment, design, automation, learning, location, testing, math, migration), none a component type. Its observability plugins, including `langfuse-observability`, are in `monitoring`.

Which axis should a category use, and where do the three observability mods go?

## Decision drivers

- A category answers what a user installs the plugin for.
- One classification axis, so every plugin has exactly one defensible category.
- Alignment with the official marketplace users already browse.
- The component type stays visible without being a category: the catalog's Includes column already shows it.

## Considered options

- **Classify by purpose only: remove `mods`, add `monitoring`, move `model-trace`, `tool-ledger` and `turn-meter` to `monitoring`, keep `file-tree-pane` in `productivity`**: chosen.
- **Keep `mods` and move every mod into it, `file-tree-pane` included**: rejected because it classifies by implementation, not by what users need, and leaves two axes in one list.
- **Remove `mods` and put the observability mods in `devops`**: rejected because `devops` covers CI/CD, infrastructure and releases; placing session observability there stretches an existing category, which the category rules forbid.

## Decision outcome

Chosen option: **classify by purpose only, with a new `monitoring` category**, because it gives every plugin one category on one axis, matches the official marketplace's taxonomy, and keeps the component type visible in the Includes column.

### Consequences

- Good, because `model-trace`, `tool-ledger` and `turn-meter` are found where users look for observability tools.
- Good, because a future mod gets its category from its purpose, with no special case.
- Bad, because `model-trace`, `tool-ledger` and `turn-meter` change `plugin.json`, so each needs a Patch version and a pull request.
- Neutral, because `file-tree-pane`, `macos-grep-guard` and `mods-engineering` keep their categories; reverting `cf33086` leaves `file-tree-pane` unchanged at 0.1.6.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| No plugin uses `mods`, and each category in `plugin.json`, `marketplace.json`, README badge and catalog row agrees | `jq` over every `plugin.json` and `marketplace.json`; `npm run check:consistency` | pending | After the reclassification commits |
| The three plugins install and load at their new versions | `npm run check:install -- --from local model-trace tool-ledger turn-meter` | pending | Before the pull request |

## More information

- Decided by the owner in this session on 2026-11-13 ("Apruebo, quitar mods, crear monitoring y reclasificar").
- The 13-category list and its rules were last defined in `scripts/categories.json` and the `plugin-categories` project skill, both deleted in commit `ced195b`; ADR_2026-10-26_category-rules-live-in-plugin-categories-skill was deleted in the same commit. The list now lives in `.claude/rules/plugins/categories.md`.
- The new category's emoji, title and scope line are set in `.claude/rules/plugins/categories.md`.
