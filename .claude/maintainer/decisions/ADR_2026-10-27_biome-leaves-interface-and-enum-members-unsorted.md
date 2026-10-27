---
status: accepted
date: 2026-10-27
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Biome leaves interface and enum members in their written order

## Scope

- The assist actions in `biome.jsonc`: `useSortedInterfaceMembers` and `useSortedEnumMembers`.
- Every TypeScript interface and enum Biome checks, maintainer and plugin files alike.
- Out of scope: the assist actions that are on (`organizeImports`, `useSortedPackageJson`, `noDuplicateClasses`).

## Context and problem statement

Biome 2.6.3 has 13 assist actions. `biome ci` enforces every enabled one, so an action that is on fails the gates until its change is applied. Two of them sort members alphabetically: `useSortedInterfaceMembers` (since 2.4.0) and `useSortedEnumMembers` (since 2.5.0). Measured one at a time in a scratch copy on 2026-10-26, neither reports anything in the repository today. Should they be on, so that every future interface and enum is sorted?

## Decision drivers

- Members are often grouped by meaning, for example a mod's types that follow the order of the engine's payload. Alphabetical order would scatter them.
- An enabled action is a gate, not a suggestion: once on, it decides the order of every new interface and enum.
- Neither action catches a defect today.

## Considered options

- **Leave both actions off**: chosen.
- **Turn both on**: rejected, because it would force alphabetical order where the written order carries meaning, and it fixes no current finding.

## Decision outcome

Chosen option: **leave both actions off**. `biome.jsonc` does not list them, and `.vscode/settings.json` does not run them on save.

### Consequences

- Good, because an interface or enum keeps the order its author chose, such as the order of a payload it mirrors.
- Bad, because nothing enforces a consistent member order; a reviewer has to notice one.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Neither action is enabled | `biome.jsonc`'s `assist.actions.source` lists only `useSortedPackageJson` and `noDuplicateClasses` | Neither is listed | Each change to `assist` |

## More information

- Decided by Nery on 2026-10-27, as D5 (off) of `.claude/specs/2026-10-26-biome-config-corrections-and-strictness-design.md`, section 7.
- The same step turned on items 16, 17 and 24 of that spec, in commit `003a20e`.
