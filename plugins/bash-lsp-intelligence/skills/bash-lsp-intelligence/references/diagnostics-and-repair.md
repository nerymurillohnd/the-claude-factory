# Shell diagnosis and repair

Establish the intended dialect before interpreting parser output. An unsupported shell, wrong source context, missing executable, and a genuine parse defect require different actions. Read the complete diagnostic rather than classifying cause solely by its numeric process status.

| Finding | Investigate | Repair principle |
|---|---|---|
| SC2086 | Intended number of arguments and whether globbing is deliberate | Quote single paths/values; use arrays for argument lists |
| SC2250 | Parameter expansion boundaries and style policy | Use braces where they clarify the intended expansion |
| SC2312 / masked statuses | Which command's failure must be observable | Capture the command's status before combining it with another operation |
| SC2154 | Declaration, source resolution, control flow, and spelling | Restore the real binding; do not invent an unrelated assignment |
| SC1090 / SC1091 | Dynamic paths and files the analyzer can actually follow | Supply accurate source metadata or lookup context when justified |
| SC1071 | Actual shebang/dialect versus tool support | Report unsupported analysis; do not force conversion |
| shfmt parse message | Supported dialect and the complete syntactic construct | Repair a demonstrated syntax error under that dialect |

Use the installed tool's documentation for unfamiliar codes. Optional rules and severity settings affect which findings appear. Preserve the active requirements instead of dropping flags, adding `disable=` directives, or suppressing a code merely to obtain success.

## Source resolution versus execution

`source ./lib/settings.sh` is cwd-dependent at runtime. `source-path=SCRIPTDIR` or `-P SCRIPTDIR` changes ShellCheck lookup, not runtime behavior. Reproduce the declared launch context for analysis; if arbitrary launch directories must work, an authorized source change may anchor the path to the script location. For Bash, `${BASH_SOURCE[0]}` identifies the current script, unlike `$0` in a sourced library.

A `# shellcheck source=...` directive must name the actual source. Pointing to `/dev/null` solely to hide missing-source evidence does not verify variables supplied by that file.

## Quoting and argument semantics

`"${directory}"/*.csv` retains intentional filename expansion while quoting the directory. `"${directory}/*.csv"` instead passes a literal pattern. An array preserves distinct filenames containing spaces; choose explicitly what should happen when no files match. Do not normalize all unquoted expressions mechanically.

Use `--` where the invoked command supports it to separate options from path operands. Check empty values, leading dashes, whitespace, wildcard characters, and argument count when those cases matter to the operation.

## Exit and cleanup behavior

An assignment containing a failed substitution, a pipeline, a trap, and a compound command each have their own status semantics. Retain the status that represents the required operation. `set -e` is not a substitute for explicit handling, and its behavior changes in conditionals. Preserve error/rejection behavior rather than adding `|| true` to erase it.

Test cleanup in a controlled workspace. Remove only artifacts created by the task; static analysis is not a reason to execute user scripts or production cleanup commands.
