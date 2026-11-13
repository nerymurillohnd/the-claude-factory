---
paths:
  - "**/*.sh"
  - "/.shellcheckrc"
  - "/.editorconfig"
---

# Shell code quality

## Formatting

- Format shell scripts with shfmt, which reads its settings from `.editorconfig`, so pass it no style flags.
- After editing a script, run `shfmt -w <file>`, then read the file again before the next edit.

## Linting

- Lint with ShellCheck: `shellcheck -S style -a <file>`; `.shellcheckrc` turns on every optional check.
- Before a commit, run `npm run lint:shell`.

## Findings

- Fix each finding at its cause.
- When a finding is a false positive, show the evidence and ask the owner before adding a `# shellcheck disable=SC<code>` line with its reason.

## LSP

- Load the `bash-lsp-intelligence:bash-lsp-intelligence` skill before renaming or deleting a shell function.
