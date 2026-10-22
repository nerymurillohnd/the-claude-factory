---
status: accepted
date: 2026-10-22
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The TypeScript post-edit hook applies its strictest policy as defaults, and the user's config wins

## Scope

- In scope: how `hooks/tsc-check.sh` and `skills/ts-lifecycle/scripts/run-fixtures.sh` of `typescript6-lsp-intelligence` and `typescript7-lsp-intelligence` pass the strict options, and what blocks an edit.
- Out of scope: which options the policy holds (`STRICT_POLICY`), the compiler search, and the hook events and matchers.

## Context and problem statement

The hook passed every strict option on the `tsc` command line, which beats the `-p` config and its whole `extends` chain, so a project's explicit `"strict": false` or `"noUnusedLocals": false` was overridden. Nery wants the plugin's strict options to be the defaults, with any option the user's config sets, at any value, winning. Research on TypeScript 6.0.3 (the compiler bundle `_tsc.js` and read-only experiments, notes under `~/Claude/projects/the-claude-factory-research/research_notes/Auditoría del hook TypeScript/`) settled how to do that without touching the user's files or environment.

## Decision drivers

- The user's explicit choice, `false` included, wins; the plugin fills only what the config leaves unset.
- The check must keep the user's program intact: files, include, references, `${configDir}`, rootDir and typeRoots.
- `noEmit true` and `noCheck false` always apply, so the check never writes and never switches off.
- A config with options deprecated in TypeScript 6 blocks the edit, since the user may not know the config stops working in TypeScript 7 (Nery, 2026-10-22).

## Considered options

- **Read the config chain with `tsc --showConfig -p <config>` and pass only the unset options**: chosen.
- **A temporary config with `extends: [pluginBase, userConfig]`**: rejected; measured on 6.0.3, it drops `references`, rebinds `${configDir}` and the default `include` to the temporary folder, and breaks the 6.0 default `rootDir` (TS6059) and default `typeRoots`.
- **Keep forcing every option on the command line**: rejected by Nery.

## Decision outcome

Chosen option: **`--showConfig` per config**. For each compiler and config, the hook reads the option keys `--showConfig` prints under `compilerOptions`, which include those inherited through `extends`, and passes on the command line only the known policy options that are missing. When the chain sets `strict`, at any value, no option of the strict family is passed, because a set family option beats `strict` in `getStrictOptionValue`. An option that 6.0.3's `verifyCompilerOptions` rejects next to the user's value stays out: `strictPropertyInitialization` and `exactOptionalPropertyTypes` with `strictNullChecks` off, `checkJs` with `allowJs` off, and `checkJs` and `allowJs` with `isolatedDeclarations`. A config `--showConfig` cannot read gets the guards only, and the check run reports its error. Deprecation errors (TS5101 and the like) are reported as such and block; an `ignoreDeprecations` the user set is respected, since `--ignoreDeprecations` cannot be unset from the command line. `run-fixtures.sh` applies the same rules, so the fixtures prove what the hook really checks.

### Consequences

- Good, because a project's deliberate choices are kept, and the policy still raises every project that leaves an option unset.
- Good, because it works on any `tsc` from TypeScript 3.2, with no array `extends`.
- Bad, because a project with `"strict": false` now gets no strict-family check from the hook; a lax project is checked as lax.
- Bad, because each config costs one more `tsc --showConfig` run per hook call.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| An explicit value wins, an unset one gets the policy, `extends` counts, `strict` keeps the family | `scripts/tests/typescript6-lsp-intelligence/tsc-check.test.mjs` ("explicitly wins", "leaves unset is applied", "extends counts", "strict false keeps it") | 58 of 58 passed on 2026-10-22 with tsc 6.0.3; with the own-option check removed on purpose, "explicitly wins" failed | Each change to the hook |
| No policy option turns into a config error next to the user's value | Same file, "needs one the project turned off" (three configs) | Passed; with one conflict row removed on purpose, it failed | Each TypeScript minor |
| A deprecated option blocks | Same file, "deprecated option ... blocks" (`baseUrl`, TS5101) | Passed | Each TypeScript minor |
| Claude fixes the errors before moving on | A live session with `claude --plugin-dir` | Pending | Before release |

## More information

Nery set the precedence on 2026-10-22 ("Gana el del usuario") and the deprecation rule the same day. This changes the 0.3.0 and 0.4.0 releases before they ship, marked **Breaking:** in both changelogs.
