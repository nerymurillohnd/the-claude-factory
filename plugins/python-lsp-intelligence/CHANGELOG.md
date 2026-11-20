# Changelog

All notable changes to **Python LSP Intelligence** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-11-20

### Added

- With each prompt you send, the plugin now tells Claude to call the `python-lsp-intelligence:python-lsp-intelligence` skill with the Skill tool and apply it end to end, including its LSP and Grep steps, before it creates, writes or edits a Python file, with any tool or command. A new `UserPromptSubmit` hook adds this short instruction to Claude's context; it sends nothing and writes nothing.

### Changed

- Post-edit hook messages: you now get one line after every check that says which tools ran on which files, whether ruff reformatted any of them, and whether they found errors, or why nothing ran (a missing tool, more files than the hook checks). Claude now gets a message only when the tools find errors: the findings, and the instruction to load `python-lsp-intelligence:python-lsp-intelligence` with the Skill tool, audit them and fix them before continuing. A clean run, a reformat or a missing tool no longer adds anything to Claude's context.
- A missing `ruff` or `basedpyright` is now reported on every call instead of once per session, so the hook no longer writes marker files to the plugin's data folder; you can delete the `notices/` folder it left there.
- When the hook itself fails (`python3` can't start it, it crashes or it runs past its 60 seconds), Claude now receives the error, as with a finding (`onFailure: "block"`), instead of the failure passing as a hook error notice.

### Removed

- **Breaking:** the first Python edit of a session no longer waits for the skill. The `PreToolUse` hook that denied the first Edit, Write or NotebookEdit call until Claude loaded `python-lsp-intelligence:python-lsp-intelligence` is gone, together with the entries that only tracked it (`PostToolUse` on the Skill tool, `UserPromptExpansion` and `PostCompact`). Claude now gets the instructions above with each prompt instead of a denied edit. Nothing for you to do: the marker files it left in the plugin's data folder, under `skill-loads/`, are no longer read, and you can delete them.

## [0.4.0] - 2026-11-19

### Added

- **Breaking:** the first Python edit of a session now waits until Claude has loaded the `python-lsp-intelligence:python-lsp-intelligence` skill. A new `PreToolUse` hook denies that one Edit, Write or NotebookEdit call, once, with a message that tells Claude to load the skill and retry; every later edit goes through, so a session that can't load skills is never locked out. A subagent counts on its own, and after compaction the next edit asks for the skill again. The hook keeps its markers in the plugin's data folder and does nothing where Claude Code gives it none.
- The skill now opens with a step that runs before the first Python file of the task: it checks that the language server is installed and that the `LSP` tool is available, starts the server with a first call, and switches to Grep and reading, reported as such, when either is missing, as in cloud sessions.

### Changed

- The skill's description now opens with the work it serves, before writing, editing, renaming or deleting Python code, even for a one-line fix, and says what it adds over a text search, so Claude loads it for everyday Python edits instead of only when asked.
- The skill now trusts an `LSP` result only after three consecutive identical answers to the same call, at most six calls, instead of two out of three, and records a result as unstable when no three match.
- The skill now says when a name is public API, which code outside the repository can import or run, and asks the user before renaming or deleting one.
- The skill now gets callers and callees with `incomingCalls` and `outgoingCalls` on the function's position, using `prepareCallHierarchy` only to confirm the position.

## [0.3.4] - 2026-11-14

### Fixed

- When ruff or basedpyright isn't installed, the hook no longer reports an error after every edit. You get one message per session with the install command, Claude is told once that the files weren't checked, and work goes on. The plugin keeps that once-per-session marker only in its own data folder; where Claude Code gives it none, the message repeats instead of the hook creating or deleting files in your system's temporary directory, which other users of the machine can write to.
- After a Bash command in a folder that isn't a Git repository, the hook no longer checks or reformats the files of a repository you cloned, a branch you checked out or a pull. Inside a Git repository below your project, it checks only the files Git lists as modified, untracked or staged.
- When a Bash command leaves more than 20 Python files outside any Git repository, such as an extracted archive, the hook checks none of them and tells Claude, instead of reformatting the first 20.
- After a Bash command, the hook no longer checks or reformats the Python files that command wrote into a place Git ignores, such as a build folder.

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

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/python-lsp-intelligence--v0.5.0...HEAD
[0.5.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.5.0
[0.4.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.4.0
[0.3.4]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.3.4
[0.3.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.3.3
[0.3.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.3.2
[0.3.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.3.1
[0.3.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.3.0
[0.2.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.2.3
[0.2.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.2.2
[0.2.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.2.1
[0.2.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.2.0
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/python-lsp-intelligence--v0.1.0
