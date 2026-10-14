# Changelog

All notable changes to **Git Hygiene** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-10-14

### Fixed

- `inventory.py` now redacts credentials in every string of a saved or loaded inventory, not only in the strings it gathers itself.

## [0.1.0] - 2026-10-14

### Added

- `git-hygiene:cleanup` skill, started only with `/git-hygiene:cleanup [path] [problem]`: audits a repository end to end (context, every local and remote branch with its exclusive work, linked worktrees, stashes, pull requests, files and noise, history, reflog), presents findings and a numbered cleanup plan (classes `prep`, `integrate`, `publish`, `local-delete`, `remote-delete`, `files`) with a mandatory backup that is part of every approval, and executes and verifies only the actions you approve.
- `inventory.py`, a read-only script that gathers the audit facts in one pass, redacts credentials and previews merges with `git merge-tree`.
- A `PreToolUse` guard, active from the moment the cleanup starts: refuses force-pushes, deleting `main` on the remote, the history-rewriting tools `filter-branch`, `filter-repo` and `bfg`, `git clean -x`, default-branch changes and anything that prints credentials or reads secret files, and asks before every command that changes state or prints file contents. It blocks the action if the guard itself cannot run.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/git-hygiene--v0.1.1...HEAD
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/git-hygiene--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/git-hygiene--v0.1.0
