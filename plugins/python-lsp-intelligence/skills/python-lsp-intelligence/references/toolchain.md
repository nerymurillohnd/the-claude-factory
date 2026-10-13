# Python toolchain: ruff and basedpyright

## Contents

- Install
- Where configuration lives
- Defaults when the project has none
- Raise strictness
- Check one file or the whole project
- Environments and interpreters
- CI
- IDE

## Install

```bash
uv tool install ruff
uv tool install basedpyright
```

`pip install ruff basedpyright` works too. basedpyright ships its own Node runtime, so nothing else is needed. Both must be on the `PATH` of the shell that starts Claude Code; `which ruff basedpyright` confirms it.

## Where configuration lives

| Tool | Lookup order | How to see what applies |
| :-- | :-- | :-- |
| ruff | The closest `ruff.toml`, `.ruff.toml` or `pyproject.toml` with `[tool.ruff]` above the file; then the user-level `~/.config/ruff/ruff.toml` (or `pyproject.toml`); then ruff's defaults. The closest file wins outright, parents are not merged (`extend = "../ruff.toml"` inherits on purpose) | `ruff check --show-settings <file>` prints `Settings path:` with the file it resolved; no such line means defaults |
| basedpyright | `pyrightconfig.json`, else `pyproject.toml` with `[tool.basedpyright]` (or `[tool.pyright]`), **in the current working directory only**. It does not walk up from the file | `basedpyright --verbose <file>` prints `Loading pyproject.toml file at …` when it found one; run it from the project root or pass `-p <config file>` |

A `pyrightconfig.json` always wins over a `pyproject.toml` beside it.

## Defaults when the project has none

Without a configuration of its own, this plugin checks with its bundled profiles, `hooks/defaults/ruff.toml` and `hooks/defaults/pyrightconfig.json` in the plugin folder, passed by path (`--config` and `-p`). The basedpyright profile is bound to your project for the run: its root (the nearest `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt` or `.git` above the file) and `src/` become the import roots, and a `.venv` there is used when present, so first-party and installed imports resolve as they do natively. They are a strict baseline: ruff `select = ["ALL"]` with the formatter- and basedpyright-owned rules ignored, 100-column lines, google docstrings; basedpyright in `recommended` mode with `failOnWarnings`, strict inference and the `report*` rules that complement the ruff ignores, and no `pythonVersion`, so basedpyright assumes the interpreter it finds.

Any `ruff.toml`, `.ruff.toml`, `pyproject.toml` (`[tool.ruff]`, `[tool.basedpyright]`) or `pyrightconfig.json` you add, in the project or at user level, replaces them entirely. To keep the baseline and adjust it, copy the two files into the project and edit the copies.

## Raise strictness

- ruff: `select = ["ALL"]` under `[lint]`, then ignore rules that another tool owns, never a rule that found a defect. `ruff rule <CODE>` explains a code.
- basedpyright: `typeCheckingMode = "strict"` or `"all"`, `failOnWarnings = true`; name individual `report*` rules (`reportAny`, `reportUnusedCallResult`, `reportMissingParameterType`) as `"error"`.
- Set `pythonVersion` to the project's minimum version, so typing APIs that newer versions add are flagged (`typing.TypeGuard` needs 3.10).

## Check one file or the whole project

```bash
ruff check --fix path/to/file.py && ruff format path/to/file.py
basedpyright path/to/file.py              # from the project root
ruff check . && ruff format --check . && basedpyright
```

- ruff exits 0 when nothing remains after fixes, 1 with remaining violations, 2 when it could not run (a broken config counts).
- basedpyright exits 0 when clean, 1 with errors (or warnings under `failOnWarnings`), 2 or more when it could not run.
- `basedpyright --outputjson` gives one JSON document with `generalDiagnostics[]` (`file`, `range`, `severity`, `message`, `rule`).
- Notebooks: ruff lints and formats `.ipynb` by default; basedpyright does not check them.

## Environments and interpreters

- basedpyright resolves imports against the project's `.venv` when there is one, else the interpreter on `PATH`; `--pythonpath <interpreter>` overrides it.
- PEP 723 scripts (`# /// script` block) run in an environment uv creates on demand; point basedpyright at it with `--pythonpath "$(uv python find --script <file>)"`.
- `reportMissingImports` on a package that runs fine means the checker is looking at a different environment: fix the environment selection, not the import.

## CI

```bash
ruff check . && ruff format --check . && basedpyright
```

Pin the versions (`uv tool install ruff==0.17.0`, `basedpyright==1.40.2`) so a release of either tool does not change the result.

## IDE

VS Code: the **Ruff** and **BasedPyright** extensions read the same configuration files, so the editor and the command line agree once the project root is the workspace folder. A mismatch between them is almost always a different interpreter or working directory.
