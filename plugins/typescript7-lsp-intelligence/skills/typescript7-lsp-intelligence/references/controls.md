# Control tests

Run the control tests only when the user asks to test tool coverage, or when a check passes code it should flag. Their fixed profile is independent of the user's project and does not authorize changing its options. Matching controls establish tool behavior on known controls, not complete tool coverage or correctness of real code.

`references/fixtures.json` lists the expected diagnostics, the profile, and the compiler versions they were tested with (`tool_versions_tested`). The runner `scripts/verify-fixtures.sh` copies each control into a fresh temporary directory, gives it explicit program membership, checks the resolved strict/no-emit/JS/library options, verifies membership, then compiles. It captures each status and complete compiler output, and never executes the controls or installs tools. Run it with the command in SKILL.md, which carries its absolute path; SKILL.md also explains its exit codes.

An already available compiler is required; `tsc` on `PATH` is the default only when no executable is supplied. Run separately against each compiler generation whose compatibility you want to establish; the runner does not locate or switch installations. A missing tool, failed configuration, missing source membership, or failed process is unsuccessful verification even with no parsed TS code.

| Control | Expected under the supplied profile |
|---|---|
| `clean_control` | Compilation passes |
| `references` | Compilation passes; separate semantic control has definition and three calls |
| `type_mismatch` | TS2322 |
| `implicit_any` | TS7006 |
| `possibly_undefined` | TS18048 |
| `javascript_type` | TS2322 with checkJs true |
| `unchecked_index` | TS2322 with noUncheckedIndexedAccess true |
| `typed_json_boundary` | Runtime narrowing compiles; see the worked repair |

The profile uses strict mode, noEmit, checked JS, noUncheckedIndexedAccess, exact optional properties, and library checking, and disables incremental/composite metadata. Extra diagnostics remain in the report. Lint, formatter, and runtime checks are independent of this runner.

Compare each `tools[].version` in the report with `tool_versions_tested`. When a version differs and a control does not match, report the version difference as the first explanation; do not revise the expected outcomes from memory.

## Semantic control

When testing the LSP tool explicitly, create a new folder inside the project the language server serves (for example `lsp-control-<random>/`). Copy `references.ts.fixture` into it as `references.ts`, and `tsconfig.json.fixture` as `tsconfig.json` with `"files": ["references.ts"]`, so the server loads the control as its own program instead of under the project's configuration; do not run it. Use the absolute path of `references.ts` with Claude `line: 2`, `character: 17` on `target`. References including the declaration should identify its definition and three calls. Raw protocol coordinates are line 1, character 16.

Inspect identity, synchronization, project loading, and capabilities before interpreting a smaller result; make at most two retries after the initial request. A stable short result remains a coverage limit. This single-file control does not prove cross-package, alias, framework, or dynamic consumer completeness. When done, delete that folder and nothing else.

Compare the user's effective policy, program membership, tool version, and actual source before explaining different outcomes. Do not silently weaken options or infer untested real code is healthy from an isolated control.
