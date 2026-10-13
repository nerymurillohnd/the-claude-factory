# Control tests

Run the control tests only when the user asks to test tool coverage, or when a check passes code it should flag. They exercise selected findings on known controls under a known profile; they do not prove that every shell dialect, project policy, or runtime behavior is covered. `.fixture` names keep the control files out of normal extension discovery, but an explicitly supplied file can still be recognized as code.

`references/fixtures.json` declares the expected outcomes and the tool versions they were tested with (`tool_versions_tested`). The runner `scripts/verify-fixtures.sh` copies the controls into fresh temporary directories, supplies a root EditorConfig and explicit ShellCheck rc, removes inherited `SHELLCHECK_OPTS` for these runs, and captures statuses and full output. It never executes the controls or changes the user's settings. Run it with the command in SKILL.md, which carries its absolute path; SKILL.md also explains its exit codes.

Tools must already be installed. Missing tools and malformed reports are incomplete verification. Nothing is installed.

| Control | Expected under the supplied profile |
|---|---|
| `clean_control` | ShellCheck and formatter pass |
| `references` | Static checks pass; definition and three calls form the semantic control |
| `unquoted_expansion` | SC2086; the harmless printf preserves the splitting defect without deleting files |
| `optional_checks` | SC2250 and SC2312 with all optional checks enabled |
| `unformatted` | shfmt returns nonzero with a diff; ShellCheck passes |

The supplied rc enables all optional checks, external sources, script-directory source lookup, and extended analysis; style severity and checking sourced files are command options. This strict profile makes the controls reproducible; it is not a default for user projects. Additional diagnostics are preserved.

Compare each `tools[].version` in the report with `tool_versions_tested`. When a version differs and a control does not match, report the version difference as the first explanation; do not revise the expected outcomes from memory.

## Semantic control

When testing the LSP tool explicitly, create a new folder inside the project the language server serves (for example `lsp-control-<random>/`) and copy `references.sh.fixture` into it as `references.sh`; do not run it. Use its absolute path, `line: 3`, and `character: 1` in the Claude client. References including the declaration should identify the definition and three calls. Raw protocol coordinates are line 2, character 0.

If results are incomplete, establish identity, workspace/discovery coverage, and synchronization before a bounded retry. Stable short or overinclusive results still require source-relationship verification. This control does not prove cross-file same-name identity or dynamic call coverage. When done, delete that folder and nothing else.

## Compare with actual policy

Check the effective rc, `SHELLCHECK_OPTS`, dialect, source paths, EditorConfig, and tool version when a project behaves differently. Preserve that evidence. Do not infer that a disabled rule is an analyzer failure, change exclusions merely to pass, or report untested real scripts as healthy because these controls matched.
