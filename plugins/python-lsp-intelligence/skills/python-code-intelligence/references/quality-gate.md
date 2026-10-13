# Python quality gate: ruff + basedpyright

The gate's hooks ship in the `basedpyright-lsp` plugin, next to the language server. This file is the
only guidance for them: read it when writing Python code or when the gate reports findings or blocks a stop.

Every Python file or notebook Claude changes goes through one chain, run by the `basedpyright-lsp` plugin's hooks after each edit and again before Claude stops:

```bash
ruff check --fix <file>; ruff format <file>; basedpyright --warnings <file>
```

- The tools run where the gate is invoked, with no `cd`, exactly as typed in the session: ruff finds the nearest config above each file, then the user's global one, then its defaults; basedpyright finds its config from the working directory up and uses the project's `.venv`.
- `ruff` fixes what it safely can and reformats the file in place. After it rewrites the file, **re-read the file before the next Edit**.
- `basedpyright --warnings` fails on warnings as well as errors.
- Imports resolve against the right interpreter. A PEP 723 script (`# /// script` block) uses its uv-managed env, and a project file uses the project's `.venv`.
- A file is Python when it ends in `.py`, `.pyi`, `.pyw` or `.ipynb`, or its shebang runs `python` or `uv run`.

## When the hook reports findings

1. Fix the root cause of each finding by its rule. `ruff rule <CODE>` explains a ruff code; basedpyright names its rule in parentheses, e.g. `(reportReturnType)`.
2. Save with Edit. The hook re-runs the chain on the edit and reports again until the file is clean.
3. A stop blocked by the hook lists every changed Python file that still fails. Fix them all, then stop again.

Never make the gate pass by weakening it: no `# noqa`, `# type: ignore` or `# pyright: ignore`, no `Any` or `cast()` just to silence a type error, and no loosening of the project's ruff or basedpyright config. A suppression or loosened config hides the defect from every later check and from the user, so the gate would report green on broken code.
The one exception is a finding you verified is a false positive. Put the narrowest suppression on that line (`# noqa: CODE`, `# pyright: ignore[rule]`) with a comment saying why, and tell the user.

## Frequent findings

| Finding | Usual cause | Fix |
|---|---|---|
| `reportMissingImports` / `reportMissingModuleSource` | The dependency is not in the env the file runs in | PEP 723 script: add it to the `dependencies` list in the `# /// script` block. Project: `uv add <pkg>` |
| `reportUnknown*` / `reportAny` | A value whose type basedpyright cannot infer | Annotate the value or the function returning it; for an untyped library, add a typed wrapper or stubs |
| `reportReturnType` / `reportAssignmentType` / `reportArgumentType` | The annotation and the value disagree | Decide which one is wrong and fix that one; never widen to `Any` |
| `reportUnusedCallResult` | A call's result is silently discarded | Use it, or assign to `_` when discarding is intended |
| `reportOptionalMemberAccess` | Using a value that may be `None` | Narrow first (`if x is None: ...`) |

## Checking files on demand

```bash
python-gate <file>...
```

`python-gate` comes from `basedpyright-lsp`'s `bin/`, on the Bash tool's `PATH` while the plugin is enabled. Exit 0 means clean. Exit 2 prints the findings for each file.
