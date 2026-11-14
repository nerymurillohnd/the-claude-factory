---
paths:
  - "**/*.sh"
  - "/.shellcheckrc"
  - "/.editorconfig"
---

# Shell scripts

- Fix every finding the `bash-lsp-intelligence` plugin's post-edit hook reports after an edit before the next edit; the hook runs `shfmt -w`, then `shellcheck`, with `.editorconfig`, `.shellcheckrc` and `SHELLCHECK_OPTS`.
- Read the file again after each edit, because the hook rewrites it.
- Add a `# shellcheck disable=SC<code>` line only with the owner's approval, and write the reason beside it.
- When no hook message follows an edit, run `shfmt -w <file>`, then `shellcheck -S style -a <file>`, yourself.
