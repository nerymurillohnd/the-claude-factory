# Changelog

All notable changes to **macOS Grep Guard** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-11-06

### Changed

- The plugin's description now names the tools and terms people type when they search for a plugin like this one in `/plugin`, which matches only the plugin's name, display name and description. Nothing changes in how the plugin works.

## [0.1.3] - 2026-11-05

### Added

- A listing icon and links to this README, the issue forms and the marketplace's privacy policy, which Anthropic's plugin directory shows on the plugin's page. Claude Code ignores these fields when it loads the plugin, so nothing changes in how it works.

## [0.1.2] - 2026-11-02

### Changed

- The plugin's keywords now name what it guards: `macos`, `grep`, `awk`, `bsd` and `zsh`.
- The README gives Claude Code 2.1.292 as the minimum in the terminal and the Desktop app, the version from which the guard sees a Bash call's repaired arguments, and describes each process the guard starts and when.

### Fixed

- The README's FAQ no longer tells you to list skills the plugin doesn't have.
- The changelog describes what 0.1.0 shipped.

## [0.1.1] - 2026-10-30

### Removed

- The `tsconfig.json` at the plugin's root, a development file that shipped by mistake: it pointed at type files your copy never has, and the mod never used it. Nothing changes in how the plugin works.

## [0.1.0] - 2026-10-28

### Added

- A mod that checks every Bash call on macOS, in the main session and in subagents:
  - It stops a recursive `grep` that would silently skip gitignored and binary files, until the command states whether they count.
  - It stops an `awk` program that relies on `IGNORECASE`, which macOS awk ignores, and suggests `tolower($0) ~ /pattern/`.
  - When a command fails with a known BSD or zsh error, such as `uniq -w`, `stat -c`, GNU-style `sed -i`, `timeout` or an unmatched glob, it adds the macOS form next to the error so Claude retries it.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/macos-grep-guard--v0.1.4...HEAD
[0.1.4]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/macos-grep-guard--v0.1.4
[0.1.3]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/macos-grep-guard--v0.1.3
[0.1.2]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/macos-grep-guard--v0.1.2
[0.1.1]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/macos-grep-guard--v0.1.1
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/macos-grep-guard--v0.1.0
