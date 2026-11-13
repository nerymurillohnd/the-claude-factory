---
status: accepted
date: 2026-11-12
decision-makers:
  - "Nery (project owner)"
supersedes: none
superseded-by: none
---

# Type-check plugin Python at its 3.12 floor with a plain pythonVersion

## Scope

`pyrightconfig.json`: `pythonVersion`, `include` and `executionEnvironments`. Maintainer Python outside `plugins/` is out of scope and will get its own config.

## Context and problem statement

The restored config set `pythonVersion` 3.15 globally and gave `plugins/` 3.12 through `executionEnvironments`. A local test showed that this layout checks only syntax at 3.12: typeshed's version guards still resolve at the global version, so `from typing import TypeIs` (3.13+) gave 0 errors, while a plain `pythonVersion` 3.12 reported `"TypeIs" is unknown import symbol`. basedpyright also never analyzes dot folders such as `.claude/`, even when included, and the `include` named a `scripts` folder that does not exist.

## Decision drivers

- Plugin Python must be checked against the stdlib users have at the 3.12 floor.
- Config entries must match folders that exist.

## Considered options

- **`pythonVersion` 3.12 for the whole config, `include` only `plugins/`, and a separate config per maintainer folder later**: chosen.
- **Keep `executionEnvironments` with a 3.15 default**: rejected because of the stdlib-guard behavior above.

## Decision outcome

Chosen option: **a plain `pythonVersion` 3.12 config for `plugins/`**, because it checks the API plugin users really have.

### Consequences

- Good, because 3.13+ APIs in plugin code are now caught.
- Bad, because `npm run typecheck:python` now reports 96 errors in github-operations: `labels-diff.py` and `check-forms.py` import `TypeIs`, and `check-forms.py`'s PEP 723 dependencies are absent from the checking environment. The fix changes plugin components and needs its own pull request.
- Bad, because maintainer Python under `scripts/` or `.claude/` needs its own `pyrightconfig.json` with 3.15.

## More information

- Source: `DetachHead/basedpyright` at tag v1.40.2 (`docs/configuration/config-files.md`, `configOptions.ts` `findExecEnvironment`, default excludes in `pathConsts.ts`); local reproduction on 2026-11-12.
- Pending: whether to run plugin Python under a real 3.12 interpreter as well, not only check it statically.
- Commit: 7fc7def.
