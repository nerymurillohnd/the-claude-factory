---
paths:
  - "**/*.sh"
  - "/.shellcheckrc"
  - "/.editorconfig"
---

# Shell code quality

Use shfmt and ShellCheck; `.editorconfig` holds shfmt's settings and `.shellcheckrc` ShellCheck's, so pass no style flags.

## Order of work on a shell script

1. Before renaming or deleting a function, find every use with the LSP tool, as `lsp.md` sets.
2. Edit the script, then fix the LSP diagnostics Claude Code reports for it.
3. Format: `shfmt -w <file>`. Run it before linting, so ShellCheck's line numbers match the final file.
4. Lint with every optional check: `shellcheck -S style -a <file>`. ShellCheck fixes nothing itself: fix each finding by hand, then repeat steps 3 and 4.
5. Read the file again before the next edit: step 3 rewrites it.

## Before a commit

- Check every shell script: `npm run lint:shell`.

## Findings

- Fix each finding at its cause.
- When a finding is a false positive, show the evidence and ask the owner before adding a `# shellcheck disable=SC<code>` line with its reason.

## LSP

- Load the `bash-lsp-intelligence:bash-lsp-intelligence` skill before renaming or deleting a shell function.
