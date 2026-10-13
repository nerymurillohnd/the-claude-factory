# Shell quality gate: shfmt + shellcheck

The gate's hooks ship in the `bash-lsp` plugin, next to the language server. This file is the
only guidance for them: read it when writing sh or Bash code or when the gate reports findings or blocks a stop.

Every sh/bash file Claude changes goes through one chain, run by the `bash-lsp` plugin's hooks after each edit and again before Claude stops:

```bash
shfmt -w <file> && shellcheck <file>
```

- Both run with no flags and no `cd`, exactly as typed in the session, so each reads its own config.
- `shfmt` rewrites the file in place. After it reformats, **re-read the file before the next Edit**.
- The style comes from the nearest `.editorconfig` (a `[[shell]]` section takes `indent_size`, `simplify`, `binary_next_line`, `switch_case_indent`, `space_redirects`). Without one, shfmt uses its defaults, tabs included. To change a shell style, edit the `.editorconfig`, never the gate.
- The rules come from the nearest `.shellcheckrc` above the script, then `~/.shellcheckrc`, then `~/.config/shellcheckrc`, plus `SHELLCHECK_OPTS`. `enable=all` there turns on every optional check. Any finding fails the gate.
- A file is sh/bash when it ends in `.sh`/`.bash` or its shebang runs `sh` or `bash`. zsh is never checked.

## When the hook reports findings

1. Fix the root cause of each finding by its SC code. `https://www.shellcheck.net/wiki/SC<code>` explains it.
2. Save with Edit. The hook re-runs the chain on the edit and reports again until the file is clean.
3. A stop blocked by the hook lists every changed shell file that still fails. Fix them all, then stop again.

Never make the gate pass by weakening it: no `# shellcheck disable=`, no `|| true` that hides a real failure, no loosening the `.shellcheckrc` or `.editorconfig`. A suppression or loosened config hides the defect from every later check and from the user, so the gate would report green on broken code.
The one exception is a finding you verified is a false positive. Put the directive on the line above, with a comment saying why, and tell the user.

## Frequent findings under `enable=all`

| Code | Finding | Fix |
|---|---|---|
| SC2086 | Unquoted expansion | `"${var}"` |
| SC2250 | Variable without braces | `${var}` |
| SC2292 | `[ ]` in bash | `[[ ]]` |
| SC2312 | `$(cmd)` inside another command masks its exit code | Assign first: `out=$(cmd) \|\| handle`, then use `${out}` |
| SC2310 | Function in a condition turns off `set -e` inside it | Call it on its own line and test `$?`, or accept it knowingly in code without `set -e` |
| SC2248 | Quote even "safe" variables | `"${n}"` |
| SC2154 | Variable referenced but never assigned | Assign it, or source the file that defines it with a `# shellcheck source=` hint |
| SC1091 | Sourced file not followed | Add `# shellcheck source=path/to/file` above the `source` line |

## Checking files on demand

```bash
shell-gate <file>...
```

`shell-gate` comes from `bash-lsp`'s `bin/`, on the Bash tool's `PATH` while the plugin is enabled. Exit 0 means clean. Exit 2 prints the findings for each file.
