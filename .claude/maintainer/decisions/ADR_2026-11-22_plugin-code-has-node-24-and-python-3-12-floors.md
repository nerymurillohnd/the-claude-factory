---
status: accepted
date: 2026-11-22
decision-makers:
  - "Nery Samuel Murillo (project owner)"
supersedes: none
superseded-by: none
---

# Plugin code has Node.js 24 and Python 3.12 floors, checked at those floors

## Scope

- Every plugin's code that runs on the user's `python3` or `node`: hook scripts, skill scripts, MCP servers and their tests in `plugins/*/`.
- The root `tsconfig.json` and `@types/node`, the root `pyproject.toml` (`[tool.ruff]`, `[tool.basedpyright]`), and Validate's `Floors` job in `.github/workflows/validate.yml`.
- Each plugin README's Prerequisites, and the versioning rule for a raised runtime minimum.
- Out of scope: maintainer tooling (`scripts/`, npm scripts, CI setup), which stays on Node 26 LTS (`.nvmrc`, `devEngines`) and Python 3.15 (`.python-version`); and mods, which run inside Claude Code, not on the user's Node.

## Context and problem statement

Plugins run on third-party users' machines with whatever Node.js and Python those users installed, while every check ran on the maintainer's Node 26.13.1 and Python 3.15.2, the top of the range. The READMEs stated different minimums (Node.js 14.17, 16.20.0, 18, 20, 22, 24; Python 3.12), and no check ran plugin code on a lower runtime, so code using a newer API could pass every check and fail for users. The root `tsconfig.json` type-checked plugin JavaScript against `@types/node` 26.6.6. What lowest Node.js and Python must plugin code support, and how is that floor checked, not only stated?

## Decision drivers

- Plugins must be self-contained and portable: no dependency on the maintainer's machine.
- A floor is real only when a check fails below it; a stated minimum alone fails silently.
- One configuration, not copies: `.claude/rules/code-quality/python.md` forbids `ruff.toml`, `.ruff.toml` and `pyrightconfig.json`, which take precedence over `pyproject.toml`.
- No change to the maintainer toolchain or its `devEngines`.

## Considered options

- **Floors Node.js 24 and Python 3.12 for plugin code, applied from the root configuration and checked in CI**: chosen.
- **A copy of the configuration in each plugin folder, git-ignored**: rejected: Ruff and basedpyright would read the copies over `pyproject.toml`, the rule above forbids them, and an ignored file is not on a fresh clone or in CI.
- **Configuration files at the root of `plugins/` that extend the root ones**: rejected for the same precedence and single-source reasons.
- **A separate plugins tsconfig with `@types/node` 24 under an npm alias**: rejected: the pre-commit gate groups files by their owning tsconfig and would need changes, and two `@types/node` copies drift; Node 24 types pass for the maintainer scripts too.
- **Floor tests only on the maintainer's machine**: rejected: it depends on a manual step; the local run stays as the way to reproduce a CI failure.

## Decision outcome

Chosen option: **Floors Node.js 24 and Python 3.12 for plugin code, applied from the root configuration and checked in CI**, because it checks the floor on every pull request from one configuration and leaves the maintainer toolchain as it is.

- Python: Ruff's `per-file-target-version` sets `plugins/**/*.py` to `py312`; basedpyright's top-level `pythonVersion = "3.12"` holds the lowest floor, since it reads stdlib stubs from the top level only (DetachHead/basedpyright#416).
- Node.js: the root `@types/node` is pinned to the floor's major, 24.19.2, so `tsc -p tsconfig.json` rejects an API newer than Node 24 in maintainer and plugin JavaScript; Dependabot holds its majors back.
- Runtime: Validate's `Floors` job sets up the toolchain, puts Python 3.12 and Node.js 24 first on `PATH`, checks both versions and runs `bash scripts/checks/plugins.sh tests`; `release` needs it. It runs the loop with bash, not npm, because the root `devEngines` rejects Node 24 and its npm.
- READMEs: each runtime minimum is the higher of the floor and the tool's own; raising it is breaking (Minor in `0.x`).

### Consequences

- Good, because a newer API or syntax fails a check instead of a user's session.
- Good, because the floors live once in `.claude/CLAUDE.md` Platforms and are applied from the existing root configuration.
- Bad, because maintainer JavaScript can't use an API newer than Node 24 either while it shares the root `tsconfig.json`.
- Bad, because Validate gains a job of about the Checks job's setup time.
- Bad, because plugins that stated Node.js 16 to 22 drop users below 24 and take a Minor bump.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Plugin tests pass on the floors | `bash scripts/checks/plugins.sh tests` with Python 3.12.16 and Node 24.22.3 first on `PATH`, on macOS | 333 Python tests (4 skipped) and 34 Node tests passed, identical to Python 3.15.2 and Node 26.13.1 (2026-11-22) | Each pull request, in `Floors` |
| `tsc` rejects an API newer than Node 24 | A probe calling `process.permission.drop` (Node 26.3) under the root `tsconfig.json` | TS2339 with `@types/node` 24.19.2; `tsc -p tsconfig.json` otherwise clean (2026-11-22) | After each `@types/node` update |
| basedpyright still needs the top-level floor | `gh issue view 416 -R DetachHead/basedpyright` | Open on basedpyright 1.40.2 (2026-11-22) | After each basedpyright upgrade |
| The `Floors` job passes in CI | Validate on the pull request that adds it | pending | That pull request |

## More information

- The owner set the floors in this session on 2026-11-22: maintainer tooling keeps Node 26 LTS and Python 3.15; plugins need Node.js 24 and Python 3.12 at least.
- Related: ADR_2026-11-22_maintainer-scripts-keep-python-and-node.
- The tailwind-development MCP server answered `initialize`, `tools/list` and real `sort_classes` and `class_css` calls identically on Node 24.22.3 and 26.13.1 (2026-11-22).
