---
paths:
  - "**/*.sh"
  - "/.shellcheckrc"
  - "/.editorconfig"
---

# Shell scripts

- Load the `bash-lsp-intelligence:bash-lsp-intelligence` skill whenever you write, edit or review a shell script.
- Fix every issue a check reports before the next step or task; never leave it as debt.

## Gotchas

- shfmt reads `.editorconfig` only when you pass no formatting flag; any flag such as `-i` makes it ignore the file.
- Without an `.editorconfig`, format with `shfmt -w -i 2 -s -bn -ci -sr <file>`.
- ShellCheck reads `.shellcheckrc` and `SHELLCHECK_OPTS`; pass `-S style -a` anyway, because `.shellcheckrc` cannot set them.
- Without a `.shellcheckrc`, lint with `shellcheck -o all -S style -a -x -P SCRIPTDIR <file>`.
- Add a `# shellcheck disable=SC<code>` line only for a proven false positive, with its reason and the owner's approval.

## After writing or editing a shell script, in this order

1. Run `shfmt -w <file>` to format it, before linting, so ShellCheck's line numbers match the final file.
2. Run `shellcheck -S style -a <file>` to lint it with every optional check; fix each finding by hand, then repeat steps 1 and 2.
3. Read the file again before the next edit, because step 1 rewrites it.

## Before a commit

1. Run `npm run lint:shell` to check every shell script.
