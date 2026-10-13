# Control tests

Run the control tests only when the user asks to test tool coverage, or when a check passes code it should flag. They test tool behavior on known controls under a known profile; they do not establish that a user's project, every rule, or runtime behavior is correct. The `.fixture` suffix keeps the control files out of normal extension-based discovery, but explicitly passed files or shebang detection can still identify code.

`references/fixtures.json` defines the conditions and expected diagnostics. The runner `scripts/verify-fixtures.sh` copies only these controls and their explicit profiles into fresh temporary directories, runs checks without executing the controls, preserves process statuses, and prints a JSON report. It never places negative controls inside a user's project. Run it with the command in SKILL.md, which carries its absolute path; SKILL.md also explains its exit codes.

Tools must already be available. A missing executable, malformed diagnostic report, or unsuccessful tool setup is incomplete verification, not a passing control. The runner installs no tools or packages.

| Control | Expected under the supplied profile |
|---|---|
| `clean_control` | No Ruff or basedpyright findings |
| `undefined_name` | F821 and reportUndefinedVariable |
| `return_type` | reportReturnType |
| `missing_import` | reportMissingImports; the import is used |
| `warning_only` | reportAny; `--warnings` fails despite failOnWarnings being false |
| `unused_missing_import` | F401 and reportMissingImports before any automatic removal |
| `references` | Static checks pass; the separate semantic control has four locations |
| `typed_json_boundary` | Typed decoder adapter and runtime narrowing pass; see the worked repair |

Extra diagnostics are retained. A matching rule plus an infrastructure failure is not successful validation.

Compare each `tools[].version` in the report with `tool_versions_tested` in `fixtures.json`. When a version differs and a control does not match, report the version difference as the first explanation; do not revise the expected outcomes from memory.

## Semantic control

When testing the LSP tool explicitly, create a new folder inside the project the language server serves (for example `lsp-control-<random>/`), copy `references.py.fixture` into it as `references.py`, and do not run it. Use its absolute path in the Claude LSP request with `line: 4`, `character: 5`. Hover should identify `target(value: int) -> int`; references including its declaration should identify the definition and three calls. Raw protocol coordinates are line 3, character 4.

Check identity, client/server coverage, and synchronization before interpreting a smaller result. Make at most two retries after the initial request. A stable short result is an unresolved coverage limit, not proof that calls do not exist. When done, delete that folder and nothing else.

## Applying a control to real policy

An isolated control uses the provided profile, not inherited user settings. To understand a project difference, compare its actual source, rules, interpreter, coverage, and exclusions without changing that policy. A control passing under another policy can mean exclusion, a disabled rule, a different environment, or source changes; establish the cause before naming it. Do not infer an untested real file is healthy from these control results.
