# Changelog

All notable changes to **Block No Verify** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and this plugin adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-20

### Added

- Denies a git command that skips commit hooks or signing, in the Bash and PowerShell tools: `--no-verify`, `-n` on `git commit` and `git am`, the abbreviations git accepts (`--no-veri`), `--no-gpg-sign`, and `commit.gpgsign` or `tag.gpgsign` set to anything git reads as false. Claude is told to run the command without the flag and to fix the failing hook.
- Guards the configuration that does the same: `git config` on the signing keys, `core.hooksPath` pointing away from the repository, `HUSKY=0`, `GIT_CONFIG_*` and an inline `-c alias.x='commit --no-verify'`.
- Reads past what stands in front of git: `sudo`, `env`, `time`, `exec` and the other wrappers, subshells, brace groups, `if` and loops, `$(…)`, backticks and `$'…'`, `bash -c`, `eval`, and heredocs that a shell runs. A message that mentions a flag, `-n` outside `commit` and `am`, and heredocs that only write text pass, Claude's own `git commit -m "$(cat <<'EOF' …)"` form included.
- Fails closed on a payload or a command it cannot read. Without `jq` it denies the commands that could involve git, says why, and lets the rest run.
- Needs Claude Code 2.1.295 or later, for the `onFailure` field, and `jq`.

[Unreleased]: https://github.com/nerymurillohnd/the-claude-factory/compare/block-no-verify--v0.1.0...HEAD
[0.1.0]: https://github.com/nerymurillohnd/the-claude-factory/releases/tag/block-no-verify--v0.1.0
