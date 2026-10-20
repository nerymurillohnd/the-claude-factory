---
status: accepted
date: 2026-10-20
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# Plugin Python has no version floor

## Scope

The Python in this repository's plugins and in the checks that cover them: the `python` job of `.github/workflows/validate.yml`, the mypy commands in `.claude/rules/QUALITY_GATE.md`, the former `pyrightconfig.json`, and the "Python floor" line in `.claude/CLAUDE.md`.

Out of scope: the plugin files themselves. Their READMEs and docstrings still say "Python 3.9 or later", and changing them needs a pull request, a version bump and a changelog entry.

## Context and problem statement

`.claude/CLAUDE.md` kept a Python floor of 3.9, enforced in three places: a CI matrix on Python 3.9 and 3.13 that asserted the interpreter version, `mypy --python-version 3.9`, and `pyrightconfig.json` with `pythonVersion` 3.9.

Nery stated on 2026-10-20 that the project had already agreed not to use a floor: the scripts inside plugins must be portable and run on the `python3` that each user has on `PATH`. The maintainers' job is to protect that with their own tools while keeping the code POSIX-style. The rule and the checks contradicted that agreement.

## Decision drivers

- Plugins run on machines the maintainers do not control; the user's `PATH` decides the interpreter.
- A pinned floor tests a promise the plugins do not make to their users.
- Portability is checked on every OS the plugins support.
- Fewer version-specific jobs and assertions to maintain.

## Considered options

- **No floor; one CI leg per OS on the newest stable Python; tools run on the maintainer's Python**: chosen.
- **Keep the 3.9 floor, its CI matrix, `--python-version 3.9` and `pyrightconfig.json`**: rejected because it enforces a version the plugins are not meant to require.

## Decision outcome

Chosen option: **no floor**, because plugins must run on whatever `python3` the user has and the repository should verify portability with its own tools instead of a pinned version.

### Consequences

- Good, because CI checks the plugins on ubuntu, macOS and Windows with the current Python and no version assertion to keep in step.
- Good, because the gates read the same on every machine: mypy and basedpyright use the interpreter they run on.
- Bad, because mypy and basedpyright no longer reject syntax or standard-library APIs newer than 3.9. A script can pass every gate and still fail on an older user Python; the care moves to writing portable, POSIX-style code.
- Bad, because the plugin READMEs and docstrings keep claiming "Python 3.9 or later" while nothing now verifies that claim.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| A plugin script uses a feature newer than the Python a user has | A contributor writes modern syntax and the gates stay green | The hook fails on that user's machine | Write portable code; decide whether the plugin READMEs keep naming a minimum | Nery Samuel Murillo |

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| mypy, basedpyright, ruff and the plugin Python tests pass without the floor | The pre-push gates run on Python 3.15 | Passed locally on 2026-10-20: mypy, basedpyright, ruff and 13 skill-diagnostics tests | At each Python release the maintainers adopt |
| The `python` job passes on ubuntu, macOS and Windows on the newest Python | `Validate` dispatched on branch `ci/drop-python-version-tests` (run 39491973331) | Pending | When the run ends |

## More information

Nery said the decision was made earlier ("habíamos quedado que no íbamos a usar piso"); this record was written on 2026-10-20 together with the change that applies it (commit 56d0115 on `ci/drop-python-version-tests`). `.claude/CLAUDE.md` now says there is no floor.
