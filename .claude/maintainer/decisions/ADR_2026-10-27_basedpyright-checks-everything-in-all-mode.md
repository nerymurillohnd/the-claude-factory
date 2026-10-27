---
status: superseded
date: 2026-10-27
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-10-24_basedpyright-is-the-only-python-type-checker
superseded-by: ADR_2026-10-27_python-version-is-set-per-scope
---

# Basedpyright is the only Python type checker, in `all` mode everywhere

## Scope

- In scope: the type checking of maintainer Python and plugin Python. That covers the root `pyrightconfig.json`, which the `basedpyright-maintainer-other` and `basedpyright-plugins` gates and the editor read, `scripts/pyrightconfig.maintainer.json`, and the Plugin Tooling rule in `.claude/CLAUDE.md`.
- Out of scope: Ruff, which stays the linter and formatter; JavaScript and TypeScript, which `tsc` checks; the profiles a plugin ships for its users' projects, such as `python-lsp-intelligence`'s `hooks/defaults/pyrightconfig.json`.

## Context and problem statement

ADR_2026-10-24_basedpyright-is-the-only-python-type-checker chose Basedpyright alone, with `all` mode for maintainer code and the default `recommended` mode for plugin code. The root `pyrightconfig.json` set no mode, so the plugin gate and VS Code ran `recommended`, and the editor showed less than the maintainer gate. `deprecateTypingAliases` was off everywhere, although `ruff.toml` turns off UP006, UP007, UP035 and UP045 on the grounds that Basedpyright owns them. Should plugin code meet the same bar as maintainer code?

## Decision drivers

- Plugins run on other people's machines; their code deserves at least the maintainers' rigor.
- One mode across the repository, so the editor and every gate agree.
- No rule Ruff hands over to Basedpyright may go unchecked.

## Considered options

- **`all` mode for the whole repository, set in the root `pyrightconfig.json`**: chosen.
- **`all` for maintainer code, `recommended` for plugin code**: rejected; it was the previous state, and it left the editor and the plugin gate below the maintainer gate.

## Decision outcome

Chosen option: **`all` everywhere**. Basedpyright remains the only Python type checker, for the reasons and measurements in ADR_2026-10-24_basedpyright-is-the-only-python-type-checker, which this record carries forward. The root `pyrightconfig.json` sets:

- `typeCheckingMode: "all"`, where every rule is an error;
- `pythonVersion: "3.15"`, the Python on PATH today, now fixed instead of taken from whatever interpreter a run finds;
- `pythonPlatform: "All"`, since plugins run on Linux, macOS and Windows through Git Bash;
- `deprecateTypingAliases: true`, which checks the typing aliases Ruff leaves to Basedpyright;
- `enableExperimentalFeatures: true`.

The rest of the earlier decision holds: a second checker needs an ADR that classifies each diagnostic it adds and justifies it only by documented defects.

### Consequences

- Good, because the plugins already pass `all` with 0 findings, and every new plugin file now meets the maintainer bar.
- Good, because VS Code reports what the gates report.
- Bad, because `pythonVersion: "3.15"` lets plugin code use APIs newer than the `python3` a user may have, without a diagnostic; the plugins' tests and READMEs remain the guard for that.
- Bad, because a placeholder `...` body in a private function still passes Basedpyright, as the earlier record measured.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Every basedpyright gate passes under `all` | `node scripts/gates.mjs --only basedpyright-` | 2026-10-27: all four pass; `basedpyright --warnings plugins`: 0 errors, 0 warnings | Each change to `pyrightconfig.json` |
| `deprecateTypingAliases` catches a typing alias | A planted `from typing import List` in a plugin file | 2026-10-27: 2 errors, `reportDeprecated` | After a Basedpyright upgrade |

## More information

- Decided by Nery on 2026-10-27, from the configuration he proposed. Keys of that proposal left out, each measured or checked against the basedpyright 1.40.2 schema: `enableBasedFeatures` (not a setting), `defineConstant` for an unused `DEBUG`, `reportUnusedCallResult: "none"` and `reportMissingTypeStubs: false` (both loosen `all` with no finding to justify it), the 17 per-rule `"error"` entries and `reportMissingImports` (already errors under `all`), and `stubPath`, `enableTypeIgnoreComments` and `failOnWarnings` (their defaults).
