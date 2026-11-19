---
paths:
  - "**/*.sh"
  - "/.shellcheckrc"
  - "/.editorconfig"
---

# Shell scripts

- Fix every finding at its cause, never its symptom. Never lower, relax, bypass or route around a gate, test, check or script to make it pass, and never add a suppression: no `# shellcheck disable=`, `|| true` to hide a failure, or loosened `.shellcheckrc`, `.editorconfig` or `SHELLCHECK_OPTS`.
- Fix every finding the `bash-lsp-intelligence` plugin's post-edit hook reports after an edit before the next edit; the hook runs `shfmt -w`, then `shellcheck`, which reads its strictness from `.shellcheckrc` and `SHELLCHECK_OPTS`.

## Writing a Bash script

- Start every standalone script with `#!/usr/bin/env bash` and `set -euo pipefail` on the next line. Drop an option only with the reason on that `set` line, such as a script that always exits 0 and reports through its output.
- Never let `set -e` pick a command hook's exit code: `grep` exits 2 on an unreadable file and `jq` on a usage or system error, and exit 2 blocks on `PreToolUse`, `Stop`, `SubagentStop` and the other events that can block. Map every unexpected failure to the code the hook means, with `set -Eeuo pipefail` and `trap 'exit 1' ERR`, or an `EXIT` trap that turns any non-zero status into 1. A guard that must fail closed maps it to 2 instead.
- Keep a plugin's scripts to Bash 3.2, the floor its README states, unless the README's Prerequisites declare Bash 4: `mapfile`, `readarray`, `${v,,}` and `${v^^}` need Bash 4.0, and `shopt -s inherit_errexit` needs 4.4.
- Test a `jq` filter's success without `-e` when it may print nothing: `-e` exits 4 when no result is produced and 1 when the last one is `false` or `null`, while plain `jq` exits 0, and 5 on a parse error or `error()`.
- Never leave `set -x` in a hook or a CI step: it prints expanded arguments, secrets included, to the log.
