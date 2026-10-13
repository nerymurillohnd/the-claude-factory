# Shell repair decisions

## Sourcing and language routing

When same-named functions appear in references, trace definitions and source paths in execution order. A same-shell caller may receive a definition through a parent-sourced library. An independent child process needs a real exported/imported connection. Trap strings, `eval`, `bash -c`, aliases and dispatch tables can add consumers outside ordinary references.

The server's discovery glob and the client's extension/language mapping have different jobs. Finding `.inc` files in a glob does not route direct client requests for `.inc` to a shell server. Inspect both settings for a coverage problem; also inspect extensionless launchers and relevant hidden directories. An include suffix alone does not establish the dialect of arbitrary code.

For a shebangless library known to be Bash from its callers, `shellcheck --shell=bash /absolute/library.inc` supplies analysis context without adding a shebang. `bash -n` parses one script per invocation; it does not parse later positional filename arguments as additional scripts.

## Strict ShellCheck context

The rc keys `enable=all`, `external-sources=true`, `source-path=SCRIPTDIR`, and `extended-analysis=true` express optional checks, source lookup and analysis. Style severity and findings in sourced files are CLI concerns: `--severity=style` and `--check-sourced`. `SHELLCHECK_OPTS` and the selected rc can also affect results; inspect relevant effective settings without dumping the environment.

An analyzer source path does not change runtime cwd. If `source ./lib/settings.sh` resolves only from a particular launch directory, reproduce that context before deciding on a path repair. In Bash, `${BASH_SOURCE[0]}` identifies the sourced script while `$0` can name its caller; anchoring paths requires understanding the intended launch contract.

## Quoting, status and rewrites

SC2086 asks whether splitting/globbing is intended. Use quoted scalar paths for one operand and arrays for argument lists. Retain intentional glob expansion and choose the intended no-match behavior. Test spaces, empty values or leading dashes when they affect the changed operation.

A semicolon sequence returns the last command's status; `&&` leaves later checks unexecuted after failure. Capture the required status before combining commands, including assignments with command substitution, pipelines and traps. `set -e` has conditional exceptions and does not replace explicit error handling.

shfmt formatting/simplification and ShellCheck fixes can change source locations or behavior. Inspect rewrites before the next edit, and use controlled launch/error cases for trap cleanup, source paths or argument semantics. Static diagnosis does not require executing a deployment or deletion script.
