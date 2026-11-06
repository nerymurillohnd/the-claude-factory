# Changelog

All notable changes to **Python LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.3] - 2026-11-06

### Changed

- The plugin's description now names the tools and terms people type when they search for a plugin like this one in `/plugin`, which matches only the plugin's name, display name and description. Nothing changes in how the plugin works.

## [0.3.2] - 2026-11-05

### Added

- A listing icon and links to this README, the issue forms and the marketplace's privacy policy, which Anthropic's plugin directory shows on the plugin's page. Claude Code ignores these fields when it loads the plugin, so nothing changes in how it works.

## [0.3.1] - 2026-11-02

### Changed

- The README now says what the hook runs and sends: `git` to find changed files (optional), at most 20 files per call, `ruff check --show-settings`, and a temporary `pyrightconfig.json` it deletes after the check. It also names extensionless files with a Python shebang and `[tool.pyright]`, and gives Claude Code 2.1.288 as the minimum, the version from which a language-server request times out instead of hanging.
- The Compatibility table gives the Claude app's Hooks cell from the marketplace matrix and names the programs the hook needs where it runs.

### Fixed

- The README no longer says `basedpyright` checks notebooks: `.ipynb` files get `ruff check --fix` and `ruff format` only.
- The changelog marks the new `python3` requirement and the removal of the control runner in 0.2.0 as breaking.

## [0.3.0] - 2026-10-27

### Changed

- **Breaking:** the post-edit hook now requires Python 3.12 or later as `python3`, up from 3.9. Check yours with `python3 --version`; older versions are no longer supported.

### Fixed

- On Windows, the post-edit hook always runs through Git Bash, never PowerShell.

## [0.2.3] - 2026-10-24

### Changed

- The marketplace now reads this plugin's catalog category from its manifest; nothing changes in how the plugin works.

## [0.2.2] - 2026-10-20

### Changed

- Post-edit hook: every message Claude receives (findings, a missing `ruff` or `basedpyright`, a reformatted file) now ends with one line telling it to use `python-lsp-intelligence:python-lsp-intelligence` and apply all its knowledge when working on Python files. What the hook checks, when it runs and how it exits are unchanged.

## [0.2.1] - 2026-10-17

### Changed

- `python-lsp-intelligence` skill: states again that a finding is fixed at its cause and never silenced with `# noqa`, `# type: ignore`, `cast()` or a relaxed rule, matching the hook's message; removes the unsupported "verified on fixtures" label from the gotchas; rewords the opening line about automatic checks.

### Fixed

- `toolchain.md` and the README said basedpyright finds its configuration only in the current working directory. It searches from the working directory upward through its parent folders, and never from the file's folder.

## [0.2.0] - 2026-10-13

### Added

- **Breaking:** post-edit hook, which needs `python3` 3.9 or later on `PATH`: after each Edit, Write, NotebookEdit or Bash call, the Python files it changed go through `ruff check --fix`, `ruff format` and `basedpyright` with your own configuration (the plugin's strict defaults only when you have none). Findings reach Claude as an error to fix; a clean run confirms with one line.

### Changed

- `python-lsp-intelligence` skill rewritten: LSP operations first with a routing table against Grep, five checks before trusting a reference result, the blind spots to grep, an impact checklist for renames and deletions, basedpyright gotchas verified on fixtures, and a `toolchain.md` reference for configuration, strictness, environments, CI and IDE.

### Removed

- **Breaking:** the control runner (`verify-fixtures.sh`) and `fixtures.json`. If you ran the runner, run each fixture as `fixtures.md` says, with the project's configuration.

## [0.1.0] - 2026-10-12

### Added

- Language server: connects Claude Code to basedpyright for `.py`, `.pyi` and `.pyw` files, with diagnostics after each edit and restart on crash.
- `python-lsp-intelligence` skill: navigates Python code with the language server; checks aliases, re-exports, entry points and dynamic consumers before a rename or deletion; fixes basedpyright and Ruff findings by validating untrusted data instead of casting, suppressing or weakening rules; and reports each check's status, the files covered and what stayed unverified.
- Optional controls: a bundled runner checks basedpyright and Ruff against known control files in a temporary folder, without running them or installing anything.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/python-lsp-intelligence--v0.3.3...HEAD
[0.3.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.3.3
[0.3.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.3.2
[0.3.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.3.1
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.3.0
[0.2.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.2.3
[0.2.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.2.2
[0.2.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.2.1
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.1.0
