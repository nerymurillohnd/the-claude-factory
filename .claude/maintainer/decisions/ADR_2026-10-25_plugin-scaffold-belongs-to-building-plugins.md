---
status: accepted
date: 2026-10-25
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Creating a plugin belongs to building-plugins; regenerating stays in the repository

## Scope

How a new plugin of this marketplace is created: the script that does it, the templates it uses, and the step that registers the plugin and updates the root README catalog.

## Context and problem statement

`scripts/new-plugin.mjs` did two jobs:
- it validated a new plugin's name and category and wrote `plugins/<name>/` from `.claude/templates/plugin/`;
- it rebuilt `.claude-plugin/marketplace.json` and the root README catalog through `scripts/generators/`.

No skill governed it. `building-plugins`, the skill that builds plugins, did not run it, and the script rendered the old README template instead of the skill's own. Where should creating a plugin live, and where should regenerating the derived files live?

## Decision drivers

- A skill owns and runs what its procedure creates or builds, with its own self-contained scripts.
- Regenerating files derived from the plugins is repository maintenance. It has one source, used by CI and every skill.
- New, validated work outranks existing files, which adapt to it.

## Considered options

- **Split the script.** Creating moves into `building-plugins` as `scripts/scaffold-plugin.py`, which writes from the skill's assets. Regenerating stays `npm run generate`, which the skill runs afterwards as a repository tool. Chosen.
- **Move `new-plugin.mjs` into the skill whole**: rejected, because it imports the generators, so the skill would depend on `scripts/` or carry a second copy of them.
- **Keep `new-plugin.mjs`**: rejected, because creation stays ungoverned and keeps rendering the old template.

## Decision outcome

Chosen option: **split the script**, because creation becomes the skill's own procedure and regeneration keeps a single source.

- `building-plugins/scripts/scaffold-plugin.py` checks the name and category and writes the plugin from `assets/` (commit 9b8f122). Step 3 of the skill runs the marketplace check, the scaffold, then `npm run generate`, and removes the folder if that fails.
- `scripts/new-plugin.mjs`, its tests and the `lib.mjs` exports only it used are gone (commit 38fd709). The tests' fixture is now built by writing the files and running the generators.
- At Nery's order, the original templates in `.claude/templates/` stay, frozen, until DEBT-011 closes (commit a8b0554). They are still read: `check-repo.mjs` enforces the old README shape, and the tests build their fixture from it.

### Consequences

- Good, because the skill that builds a plugin now governs how it is created, and the generators stay one source.
- Good, because the scaffold renders the template the skill sets.
- Bad, because until DEBT-011 closes a plugin the scaffold creates fails `check-repo.mjs`, and the templates exist twice: the skill's assets and the frozen originals.
- Bad, because the rollback that `new-plugin.mjs` did itself, removing the folder when registering failed, is now a step the skill tells you to do.

## More information

Decided by Nery on 2026-10-25, after reviewing the script's stages and the plan in this session ("No es lo mismo crear que regenerar… la regeneración sí compete al repositorio"). Revisit when DEBT-011 closes.
