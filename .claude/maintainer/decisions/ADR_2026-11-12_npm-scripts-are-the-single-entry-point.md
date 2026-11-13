---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Run every maintainer command through npm scripts, with no Makefile

## Scope

The `scripts` block of the root `package.json`. Maintainer scope.

## Context and problem statement

The reset removed every maintainer script, so each tool ran by hand. The owner wants every command run from `package.json` and asked whether to add a Makefile.

## Decision drivers

- One entry point, discoverable with `npm run`.
- Portable script bodies on macOS and Linux.
- Behavior that does not change under `npm ci --ignore-scripts`.

## Considered options

- **npm scripts, chained with `&&`, with no pre/post hooks and no task-runner dependency**: chosen.
- **A Makefile**: rejected because it adds a second entry point and a second shell dialect; `npm run` with no arguments already lists every script.
- **npm-run-all2**: rejected because `&&` is portable in `/bin/sh` and stops at the first failure without a dependency.
- **pre/post scripts**: rejected because npm skips them, without a warning, under `--ignore-scripts`.

## Decision outcome

Chosen option: **npm scripts chained with `&&`**: `lint` (`lint:js`, `lint:python`, `lint:shell`, `lint:workflows`), `typecheck` (`typecheck:ts`, `typecheck:python`), `validate`, `check`, `format`, `fix` and `prepare`. Python tools run with `uv run --locked`.

### Consequences

- Good, because `lint:python`, `lint:shell`, `lint:workflows`, `typecheck:ts` and `validate` pass.
- Bad, because `lint:js` and `typecheck:python` fail until the plugin fixes in ADR_2026-11-12_biome-2-6-ruleset-without-custom-plugin and ADR_2026-11-12_basedpyright-checks-plugins-at-python-3-12 land.
- Bad, because npm runs scripts with `/bin/sh` on POSIX and `cmd.exe` on Windows, so bodies stay POSIX `sh`; the maintainer scope targets macOS and Linux only.

## More information

- Sources: npm CLI docs v12, `npm-run`, `scripts` and `config` (`ignore-scripts`, `script-shell`); npm/cli source at v12.2.1.
- Commit: 894b878.
