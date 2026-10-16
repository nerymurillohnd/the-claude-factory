# Changelog

All notable changes to **Bash LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- `bash-lsp-intelligence` skill: the routing table no longer offers `prepareCallHierarchy` and `goToImplementation`, which bash-language-server does not support; callers come from `findReferences` and callees from reading the body.
- `bash-lsp-intelligence` skill: the Checks section gives the post-edit hook's defaults (`shfmt -i 2 -ci -bn`, `shellcheck -o all -S style -x -a -P SCRIPTDIR`) for projects without configuration, so a manual run matches the hook.
- `bash-lsp-intelligence` skill: the Gotchas heading no longer claims every gotcha was verified on fixtures.
- Toolchain reference: shfmt installs pin v3.14.1 (the `go install` form no longer says `@latest`) and pick the release binary for the machine's architecture; the project-wide examples quote file names with `git ls-files -z | xargs -0`; the suppression note matches the hook, which asks for findings to be fixed, not suppressed.
- README: the requirement is Node.js 20 or later, which bash-language-server itself needs; it also runs the hook.

## [0.2.0] - 2026-10-13

### Added

- Post-edit hook: after each Edit, Write or Bash call, the shell scripts it changed go through `shfmt -w` and `shellcheck` with your own `.editorconfig`, `.shellcheckrc` and `SHELLCHECK_OPTS` (the plugin's strict defaults only when you have none). Findings reach Claude as an error to fix; a clean run confirms with one line; a zsh script is reported as not checked.

### Changed

- `bash-lsp-intelligence` skill rewritten: LSP operations first with a routing table against Grep, five checks before trusting a reference result, the blind spots to grep, an impact checklist for renames and deletions, bash-language-server gotchas verified on fixtures, and a `toolchain.md` reference for install, configuration, frequent findings, CI and IDE.

### Removed

- The control runner (`verify-fixtures.sh`) and `fixtures.json`; the fixtures now come with `fixtures.md`, which says how to run each one with the project's configuration.

## [0.1.0] - 2026-10-12

### Added

- Language server: connects Claude Code to bash-language-server for `.sh`, `.inc`, `.bash` and `.command` files, with diagnostics after each edit and restart on crash.
- `bash-lsp-intelligence` skill: navigates shell code with the language server; traces direct and transitive `source` chains before trusting same-named functions; respects the script's real dialect; fixes ShellCheck and shfmt findings without changing quoting, globbing or exit-status behavior; and reports each check's status, the scripts covered and what stayed unverified.
- Optional controls: a bundled runner checks ShellCheck and shfmt against known control files in a temporary folder, without running them or installing anything.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/bash-lsp-intelligence--v0.2.0...HEAD
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/bash-lsp-intelligence--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/bash-lsp-intelligence--v0.1.0
