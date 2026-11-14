---
paths:
  - "**/*.sh"
  - "/.shellcheckrc"
  - "/.editorconfig"
---

# Shell scripts

- Fix every finding at its cause, never its symptom. Never lower, relax, bypass or route around a gate, test, check or script to make it pass, and never add a suppression: no `# shellcheck disable=`, `|| true` to hide a failure, or loosened `.shellcheckrc`, `.editorconfig` or `SHELLCHECK_OPTS`.
- Fix every finding the `bash-lsp-intelligence` plugin's post-edit hook reports after an edit before the next edit; the hook runs `shfmt -w`, then `shellcheck`, which reads its strictness from `.shellcheckrc` and `SHELLCHECK_OPTS`.
- Read the file again after each edit, because the hook rewrites it.
- When no hook message follows an edit, run `shfmt -w <file>`, then `shellcheck -S style -a <file>`, yourself, as `npm run lint:shell` does.
