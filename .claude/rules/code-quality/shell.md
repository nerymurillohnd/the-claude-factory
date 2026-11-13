---
paths:
  - "**/*.sh"
  - "/.shellcheckrc"
  - "/.editorconfig"
---

# Shell scripts

- Load the `bash-lsp-intelligence:bash-lsp-intelligence` skill.
- Fix every finding before moving on; never leave one as debt.
- Disable a ShellCheck code only for a proven false positive, with its reason and the owner's approval.

## After each write or edit, run in order

1. Format: `shfmt -w <file>` when `.editorconfig` exists, with no formatting flags; otherwise `shfmt -w -i 2 -s -bn -ci -sr <file>`.
2. Lint: `shellcheck -S style -a <file>` when `.shellcheckrc` exists; otherwise `shellcheck -o all -S style -a -x -P SCRIPTDIR <file>`.
3. Fix every finding, then repeat steps 1 and 2 until both pass.
4. Read the file again before the next edit.
