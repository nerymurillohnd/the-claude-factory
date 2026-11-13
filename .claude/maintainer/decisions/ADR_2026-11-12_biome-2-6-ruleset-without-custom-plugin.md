---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Run Biome 2.6.6 with the recommended nursery rules and no custom GritQL plugin

## Scope

The linter, `plugins` and `overrides` sections of `biome.jsonc`. The Markdown includes are covered by ADR_2026-11-12_biome-formats-only-human-markdown.

## Context and problem statement

The `biome.jsonc` restored from `main` named the GritQL plugin `scripts/biome-plugins/main-module.grit`, which the reset removed. A missing plugin file aborts every Biome run: "Biome couldn't find the plugin file", exit 1, no file processed. Its nursery list matched Biome 2.6.3 and lacked 24 recommended nursery rules added in 2.6.4 to 2.6.6. The test domain was on for the whole repository, so its globals (`describe`, `it`, `expect`) counted as declared in every file.

## Decision drivers

- Biome must run.
- Use every rule Biome 2.6.6 recommends.
- Keep test globals out of non-test files.

## Considered options

- **Drop the plugin entry, add the 24 recommended nursery rules, scope the test domain to the tests override**: chosen.
- **Restore the `.grit` file from `main`**: rejected because it depends on `scripts/lib.mjs`, which does not exist yet. A custom plugin comes back only with that file and a fixture that proves it fires.

## Decision outcome

Chosen option: **drop the plugin entry, add the recommended nursery rules and scope the test domain**, because Biome then runs and applies its current recommendations.

### Consequences

- Good, because `biome migrate` reports "no migration needed" and every key is valid on 2.6.6.
- Bad, because the new nursery rules report 9 findings in plugin code (file-tree-pane, model-trace, project-maintainer, tailwind-development: noArrayForEach, noNegatedArrayPredicate, noUselessLengthCheck). Fixing them changes plugin components, so it needs its own pull request; until then `npm run lint:js` fails.
- Bad, because nursery rules sit outside semver, so each Biome upgrade rechecks the list.

## More information

- Sources: `biome explain` on 2.6.6 for every rule; `biomejs/biome` CHANGELOG at tag `@biomejs/biome@2.6.6`.
- Commit: b5dc1a9.
