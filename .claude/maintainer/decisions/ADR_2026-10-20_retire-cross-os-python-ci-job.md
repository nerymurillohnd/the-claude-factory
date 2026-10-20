---
status: accepted
date: 2026-10-20
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# CI no longer runs the plugins' Python tests or by_path scripts on three operating systems

## Scope

The `python` job of `.github/workflows/validate.yml`, which ran every plugin's Python unit tests and every `.github/scripts/tests/*/by_path.sh` on ubuntu, macOS and Windows, and the `BASEDPYRIGHT_VERSION` pin only that job used.

Out of scope: the `python-lint` job (ruff and mypy), the `policy` job (Node tests, repository policy, catalog, version bumps), `claude-validate` and `lint`. They stay. The local gates, QUALITY_GATE steps 12 and 13, stay too.

## Context and problem statement

After the Python version floor was dropped (ADR_2026-10-20_no-python-version-floor), the `python` job still ran on three operating systems on every push, and the macOS leg took about 650 s against about 50 s on Ubuntu (run 39481039232, measured by a review agent). Nery called the wait absurd and asked why the tests run again in CI when they already pass locally.

Cause of the macOS time, measured locally on 2026-10-20 with the macOS `/bin/bash` 3.2.57: the long-command case of `block-no-verify`'s `by_path.sh` builds its string with `${long// /a}`, which grows with the square of the length (5000 characters: 5 s, 10000: 40 s, in a UTF-8 locale; 4 s at 10000 in the C locale). The handler itself reads 20000 characters in 0 s locally. That the runner's 536 s for 20 KB comes from the same line is an inference: the runner's locale and speed were not measured.

## Decision drivers

- Tests already run locally in the pre-push gates (QUALITY_GATE steps 12 and 13) before anything is pushed.
- The static checks (shellcheck, shfmt, ruff, mypy, basedpyright) already cover the code.
- Evals are what guarantees plugins execute; they exist for some plugins and not others, and Nery often tests locally, then retires the evals.
- Plugins use the interpreter the user has; CI does not choose it.
- Cost: about 11 minutes of wall-clock per push for checks that repeat the local run.
- Nery's wish to stop complicating the setup.

## Considered options

- **Remove the `python` job from CI**: chosen.
- **Keep three legs and fix the slow line in `block-no-verify`'s test**: rejected by Nery, who asked why test again what is tested locally. It would have kept macOS and Windows coverage at roughly one minute per leg (estimate, never measured).
- **Keep only the Ubuntu leg**: offered, not chosen.

## Decision outcome

Chosen option: **remove the `python` job**, because the local gates, the static checks and the evals are the guarantee, and repeating the same tests on three runners costs more than it adds.

### Consequences

- Good, because `Validate` no longer waits for the macOS leg; it ends with the Ubuntu jobs.
- Good, because one job, one env pin and one workflow section less to maintain.
- Bad, because nothing in CI now runs the plugins' Python tests (`python-lsp-intelligence`, `skill-diagnostics`) or the `by_path.sh` scripts on any system. A regression is found only when the maintainer runs steps 12 and 13 locally, and the macOS, Windows and CRLF-`jq` cases of the scripts are no longer exercised on those systems.
- Bad, because ADR_2026-10-20_no-python-version-floor says CI checks the plugins on three systems; that consequence no longer holds.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| A change breaks a hook on macOS or Windows and nothing flags it | A plugin is changed and steps 12 and 13 are skipped, or the bug only appears on another system | The hook fails on a user's machine | Run steps 12 and 13 before each push; use evals for plugins that need them | Nery Samuel Murillo |

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| The remaining jobs of `Validate` pass without the `python` job | `actionlint` on the workflow, then `Validate` on the branch and on `main` | `actionlint` passed locally on 2026-10-20; `Validate` pending | When the branch run ends |
| The slow macOS time came from the test's string building, not the handler | Run the long-command case on a macOS runner after replacing `${long// /a}` | Not run: the job was retired instead | If the `by_path.sh` scripts return to CI |

## More information

Nery gave the reasons on 2026-10-20 in the conversation. Applied in the commit that removes the job from `validate.yml` and updates the headers of the four `by_path.sh` files and `.claude/rules/QUALITY_GATE.md`.
