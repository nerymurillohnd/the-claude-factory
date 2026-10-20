# Changelog

All notable changes to **Block No Verify** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-20

### Added

- Denies a Bash command that runs git with `--no-verify`, `--no-gpg-sign`, `-c commit.gpgsign=false` or `-c tag.gpgsign=false`, before it runs. Claude is told to run the command without the flag and to fix the failing hook.
- Reads past the usual disguises: `-n` on `git commit` and `git am`, the abbreviations git accepts (`--no-veri`, `--no-g`), a flag moved to the next line with a backslash, `sudo`, `env`, `timeout` and the other wrappers, `git.exe`, and `bash -c`, `sh -c` or `eval` up to three levels deep.
- Leaves normal work alone: a message that mentions a flag, `-n` in `git push`, `git merge` and the other commands where it means something else, and Claude's own `git commit -m "$(cat <<'EOF' …)"` form all pass.
- Starts from a launcher that checks for Python 3.9 or later. Without it the guard shows a notice that it is inactive and blocks nothing.
- Needs Claude Code 2.1.295 or later: a hook that fails to run blocks the command instead of letting it through.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/block-no-verify--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/block-no-verify--v0.1.0
