# Shell verification evidence

Use the supported dialect and the declared formatting/lint policy. `shfmt -w` rewrites source; `shfmt -d` reports formatting differences without rewriting. Formatting is not type checking and does not replace behavior tests.

## Find the declared policy

The project's policy is what it already runs or configures: a `.shellcheckrc` (ShellCheck searches from each script's directory upward, then the user's home configuration), `SHELLCHECK_OPTS`, an `.editorconfig` shell section, and the ShellCheck or shfmt invocations in its CI, Makefile, scripts or contributor docs. Use those flags as declared.

When the project declares nothing, run the default and say in the report that no policy was declared:

```text
shfmt -d <affected scripts>
shellcheck --check-sourced <affected scripts>
```

These are independent invocations; retain each status. `--check-sourced` reports findings in the sourced files ShellCheck follows; without it, those files are followed but not reported. Do not add optional checks (`enable=all`, `--severity=style`) or `--external-sources` on your own: the strict profile in the control tests exists to make those tests reproducible, not as a default for user projects.

Keep formatter policy separate from ShellCheck rule policy. Style flags can override EditorConfig; do not silently introduce a forced style or simplification flag.

## Repeat after a fix

After each fix, rerun the same checks on the same scope. Stop when they report no actionable diagnostics, or after three rounds that leave the same findings; then report what remains with its evidence.

## Evidence boundaries

Compare executable versions, dialect, input snapshot, cwd/source resolution, flags, rc files, and relevant option environment when analysis differs. Inspect non-secret effective settings rather than printing a full environment or reading credential files. Neutralizing settings in a controlled test is not permission to alter real policy.

A stage that never ran because an earlier one failed is unexecuted, not passed. Retain full stderr, particularly for parser or setup failures.

Static parsing can be checked with a supported shell's syntax-only mode. Do not execute deploy/delete/service commands while investigating a static diagnostic.

For a shebangless library, establish its intended dialect from actual callers before selecting `shellcheck --shell=bash /absolute/library.sh`. This supplies known analysis context without adding an executable shebang or converting the language. Preserve the declared source lookup policy as well. For Bash syntax checks, invoke `bash -n /absolute/script.sh` separately for each script: later filenames in one invocation become script arguments rather than additional scripts to parse.

For behavior changes, test normal and error arguments, meaningful launch directories, exit codes, traps, sourced-state behavior, and relevant path edge cases. Report exactly which scripts and contexts were verified and which remain unsupported or untested.
