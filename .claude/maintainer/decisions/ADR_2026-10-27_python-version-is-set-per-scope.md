---
status: accepted
date: 2026-10-27
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-27_basedpyright-checks-everything-in-all-mode
superseded-by: none
---

# Each scope checks its Python against its own version, with a 3.12 floor for plugins

## Scope

- In scope: the Python version Ruff and Basedpyright assume for each part of the repository: `target-version` and `per-file-target-version` in `ruff.toml`; `pythonVersion` and `executionEnvironments` in the root `pyrightconfig.json`; `.claude/skills/pyrightconfig.json`; the Plugin Tooling rule in `.claude/CLAUDE.md` and the Python lines of `.claude/rules/hooks-and-scripts.md`. It carries forward Basedpyright as the only type checker, in `all` mode everywhere, and also replaces ADR_2026-10-20_no-python-version-floor.
- Out of scope: `scripts/pyrightconfig.maintainer.json` and the PEP 723 scripts, which keep `requires-python = "==3.15.*"`; the plugin files themselves, whose README changes go through plugin pull requests.

## Context and problem statement

ADR_2026-10-27_basedpyright-checks-everything-in-all-mode set `pythonVersion: "3.15"` in the root `pyrightconfig.json`, which also covers `plugins/`, and Nery set `target-version = "py315"` in `ruff.toml` for the whole repository. Plugin Python runs on the user's `python3`, and the project skills' scripts run on the `python3` of CI's ubuntu-24.04 runner (3.12.3, per the runner image) in the `policy` job and in `release.yml`. Measured with py315 everywhere: `ruff check` proposed 18 TC003 lazy imports (Python 3.15 syntax) in `.claude/skills/*/scripts/`, and `ruff format` would have rewritten `except (A, B):` to `except A, B:` (Python 3.14 syntax) in two plugin hooks and in skill scripts. Either change would break those files on the Python that runs them. ADR_2026-10-20_no-python-version-floor had left plugins with no floor and no version check. Which Python must each scope be checked against?

## Decision drivers

- A checker must flag syntax and APIs the target interpreter lacks; a version above that interpreter hides the failure.
- The maintainer and plugin scopes never share a rule (`.claude/CLAUDE.md`).
- One setting per tool, so the editor and every gate agree.

## Considered options

- **Python 3.15 for maintainer code; 3.12 for plugins and for the skills' scripts**: chosen.
- **Python 3.15 for the whole repository**: rejected because the formatter and the linter would turn plugin and skill code into syntax the runtime rejects.
- **A plugin floor of 3.9, which the stock `python3` of macOS (3.9.6 on macOS 27) and the two plugin READMEs match**: rejected by Nery, who set the plugin floor at 3.12.
- **No floor (ADR_2026-10-20_no-python-version-floor)**: rejected because nothing checked plugin code against any older interpreter.

## Decision outcome

Chosen option: **a version per scope**, because each tool then checks code against the interpreter that runs it.

- `ruff.toml`: `target-version = "py315"`, with `per-file-target-version` set to `py312` for `plugins/**/*.py` and `.claude/skills/**/*.py`.
- Root `pyrightconfig.json`: `pythonVersion: "3.15"`, with an execution environment rooted at `plugins` on `pythonVersion: "3.12"`. `typeCheckingMode: "all"`, `pythonPlatform: "All"`, `deprecateTypingAliases` and `enableExperimentalFeatures` stay as ADR_2026-10-27_basedpyright-checks-everything-in-all-mode set them.
- `.claude/skills/pyrightconfig.json`: `pythonVersion: "3.12"`.
- Plugin Python is written for `python3` 3.12 or later, and every plugin that runs Python states that minimum in its README.

### Consequences

- Good, because a 3.13+ construct in a plugin or skill script now fails the gates: the 3.12 check found `typing.TypeIs` (3.13) in `check-catalog-categories.py`, fixed with `TypeGuard`.
- Good, because `ruff format` no longer rewrites plugin or skill code into newer syntax.
- Bad, because the stock `python3` of macOS is 3.9.6: a plugin hook may use 3.10–3.12 features that fail there, and users on stock macOS need a newer Python.
- Bad, because `python-lsp-intelligence` and `skill-diagnostics` still declare "3.9 or later" in their READMEs until their pull requests change it.

### Risks and mitigations

| Risk | Likelihood or condition | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| A user runs a plugin hook on a `python3` older than 3.12 | Stock macOS, or an older Linux distribution | The hook fails on start | The README states the 3.12 minimum and how to get it | Nery Samuel Murillo |
| CI's runner image changes its `python3` | A new ubuntu image or runner label | The skills' floor no longer matches CI | Re-check the runner image's Python when `runs-on` changes | Nery Samuel Murillo |

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Plugins and skill scripts reject syntax newer than 3.12, and maintainer code accepts it | A planted `except OSError, ValueError:` and `type Alias = int` in `plugins/`, `.claude/skills/` and `scripts/`, under `ruff check` and `basedpyright` | 2026-10-27: plugins and skills fail on the `except` line with both tools and accept the `type` alias; `scripts/` passes | After a Ruff or Basedpyright upgrade |
| Every Python gate passes | `node scripts/gates.mjs --only ruff-,basedpyright-,validator:` | 2026-10-27: all pass | Each change to these configs |
| The two plugin READMEs state 3.12 or later | Their pull requests | pending | When each plugin's next pull request merges |

## More information

- Decided by Nery on 2026-10-27, who confirmed the 3.12 floor after being told that stock macOS ships 3.9.6.
- The `"**/*.py"` entry Nery added to `include` in `pyrightconfig.json` adds nothing, since `"."` already covers it.
