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

## Run in this order after each write or edit

1. Run `shfmt -w <file>` to format it with the `.editorconfig` settings; without an `.editorconfig`, run `shfmt -w -i 2 -s -bn -ci -sr <file>`.
2. Run `shellcheck -S style -a <file>` to lint it with every check; without a `.shellcheckrc`, run `shellcheck -o all -S style -a -x -P SCRIPTDIR <file>`.
3. Fix every finding, then run steps 1 and 2 again until both pass.
4. Read the file again before the next edit.
