# Shell toolchain: shfmt and ShellCheck

## Contents

- Install
- Where configuration lives
- Defaults when the project has none
- A strict project configuration
- Frequent findings
- Check one file or the whole project
- CI
- IDE

## Install

| Platform | Commands |
| :-- | :-- |
| macOS | `brew install shfmt shellcheck` and `npm install -g bash-language-server` |
| Debian / Ubuntu | `sudo apt install shellcheck`; shfmt from the release binary for your architecture (`sudo curl -sSfL -o /usr/local/bin/shfmt "https://github.com/mvdan/sh/releases/download/v3.14.1/shfmt_v3.14.1_linux_$(dpkg --print-architecture)" && sudo chmod 755 /usr/local/bin/shfmt`) or `go install mvdan.cc/sh/v3/cmd/shfmt@v3.14.1`; `npm install -g bash-language-server` |
| Windows | Git Bash with the same binaries on `PATH` |

`which shfmt shellcheck bash-language-server` confirms they are on the `PATH` of the shell that starts Claude Code.

## Where configuration lives

| Tool | Lookup | Notes |
| :-- | :-- | :-- |
| shfmt | `.editorconfig`, searched from the file's directory upward; a `[[shell]]` section sets `indent_style`, `indent_size`, `simplify`, `binary_next_line`, `switch_case_indent`, `space_redirects` | Any formatting flag on the command line (`-i`, `-ci`, …) turns EditorConfig off for that run |
| ShellCheck | The first `.shellcheckrc` or `shellcheckrc` from the script's directory upward, then `~/.shellcheckrc`, then `$XDG_CONFIG_HOME/shellcheckrc`; `SHELLCHECK_OPTS` adds flags to every run | `shellcheck --norc` ignores the files; the dialect comes from `--shell`, a `# shellcheck shell=` directive, the shebang, or the extension |

## Defaults when the project has none

With no `.editorconfig` above the file, this plugin formats with `shfmt -i 2 -ci -bn` (two-space indent, indented `case` branches, binary operators at line start). With no `.shellcheckrc` anywhere and `SHELLCHECK_OPTS` unset, it analyzes with `shellcheck -o all -S style -x -a -P SCRIPTDIR` (every optional check, style severity, follow and check sourced files, resolve `source` paths from the script's directory). An `.editorconfig`, a `.shellcheckrc` or `SHELLCHECK_OPTS` of your own replaces the corresponding default entirely.

## A strict project configuration

`.editorconfig`:

```ini
root = true

[[shell]]
indent_style = space
indent_size = 2
switch_case_indent = true
binary_next_line = true
simplify = true
space_redirects = true
```

`.shellcheckrc` (`-S style` and `-a` have no rc key; put them in `SHELLCHECK_OPTS="-S style -a"`):

```ini
enable=all
external-sources=true
source-path=SCRIPTDIR
```

## Frequent findings

| Code | Finding | Fix |
| :-- | :-- | :-- |
| SC2086 | Unquoted expansion | `"${var}"`; keep an unquoted glob only when expansion is intended |
| SC2250 | Variable without braces (optional check) | `${var}` |
| SC2292 | `[ ]` in bash | `[[ ]]` |
| SC2312 | `$(cmd)` inside another command masks its exit status | `out=$(cmd) \|\| handle`, then use `${out}` |
| SC2310 | A function in a condition disables `set -e` inside it | Call it on its own line and test `$?` |
| SC2154 | Variable referenced but never assigned | Assign it, or `# shellcheck source=path` above the `source` line |
| SC1091 | Sourced file not followed | `# shellcheck source=path/to/file` |
| SC1071 | Unsupported dialect (zsh) | ShellCheck can't check it; use a zsh-aware tool or Bash |

Fix a finding; do not suppress it with `# shellcheck disable=SCnnnn` to get a clean result. When you can show that a finding is a false positive, report it with the evidence and let the project owner decide.

## Check one file or the whole project

```bash
shfmt -w path/to/script.sh && shellcheck path/to/script.sh
shfmt -d . && git ls-files -z '*.sh' | xargs -0 shellcheck -x
bash -n path/to/script.sh
```

- `shfmt -d` exits 1 when a file would change, `-l` lists such files, `-w` rewrites them.
- `shellcheck` exits 1 with findings, 0 when clean; `-f gcc` gives one `file:line:col: level: message [SCnnnn]` per finding.
- `bash -n` parses one script per invocation; a second file name is an argument to the first script, not another script.

## CI

```bash
shfmt -d .
git ls-files -z '*.sh' | xargs -0 shellcheck -o all -S style -x -a -P SCRIPTDIR
```

Pin the versions (shfmt 3.14.1, ShellCheck 0.10 or later) so a release does not change the result.

## IDE

VS Code: the **ShellCheck** and **shell-format** extensions read the same `.shellcheckrc` and `.editorconfig`, so the editor and the command line agree.
