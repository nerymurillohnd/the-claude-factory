---
paths:
  - "**/*.sh"
  - "/.shellcheckrc"
  - "/.editorconfig"
---

# Shell code quality

Use shfmt and ShellCheck; `.editorconfig` holds shfmt's settings and `.shellcheckrc` ShellCheck's, so pass no style flags.

## After editing a shell script

- Format it: `shfmt -w <file>`.
- Lint it with every optional check: `shellcheck -S style -a <file>`.
- Read the file again before the next edit: `shfmt -w` rewrites it.

## Before a commit

- Check every shell script: `npm run lint:shell`.

## Findings

- Fix each finding at its cause.
- When a finding is a false positive, show the evidence and ask the owner before adding a `# shellcheck disable=SC<code>` line with its reason.

## LSP

- Load the `bash-lsp-intelligence:bash-lsp-intelligence` skill before renaming or deleting a shell function.
